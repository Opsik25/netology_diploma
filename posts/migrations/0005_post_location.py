# Generated by Django 5.0.2 on 2024-05-31 17:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0004_comment_updated_at_post_updated_at'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='location',
            field=models.CharField(blank=True, max_length=64, null=True),
        ),
    ]
