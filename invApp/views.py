from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from .models import Product
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from django.http import JsonResponse
from django.urls import reverse
from .forms import ProductForm, RegistrationForm, OrderOutForm, ShipmentOutForm, ReturnForm, ShipmentInForm, StockInForm, DamageReturnForm, ProductOnHoldForm, ComboProductForm, UploadFileForm
from .models import Product, UserProfile, OrderOut, ShipmentOut, Return, ShipmentIn, StockIn, DamageReturn, ProductOnHold, ComboProduct
from django.contrib.auth.decorators import login_required
import barcode
from barcode.writer import ImageWriter
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from PIL import Image, ImageDraw, ImageFont
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
import os
import re
import logging
import fitz  # PyMuPDF
import io
import PyPDF2
import openpyxl
from reportlab.lib.pagesizes import A4  # Adjust the import to include A4
from tempfile import NamedTemporaryFile
from reportlab.lib.utils import ImageReader
from reportlab.graphics.barcode import code128
import json
from datetime import datetime
from django.db.models.functions import ExtractMonth, ExtractYear
from django.utils import timezone
from PyPDF2 import PdfReader, PdfWriter
from django.utils.timezone import now, timedelta
import pandas as pd



# Home View

from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.db.models import Sum


def get_total(queryset, field_name):
    return queryset.aggregate(total=Sum(field_name))['total'] or 0
@login_required
def dashboard_view(request):

    current_year = datetime.now().year
    years = range(current_year, 1999, -1)  # From current year to 2000
    # Get the current user's profile
    user = request.user
    try:
        user_profile = UserProfile.objects.get(user=user)
        current_company_name = user_profile.company_name
    except UserProfile.DoesNotExist:
        # Handle the case where the user profile does not exist
        return render(request, 'invApp/dashboard.html', {'error': 'Profile not found for this user'})

    today = now().date()  # Get today's date
    yesterday = today - timedelta(days=1)
    last_7_days = today - timedelta(days=7)
    last_15_days = today - timedelta(days=15)
    last_month = today.replace(day=1) - timedelta(days=1)

    total_orders_count = OrderOut.objects.filter(user__userprofile__company_name=current_company_name).aggregate(total=Sum('quantity'))['total'] or 0
    orders_yesterday = OrderOut.objects.filter(
        user__userprofile__company_name=current_company_name,
        date=yesterday
    ).aggregate(total=Sum('quantity'))['total'] or 0

    orders_last_7_days = OrderOut.objects.filter(
        user__userprofile__company_name=current_company_name,
        date__gte=last_7_days
    ).aggregate(total=Sum('quantity'))['total'] or 0

    orders_last_15_days = OrderOut.objects.filter(
        user__userprofile__company_name=current_company_name,
        date__gte=last_15_days
    ).aggregate(total=Sum('quantity'))['total'] or 0

    orders_last_month = OrderOut.objects.filter(
        user__userprofile__company_name=current_company_name,
        date__year=last_month.year,
        date__month=last_month.month
    ).aggregate(total=Sum('quantity'))['total'] or 0

    total_returns_count = Return.objects.filter(user__userprofile__company_name=current_company_name).aggregate(total=Sum('quantity'))['total'] or 0
    total_shipment_in_count = ShipmentIn.objects.filter(user__userprofile__company_name=current_company_name).aggregate(total=Sum('quantity'))['total'] or 0
    total_shipment_out_count = ShipmentOut.objects.filter(user__userprofile__company_name=current_company_name).aggregate(total=Sum('quantity'))['total'] or 0
    total_productonhold_count = ProductOnHold.objects.filter(user__userprofile__company_name=current_company_name).aggregate(total=Sum('quantity'))['total'] or 0

    products = Product.objects.all()

    products_data = []
    low_stock_products = []
    for product in products:
        # Calculate totals for each product over the last 15 days
        total_orders_out_15_days = get_total(OrderOut.objects.filter(product=product, date__gte=last_15_days),
                                             'quantity')
        total_shipment_out_15_days = get_total(ShipmentOut.objects.filter(product=product, date__gte=last_15_days),
                                               'quantity')

        # Calculate the average daily consumption for the product
        total_consumed_15_days = total_orders_out_15_days + total_shipment_out_15_days
        average_daily_consumption = total_consumed_15_days / 15 if total_consumed_15_days > 0 else 0

        # Calculate totals for each product
        total_orders_out = get_total(OrderOut.objects.filter(product=product), 'quantity')
        total_returns_in = get_total(Return.objects.filter(product=product), 'quantity')
        total_shipment_in = get_total(ShipmentIn.objects.filter(product=product), 'quantity')
        total_shipment_out = get_total(ShipmentOut.objects.filter(product=product), 'quantity')
        total_stock_in = get_total(StockIn.objects.filter(product=product), 'quantity')
        total_productonhold = get_total(ProductOnHold.objects.filter(product=product), 'quantity')

        # Calculate TotalAvailable using the provided formula
        total_available = (total_stock_in + total_returns_in + total_shipment_in) - (
                    total_orders_out + total_shipment_out)

        # Check if available stock is less than the required stock for the next 15 days
        required_stock_for_15_days = average_daily_consumption * 15
        if total_available < required_stock_for_15_days:
            low_stock_products.append({
                'ProductName': product.name,
                'TotalAvailable': total_available,
                'AverageDailyConsumption': average_daily_consumption,
                'RequiredStockFor15Days': required_stock_for_15_days,
            })


        products_data.append({
            'ProductName': product.name,
            'TotalAvailable': total_available,
            'TotalOrdersCount': get_total(OrderOut.objects.filter(product=product), 'quantity'),
            'TotalReturnsCount': get_total(Return.objects.filter(product=product), 'quantity'),
            'TotalShipmentsInCount': get_total(ShipmentIn.objects.filter(product=product), 'quantity'),
            'TotalShipmentsOutCount': get_total(ShipmentOut.objects.filter(product=product), 'quantity'),
            'TotalStockInCount': get_total(StockIn.objects.filter(product=product), 'quantity'),
        })

        # Debugging statement
        print(products_data)  # Print the products data to the console


    selected_month = request.GET.get('selected_month', 0)

    # Top Selling Products
    top_selling_products = (OrderOut.objects
                            .filter(user__userprofile__company_name=current_company_name)  # Filter by supplier
                            .values('product__name')  # Group by product name
                            .annotate(total_orders=Sum('quantity'))  # Sum the quantity ordered
                            .order_by('-total_orders')[:10]  # Get the top 10 products
                            )



    # Prepare the context to send to the template
    context = {
        'years': years,
        'total_orders_count': total_orders_count,
        'total_returns_count': total_returns_count,
        'total_shipment_in_count': total_shipment_in_count,
        'total_shipment_out_count': total_shipment_out_count,
        'company_name': current_company_name,  # Pass the current company name for display
        'products': products_data,
        'top_selling_products': top_selling_products,
        'selected_month': selected_month,
        'orders_yesterday': orders_yesterday,
        'orders_last_7_days': orders_last_7_days,
        'orders_last_15_days': orders_last_15_days,
        'orders_last_month': orders_last_month,
        'low_stock_products': low_stock_products,
    }

    return render(request, 'invApp/dashboard.html', context)


