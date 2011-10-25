from django.conf.urls.defaults import patterns

urlpatterns = patterns('',
                       (r'^$',
                        'errormon.views.home'),
                       (r'^status/$',
                        'errormon.views.status'),
                       (r'^status_summary/$',
                         'errormon.views.status_summary'),
                       (r'^delete_old/$',
                         'errormon.views.delete_old'),
                       (r'^sample_error/$',
                         'errormon.views.sample_error'),
                       )
