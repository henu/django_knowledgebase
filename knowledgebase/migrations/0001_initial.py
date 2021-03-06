# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2017-11-24 15:16
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Concept',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('description', models.TextField(blank=True, default=None, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='QuantityValue',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('value', models.DecimalField(decimal_places=12, max_digits=30)),
                ('lower_bound', models.DecimalField(blank=True, decimal_places=12, max_digits=30, null=True)),
                ('upper_bound', models.DecimalField(blank=True, decimal_places=12, max_digits=30, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Statement',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('concept', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='statements', to='knowledgebase.Concept')),
                ('pred', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='as_predicate', to='knowledgebase.Concept')),
                ('statement', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='qualifiers', to='knowledgebase.Statement')),
                ('value', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='as_value', to='knowledgebase.Concept')),
            ],
        ),
        migrations.CreateModel(
            name='StringValue',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('value', models.TextField()),
                ('statement', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='string_value', to='knowledgebase.Statement')),
            ],
        ),
        migrations.CreateModel(
            name='Translation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('translation', models.CharField(max_length=250)),
                ('lang', models.CharField(max_length=15)),
                ('case', models.CharField(blank=True, default=None, max_length=40, null=True)),
                ('concept', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='translations', to='knowledgebase.Concept')),
            ],
        ),
        migrations.AddField(
            model_name='quantityvalue',
            name='statement',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='quantity_value', to='knowledgebase.Statement'),
        ),
        migrations.AlterUniqueTogether(
            name='translation',
            unique_together=set([('lang', 'case')]),
        ),
        migrations.AlterIndexTogether(
            name='translation',
            index_together=set([('lang', 'case')]),
        ),
    ]