def upload_excel_view(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            file = request.FILES['file']
            try:
                # Read the Excel file using pandas
                df = pd.read_excel(file)

                # Assuming your Excel file has the following columns:
                # 'Product Name', 'Quantity', 'Order Date', etc.
                for index, row in df.iterrows():
                    product_name = row['Product Name']
                    quantity = row['Quantity']
                    order_date = row['Order Date']
                    shipment_out = row['ShipmentOut']  # If you want to handle shipments

                    # Get or create product by name
                    product, created = Product.objects.get_or_create(name=product_name)

                    # Add data to the OrderOut table
                    OrderOut.objects.create(
                        product=product,
                        quantity=quantity,
                        date=order_date,
                    )

                    # Optionally handle ShipmentOut
                    ShipmentOut.objects.create(
                        product=product,
                        quantity=shipment_out,
                        date=order_date,
                    )

                messages.success(request, 'Data successfully uploaded and saved!')
                return redirect('dashboard')  # Redirect to dashboard or relevant page
            except Exception as e:
                messages.error(request, f"Error reading the file: {e}")
    else:
        form = UploadFileForm()

    return render(request, 'invApp/upload_excel.html', {'form': form})


# Register
def register_view(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            form.save()  # The form's save() method handles creating the user and profile
            messages.success(request, 'Registration successful! You can now log in.')
            return redirect('login')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = RegistrationForm()

    return render(request, 'invApp/register.html', {'form': form})

# Login

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            next_url = request.GET.get('next', 'product_list')  # Get 'next' param or redirect to default
            return redirect(next_url)
        else:
            messages.error(request, 'Invalid username or password.')
    return render(request, 'invApp/login.html')

# Logout
def logout_view(request):
    logout(request)
    return redirect('login')  # Redirect to the login page after logout

# Create View

@login_required
def product_create_view(request):
    # Query all products to get assigned locations and names
    assigned_products = Product.objects.values('section', 'subsection', 'name')

    if request.method == 'POST':
        form = ProductForm(request.POST)
        if form.is_valid():
            product = form.save(commit=False)
            product.user = request.user
            product.save()
            messages.success(request, 'Product created successfully!')
            return redirect('product_list')
    else:
        form = ProductForm()

    return render(request, 'invApp/product_form.html', {
        'form': form,
        'assigned_products': assigned_products,
    })


@login_required
def orderout_create(request):
    if request.method == 'POST':
        form = OrderOutForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)  # Don't save yet
            order.user = request.user  # Set the user to the currently logged-in user

            # Get the selected product and set the product name
            product = form.cleaned_data['product']
            order.product_name = product.name  # Ensure product_name field exists in your model

            order.save()  # Save the order
            return redirect('orderout_list')  # Redirect to the orderout list view
        else:
            print(form.errors)  # Print the form errors for debugging
    else:
        form = OrderOutForm()

    return render(request, 'invApp/orderout_create.html', {'form': form})


@login_required
def stockin_create(request):
    if request.method == 'POST':
        form = StockInForm(request.POST)
        if form.is_valid():
            stockin = form.save(commit=False)  # Don't save yet
            stockin.user = request.user  # Set the user to the currently logged-in user

            # Get the selected product and set the product name
            product = form.cleaned_data['product']
            stockin.product_name = product.name  # Ensure product_name field exists in your model

            stockin.save()  # Save the order
            return redirect('stockin_list')
        else:
            print(form.errors)  # Print the form errors for debugging
    else:
        form = StockInForm()

    return render(request, 'invApp/stockin_create.html', {'form': form})


@login_required
def return_create(request):
    if request.method == 'POST':
        form = ReturnForm(request.POST)
        if form.is_valid():
            returns = form.save(commit=False)  # Don't save yet
            returns.user = request.user  # Set the user to the currently logged-in user

            # Get the selected product and set the product name
            product = form.cleaned_data['product']
            returns.product_name = product.name  # Ensure product_name field exists in your model

            returns.save()  # Save the order
            return redirect('return_list')  # Redirect to the orderout list view
        else:
            print(form.errors)  # Print the form errors for debugging
    else:
        form = ReturnForm()

    return render(request, 'invApp/return_create.html', {'form': form})



@login_required
def damagereturn_create(request):
    if request.method == 'POST':
        form = DamageReturnForm(request.POST)
        if form.is_valid():
            damagereturns = form.save(commit=False)  # Don't save yet
            damagereturns.user = request.user  # Set the user to the currently logged-in user

            # Get the selected product and set the product name
            product = form.cleaned_data['product']
            damagereturns.product_name = product.name  # Ensure product_name field exists in your model

            damagereturns.save()  # Save the order
            return redirect('damagereturn_list')  # Redirect to the orderout list view
        else:
            print(form.errors)  # Print the form errors for debugging
    else:
        form = DamageReturnForm()

    return render(request, 'invApp/damagereturn_create.html', {'form': form})


@login_required
def shipmentout_create(request):
    if request.method == 'POST':
        form = ShipmentOutForm(request.POST)
        if form.is_valid():
            shipmentout = form.save(commit=False)  # Don't save yet
            shipmentout.user = request.user  # Set the user to the currently logged-in user

            # Get the selected product and set the product name
            product = form.cleaned_data['product']
            shipmentout.product_name = product.name  # Ensure product_name field exists in your model

            shipmentout.save()  # Save the order
            return redirect('shipmentout_list')  # Redirect to the orderout list view
        else:
            print(form.errors)  # Print the form errors for debugging
    else:
        form = ShipmentOutForm()

    return render(request, 'invApp/shipmentout_create.html', {'form': form})


def transfer_to_shipment_out(request, productonhold_id):
    # Use get_object_or_404 to handle non-existent productonhold gracefully
    productonhold = get_object_or_404(ProductOnHold, productonhold_id=productonhold_id)

    # Create a new ShipmentOut entry with the same data
    shipment_out = ShipmentOut.objects.create(
        product=productonhold.product,  # Assuming 'product' is a ForeignKey in ShipmentOut
        product_name=productonhold.product_name,
        quantity=productonhold.quantity,
        date=productonhold.date,
        user=request.user  # Assuming you want to associate the current user
        # Add other fields as needed for ShipmentOut
    )

    # Delete the entry from ProductOnHold after transferring
    productonhold.delete()

    # Redirect to the list page or anywhere else
    return redirect('productonhold_list')


@login_required
def shipmentin_create(request):
    if request.method == 'POST':
        form = ShipmentInForm(request.POST)
        if form.is_valid():
            shipmentin = form.save(commit=False)  # Don't save yet
            shipmentin.user = request.user  # Set the user to the currently logged-in user

            # Get the selected product and set the product name
            product = form.cleaned_data['product']
            shipmentin.product_name = product.name  # Ensure product_name field exists in your model

            shipmentin.save()  # Save the order
            return redirect('shipmentin_list')  # Redirect to the orderout list view
        else:
            print(form.errors)  # Print the form errors for debugging
    else:
        form = ShipmentInForm()

    return render(request, 'invApp/shipmentin_create.html', {'form': form})


@login_required
def productonhold_create(request):
    if request.method == 'POST':
        form = ProductOnHoldForm(request.POST)
        if form.is_valid():
            productonhold = form.save(commit=False)  # Don't save yet
            productonhold.user = request.user  # Set the user to the currently logged-in user

            # Get the selected product and set the product name
            product = form.cleaned_data['product']
            productonhold.product_name = product.name  # Ensure product_name field exists in your model

            productonhold.save()  # Save the order
            return redirect('productonhold_list')  # Redirect to the orderout list view
        else:
            print(form.errors)  # Print the form errors for debugging
    else:
        form = ProductOnHoldForm()

    return render(request, 'invApp/productonhold_create.html', {'form': form})


# Read (List) View
@login_required
def product_list_view(request):
    products = Product.objects.all()  # Fetch all products initially

    # Get the month and year from the request GET parameters
    selected_month = request.GET.get('month')
    selected_year = request.GET.get('year')

    # If both month and year are provided, filter the products by the date field
    if selected_month and selected_year:
        products = products.annotate(month=ExtractMonth('date'), year=ExtractYear('date')).filter(
            month=selected_month, year=selected_year
        )

    # Example range for year selection (customize as needed)
    year_range = range(2020, 2031)

    context = {
        'products': products,
        'year_range': year_range,
        'selected_month': selected_month,
        'selected_year': selected_year,
    }

    return render(request, 'invApp/product_list.html', context)


def combo_create(request):
    if request.method == 'POST':
        form = ComboProductForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('combo_list')  # Redirect to combo list after creation
    else:
        form = ComboProductForm()
    return render(request, 'invApp/combo_create.html', {'form': form})


@login_required
def combo_list(request):
    # Assuming Combo is the model you're dealing with
    combos = ComboProduct.objects.all()

    # Example of filtering or processing combo data
    for combo in combos:
        if combo.product1 and combo.product2:
            print(combo.product1.product_id, combo.product2.product_id)  # Use product_id instead of id

    context = {
        'combos': combos
    }

    return render(request, 'invApp/combo_list.html', context)


@login_required
def orderout_list_view(request):
    orderouts = OrderOut.objects.all()
    products = Product.objects.all()  # Assuming you have a Product model

    product_name = request.GET.get('product_name')
    date_range = request.GET.get('date_range')

    if date_range:
        # Split the date range into start and end dates
        start_date_str, end_date_str = date_range.split(' to ')
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d')

        # Filter OrderOut based on date range
        orderouts = orderouts.filter(
            date__range=(start_date, end_date)
        )

        # Add product name filtering if it exists
        if product_name:
            orderouts = orderouts.filter(product__name=product_name)

    context = {
        'orderouts': orderouts,
        'products': products,
        'product_name': product_name,
    }
    return render(request, 'invApp/orderout_list.html', context)


@login_required
def return_list_view(request):
    returns = Return.objects.all()
    products = Product.objects.all()  # Assuming you have a Product model

    product_name = request.GET.get('product_name')
    date_range = request.GET.get('date_range')

    if date_range:
        # Split the date range into start and end dates
        start_date_str, end_date_str = date_range.split(' to ')
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d')

        # Filter OrderOut based on date range
        returns = returns.filter(
            date__range=(start_date, end_date)
        )

        # Add product name filtering if it exists
        if product_name:
            returns = returns.filter(product__name=product_name)

    context = {
        'returns': returns,
        'products': products,
        'product_name': product_name,
    }
    return render(request, 'invApp/return_list.html', context)


@login_required
def stockin_list_view(request):
    stockins = StockIn.objects.all()

    # Filter by month and year if provided
    month = request.GET.get('month')
    year = request.GET.get('year')
    if month and year:
        stockins = stockins.filter(date__month=month, date__year=year)

    # Filter damage only if checkbox is selected
    damage_only = request.GET.get('damageOnly')
    if damage_only:
        stockins = stockins.filter(damage_quantity__gt=0)

    context = {
        'stockins': stockins,
        'year_range': range(2020, 2031),  # Example year range
    }
    return render(request, 'invApp/stockin_list.html', context)


@login_required
def damagereturn_list_view(request):
    damagereturns = DamageReturn.objects.all()
    year_range = range(2020, 2031)  # Example range for year selection (if needed)

    context = {
        'damagereturns': damagereturns,
        'year_range': year_range,  # If you're using this in your template
    }
    return render(request, 'invApp/damagereturn_list.html', context)




@login_required
def shipmentout_list_view(request):
    shipmentouts = ShipmentOut.objects.all()
    products = Product.objects.all()  # Assuming you have a Product model

    product_name = request.GET.get('product_name')
    date_range = request.GET.get('date_range')

    if date_range:
        # Split the date range into start and end dates
        start_date_str, end_date_str = date_range.split(' to ')
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d')

        # Filter OrderOut based on date range
        shipmentouts = shipmentouts.filter(
            date__range=(start_date, end_date)
        )

        # Add product name filtering if it exists
        if product_name:
            shipmentouts = shipmentouts.filter(product__name=product_name)

    context = {
        'shipmentouts': shipmentouts,
        'products': products,
        'product_name': product_name,
    }
    return render(request, 'invApp/shipmentout_list.html', context)



@login_required
def shipmentin_list_view(request):
    shipmentins = ShipmentIn.objects.all()
    products = Product.objects.all()  # Assuming you have a Product model

    product_name = request.GET.get('product_name')
    date_range = request.GET.get('date_range')

    if date_range:
        # Split the date range into start and end dates
        start_date_str, end_date_str = date_range.split(' to ')
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d')

        # Filter OrderOut based on date range
        shipmentins = shipmentins.filter(
            date__range=(start_date, end_date)
        )

        # Add product name filtering if it exists
        if product_name:
            shipmentins = shipmentins.filter(product__name=product_name)

    context = {
        'shipmentins': shipmentins,
        'products': products,
        'product_name': product_name,
    }
    return render(request, 'invApp/shipmentin_list.html', context)



@login_required
def productonhold_list_view(request):
    productonhold = ProductOnHold.objects.all()
    year_range = range(2020, 2031)  # Example range for year selection (if needed)

    context = {
        'productonholds': productonhold,
        'year_range': year_range,  # If you're using this in your template
    }
    return render(request, 'invApp/productonhold_list.html', context)



@login_required
# Update View
def product_update_view(request, product_id):
    product = get_object_or_404(Product, product_id=product_id)

    if request.method == "POST":
        form = ProductForm(request.POST, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, 'Product updated successfully!')
            return redirect('product_list')  # Redirect to your product list
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = ProductForm(instance=product)

    return render(request, 'invApp/product_update.html', {'form': form})


@login_required
def orderout_update_view(request, orderout_id):
    orderout = get_object_or_404(OrderOut, orderout_id=orderout_id)

    if request.method == "POST":
        form = OrderOutForm(request.POST, instance=orderout)
        if form.is_valid():
            form.save()
            messages.success(request, 'Order updated successfully!')
            return redirect('orderout_list')  # Redirect to your product list
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = OrderOutForm(instance=orderout)

    return render(request, 'invApp/orderout_update.html', {'form': form})



@login_required
def stockin_update_view(request, stockin_id):
    stockin = get_object_or_404(StockIn, stockin_id=stockin_id)

    if request.method == "POST":
        form = StockInForm(request.POST, instance=stockin)
        if form.is_valid():
            form.save()
            messages.success(request, 'StockIn updated successfully!')
            return redirect('stockin_list')  # Redirect to your product list
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = StockInForm(instance=stockin)

    return render(request, 'invApp/stockin_update.html', {'form': form})



@login_required
def return_update_view(request, return_id):
    returns = get_object_or_404(Return, return_id=return_id)

    if request.method == "POST":
        form = ReturnForm(request.POST, instance=returns)
        if form.is_valid():
            form.save()
            messages.success(request, 'Return updated successfully!')
            return redirect('return_list')  # Redirect to your product list
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = ReturnForm(instance=returns)

    return render(request, 'invApp/return_update.html', {'form': form})


@login_required
def damagereturn_update_view(request, damagereturn_id):
    damagereturns = get_object_or_404(DamageReturn, damagereturn_id=damagereturn_id)

    if request.method == "POST":
        form = DamageReturnForm(request.POST, instance=damagereturns)
        if form.is_valid():
            form.save()
            messages.success(request, 'Return updated successfully!')
            return redirect('damagereturn_list')  # Redirect to your product list
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = DamageReturnForm(instance=damagereturns)

    return render(request, 'invApp/damagereturn_update.html', {'form': form})


@login_required
def shipmentout_update_view(request, shipmentout_id):
    shipmentout = get_object_or_404(ShipmentOut, shipmentout_id=shipmentout_id)

    if request.method == "POST":
        form = ShipmentOutForm(request.POST, instance=shipmentout)
        if form.is_valid():
            form.save()
            messages.success(request, 'Shipment updated successfully!')
            return redirect('shipmentout_list')  # Redirect to your product list
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = ShipmentOutForm(instance=shipmentout)

    return render(request, 'invApp/shipmentout_update.html', {'form': form})


@login_required
def shipmentin_update_view(request, shipmentin_id):
    shipmentin = get_object_or_404(ShipmentIn, shipmentin_id=shipmentin_id)

    if request.method == "POST":
        form = ShipmentInForm(request.POST, instance=shipmentin)
        if form.is_valid():
            form.save()
            messages.success(request, 'ShipmentIn updated successfully!')
            return redirect('shipmentin_list')  # Redirect to your product list
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = ShipmentInForm(instance=shipmentin)

    return render(request, 'invApp/shipmentin_update.html', {'form': form})



@login_required
def productonhold_update_view(request, productonhold_id):
    productonhold = get_object_or_404(ProductOnHold, productonhold_id=productonhold_id)

    if request.method == "POST":
        form = ProductOnHoldForm(request.POST, instance=productonhold)
        if form.is_valid():
            form.save()
            messages.success(request, 'ProductOnHold updated successfully!')
            return redirect('productonhold_list')  # Redirect to your product list
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = ProductOnHoldForm(instance=productonhold)

    return render(request, 'invApp/productonhold_update.html', {'form': form})



# Delete View
@login_required
def product_delete_view(request, product_id):
    product = get_object_or_404(Product, product_id=product_id)

    if request.method == 'POST':
        product.delete()
        return JsonResponse({'success': True})  # Return a JSON response for AJAX

    # If not a POST request, render a confirmation page (if needed)
    return render(request, 'invApp/product_confirm_delete.html', {'product': product})



@login_required
def stockin_delete_view(request, stockin_id):
    stockin = get_object_or_404(StockIn, stockin_id=stockin_id)

    if request.method == 'POST':
        stockin.delete()
        return JsonResponse({'success': True})  # Return a JSON response for AJAX

    # If not a POST request, render a confirmation page (if needed)
    return render(request, 'invApp/stockin_confirm_delete.html', {'stockin': stockin})


@login_required
def orderout_delete_view(request, orderout_id):
    orderout = get_object_or_404(OrderOut, orderout_id=orderout_id)

    if request.method == 'POST':
        orderout.delete()
        return JsonResponse({'success': True})  # Return a JSON response for AJAX

    # If not a POST request, render a confirmation page (if needed)
    return render(request, 'invApp/orderout_confirm_delete.html', {'orderout': orderout})


@login_required
def return_delete_view(request, return_id):
    returns = get_object_or_404(Return, return_id=return_id)

    if request.method == 'POST':
        returns.delete()
        return JsonResponse({'success': True})  # Return a JSON response for AJAX

    # If not a POST request, render a confirmation page (if needed)
    return render(request, 'invApp/return_confirm_delete.html', {'returns': returns})


@login_required
def damagereturn_delete_view(request, damagereturn_id):
    damagereturns = get_object_or_404(DamageReturn, damagereturn_id=damagereturn_id)

    if request.method == 'POST':
        damagereturns.delete()
        return JsonResponse({'success': True})  # Return a JSON response for AJAX

    # If not a POST request, render a confirmation page (if needed)
    return render(request, 'invApp/damagereturn_confirm_delete.html', {'damagereturns': damagereturns})


@login_required
def shipmentout_delete_view(request, shipmentout_id):
    shipmentout = get_object_or_404(ShipmentOut, shipmentout_id=shipmentout_id)

    if request.method == 'POST':
        try:
            shipmentout.delete()  # Attempt to delete the shipmentout
            return JsonResponse({'success': True})  # Return a JSON response for AJAX
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})  # Handle exceptions

    # If not a POST request, render a confirmation page (if needed)
    return render(request, 'invApp/shipmentout_confirm_delete.html', {'shipmentout': shipmentout})


