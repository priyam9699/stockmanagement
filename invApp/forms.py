from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Product, UserProfile, OrderOut, ShipmentOut, Return, ShipmentIn, StockIn, DamageReturn, ProductOnHold, ComboProduct


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        exclude = ['product_id', 'user']  # Excluding the user and product_id fields
        labels = {
            'date': 'Date',
            'name': 'Product Name',
            'sku': 'SKU',
            'section': 'Section',
            'subsection': 'Subsection',
        }
        widgets = {
            'date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control datepicker',
                'id': 'datepicker',
                'placeholder': 'Select a date',
                'name': 'date',
            }),
            'name': forms.TextInput(attrs={
                'placeholder': 'e.g. Shirt',
                'class': 'form-control',
            }),
            'sku': forms.TextInput(attrs={
                'placeholder': 'e.g. S123',
                'class': 'form-control',
            }),
            'section': forms.Select(attrs={
                'class': 'form-control',
                'id': 'id_section',
            }),
            'subsection': forms.Select(attrs={
                'class': 'form-control',
                'id': 'id_subsection',
            }),
        }

class UploadFileForm(forms.Form):
    file = forms.FileField(label='Select an Excel file')


class ComboProductForm(forms.ModelForm):
    class Meta:
        model = ComboProduct
        fields = ['combo_name', 'product1', 'product2', 'combo_sku']
        widgets = {
            'combo_name': forms.TextInput(attrs={
                'class': 'form-control',
            }),
            'product1': forms.Select(attrs={
                'class': 'form-control',
            }),
            'product2': forms.Select(attrs={
                'class': 'form-control',
            }),
            'combo_sku': forms.TextInput(attrs={
                'class': 'form-control',
            })
        }

    def __init__(self, *args, **kwargs):
        super(ComboProductForm, self).__init__(*args, **kwargs)
        self.fields['product1'].queryset = Product.objects.all()
        self.fields['product2'].queryset = Product.objects.all()


class StockInForm(forms.ModelForm):
    class Meta:
        model = StockIn
        exclude = ['stockin_id']

        fields = ['date', 'product', 'quantity', 'damage_quantity']

        widgets = {
            'date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control',
                'placeholder': 'Select a date',
            }),
            'product': forms.Select(attrs={
                'class': 'form-control',
            }),
            'quantity': forms.NumberInput(attrs={
                'placeholder': 'e.g. 1',
                'class': 'form-control',
                'min': '1',
            }),
            'damage_quantity': forms.NumberInput(attrs={
                'placeholder': 'e.g. 1',
                'class': 'form-control',

            }),
        }

    def __init__(self, *args, **kwargs):
        super(StockInForm, self).__init__(*args, **kwargs)
        # Fetch all products from the database
        products = Product.objects.all()

        # Create a default option
        self.fields['product'].choices = [(0, "--Select Product--")] + [(product.product_id, product.name) for product in
                                                                    products]

class OrderOutForm(forms.ModelForm):
    class Meta:
        model = OrderOut
        exclude = ['orderout_id']

        fields = ['date', 'product', 'quantity']

        widgets = {
            'date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control',
                'placeholder': 'Select a date',
            }),
            'product': forms.Select(attrs={
                'class': 'form-control',
            }),
            'quantity': forms.NumberInput(attrs={
                'placeholder': 'e.g. 1',
                'class': 'form-control',
                'min': '1',
            }),
        }

    def __init__(self, *args, **kwargs):
        super(OrderOutForm, self).__init__(*args, **kwargs)
        # Fetch all products from the database
        products = Product.objects.all()

        # Create a default option
        self.fields['product'].choices = [(0, "--Select Product--")] + [(product.product_id, product.name) for product in
                                                                    products]


class ReturnForm(forms.ModelForm):
    class Meta:
        model = Return
        exclude = ['return_id']

        fields = ['date', 'product', 'quantity']

        widgets = {
            'date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control',
                'placeholder': 'Select a date',
            }),
            'product': forms.Select(attrs={
                'class': 'form-control',
            }),
            'quantity': forms.NumberInput(attrs={
                'placeholder': 'e.g. 1',
                'class': 'form-control',
                'min': '1',
            }),
        }

    def __init__(self, *args, **kwargs):
        super(ReturnForm, self).__init__(*args, **kwargs)
        # Fetch all products from the database
        products = Product.objects.all()

        # Create a default option
        self.fields['product'].choices = [(0, "--Select Product--")] + [(product.product_id, product.name) for product in
                                                                    products]


class DamageReturnForm(forms.ModelForm):
    class Meta:
        model = DamageReturn
        exclude = ['damagereturn_id']

        fields = ['date', 'product', 'quantity']

        widgets = {
            'date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control',
                'placeholder': 'Select a date',
            }),
            'product': forms.Select(attrs={
                'class': 'form-control',
            }),
            'quantity': forms.NumberInput(attrs={
                'placeholder': 'e.g. 1',
                'class': 'form-control',
                'min': '1',
            }),
        }

    def __init__(self, *args, **kwargs):
        super(DamageReturnForm, self).__init__(*args, **kwargs)
        # Fetch all products from the database
        products = Product.objects.all()

        # Create a default option
        self.fields['product'].choices = [(0, "--Select Product--")] + [(product.product_id, product.name) for product in
                                                                    products]


