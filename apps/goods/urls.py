from django.urls import path
from apps.goods.views import IndexView,ListView
from apps.goods.views import SKUSearchView,DetailView,CategoryVisitCountView

urlpatterns = [
    path('index/',IndexView.as_view()),
    path('list/<category_id>/skus/',ListView.as_view()),

    path('search/',SKUSearchView()),

    path('detail/<sku_id>/',DetailView.as_view()),

    path('detail/visit/<category_id>/',CategoryVisitCountView.as_view()),
]