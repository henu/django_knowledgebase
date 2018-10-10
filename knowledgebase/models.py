# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from dateutil.relativedelta import relativedelta

from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _


@python_2_unicode_compatible
class Concept(models.Model):
    description = models.TextField(null=True, blank=True, default=None)

    def get_translation(self, lang=settings.LANGUAGE_CODE, case=None, strict_case=False):
        """ Tries to get proper translation and case, but may return
        some other translation or case, if requested one is not available.

        If "strict_case" is set to true, then None is returned if case was not found
        """

        # Try requested language and case
        translation = self.translations.filter(lang=lang, case=case).first()
        if translation:
            return translation.translation
        if strict_case:
            return None

        # Try requested language
        translation = self.translations.filter(lang=lang).first()
        if translation:
            return translation.translation

        # Try any language
        translation = self.translations.first()
        if translation:
            return translation.translation

        return ''

    def __str__(self):
        return self.get_translation() or self.description


@python_2_unicode_compatible
class Translation(models.Model):
    concept = models.ForeignKey(Concept, related_name='translations', on_delete=models.CASCADE)
    translation = models.CharField(max_length=250)
    lang = models.CharField(max_length=15)
    case = models.CharField(max_length=40, null=True, blank=True, default=None)

    class Meta:
        unique_together = ['lang', 'case']
        index_together = ['lang', 'case']

    def __str__(self):
        if self.case:
            return '{} ({}:{})'.format(self.translation, self.lang, self.case)
        return '{} ({})'.format(self.translation, self.lang)


@python_2_unicode_compatible
class Statement(models.Model):
    concept = models.ForeignKey(Concept, related_name='statements', on_delete=models.CASCADE, null=True, blank=True)
    statement = models.ForeignKey('Statement', related_name='qualifiers', on_delete=models.CASCADE, null=True, blank=True)
    pred = models.ForeignKey(Concept, related_name='as_predicate', on_delete=models.CASCADE)
    value = models.ForeignKey(Concept, related_name='as_value', on_delete=models.CASCADE, null=True, blank=True)

    updated_at = models.DateTimeField(auto_now=True)

    def get_value_as_string(self):
        if self.value:
            return '{:s}'.format(str(self.value))
        if hasattr(self, 'string_value'):
            return '{:s}'.format(str(self.string_value))
        if hasattr(self, 'quantity_value'):
            return '{}'.format(str(self.quantity_value))
        if hasattr(self, 'time_value'):
            return '{}'.format(str(self.time_value))
        if hasattr(self, 'coordinate_value'):
            return '{}'.format(str(self.coordinate_value))
        return '*NO VALUE*'

    def __str__(self):
        if self.concept:
            return '{}, {}, {}'.format(str(self.concept), str(self.pred), self.get_value_as_string())
        assert self.statement
        return '{} ({}, {})'.format(str(self.statement), str(self.pred), self.get_value_as_string())


@python_2_unicode_compatible
class StringValue(models.Model):
    statement = models.OneToOneField(Statement, related_name='string_value', on_delete=models.CASCADE)
    value = models.TextField()

    def __str__(self):
        return '"{}"'.format(self.value)


@python_2_unicode_compatible
class QuantityValue(models.Model):
    statement = models.OneToOneField(Statement, related_name='quantity_value', on_delete=models.CASCADE)
    value = models.DecimalField(max_digits=30, decimal_places=12)
    lower_bound = models.DecimalField(max_digits=30, decimal_places=12, null=True, blank=True)
    upper_bound = models.DecimalField(max_digits=30, decimal_places=12, null=True, blank=True)

    def __str__(self):
        if self.lower_bound is not None and self.upper_bound is not None:
            return '{} - {}'.format(self.lower_bound, self.upper_bound)
        return '{}'.format(self.value)


