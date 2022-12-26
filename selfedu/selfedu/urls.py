"""selfedu URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from selfedu import settings
from players.views import pageNotFound, PlayerAPIList, PlayerAPIUpdate, PlayerAPIDetailView, PlayerViewSet
from players.views import PlayerAPIView, PlayerAPIViewV2
from rest_framework import routers


router = routers.SimpleRouter()
router.register(r'player', PlayerViewSet, basename='player ')


urlpatterns = [
    path('admin/', admin.site.urls),
    path('captcha/', include('captcha.urls')),
    path('', include('players.urls')),
    path('api/v1/playerlist/', PlayerAPIView.as_view()),
    path('api/v2/playerlist/', PlayerAPIViewV2.as_view()),
    path('api/v2/playerlist/<int:pk>/', PlayerAPIViewV2.as_view()),
    path('api/v3/playerlist/', PlayerAPIList.as_view()),
    path('api/v3/playerlist/<int:pk>/', PlayerAPIUpdate.as_view()),
    path('api/v3/playerdetail/<int:pk>/', PlayerAPIDetailView.as_view()),
    path('api/v4/playerdetail/', PlayerViewSet.as_view({'get': 'list'})),
    path('api/v4/playerdetail/<int:pk>/', PlayerViewSet.as_view({'put': 'update'})),
    path('api/v5/', include(router.urls)),

]

if settings.DEBUG:
    import debug_toolbar

    urlpatterns = [
        path('__debug__/', include(debug_toolbar.urls))
    ] + urlpatterns

    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


handler404 = pageNotFound
