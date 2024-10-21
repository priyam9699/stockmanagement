from django.urls import path
from django.views.generic import RedirectView
from . import views

urlpatterns = [
    # Home redirect
    path('', RedirectView.as_view(url='/register/', permanent=False), name='home'),
    path('dashboard/', views.dashboard_view, name='Dashboard'),  # Add this lin

    # Product views
    path('products/', views.product_list_view, name='product_list'),
    path('products/create/', views.product_create_view, name='product_create'),
    path('products/<int:product_id>/edit/', views.product_update_view, name='product_update'),
    path('products/<int:product_id>/delete/', views.product_delete_view, name='product_delete'),
    path('products/export/', views.export_products_to_excel, name='export_products_to_excel'),


    path('combo/create/', views.combo_create, name='combo_create'),  # Add this if it's missing
    path('combo/list/', views.combo_list, name='combo_list'),  # Existing combo list

    # StockIn views
    path('stockin/', views.stockin_list_view, name='stockin_list'),
    path('stockin/create/', views.stockin_create, name='stockin_create'),
    path('stockin/<int:stockin_id>/edit/', views.stockin_update_view, name='stockin_update'),
    path('stockin/<int:stockin_id>/delete/', views.stockin_delete_view, name='stockin_delete'),


    # OrderOut views
    path('orderout/', views.orderout_list_view, name='orderout_list'),
    path('orderout/create/', views.orderout_create, name='orderout_create'),
    path('orderout/<int:orderout_id>/edit/', views.orderout_update_view, name='orderout_update'),
    path('orderout/<int:orderout_id>/delete/', views.orderout_delete_view, name='orderout_delete'),


    # ShipmentOut Views
    path('shipmentout/', views.shipmentout_list_view, name='shipmentout_list'),
    path('shipmentout/create/', views.shipmentout_create, name='shipmentout_create'),
    path('shipmentout/<int:shipmentout_id>/edit/', views.shipmentout_update_view, name='shipmentout_update'),
    path('shipmentout/<int:shipmentout_id>/delete/', views.shipmentout_delete_view, name='shipmentout_delete'),

    # Return views
    path('return/', views.return_list_view, name='return_list'),
    path('return/create/', views.return_create, name='return_create'),
    path('return/<int:return_id>/edit/', views.return_update_view, name='return_update'),
    path('return/<int:return_id>/delete/', views.return_delete_view, name='return_delete'),

    # DamageReturn views
    path('damagereturn/', views.damagereturn_list_view, name='damagereturn_list'),
    path('damagereturn/create/', views.damagereturn_create, name='damagereturn_create'),
    path('damagereturn/<int:damagereturn_id>/edit/', views.damagereturn_update_view, name='damagereturn_update'),
    path('damagereturn/<int:damagereturn_id>/delete/', views.damagereturn_delete_view, name='damagereturn_delete'),


    # ShipmentIn Views
    path('shipmentin/', views.shipmentin_list_view, name='shipmentin_list'),
    path('shipmentin/create/', views.shipmentin_create, name='shipmentin_create'),
    path('shipmentin/<int:shipmentin_id>/edit/', views.shipmentin_update_view, name='shipmentin_update'),
    path('shipmentin/<int:shipmentin_id>/delete/', views.shipmentin_delete_view, name='shipmentin_delete'),


    # ProductOnHold Views
    path('productonhold/', views.productonhold_list_view, name='productonhold_list'),
    path('productonhold/create/', views.productonhold_create, name='productonhold_create'),
    path('productonhold/<int:productonhold_id>/edit/', views.productonhold_update_view, name='productonhold_update'),
    path('productonhold/<int:productonhold_id>/delete/', views.productonhold_delete_view, name='productonhold_delete'),
    path('transfer-to-shipment-out/<int:productonhold_id>/', views.transfer_to_shipment_out, name='transfer_to_shipment_out'),


    # User authentication
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('product/<int:product_id>/barcode/', views.generate_barcode, name='generate_barcode'),
    path('generate-combo-barcode/<int:product1_id>/<int:product2_id>/', views.generate_combo_barcode, name='generate_combo_barcode'),




    path('scan/', views.scan_here, name='scan_here'),
    path('get_product/', views.get_product, name='get_product'),
    path('submit_order/', views.submit_order, name='submit_order'),
    path('save_entries/', views.save_entries, name='save_entries'),

    path('label-crop/', views.label_crop_view, name='labelcrop'),
    path('upload-pdf/', views.upload_pdf, name='upload_pdf'),

]
