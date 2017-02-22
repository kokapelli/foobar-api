from django.conf import settings
from django.conf.urls import include, url
from django.contrib import admin

from rest_framework_swagger.views import get_swagger_view
import foobar.views
import rest_framework.urls

from .rest.urls import router

schema_view = get_swagger_view(title='FooBar API')

urlpatterns = [
    url(r'^api/', include(router.urls, namespace='api')),
    url(r'^docs/', schema_view),
    url(r'^api-auth/', include(rest_framework.urls,
        namespace='rest_framework')),
    url(r'^admin/wallet_management/(?P<obj_id>.+)',
        foobar.views.wallet_management,
        name="wallet_management"),
    url(r'^admin/foobar/account/card/(?P<card_id>\d+)',
        foobar.views.account_for_card, name='account_for_card'),
    url(r'^admin/', include(admin.site.urls)),
]

if settings.DEBUG:
    try:
        import debug_toolbar
        urlpatterns += [
            url(r'^__debug__/', include(debug_toolbar.urls)),
        ]
    except ImportError:
        pass
