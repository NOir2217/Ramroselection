from django.db import migrations, models
import products.models

class Migration(migrations.Migration):

    dependencies = [
        ('products', '0004_alter_product_brand_alter_product_finish_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='closure_type',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='product',
            name='material',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='product',
            name='image',
            field=models.ImageField(blank=True, max_length=500, null=True, upload_to='products/primary/', validators=[products.models.validate_image_size]),
        ),
        migrations.AlterField(
            model_name='product',
            name='product_type',
            field=models.CharField(choices=[('clothing', 'Clothing'), ('bags', 'Bags'), ('cosmetics', 'Cosmetics'), ('other', 'Other')], default='other', max_length=20),
        ),
        migrations.AlterField(
            model_name='productimage',
            name='image_url',
            field=models.ImageField(blank=True, max_length=500, null=True, upload_to='products/gallery/', validators=[products.models.validate_image_size]),
        ),
    ]
