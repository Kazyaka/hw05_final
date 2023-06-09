# Generated by Django 2.2.16 on 2023-04-06 16:54

from django.db import migrations, models
import django.db.models.expressions


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0008_auto_20230406_1647'),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name='follow',
            name='following',
        ),
        migrations.AddConstraint(
            model_name='follow',
            constraint=models.UniqueConstraint(fields=('author', 'user'), name='unique_subscription'),
        ),
        migrations.AddConstraint(
            model_name='follow',
            constraint=models.CheckConstraint(check=models.Q(user=django.db.models.expressions.F('author')), name='without_self-subscription'),
        ),
    ]
