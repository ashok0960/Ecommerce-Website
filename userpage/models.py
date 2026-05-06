from django.db import models
from django.core.validators import MinLengthValidator
from product.models import*
from django.contrib.auth.models import User


# Create your models here.
class Setting(models.Model):
    name = models.CharField(max_length=130)
    favicon =models.ImageField(upload_to='static/uploads/')
    logo = models.ImageField(upload_to='static/uploads/')
    email = models.EmailField()
    address = models.CharField(max_length=300)
    phone = models.CharField(max_length=14, validators=[MinLengthValidator(9)])
    fb_link = models.URLField(blank=True)
    insta_link = models.URLField(blank=True)
    linkedin_link = models.URLField(blank=True)


    def __str__(self):
        return self.name


class Cart(models.Model):
    product = models.ForeignKey(Product,on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.user.username}-{self.product.title}"
    


class Order(models.Model):
    STATUS =(('In Progress','In Progress'),
             ('way to deliver','way to deliver'),
             ('Complete','complete'))
    PAYMENTS=(('COD','COD'),
              ('Card','Card (Stripe)'),
              ('Khalti','Khalti'),
              ('Daraja','Daraja (M-Pesa)'))

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    total_price = models.FloatField()
    address = models.CharField(max_length=300)
    email= models.EmailField()
    phone = models.CharField(max_length=14, validators=[MinLengthValidator(10)])
    payment_method = models.CharField(max_length=20, choices=PAYMENTS)
    payment_status = models.CharField(default=False,null=True)
    order_status = models.CharField(max_length=20, choices=STATUS,default='In Progress')
    transaction_id = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Order #{self.id} - {self.user.username}"

    def can_delete(self):
        """Check if order can be deleted by user"""
        # Users can delete unpaid orders only
        if self.payment_status == False or self.payment_status == 'False':
            return True
        return False

    def is_paid(self):
        """Check if order is paid"""
        return self.payment_status == True or self.payment_status == 'True'


class Contact(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    subject = models.CharField(max_length=200)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.subject}"


class Wishlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'product')

    def __str__(self):
        return f"{self.user.username} - {self.product.title}"

    def __str__(self):
        return f"{ self.user.username}-{self.product.title}"