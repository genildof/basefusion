from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('processamento', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='baseconsolidada',
            name='delta_rec_liq',
            field=models.FloatField(null=True, blank=True),
        ),
    ] 