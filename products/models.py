import os
from io import BytesIO

from PIL import Image
from django.core.files.uploadedfile import SimpleUploadedFile
from django.db import models
from django.db.models import Manager, QuerySet, OuterRef, Sum, Subquery
from django.db.models.functions import Coalesce
from django.db.models.signals import post_save
from django.dispatch import receiver

from orders.models import OrderProduct


class Category(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Tag(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class ProductQuerySet(QuerySet):
    def popular(self):
        return self.annotate(
            total_quantity=Coalesce(Sum('orderproduct__quantity'), 0, output_field=models.DecimalField())
        ).order_by('-total_quantity')


class ProductManager(Manager):
    def get_queryset(self):
        return ProductQuerySet(self.model, using=self._db)

    def popular(self):
        return self.get_queryset().popular()


class Product(models.Model):
    name = models.CharField(max_length=255, unique=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)  # 99999999.99
    description = models.TextField(blank=True, null=True)
    is_18_plus = models.BooleanField(default=False)

    category = models.ForeignKey(Category, null=True, blank=True, on_delete=models.CASCADE, related_name='products')
    # CASCADE - delete all products in this category
    # SET_NULL - set category to NULL
    # SET_DEFAULT - set category to default value
    # RESTRICT - raise an error
    # DO_NOTHING - do nothing
    # PROTECT - raise an error (same as RESTRICT)

    tags = models.ManyToManyField(Tag, blank=True)

    # Active Record pattern
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    image = models.ImageField(upload_to='products', null=True, blank=True)

    manual = models.FileField(upload_to='manuals', null=True, blank=True)

    objects = ProductManager()

    def __str__(self):
        return self.name

    def process_image(self):
        image = Image.open(self.image)
        image.thumbnail((200, 200))

        _, thumb_extension = os.path.splitext(self.image.name)

        thumb_name = self.name

        thumb_filename = thumb_name + "_thumb" + ".jpg"

        temp_thumb = BytesIO()
        image.convert("RGB").save(temp_thumb, format='JPEG')
        temp_thumb.seek(0)

        # set save=False, otherwise it will run in an infinite loop
        self.image.save(thumb_filename,
                        SimpleUploadedFile(
                            thumb_filename,
                            temp_thumb.read(),
                            content_type=f"image/jpeg",
                        ),
                        save=False)


    def save(
        self, force_insert=False, force_update=False, using=None, update_fields=None
    ):
        # If image changed - process it
        if not self.pk:
            self.process_image()
        else:
            # Get current product
            current_product = Product.objects.filter(pk=self.pk).first()
            current_image = current_product.image if current_product else None

            # If image changed - process it
            if current_image.name != self.image.name:
                self.process_image()

        return super().save(force_insert, force_update, using, update_fields)


@receiver(post_save, sender=Product)
def clear_cache(sender, instance, **kwargs):
    from django.core.cache import cache
    cache.delete('popular_products')

    # Delete all orders cache
    keys = cache.keys('orders:*')
    cache.delete_many(keys)
