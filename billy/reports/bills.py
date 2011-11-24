import datetime
from collections import defaultdict

from billy import db


def _bill_report_dict():
    return {'bill_count': 0,
            'bill_types': defaultdict(int),
            '_updated_this_year_count': 0,
            '_updated_this_month_count': 0,
            '_updated_today_count': 0,
            'actions_unsorted': set(),
            'actionless': set(),
            'action_count': 0,
            'actions_per_type': defaultdict(int),
            'actions_per_actor': defaultdict(int),
            'actions_per_month': defaultdict(int),
            'sponsorless': set(),
            '_sponsor_count': 0,
            '_sponsors_with_leg_id_count': 0,
            'sponsors_per_type': defaultdict(int),
            'vote_count': 0,
            '_passed_vote_count': 0,
            'votes_per_month': defaultdict(int),
            'votes_per_chamber': defaultdict(int),
            'votes_per_type': defaultdict(int),
            'bad_vote_counts': set(),
            '_rollcall_count': 0,
            '_rollcalls_with_leg_id_count': 0,
            '_subjects_count': 0,
            'bills_per_subject': defaultdict(int),
            'sourceless': set(),
            'versionless': set(),
           }



def scan_bills(abbr):
    metadata = db.metadata.find_one({'_id': abbr})
    level = metadata['level']

    yesterday = datetime.datetime.utcnow() - datetime.timedelta(days=1)
    last_month = datetime.datetime.utcnow() - datetime.timedelta(days=30)
    last_year = datetime.datetime.utcnow() - datetime.timedelta(days=365)

    duplicate_sources = defaultdict(int)
    duplicate_versions = defaultdict(int)
    sessions = defaultdict(_bill_report_dict)

    for bill in db.bills.find({'level': level, level: abbr}):
        session_d = sessions[bill['session']]

        # normal bill count & bill_types
        session_d['bill_count'] += 1
        for type in bill['type']:
            session_d['bill_types'][type] += 1

        # updated date
        if bill['updated_at'] >= yesterday:
            session_d['_updated_today_count'] += 1
            if bill['updated_at'] >= last_month:
                session_d['_updated_this_month_count'] += 1
                if bill['updated_at'] >= last_year:
                    session_d['_updated_this_year_count'] += 1

        # actions
        last_date = datetime.datetime(1900,1,1)
        for action in bill['actions']:
            date = action['date']
            if date < last_date:
                session_d['actions_unsorted'].add(bill['_id'])
            session_d['action_count'] += 1
            for type in action['type']:
                session_d['actions_per_type'][type] += 1
            session_d['actions_per_actor'][action['actor']] += 1
            session_d['actions_per_month'][date.strftime('%Y-%m')] += 1
        if not bill['actions']:
            session_d['actionless'].add(bill['_id'])

        # sponsors
        for sponsor in bill['sponsors']:
            session_d['_sponsor_count'] += 1
            if sponsor.get('leg_id'):
                session_d['_sponsors_with_leg_id_count'] += 1
            session_d['sponsors_per_type'][sponsor['type']] += 1
        if not bill['sponsors']:
            session_d['sponsorless'].add(bill['_id'])

        # votes
        for vote in bill['votes']:
            session_d['vote_count'] += 1
            if vote['passed']:
                session_d['_passed_vote_count'] += 1
            session_d['votes_per_type'][vote['type']] += 1
            session_d['votes_per_chamber'][vote['chamber']] += 1
            session_d['votes_per_month'][vote['date'].strftime('%Y-%m')] += 1

            # roll calls
            has_rollcalls = False
            for rc in (vote['yes_votes'] + vote['no_votes'] +
                       vote['other_votes']):
                has_rollcalls = True
                session_d['_rollcall_count'] += 1
                if rc.get('leg_id'):
                    session_d['_rollcalls_with_leg_id_count'] += 1

            # check counts if any rollcalls are present
            if (has_rollcalls and
                (len(vote['yes_votes']) != vote['yes_count'] or
                 len(vote['no_votes']) != vote['no_count'] or
                 len(vote['other_votes']) != vote['other_count'])):
                session_d['bad_vote_counts'].add(bill['_id'])

        # subjects
        if bill.get('subjects'):
            session_d['_subjects_count'] += 1
            for subject in bill['subjects']:
                session_d['bills_per_subject'][subject] += 1

        # sources
        for source in bill['sources']:
            duplicate_sources[source['url']] += 1
        if not bill['sources']:
            session_d['sourceless'].add(bill['_id'])

        # versions
        if not bill['versions']:
            session_d['versionless'].add(bill['_id'])
        for doc in (bill['versions'] + bill['documents']):
            duplicate_versions[doc['url']] += 1

    dup_version_urls = []
    dup_source_urls = []
    for url, n in duplicate_versions.iteritems():
        if n > 1:
            dup_version_urls.append(url)
    for url, n in duplicate_sources.iteritems():
        if n > 1:
            dup_source_urls.append(url)

    return {'duplicate_versions': dup_version_urls,
            'duplicate_sources': dup_source_urls,
            'sessions': sessions,
           }

