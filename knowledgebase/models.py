# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings
from django.db import models


class Concept(models.Model):
    description = models.TextField(null=True, blank=True, default=None)

    def get_translation(self, lang=settings.LANGUAGE_CODE, case=None):
        """ Tries to get proper translation and case, but may return
        some other translation or case, if requested one is not available.
        """

        # Try requested language and case
        translation = self.translations.filter(lang=lang, case=case).first()
        if translation:
            return translation.translation

        # Try requested language
        translation = self.translations.filter(lang=lang).first()
        if translation:
            return translation.translation

        # Try any language
        translation = self.translations.first()
        if translation:
            return translation.translation

        return ''

    def __unicode__(self):
        return self.get_translation() or self.description


class Translation(models.Model):
    concept = models.ForeignKey(Concept, related_name='translations')
    translation = models.CharField(max_length=250)
    lang = models.CharField(max_length=15)
    case = models.CharField(max_length=40, null=True, blank=True, default=None)

    class Meta:
        unique_together = ['lang', 'case']
        index_together = ['lang', 'case']

    def __unicode__(self):
        if self.case:
            return '{} ({}:{})'.format(self.translation, self.lang, self.case)
        return '{} ({})'.format(self.translation, self.lang)


class Statement(models.Model):
    concept = models.ForeignKey(Concept, related_name='statements', null=True, blank=True)
    statement = models.ForeignKey('Statement', related_name='qualifiers', null=True, blank=True)
    pred = models.ForeignKey(Concept, related_name='as_predicate')
    value = models.ForeignKey(Concept, related_name='as_value', null=True, blank=True)

    updated_at = models.DateTimeField(auto_now=True)

    def get_value_as_string(self):
        if self.value:
            return '{:s}'.format(self.value)
        if hasattr(self, 'string_value'):
            return '{:s}'.format(self.string_value)
        if hasattr(self, 'quantity_value'):
            return '{}'.format(self.quantity_value)
        return '*NO VALUE*'

    def __unicode__(self):
        if self.concept:
            return '{}, {}, {}'.format(self.concept, self.pred, self.get_value_as_string())
        assert self.statement
        return '{} ({}, {})'.format(self.statement, self.pred, self.get_value_as_string())


class StringValue(models.Model):
    statement = models.OneToOneField(Statement, related_name='string_value')
    value = models.TextField()

    def __unicode__(self):
        return '"{}"'.format(self.value)


class QuantityValue(models.Model):
    statement = models.OneToOneField(Statement, related_name='quantity_value')
    value = models.DecimalField(max_digits=30, decimal_places=12)
    lower_bound = models.DecimalField(max_digits=30, decimal_places=12, null=True, blank=True)
    upper_bound = models.DecimalField(max_digits=30, decimal_places=12, null=True, blank=True)

    def __unicode__(self):
        if self.lower_bound is not None and self.upper_bound is not None:
            return '{} - {}'.format(self.lower_bound, self.upper_bound)
        return '{}'.format(self.value)
