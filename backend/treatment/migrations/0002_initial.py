# Generated by Django 5.1 on 2024-09-05 10:09

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('treatment', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='treatmenthistory',
            name='doctor',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='treatments_given', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='treatmenthistory',
            name='patient',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='treatment_histories', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='treatmenthistory',
            name='treatment',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='treatment.treatment'),
        ),
    ]