def combine_bill_reports(reports):
    report = _bill_report_dict()

    for session in reports.itervalues():
        # go over all report fields
        # integers are summed, sets are combined, and dicts summed by key
        for field, value in report.iteritems():
            if isinstance(value, int):
                report[field] += session[field]
            elif isinstance(value, set):
                report[field].update(session[field])
                session[field] = list(session[field])
            elif isinstance(value, defaultdict):
                for k, v in session[field].iteritems():
                    report[field][k] += v

    for field, value in report.iteritems():
        if isinstance(value, set):
            report[field] = list(value)
    return report

def calculate_percentages(report):
    # general bill stuff
    bill_count = float(report['bill_count'])/100
    if bill_count:
        report['updated_this_year'] = (report.pop('_updated_this_year_count') /
                                       bill_count)
        report['updated_this_month'] = (report.pop('_updated_this_month_count') /
                                        bill_count)
        report['updated_today'] = (report.pop('_updated_today_count') /
                                   bill_count)
        report['have_subjects'] = report.pop('_subjects_count') / bill_count

    # actions
    action_count = float(report['action_count'])/100
    if action_count:
        for k in report['actions_per_type'].iterkeys():
            report['actions_per_type'][k] /= action_count
        for k in report['actions_per_actor'].iterkeys():
            report['actions_per_actor'][k] /= action_count
        for k in report['actions_per_month'].iterkeys():
            report['actions_per_month'][k] /= action_count

    # sponsors
    _sponsor_count = float(report.pop('_sponsor_count'))/100
    if _sponsor_count:
        report['sponsors_with_leg_id'] = (
            report.pop('_sponsors_with_leg_id_count') / _sponsor_count)
        for k in report['sponsors_per_type'].iterkeys():
            report['sponsors_per_type'][k] /= _sponsor_count

    # votes
    vote_count = float(report['vote_count'])/100
    if vote_count:
        report['votes_passed'] = report.pop('_passed_vote_count') / vote_count
        for k in report['votes_per_type'].iterkeys():
            report['votes_per_type'][k] /= vote_count
        for k in report['votes_per_chamber'].iterkeys():
            report['votes_per_chamber'][k] /= vote_count
        for k in report['votes_per_month'].iterkeys():
            report['votes_per_month'][k] /= vote_count
    rollcall_count = float(report.pop('_rollcall_count'))/100
    if rollcall_count:
        report['rollcalls_with_leg_id'] = (
            report.pop('_rollcalls_with_leg_id_count') / rollcall_count
        )


def bill_report(abbr):
    report = scan_bills(abbr)
    combined_report = combine_bill_reports(report['sessions'])
    for session in report['sessions'].itervalues():
        calculate_percentages(session)
    calculate_percentages(combined_report)
    report.update(combined_report)
    return report