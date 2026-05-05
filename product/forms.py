from .models import *
from django import forms


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name']


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['title', 'category', 'actual_price', 'discounted_price', 'image', 'trending', 's_description', 'l_description', 'stock', 'tag']