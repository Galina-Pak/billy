from django.conf.urls import url

from billy.web.public.views.misc import VotesList
from billy.web.public.views.bills import (BillList, AllBillList,
                                          AllBillCSVList, BillFeed)
from billy.web.public.feeds import VotesListFeed, EventsFeed
from django.views.decorators.csrf import ensure_csrf_cookie

from billy.web.public.views import misc, region, events, legislators, committees, bills

# misc. views
urlpatterns = [
    url(r'^$', misc.homepage, name='homepage'),
    url(r'^downloads/$', misc.downloads, name='downloads'),
    url(r'^find_your_legislator/$', misc.find_your_legislator,
        name='find_your_legislator'),
    url(r'^get_district/(?P<district_id>.+)/$', misc.get_district,
        name='get_district'),

    # votes
    url(r'^(?P<abbr>[a-z-]+)/(?P<collection_name>[\w-]+)'
        '/(?P<_id>[\w-]+)/votes/$', VotesList.as_view(), name='votes_list'),
    url(r'^(?P<abbr>[a-z-]+)/(?P<collection_name>[\w-]+)/(?P<_id>[\w-]+)/'
        'votes/rss/$',
        VotesListFeed(), name='votes_list_rss'),

    # region specific
    url(r'^(?P<abbr>[a-z-]+)/search/$', region.search, name='search'),
    url(r'^(?P<abbr>[a-z-]+)/$', region.region, name='region'),
    url(r'^region_selection/$', region.region_selection, name='region_selection'),

    # events
    url(r'^(?P<abbr>[a-z-]+)/events/$', events.events,
        name='events'),
    url(r'^(?P<abbr>[a-z-]+)/events/rss/$', EventsFeed(),
        name='events_rss'),
    url(r'^(?P<abbr>[a-z-]+)/events/json_for_date/(?P<year>\d+)/(?P<month>\d+)/',
        events.events_json_for_date, name='events_json_for_date'),
    url(r'^(?P<abbr>[a-z-]+)/events/(?P<event_id>[\w-]+)/', events.event,
        name='event'),
    url(r'^(?P<abbr>[a-z-]+)/ical/(?P<event_id>[\w-]+)/', events.event_ical,
        name='event_ical'),

    # committees
    url(r'^(?P<abbr>[a-z-]+)/committees/$', committees.committees, name='committees'),
    url(r'^(?P<abbr>[a-z-]+)/committees/(?P<committee_id>[A-Z]{3}\d+)/',
        committees.committee, name='committee'),

    # legislators
    url(r'^(?P<abbr>[a-z-]+)/legislators/$', legislators.legislators,
        name='legislators'),
    url(r'^(?P<abbr>[a-z-]+)/legislators/(?P<_id>[\w-]+)/(?P<slug>[^/]*)/$',
        legislators.legislator, name='legislator'),
    url(r'^(?P<abbr>[a-z-]+)/legislators/(?P<_id>[\w-]+)/$',
        legislators.legislator, name='legislator_noslug'),

    # bills
    url(r'^(?P<abbr>all)/bills/$', ensure_csrf_cookie(AllBillList.as_view()),
        name='all_bills'),
    url(r'^(?P<abbr>all)/bills-csv/$',
        ensure_csrf_cookie(AllBillCSVList.as_view()), name='all_bills_csv'),
    url(r'^(?P<abbr>[a-z-]+)/bills/$', ensure_csrf_cookie(BillList.as_view()),
        name='bills'),
    url(r'^(?P<abbr>[a-z-]+)/bills/feed/$', BillFeed.as_view(),
        name='bills_feed'),
    url(r'^(?P<abbr>[a-z-]+)/bills/(?P<session>[^/]+)/(?P<bill_id>[^/]+)/$',
        bills.bill, name='bill'),
    url(r'^(?P<abbr>[a-z-]+)/(?P<bill_id>[^/]+)/$',
        bills.bill_noslug, name='bill_noslug'),
    url(r'^(?P<abbr>[a-z-]+)/bills/(?P<session>[^/]+)/'
        r'(?P<bill_id>[^/]+)/(?P<key>documents)/$', bills.all_documents,
        name='bill_all_documents'),
    url(r'^(?P<abbr>[a-z-]+)/bills/(?P<session>[^/]+)/'
        r'(?P<bill_id>[^/]+)/documents/(?P<doc_id>[\w-]+)/$', bills.document,
        name='document'),
    url(r'^(?P<abbr>[a-z-]+)/bills/(?P<session>[^/]+)/'
        r'(?P<bill_id>[^/]+)/(?P<key>versions)/$', bills.all_versions,
        name='bill_all_versions'),
    url(r'^(?P<abbr>[a-z-]+)/votes/(?P<vote_id>[\w-]+)/$',
        bills.vote, name='vote'),
]