@login_required
def shipmentin_delete_view(request, shipmentin_id):
    shipmentin = get_object_or_404(ShipmentIn, shipmentin_id=shipmentin_id)

    if request.method == 'POST':
        try:
            shipmentin.delete()  # Attempt to delete the shipmentin
            return JsonResponse({'success': True})  # Return a JSON response for AJAX
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})  # Handle exceptions

    # If not a POST request, render a confirmation page (if needed)
    return render(request, 'invApp/shipmentin_confirm_delete.html', {'shipmentin': shipmentin})


@login_required
def productonhold_delete_view(request, productonhold_id):
    productonhold = get_object_or_404(ProductOnHold, productonhold_id=productonhold_id)

    if request.method == 'POST':
        try:
            productonhold.delete()  # Attempt to delete the shipmentin
            return JsonResponse({'success': True})  # Return a JSON response for AJAX
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})  # Handle exceptions

    # If not a POST request, render a confirmation page (if needed)
    return render(request, 'invApp/productonhold_confirm_delete.html', {'productonhold': productonhold})


@login_required
def generate_barcode(request, product_id):
    # Retrieve the product object by product_id
    product = get_object_or_404(Product, product_id=product_id)

    # Create a BytesIO buffer to hold the PDF data
    buffer = io.BytesIO()

    # Create a canvas for PDF generation
    p = canvas.Canvas(buffer, pagesize=letter)

    # Generate a Code128 barcode using product ID with increased barWidth
    barcode = code128.Code128(str(product.product_id), barHeight=50, barWidth=4)  # Increased barWidth for wider barcode

    # Set the x and y position for the barcode and draw it on the PDF
    x_position = 100  # Adjust the x position
    y_position = 110  # Adjust the y position
    barcode.drawOn(p, x_position, y_position)

    # Set the font for SKU and Product ID text
    p.setFont("Helvetica", 10)

    # Draw SKU text and center it slightly left
    sku_text = f"SKU: {product.sku}"
    sku_width = p.stringWidth(sku_text, "Helvetica", 10)  # Calculate the width of SKU text
    left_adjustment = 80  # Adjust this value to move the text left from center
    p.drawString((letter[0] - sku_width) / 2 - left_adjustment, y_position - 15, sku_text)  # Center SKU text slightly left

    # Draw Product ID text and center it slightly left
    product_id_text = f"Product ID: {product.product_id}"
    product_id_width = p.stringWidth(product_id_text, "Helvetica", 10)  # Calculate the width of Product ID text
    p.drawString((letter[0] - product_id_width) / 2 - left_adjustment, y_position - 30, product_id_text)  # Center Product ID text slightly left

    # Finalize the PDF
    p.showPage()
    p.save()

    # Crop the PDF by adjusting the mediabox
    buffer.seek(0)
    pdf_reader = PyPDF2.PdfReader(buffer)  # Use PyPDF2 to read the PDF
    pdf_writer = PyPDF2.PdfWriter()

    # Loop through all the pages (in this case just one)
    for page in pdf_reader.pages:
        # Crop the page using the mediabox method
        page.mediabox.lower_left = (110, 70)  # Adjust these values to crop from left and bottom
        page.mediabox.upper_right = (page.mediabox.width - 165, page.mediabox.height - 550)  # Crop from right and top
        pdf_writer.add_page(page)

    # Create a new BytesIO buffer to hold the cropped PDF data
    cropped_buffer = io.BytesIO()
    pdf_writer.write(cropped_buffer)
    cropped_buffer.seek(0)

    # Return the cropped PDF as a response with direct download
    response = HttpResponse(cropped_buffer.getvalue(), content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{product.sku}.pdf"'  # Set for download

    return response



@login_required
def generate_combo_barcode(request, product1_id, product2_id):
    # Use 'product_id' instead of 'id' to retrieve the products
    product1 = get_object_or_404(Product, product_id=product1_id)
    product2 = get_object_or_404(Product, product_id=product2_id)

    # Create a BytesIO buffer to hold the PDF data
    buffer = io.BytesIO()

    # Create a canvas for PDF generation
    p = canvas.Canvas(buffer, pagesize=letter)

    # Combine the product IDs to create a unique barcode for the combo
    combined_product_ids = f"{product1.product_id}&{product2.product_id}"

    # Generate a Code128 barcode using the combined product IDs
    barcode = code128.Code128(combined_product_ids, barHeight=50, barWidth=3)

    # Set the x and y position for the barcode and draw it on the PDF
    x_position = 90  # Adjust the x position
    y_position = 110  # Adjust the y position
    barcode.drawOn(p, x_position, y_position)

    # Set the font for Combo Name and Product IDs text
    p.setFont("Helvetica", 10)

    # Define the left offset for text
    left_offset = 85

    # Draw combo name slightly to the left of the barcode
    combo_text = f"Combo: {product1.name} & {product2.name}"
    combo_width = p.stringWidth(combo_text, "Helvetica", 10)
    p.drawString(((letter[0] - combo_width) / 2) - left_offset, y_position - 15, combo_text)

    # Draw product IDs slightly to the left of the barcode
    product_ids_text = f"Product IDs: {product1.product_id} & {product2.product_id}"
    product_ids_width = p.stringWidth(product_ids_text, "Helvetica", 10)
    p.drawString(((letter[0] - product_ids_width) / 2) - left_offset, y_position - 30, product_ids_text)

    # Finalize the PDF
    p.showPage()
    p.save()

    # Crop the PDF by adjusting the mediabox (if needed)
    buffer.seek(0)
    pdf_reader = PyPDF2.PdfReader(buffer)
    pdf_writer = PyPDF2.PdfWriter()

    for page in pdf_reader.pages:
        page.mediabox.lower_left = (110, 70)
        page.mediabox.upper_right = (page.mediabox.width - 165, page.mediabox.height - 550)
        pdf_writer.add_page(page)

    cropped_buffer = io.BytesIO()
    pdf_writer.write(cropped_buffer)
    cropped_buffer.seek(0)

    # Return the cropped PDF as a response
    response = HttpResponse(cropped_buffer.getvalue(), content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{product1.sku}_{product2.sku}_combo.pdf"'

    return response



@login_required
def scan_here(request):
    return render(request, 'invApp/barcode_scan.html')


def get_product(request):
    # Get product_id from the request
    product_id = request.GET.get('product_id')

    try:
        # First, check if the product_id corresponds to a combo
        combo = ComboProduct.objects.get(combo_id=product_id)
        combo_products = combo.products.all()  # Assuming a many-to-many field named 'products' in Combo

        # Prepare response data for combo products
        product_data = [
            {'product_name': prod.name, 'quantity': prod.quantity}
            for prod in combo_products
        ]

        return JsonResponse({'success': True, 'combo': True, 'products': product_data})

    except ComboProduct.DoesNotExist:
        # If not a combo, check for an individual product
        try:
            product = Product.objects.get(product_id=product_id)
            return JsonResponse(
                {'success': True, 'combo': False, 'product_name': product.name, 'quantity': product.quantity})

        except Product.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Product not found!'})


@csrf_exempt
def submit_order(request):
    if request.method == 'POST':
        order_type = request.POST.get('orderType')
        product_id = request.POST.get('barcode')  # Ensure you're using product_id here
        quantity = int(request.POST.get('quantity'))
        date_str = request.POST.get('date')  # Get the date from the form

        try:
            product = Product.objects.get(product_id=product_id)  # Fetch product using product_id

            # Respond with the necessary data
            response_data = {
                'success': True,
                'data': {
                    'product_name': product.name,
                    'quantity': quantity,
                    'order_type': order_type,
                    'date': date_str  # Include date in response if needed
                }
            }

            return JsonResponse(response_data)
        except Product.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Product not found!'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})
    else:
        return JsonResponse({'success': False, 'message': 'Invalid request method.'})



@csrf_exempt
def save_entries(request):
    if request.method == 'POST':
        try:
            entries = json.loads(request.POST.get('entries'))
            print("Entries received:", entries)
            for entry in entries:
                product = Product.objects.get(name=entry['product_name'])

                if entry['order_type'].lower() == 'orderout':
                    OrderOut.objects.create(
                        user=request.user,
                        product=product,
                        product_name=entry['product_name'],
                        date=datetime.strptime(entry['date'], '%d/%m/%Y'),
                        quantity=int(entry['quantity'])
                    )

                elif entry['order_type'].lower() == 'return':

                    Return.objects.create(
                        user=request.user,
                        product=product,
                        product_name=entry['product_name'],
                        date=datetime.strptime(entry['date'], '%d/%m/%Y'),
                        quantity=int(entry['quantity']),
                    )

                elif entry['order_type'].lower() == 'damagereturn':

                    DamageReturn.objects.create(
                        user=request.user,
                        product=product,
                        product_name=entry['product_name'],
                        date=datetime.strptime(entry['date'], '%d/%m/%Y'),
                        quantity=int(entry['quantity']),
                    )


                elif entry['order_type'].lower() == 'shipmentout':
                    ShipmentOut.objects.create(
                        user=request.user,
                        product=product,
                        product_name=entry['product_name'],
                        date=datetime.strptime(entry['date'], '%d/%m/%Y'),
                        quantity=int(entry['quantity'])
                    )

                elif entry['order_type'].lower() == 'shipmentin':
                    ShipmentIn.objects.create(
                        user=request.user,
                        product=product,
                        product_name=entry['product_name'],
                        date=datetime.strptime(entry['date'], '%d/%m/%Y'),
                        quantity=int(entry['quantity'])
                    )

            return JsonResponse({'success': True})
        except Product.DoesNotExist:
            print("Product not found!")  # Debug: Log if product is not found
            return JsonResponse({'success': False, 'message': 'Product not found!'})
        except Exception as e:
            print("Error occurred:", str(e))  # Log the error
            return JsonResponse({'success': False, 'message': str(e)})
    return JsonResponse({'success': False, 'message': 'Invalid request method.'})



def export_products_to_excel(request):
    start_date = request.GET.get('startDate')
    end_date = request.GET.get('endDate')

    products = Product.objects.all()
    if start_date and end_date:
        start_date = datetime.strptime(start_date, '%Y-%m-%d')
        end_date = datetime.strptime(end_date, '%Y-%m-%d')
        products = products.filter(date__range=[start_date, end_date])


    # Create a workbook and active sheet
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = 'Products'

    # Define the header
    ws.append(['Sr No.', 'Date', 'Product Name', 'SKU', 'Price', 'Quantity', 'Supplier'])

    # Get the products from the database
    products = Product.objects.all()

    # Add data to the sheet
    for idx, product in enumerate(products, start=1):
        ws.append([idx, product.date.strftime('%d/%m/%Y'), product.name, product.sku, product.price, product.quantity, product.supplier])

    # Create a response object for the Excel file
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=products.xlsx'

    # Save the workbook to the response
    wb.save(response)

    return response


#Label Crop
@login_required
def label_crop_view(request):
    return render(request, 'invApp/labelcrop.html')  # Ensure 'label_crop.html' exists in your templates folder


def extract_sku_and_quantity(page_text):
    """Extract SKU and Quantity from the page text."""
    sku = None
    quantity = None

    # Extract the section that contains "Description"
    description_match = re.search(r'Description\s*(.*?)(HSN:|$)', page_text, re.DOTALL)
    if description_match:
        description_text = description_match.group(1)
        print(f"Extracted Description Text: {description_text.strip()}")

        # Find the SKU in the format: "( CI - Belly Belt 3 meter )"
        sku_match = re.search(r'\|\s*.*?\s*\(\s*(.*?)\s*\)', description_text)
        if sku_match:
            sku = sku_match.group(1).strip()  # Extract SKU text and strip whitespace
            print(f"Extracted SKU: {sku}")

        # Find the quantity
        qty_match = re.search(r"(?:Qty|Quantity)[^\d]*(\d+)", page_text, re.IGNORECASE)
        if qty_match:
            quantity = int(qty_match.group(1))  # Extract the quantity as an integer
            print(f"Extracted Quantity: {quantity}")

    return sku, quantity

def write_sku_to_page(pdf_writer, page, sku, quantity):
    """Write SKU and Quantity to the given page."""
    packet = io.BytesIO()
    # Create a new PDF with ReportLab
    can = canvas.Canvas(packet)

    # Set font size and bold
    can.setFont("Helvetica-Bold", 16)  # Set font to Helvetica Bold and size to 12

    # Set position and text to write SKU and Quantity
    can.drawString(55, 160, f" {sku} | Qty: {quantity}")
    can.save()

    # Move to the beginning of the BytesIO buffer
    packet.seek(0)

    # Create a new PDF from the canvas
    overlay_pdf = PyPDF2.PdfReader(packet)

    # Merge the overlay page with the original odd page
    page.merge_page(overlay_pdf.pages[0])

    # Add the merged page to the PDF writer
    pdf_writer.add_page(page)


def add_summary_page(pdf_writer, sku_quantity_list,company_name):
    """Add a summary page with the SKU, Quantity, and Total Orders."""
    # Create a new PDF page for the summary
    packet = io.BytesIO()
    can = canvas.Canvas(packet)

    # Set font for the header
    can.setFont("Helvetica-Bold", 14)
    can.drawString(100, 750, "Summary")  # Title

    # Set font for the table header
    can.setFont("Helvetica-Bold", 12)
    can.drawString(50, 700, "Order")
    can.drawString(200, 700, "Qty")
    can.drawString(300, 700, "SKU")

    # Set font for the table content
    can.setFont("Helvetica", 12)

    # Create a dictionary to aggregate orders and quantities for each SKU
    sku_aggregated = {}

    # Aggregate quantities for each SKU
    for sku, quantity in sku_quantity_list:
        if sku in sku_aggregated:
            sku_aggregated[sku]['total_qty'] += quantity  # Total quantity for each SKU
            sku_aggregated[sku]['order_count'] += 1  # Count of how many times this SKU was ordered
        else:
            sku_aggregated[sku] = {'total_qty': quantity, 'order_count': 1}  # First occurrence

    # Add the content to the summary page
    y_position = 680  # Starting position for the first line of content
    for sku, info in sku_aggregated.items():
        can.drawString(50, y_position, str(info['total_qty']))  # Total Quantity for each SKU
        can.drawString(200, y_position, str(info['order_count']))  # Count of distinct orders for each SKU
        can.drawString(300, y_position, sku)  # SKU

        y_position -= 20  # Move down for the next line

    # Calculate total packages (the total number of distinct SKUs)
    total_orders = sum(info['order_count'] for info in sku_aggregated.values())  # Total distinct orders

    # Add the total package line
    can.setFont("Helvetica-Bold", 12)
    can.drawString(50, y_position, f"Total Package: {total_orders}")

    # Add the company name at the top of the summary page
    can.setFont("Helvetica", 12)
    can.drawString(50, 730, f"Company Name: {company_name}")

    # Save the page
    can.save()

    # Move to the beginning of the BytesIO buffer
    packet.seek(0)

    # Create a new PDF from the canvas
    summary_pdf = PyPDF2.PdfReader(packet)

    # Add the summary page to the PDF writer
    pdf_writer.add_page(summary_pdf.pages[0])



def extract_company_name_from_page(pdf_file, page_index):
    """Extract the company name from a specific page in the PDF."""
    try:
        pdf_file.seek(0)  # Ensure you're reading from the beginning of the file
        reader = PyPDF2.PdfReader(pdf_file)

        # Check if the page index is valid
        if page_index >= len(reader.pages):
            print(f"Error: Page index {page_index} out of range. PDF has {len(reader.pages)} pages.")
            return ""

        # Extract the text from the specified page
        page = reader.pages[page_index]
        page_text = page.extract_text()

        # Log the extracted text for debugging (optional)
        print(f"Extracted text from page {page_index + 1}:\n{page_text}")

        # Updated pattern to capture the company name after "Sold By:"
        sold_by_pattern = r"Sold By\s*:\s*([^\n*]+)"
        sold_by_match = re.search(sold_by_pattern, page_text, re.IGNORECASE)

        if sold_by_match:
            company_name = sold_by_match.group(1).strip()
            print(f"Matched company name (Sold By): {company_name}")  # Debugging output
            return company_name

        # If no match found
        print("No company name matched. Extracted text:")
        print(page_text)  # Output the full text to see if anything seems off

        return ""

    except Exception as e:
        print(f"Error reading the PDF or extracting text: {e}")
        return ""



def upload_pdf(request):
    """Process the uploaded PDF and return a modified PDF with SKU, quantity, and a summary page."""
    if request.method == 'POST':
        print("PDF upload process started")  # Debugging print

        # Get the uploaded PDF file
        pdf_file = request.FILES['pdfFile']
        add_summary = 'addSummary' in request.POST  # Check if the checkbox is checked
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        pdf_writer = PyPDF2.PdfWriter()

        sku_quantity_list = []  # To store all extracted SKUs and quantities

        # Extract the company name from the first page (you can adjust the page index)
        company_name = extract_company_name_from_page(pdf_file, 0)
        print(f"Extracted Company Name: {company_name}")  # Debugging print

        for page_num in range(len(pdf_reader.pages)):
            # If it's an even page, extract SKU and Quantity
            if page_num % 2 != 0:  # Even pages (0-based index, so page_num % 2 != 0 means even pages for humans)
                even_page = pdf_reader.pages[page_num]
                even_page_text = even_page.extract_text()
                print(f"Text from even page {page_num}: {even_page_text[:100]}...")  # Debug print

                # Extract SKU and quantity
                sku, quantity = extract_sku_and_quantity(even_page_text)

                if sku and quantity:
                    # Append to the SKU and quantity list
                    sku_quantity_list.append((sku, quantity))

                    # Get the corresponding odd page (previous page)
                    odd_page = pdf_reader.pages[page_num - 1]
                    print(f"Writing to odd page {page_num - 1}")

                    # Write SKU and quantity to the odd page
                    write_sku_to_page(pdf_writer, odd_page, sku, quantity)

            else:
                # Skip even pages (i.e., do not add them to the PDF writer)
                continue

        # Add a summary page at the end of the PDF, including the company name
        if add_summary and sku_quantity_list:
            print("Adding summary page.")
            add_summary_page(pdf_writer, sku_quantity_list, company_name)

        # Generate a new PDF in memory
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="output_with_summary.pdf"'

        pdf_writer.write(response)
        return response

    return render(request, 'invApp/upload_pdf.html')























