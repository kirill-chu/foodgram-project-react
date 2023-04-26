from django.urls import include, path
from rest_framework import routers

from .views import CreateUserViewset

router_v1 = routers.DefaultRouter()
router_v1.register('users', CreateUserViewset)

urlpatterns = [
    path('', include(router_v1.urls))
]
