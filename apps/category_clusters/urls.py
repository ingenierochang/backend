from django.urls import path
from apps.category_clusters.views.category_cluster import CategoryClusterView
from apps.category_clusters.views.update_category_cluster_order import update_category_cluster_order


urlpatterns = [

    path('', CategoryClusterView.as_view(), name='handle_category_cluster'),
    path('<int:category_cluster_id>/', CategoryClusterView.as_view(), name='handle_category_cluster'),
    path('order/', update_category_cluster_order, name='update-category-cluster-order'),

]
