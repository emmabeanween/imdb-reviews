# Generated by Django 2.2.2 on 2019-09-04 04:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('imdbreviews', '0004_auto_20190828_0234'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('username', models.CharField(max_length=100)),
                ('password', models.CharField(max_length=100)),
                ('user_id', models.CharField(max_length=100)),
                ('num_reviews', models.IntegerField()),
                ('date_joined', models.DateTimeField()),
            ],
        ),
        migrations.AlterField(
            model_name='movie',
            name='actors',
            field=models.CharField(max_length=100000),
        ),
    ]