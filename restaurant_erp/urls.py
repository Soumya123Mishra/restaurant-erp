from django.urls import path
from . import views
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin

urlpatterns = [
    # Root URL jo home view par jayega
    path('', views.home, name='home'),
    
    path('admin/', admin.site.urls),
    
    # Auth URLs (Yeh missing the isliye error aaya)
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard_redirect, name='dashboard'),
    
    # Role-based Dashboards
    path('dashboard/owner/', views.owner_dashboard, name='owner_dashboard'),
    path('dashboard/manager/', views.manager_dashboard, name='manager_dashboard'),
    path('dashboard/waiter/', views.waiter_dashboard, name='waiter_dashboard'),
    path('dashboard/chef/', views.chef_dashboard, name='chef_dashboard'),

    # Employees
    path("employees/", views.employee_list, name="employee_list"),
    path("employees/new/", views.employee_create, name="employee_create"),
    path("employees/<int:pk>/edit/", views.edit_employee, name="edit_employee"),
    path("employees/<int:pk>/delete/", views.delete_employee, name="delete_employee"),
  
    # Inventory
    path('inventory/', views.inventory_list, name='inventory_list'),
    path('inventory/new/', views.inventory_create, name='inventory_create'),
    path('inventory/<int:pk>/edit/', views.inventory_edit, name='inventory_edit'),
    path('inventory/<int:pk>/delete/', views.inventory_delete, name='inventory_delete'),

    # Menu
    path("menu/", views.menu_list, name="menu_list"),
    path("menu/new/", views.menu_create, name="menu_create"),
    path("menu/<int:pk>/edit/", views.edit_menu, name="edit_menu"),
    path("menu/<int:pk>/delete/", views.delete_menu, name="delete_menu"),

    # Orders
    path("orders/", views.order_list, name="order_list"),
    path("orders/new/", views.order_create, name="order_create"),
    path("orders/<int:pk>/edit/", views.order_edit, name="order_edit"),
    path("orders/<int:pk>/delete/", views.order_delete, name="order_delete"),
    path("orders/<int:pk>/", views.order_detail, name="order_detail"),
    path("orders/<int:pk>/paid/", views.order_mark_paid, name="order_mark_paid"),
    
    # Bill
    path("orders/<int:pk>/bill/", views.order_bill, name="order_bill"),
    
    # Feedback
    path('order/<int:order_id>/feedback/', views.add_feedback, name='add_feedback'),
    
    # Kitchen
    path('kitchen/', views.kitchen_dashboard, name='kitchen_dashboard'),
    path('kitchen/update/<int:order_id>/', views.update_order_status, name='update_order_status'),
    path('kitchen/orders-list/', views.kitchen_orders_list, name='kitchen_orders_list'), 
    
    # Reports
    path("reports/", views.reports_dashboard, name="reports_dashboard"),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
