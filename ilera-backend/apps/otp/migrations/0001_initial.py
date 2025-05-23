# Generated by Django 5.2.1 on 2025-05-21 17:08

import apps.core.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='OTPRequest',
            fields=[
                ('id', apps.core.fields.ULIDField(editable=False, max_length=26, primary_key=True, serialize=False, unique=True)),
                ('phone', models.CharField(max_length=15)),
                ('code', models.CharField(max_length=6)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('is_verified', models.BooleanField(default=False)),
            ],
            options={
                'verbose_name': 'OTP Request',
                'ordering': ['-created_at'],
                'indexes': [models.Index(fields=['phone', 'code'], name='otp_otprequ_phone_8c7036_idx')],
            },
        ),
    ]
