# Generated by Django 5.1.3 on 2025-05-07 14:17

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('blogapp', '0004_alter_blog_gender'),
    ]

    operations = [
        migrations.RenameField(
            model_name='blog',
            old_name='gender',
            new_name='genre',
        ),
    ]
