# Generated by Django 2.2.16 on 2023-04-06 16:57

from django.db import migrations, models
import django.db.models.expressions


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0009_auto_20230406_1954'),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name='follow',
            name='without_self-subscription',
        ),
        migrations.AddConstraint(
            model_name='follow',
            constraint=models.CheckConstraint(check=models.Q(_negated=True, user=django.db.models.expressions.F('author')), name='without_self-subscription'),
        ),
    ]