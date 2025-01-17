# Generated by Django 4.2.4 on 2024-01-20 15:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cart', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cart',
            name='is_checked',
            field=models.BooleanField(blank=True, default=1, help_text='是否选中', verbose_name='是否选中'),
        ),
        migrations.AlterField(
            model_name='cart',
            name='number',
            field=models.SmallIntegerField(blank=True, default=1, help_text='商品数量', verbose_name='商品数量'),
        ),
    ]