# TODO: Support negative years and also billions of years
@python_2_unicode_compatible
class TimeValue(models.Model):
    PRECISION_CHOICES = [
        (6, _('millenium')),
        (7, _('century')),
        (8, _('decade')),
        (9, _('year')),
        (10, _('month')),
        (11, _('day')),
        (12, _('hour')),
        (13, _('minute')),
        (14, _('second')),
    ]

    statement = models.OneToOneField(Statement, related_name='time_value', on_delete=models.CASCADE)
    value = models.DateTimeField()

    precision = models.PositiveSmallIntegerField(choices=PRECISION_CHOICES)

    # If time point is not exact, before and after can be used. Measured in precision units.
    before = models.PositiveIntegerField(null=True, blank=True)
    after = models.PositiveIntegerField(null=True, blank=True)

    def __str__(self):
        if self.precision == 6:
            year = int(round(self.value.year / 1000.0)) * 1000
            year_unit = 1000
        elif self.precision == 7:
            year = int(round(self.value.year / 100.0)) * 100
            yar_unit = 100
        elif self.precision == 8:
            year = int(round(self.value.year / 1.0)) * 10
            year_unit = 10
        elif self.precision >= 9:
            year = self.value.year
            year_unit = 1

        # Only years
        if self.precision <= 9:
            if self.before is not None and self.after is not None:
                if self.before > 0 or self.after > 0:
                    return '{} – {}'.format(year - year_unit * self.before, year + year_unit * self.after)
            return str(year)

        if self.before is not None and self.after is not None and (self.before > 0 or self.after > 0):
            if self.precision == 10:
                date_before = self.value - relativedelta(months=self.before)
                date_after = self.value + relativedelta(months=self.after)
            elif self.precision == 11:
                date_before = self.value - relativedelta(days=self.before)
                date_after = self.value + relativedelta(days=self.after)
            elif self.precision == 12:
                date_before = self.value - relativedelta(hours=self.before)
                date_after = self.value + relativedelta(hours=self.after)
            elif self.precision == 13:
                date_before = self.value - relativedelta(minutes=self.before)
                date_after = self.value + relativedelta(minutes=self.after)
            elif self.precision == 14:
                date_before = self.value - relativedelta(seconds=self.before)
                date_after = self.value + relativedelta(seconds=self.after)
            return '{} – {}'.format(self._to_precision_date(date_before), self._to_precision_date(date_after))

        return self._to_precision_date(self.value)

    def _to_precision_date(self, value):
        result = '{:04d}.{:02d}'.format(value.year, value.month)
        if self.precision >= 11:
            result += '.{:02d}'.format(value.day)
        if self.precision >= 12:
            result += ' {:02d}'.format(value.hour)
        if self.precision >= 13:
            result += ':{:02d}'.format(value.minute)
        if self.precision >= 14:
            result += ':{:02d}'.format(value.second)
        return result


@python_2_unicode_compatible
class CoordinateValue(models.Model):
    statement = models.OneToOneField(Statement, related_name='coordinate_value', on_delete=models.CASCADE)
    latitude = models.FloatField(validators=[MinValueValidator(-90), MaxValueValidator(90)])
    longitude = models.FloatField(validators=[MinValueValidator(-180), MaxValueValidator(180)])
    precision_m = models.FloatField(default=0)
    height_m = models.FloatField(null=True, blank=True, default=None)
    globe = models.ForeignKey(Concept, related_name='coordinates', on_delete=models.PROTECT)

    def __str__(self):
        if self.height_m is None:
            return '{} lat, {} lon with {} m precision on {}'.format(
                self.latitude, self.longitude, self.precision_m, str(self.globe)
            )
        return '{} lat, {} lon at {} m height with {} m precision on {}'.format(
            self.latitude, self.longitude, self.height_m, self.precision_m, str(self.globe)
        )


@python_2_unicode_compatible
class Reference(models.Model):
    statements = models.ManyToManyField(Statement, related_name='references')
    url = models.URLField(unique=True, max_length=250, null=True, blank=True)
    description = models.CharField(max_length=250, null=True, blank=True)

    def __str__(self):
        if self.url:
            return self.url
        if self.description:
            return self.description
        return ''
