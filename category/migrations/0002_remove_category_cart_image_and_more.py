# Generated by Django 4.2.7 on 2023-11-16 17:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('category', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='category',
            name='cart_image',
        ),
        migrations.RemoveField(
            model_name='category',
            name='description',
        ),
        migrations.AddField(
            model_name='category',
            name='icon',
            field=models.CharField(default=0, max_length=200),
            preserve_default=False,
        ),
    ]
