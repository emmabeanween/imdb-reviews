# Generated by Django 2.2.2 on 2019-08-19 05:57

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Movie',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=500)),
                ('summary', models.CharField(max_length=8000)),
                ('actors', models.CharField(max_length=1000)),
                ('release_date', models.DateTimeField()),
                ('movie_id', models.CharField(max_length=10)),
            ],
        ),
    ]