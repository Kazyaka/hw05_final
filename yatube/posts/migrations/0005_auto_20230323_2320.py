# Generated by Django 2.2.16 on 2023-03-23 20:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0004_alter_group_options_alter_post_options'),
    ]

    operations = [
        migrations.AlterField(
            model_name='group',
            name='description',
            field=models.TextField(help_text='введите описание группы (максимум 400 символов)', max_length=400, verbose_name='Описание'),
        ),
    ]