class ShipmentOutForm(forms.ModelForm):
    class Meta:
        model = ShipmentOut
        exclude = ['shipmentout_id']

        fields = ['date', 'product', 'quantity']

        widgets = {
            'date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control',
                'placeholder': 'Select a date',
            }),
            'product': forms.Select(attrs={
                'class': 'form-control',
            }),
            'quantity': forms.NumberInput(attrs={
                'placeholder': 'e.g. 1',
                'class': 'form-control',
                'min': '1',
            }),
        }

    def __init__(self, *args, **kwargs):
        super(ShipmentOutForm, self).__init__(*args, **kwargs)
        # Fetch all products from the database
        products = Product.objects.all()

        # Create a default option
        self.fields['product'].choices = [(0, "--Select Product--")] + [(product.product_id, product.name) for product in
                                                                    products]


class ShipmentInForm(forms.ModelForm):
    class Meta:
        model = ShipmentIn
        exclude = ['shipmentin_id']

        fields = ['date', 'product', 'quantity']

        widgets = {
            'date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control',
                'placeholder': 'Select a date',
            }),
            'product': forms.Select(attrs={
                'class': 'form-control',
            }),
            'quantity': forms.NumberInput(attrs={
                'placeholder': 'e.g. 1',
                'class': 'form-control',
                'min': '1',
            }),
        }

    def __init__(self, *args, **kwargs):
        super(ShipmentInForm, self).__init__(*args, **kwargs)
        # Fetch all products from the database
        products = Product.objects.all()

        # Create a default option
        self.fields['product'].choices = [(0, "--Select Product--")] + [(product.product_id, product.name) for product in
                                                                    products]


class ProductOnHoldForm(forms.ModelForm):
    class Meta:
        model = ProductOnHold
        exclude = ['productonhold_id']

        fields = ['date', 'product', 'quantity']

        widgets = {
            'date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control',
                'placeholder': 'Select a date',
            }),
            'product': forms.Select(attrs={
                'class': 'form-control',
            }),
            'quantity': forms.NumberInput(attrs={
                'placeholder': 'e.g. 1',
                'class': 'form-control',
                'min': '1',
            }),
        }

    def __init__(self, *args, **kwargs):
        super(ProductOnHoldForm, self).__init__(*args, **kwargs)
        # Fetch all products from the database
        products = Product.objects.all()

        # Create a default option
        self.fields['product'].choices = [(0, "--Select Product--")] + [(product.product_id, product.name) for product in
                                                                    products]


class RegistrationForm(UserCreationForm):
    # Custom fields (not part of the User model)
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={
        'placeholder': 'Enter your email',
        'class': 'form-control',
    }))
    mobile_number = forms.CharField(max_length=15, widget=forms.TextInput(attrs={
        'placeholder': 'Enter your mobile number',
        'class': 'form-control',
    }))
    company_name = forms.CharField(max_length=50, widget=forms.TextInput(attrs={
        'placeholder': 'Enter your company name',
        'class': 'form-control',
    }))

    class Meta:
        model = User
        fields = ['username', 'email', 'mobile_number', 'company_name', 'password1', 'password2']
        widgets = {
            'username': forms.TextInput(attrs={
                'placeholder': 'Enter your username',
                'class': 'form-control',
            }),
            'email': forms.EmailInput(attrs={
                'placeholder': 'Enter your email',
                'class': 'form-control',
            }),
            'password1': forms.PasswordInput(attrs={
                'placeholder': 'Enter your password',
                'class': 'form-control',  # Same class for consistent design
            }),
            'password2': forms.PasswordInput(attrs={
                'placeholder': 'Confirm your password',
                'class': 'form-control',  # Same class for consistent design
            }),

        }

        help_texts = {
            'password2': '',
            'password1': '',
            'username': '',

        }

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("This email address is already in use.")
        return email

    def clean_mobile_number(self):
        mobile_number = self.cleaned_data.get('mobile_number')
        if not mobile_number.isdigit():
            raise forms.ValidationError("Mobile number must contain only digits.")
        if len(mobile_number) != 10:  # Assuming mobile numbers must be 10 digits
            raise forms.ValidationError("Mobile number must be exactly 10 digits.")
        return mobile_number

    def save(self, commit=True):
        user = super(RegistrationForm, self).save(commit=False)
        user.email = self.cleaned_data['email']

        if commit:
            user.save()

            # Check if a UserProfile for this user already exists
            if not UserProfile.objects.filter(user=user).exists():
                UserProfile.objects.create(
                    user=user,
                    mobile_number=self.cleaned_data['mobile_number'],
                    company_name=self.cleaned_data['company_name']
                )

        return user
