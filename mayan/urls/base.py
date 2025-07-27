from django.urls import include, re_path

__all__ = ('urlpatterns',)

urlpatterns = [
    # Research platform URLs - using urlpatterns from urls directory
    re_path(
        route=r'^research/', 
        view=include(('mayan.apps.research.urls.urlpatterns', 'research'))
    ),
]
