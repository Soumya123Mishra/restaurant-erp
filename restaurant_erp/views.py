from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum
from .models import Employee, MenuItem,Order, STATUS,OrderItem, Inventory,Feedback
from .forms import  EmployeeForm, MenuItemForm,MenuItemIngredient,MenuItemIngredientFormSet, OrderForm, OrderItemFormSet,InventoryForm,FeedbackForm
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from decimal import Decimal
# from bson.decimal128 import Decimal128
from django.http import HttpResponse
#  Login Redirect 
from django.contrib.auth.forms import AuthenticationForm
def login_view(request):
    form = AuthenticationForm(request, data=request.POST or None)
    if request.method == "POST":
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect("dashboard")
    return render(request, "login.html", {"form": form})

@login_required
def logout_view(request):
    logout(request)
    return redirect("login")

def home(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    else:
        return redirect('login')  
#Dashboard

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

@login_required
def dashboard_redirect(request):
    """Redirect user to their role-based dashboard"""
    user = request.user
    if user.is_superuser or user.groups.filter(name='Owner').exists():
        return redirect('owner_dashboard')
    elif user.groups.filter(name='Manager').exists():
        return redirect('manager_dashboard')
    elif user.groups.filter(name='Waiter').exists():
        return redirect('waiter_dashboard')
    elif user.groups.filter(name='Chef').exists():
        return redirect('chef_dashboard')
    else:
        # Default fallback dashboard
        return redirect('waiter_dashboard')


# Individual Dashboards
@login_required
def owner_dashboard(request):
    recent_orders = list(Order.objects.order_by('-created_at')[:5])
    total_orders = Order.objects.count()
    
    # SQLite compatible total sales calculation using aggregate Sum
    total_sales_sum = Order.objects.aggregate(sum_sales=Sum('total_price'))['sum_sales']
    total_sales = float(total_sales_sum) if total_sales_sum else 0.0
    
    total_employees = Employee.objects.count()
    context = {
        'total_orders': total_orders,
        'total_sales': total_sales,
        'total_employees': total_employees,
        'recent_orders': recent_orders,
    }
    return render(request, 'owner_dashboard.html', context)

@login_required
def manager_dashboard(request):
    low_stock_items = MenuItemIngredient.objects.filter(quantity__lte=5)
    orders = Order.objects.all().order_by('-created_at')[:5]
    context = {
        'low_stock_items': low_stock_items,
        'recent_orders': orders,
    }
    return render(request, 'manager_dashboard.html', context)

@login_required
def waiter_dashboard(request):
    pending = Order.objects.filter(status__in=['pending','new']).order_by('-created_at')
    preparing = Order.objects.filter(status='preparing').order_by('-created_at')
    ready = Order.objects.filter(status='ready').order_by('-created_at')
    completed = Order.objects.filter(status='completed').order_by('-created_at') 
    feedbacks=Feedback.objects.filter(order__in=completed).order_by('created_at')
    context = {
        'pending_orders': pending,
        'preparing_orders': preparing,
        'ready_orders': ready,
        'completed_orders': completed,
        'feedbacks':feedbacks,
    }
    return render(request, 'waiter_dashboard.html', context)
    
@login_required
def chef_dashboard(request):
    pending_orders = Order.objects.filter(status='pending').order_by('created_at')
    preparing_orders = Order.objects.filter(status='preparing').order_by('created_at')
    ready_orders = Order.objects.filter(status='ready').order_by('created_at')
    completed = Order.objects.filter(status='completed').order_by('-created_at') 
    feedbacks=Feedback.objects.all().order_by('created_at')
    
    context = {
        'pending_orders': pending_orders,
        'preparing_orders': preparing_orders,
        'ready_orders': ready_orders,
         'completed_orders': completed,
        'feedbacks':feedbacks,
    }
    return render(request, 'chef_dashboard.html', context)

#  Employees 
def employee_list(request):
    employees = Employee.objects.all()
    return render(request, 'employee_list.html', {'employees': employees})

def employee_create(request):
    if request.method == 'POST':
        form = EmployeeForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('employee_list')
    else:
        form = EmployeeForm()
    return render(request, 'employee_form.html', {'form': form})

def edit_employee(request, pk):
    employee = get_object_or_404(Employee, pk=pk)
    if request.method == 'POST':
        form = EmployeeForm(request.POST, instance=employee)
        if form.is_valid():
            form.save()
            return redirect('employee_list')
    else:
        form = EmployeeForm(instance=employee)
    return render(request, 'edit_employee.html', {'form': form})

def delete_employee(request, pk):
    employee = get_object_or_404(Employee, pk=pk)
    employee.delete()
    return redirect('employee_list')
#Inventory
def inventory_list(request):
    items = Inventory.objects.all()
    return render(request, 'inventory_list.html', {
        'inventory_list': items
    })

def inventory_create(request):
    if request.method == "POST":
        form = InventoryForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Inventory Added Successfully.")
            return redirect('inventory_list')
    else:
        form = InventoryForm()

    return render(request, 'inventory_form.html', {'form': form})

def inventory_edit(request, pk):    
    item = get_object_or_404(Inventory, pk=pk)
    form = InventoryForm(request.POST or None, instance=item)
    if form.is_valid():
        form.save()
        messages.success(request, "Inventory Updated Successfully.")
        return redirect('inventory_list')

    return render(request, 'inventory_edit.html', {
        'form': form,
        'item': item
    })

def inventory_delete(request, pk):
    item = get_object_or_404(Inventory, pk=pk)
    if request.method == "POST":
        item.delete()
        messages.success(request, "Item deleted.")
        return redirect('inventory_list')

    return render(request, "confirm_delete.html", {"item": item})

#Menu

def menu_list(request):
    menus = MenuItem.objects.all()
    return render(request, 'menu_list.html', {'menus': menus})

from django.shortcuts import render, redirect
from .forms import MenuItemForm, MenuItemIngredientFormSet

 
def menu_create(request):
    if request.method == "POST":
        form = MenuItemForm(request.POST, request.FILES)
        formset = MenuItemIngredientFormSet(request.POST) # Formset ko yahan define karein

        if form.is_valid() and formset.is_valid():
            menu_item = form.save(commit=False)
            formset.instance = menu_item
            menu_item.save()  
            formset.save()  
            messages.success(request, "Menu created successfully.") 
            return redirect("menu_list")
        else:
            print("FORM ERRORS:", form.errors)
            print("FORMSET ERRORS:", formset.errors)

        return render(request, "menu_form.html", {'form': form, 'formset': formset})    
    else:
        form = MenuItemForm()
        formset = MenuItemIngredientFormSet(instance=MenuItem())

    return render(request, "menu_form.html", {
        "form": form,
        "formset": formset,
    })


def edit_menu(request, pk):
    menu_item = get_object_or_404(MenuItem, pk=pk)

    if request.method == "POST":
        form = MenuItemForm(request.POST, request.FILES, instance=menu_item)
        formset = MenuItemIngredientFormSet(request.POST, instance=menu_item)

        if form.is_valid() and formset.is_valid():
            form.save()  
            formset.save()
            messages.success(request, "Menu Updated Successfully.")
            return redirect('menu_list')
       
    else:
        form = MenuItemForm(instance=menu_item)
        formset = MenuItemIngredientFormSet(instance=menu_item)

    return render(request, 'menu_form.html', {
        'form': form,
        'formset': formset
    })
    
def delete_menu(request, pk):
    menu_item = get_object_or_404(MenuItem, pk=pk)
    if request.method == "POST":
        menu_item.delete()
        messages.success(request, "Menu item deleted successfully!")
        return redirect("menu_list")
    return render(request, "confirm_delete.html", {"menu_item": menu_item})
#  Orders 
@login_required
def order_list(request):
    orders = Order.objects.all().order_by("-created_at")
    return render(request, "order_list.html", {"orders": orders})

@login_required
def order_create(request):
    if request.method == "POST":
        form = OrderForm(request.POST)
        order_items = OrderItemFormSet(request.POST)

        if form.is_valid() and order_items.is_valid():
            order = form.save(commit=False)
            order.save()
            order_items.instance = order
            order_items.save()

            order.update_total()
            messages.success(request, f"Order #{order.id} created successfully!")
            return redirect("order_list")
    else:
        form = OrderForm()
        order_items = OrderItemFormSet()

    return render(request, "order_form.html", {
        "form": form,
        "order_items": order_items,
    })
@login_required
def order_edit(request, pk):
    order = get_object_or_404(Order, pk=pk)

    if request.method == "POST":
        form = OrderForm(request.POST, instance=order)
        order_items = OrderItemFormSet(request.POST, instance=order)

        if form.is_valid() and order_items.is_valid():
            order=  form.save(commit=False)
            order_items.save()
            order.update_total()
            order.save()
            messages.success(request, f"Order #{order.id} updated successfully!")
            return redirect("order_list")
    else:
        form = OrderForm(instance=order)
        order_items = OrderItemFormSet(instance=order)

    return render(request, "order_form.html", {
        "form": form,
        "order_items": order_items,
    })


@login_required
def order_delete(request, pk):
    order = get_object_or_404(Order, pk=pk)
    order.delete()
    messages.success(request, "Order deleted successfully.")
    return redirect("order_list")


@login_required
def order_detail(request, pk):
    order = get_object_or_404(Order, pk=pk)
    items = order.items.all()
    return render(request, "order_detail.html", {"order": order, "items": items})
#  Mark Paid 
@login_required
def order_mark_paid(request, pk):
    order = get_object_or_404(Order, pk=pk)
    if not order.paid:
        order.paid = True
        if order.status != 'completed':
            order.status = 'completed'  
        order.save(update_fields=['paid', 'status'])
    if order.can_deduct_inventory():
        messages.success(request, "✅ Paid & Inventory Deducted Successfully")
    else:
        messages.warning(request, "✅ Paid. Inventory deduction attempted")    
    #messages.success(request, "✅ Paid & Inventory Deducted Successfully")
    return redirect('order_list')

#Bill generate
@login_required
def order_bill(request, pk):
    order = get_object_or_404(Order, pk=pk)
    items = order.items.all() 
    subtotal = order.get_total_price()       
    gst_rate = Decimal('0.05')                 
    gst_amount = subtotal * gst_rate          
    grand_total = subtotal + gst_amount
    return render(request,'order_bill.html',{'order':order,
                                                    'item':items,
                                                    "subtotal": subtotal,
                                                    "gst_rate": "5%",
                                                    "gst_amount": gst_amount, 
                                                    "grand_total": grand_total,})

# Customer Feedback 
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Order, Feedback
from .forms import FeedbackForm

def add_feedback(request, order_id):
    # Step 1: Get the order
    order = get_object_or_404(Order, id=order_id)

    # Step 2: Check if feedback already exists
    feedback_instance = Feedback.objects.filter(order=order).first()

    # Step 3: If order is not completed, restrict feedback
    if order.status != "completed":
        messages.warning(request, "Feedback can be submitted only after the order is completed.")
        return redirect("order_list")   # Replace with your actual orders page URL name

    # Step 4: Handle POST request
    if request.method == "POST":
        form = FeedbackForm(request.POST, instance=feedback_instance or Feedback(order=order))
        if form.is_valid():
            feedback = form.save(commit=False)
            feedback.order = order
            feedback.save()
            messages.success(request, "Thank you for your feedback!")
            return redirect("order_list")   # Redirect after successful feedback submission
    else:
        form = FeedbackForm(instance=feedback_instance or Feedback(order=order))

    # Step 5: Render template
    return render(request, "order_feedback.html", {
        "form": form,
        "order": order
    })
# Kitchen Module
@login_required
def kitchen_dashboard(request):
    orders = Order.objects.exclude(status='completed').order_by('-created_at')
    return render(request, 'kitchen_dashboard.html', {'orders': orders,'status_choices':STATUS})

@login_required
def update_order_status(request,order_id):
    order = get_object_or_404(Order,id=order_id)
    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status in dict(STATUS):
            order.status = new_status
            order.save()
    return redirect('kitchen_dashboard')
@login_required
def kitchen_orders_list(request):
    orders = Order.objects.exclude(status='completed').order_by('-created_at')
    return render(request, 'kitchen_orders_list.html', {'orders': orders,'status_choices':STATUS})

#Reports Dashboard
from django.utils import timezone
@login_required
def reports_dashboard(request):
    # Total Sales (SQLite compatible)
    total_sales = Order.objects.aggregate(sum_sales=Sum('total_price'))['sum_sales'] or Decimal('0.00')

    # Monthly Sales
    today = timezone.localtime()
    start_month = today.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    monthly_sales = Order.objects.filter(
        created_at__gte=start_month
    ).aggregate(sum_monthly=Sum('total_price'))['sum_monthly'] or Decimal('0.00')
    # Most Ordered Dishes
    top_dishes = (
        OrderItem.objects.values("menu_item__name")
        .annotate(total_qty=Sum("quantity"))
        .order_by("-total_qty")[:5]
    )
    # Low Stock Items (below 10 units)
    low_stock = Inventory.objects.filter(quantity__lt=5.0)

    context = {
        "total_sales": total_sales,
        "monthly_sales": monthly_sales,
        "top_dishes": top_dishes,
        "low_stock": low_stock,
    }
    return render(request, "reports_dashboard.html", context)