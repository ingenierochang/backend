from django.urls import path
from apps.categories.views.category import CategoryView
from apps.categories.views.update_categories_order import update_categories_order
from apps.categories.views.update_category_products_order import update_category_products_order

urlpatterns = [
    path('', CategoryView.as_view(), name='handle_category'),
    path('<int:category_id>/', CategoryView.as_view(), name='handle_category'),

    path('order/', update_categories_order, name='update-categories-order'),


    path('<str:category_slug>/update-products-order/', update_category_products_order, name='update_category_products_order'),

]
