# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
from django.utils.html import format_html

from knowledgebase.models import Concept, Translation, Statement, StringValue, QuantityValue, TimeValue

@admin.register(Concept)
class ConceptAdmin(admin.ModelAdmin):

    readonly_fields = ['show_statements', 'show_translations']

    def show_statements(self, instance):
        html = format_html('<ul>')
        for statement in instance.statements.all():
            html += format_html('<li>{}: {}', statement.pred, statement.get_value_as_string())
            if statement.qualifiers.exists():
                html += format_html('<ul>')
                for qualifier in statement.qualifiers.all():
                    html += format_html('<li>{}: {}</li>', qualifier.pred, qualifier.get_value_as_string())
                html += format_html('</ul>')
            html += format_html('</li>')
        html += format_html('</ul>')
        return html
    show_statements.short_description = 'Statements'

    def show_translations(self, instance):
        html = format_html('<ul>')
        for translation in instance.translations.all():
            if translation.case:
                html += format_html('<li>{} / {}: {}</li>', translation.lang, translation.case, translation.translation)
            else:
                html += format_html('<li>{}: {}</li>', translation.lang, translation.translation)
        html += format_html('</ul>')
        return html
    show_translations.short_description = 'Translations'

@admin.register(Translation)
class TranslationAdmin(admin.ModelAdmin):
    pass

@admin.register(Statement)
class StatementAdmin(admin.ModelAdmin):
    pass

@admin.register(StringValue)
class StringValueAdmin(admin.ModelAdmin):
    pass

@admin.register(QuantityValue)
class QuantityValueAdmin(admin.ModelAdmin):
    pass

@admin.register(TimeValue)
class TimeValueAdmin(admin.ModelAdmin):
    pass
