from django.urls import path
from .views import *

urlpatterns = [
    # path('', UserList.as_view(), name='user-list'),
    path('<int:pk>/', UserDetail.as_view(), name='user-detail'),
    path('login/', LoginAPIView.as_view(), name='login'),

]
