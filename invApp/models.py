from django.db import models
from django.utils import timezone  # Import timezone
from django.contrib.auth.models import User
import string

# Create your models here.
class Product(models.Model):
    SECTIONS = [('A', 'A'), ('B', 'B'), ('C', 'C'), ('D', 'D'), ('E', 'E'), ('F', 'F'),
                ('G', 'G'), ('H', 'H'), ('I', 'I'), ('J', 'J'), ('K', 'K'), ('L', 'L'),
                ('M', 'M'), ('N', 'N')]

    SUBSECTIONS = [(f"{section}{i}", f"{section}{i}") for section in 'ABCDEFGHIJKLMN' for i in range(1, 4)]


    product_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='products')
    date = models.DateTimeField(default=timezone.now,)
    name = models.CharField(max_length=50)
    sku = models.CharField(max_length=50, unique=True)
    section = models.CharField(max_length=1, choices=SECTIONS)
    subsection = models.CharField(max_length=3, choices=SUBSECTIONS)


    def __str__(self):
        return self.name


class ComboProduct(models.Model):
    combo_name = models.CharField(max_length=255)
    product1 = models.ForeignKey(Product, related_name='product1_combo', on_delete=models.CASCADE)
    product2 = models.ForeignKey(Product, related_name='product2_combo', on_delete=models.CASCADE)
    combo_sku = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.combo_name} - {self.combo_sku}"


class OrderOut(models.Model):
    orderout_id = models.AutoField(primary_key=True)  # Automatically incrementing ID
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='order_outs')  # Link to the User model
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='order_outs')  # Link to the Product model
    product_name = models.CharField(max_length=255)
    date = models.DateField()  # Date the order was created
    quantity = models.PositiveIntegerField()  # Quantity of the product ordered

    def __str__(self):
        return f"OrderOut {self.orderout_id} - {self.product.name} (Quantity: {self.quantity})"


class Return(models.Model):
    return_id = models.AutoField(primary_key=True)  # Automatically incrementing ID
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='returns')  # Link to the User model
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='returns')  # Link to the Product model
    product_name = models.CharField(max_length=255)
    date = models.DateField()  # Date the order was created
    quantity = models.PositiveIntegerField()  # Quantity can now be nullable and blank



    def __str__(self):
        return f"Return {self.return_id} - {self.product.name} (Quantity: {self.quantity})"

class DamageReturn(models.Model):
    damagereturn_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='damage_returns')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='damage_returns')
    product_name = models.CharField(max_length=255)
    date = models.DateField()
    quantity = models.PositiveIntegerField()

    def __str__(self):
        return f"DamageReturn {self.damagereturn_id} - {self.product.name} (Quantity: {self.quantity})"


class ShipmentOut(models.Model):
    shipmentout_id = models.AutoField(primary_key=True)  # Automatically incrementing ID
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='shipment_outs')  # Link to the User model
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='shipment_outs')  # Link to the Product model
    product_name = models.CharField(max_length=255)
    date = models.DateField()  # Date the order was created
    quantity = models.PositiveIntegerField()  # Quantity of the product ordered

    def __str__(self):
        return f"ShipmentOut {self.shipmentout_id} - {self.product.name} (Quantity: {self.quantity})"


class ShipmentIn(models.Model):
    shipmentin_id = models.AutoField(primary_key=True)  # Automatically incrementing ID
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='shipment_ins')  # Link to the User model
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='shipment_ins')  # Link to the Product model
    product_name = models.CharField(max_length=255)
    date = models.DateField()  # Date the order was created
    quantity = models.PositiveIntegerField()  # Quantity of the product ordered

    def __str__(self):
        return f"ShipmentIn {self.shipmentin_id} - {self.product.name} (Quantity: {self.quantity})"


class ProductOnHold(models.Model):
    productonhold_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='product_on_hold')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='product_on_hold')
    product_name = models.CharField(max_length=255)
    date = models.DateField()
    quantity = models.PositiveIntegerField()

    def __str__(self):
        return f"ProductOnHold {self.productonhold_id} - {self.product.name} (Quantity: {self.quantity})"


class StockIn(models.Model):
    stockin_id = models.AutoField(primary_key=True)  # Automatically incrementing ID
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='stock_in')  # Link to the User model
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='stock_in')  # Link to the Product model
    product_name = models.CharField(max_length=255)
    date = models.DateField()  # Date the order was created
    quantity = models.PositiveIntegerField(null=True, blank=True)  # Quantity can now be nullable and blank
    damage_quantity = models.PositiveIntegerField(null=True, blank=True)  # New field for damaged quantity, nullable and blank

    def __str__(self):
        return f"StockIn {self.stockin_id} - {self.product.name} (Quantity: {self.quantity})"


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    mobile_number = models.CharField(max_length=15)
    company_name = models.CharField(max_length=50)

    def __str__(self):
        return self.user.username
