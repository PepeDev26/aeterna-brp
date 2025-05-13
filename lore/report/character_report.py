# -*- coding: utf-8 -*-
from odoo import api, models


class CharacterProfileReport(models.AbstractModel):
    _name = 'report.lore.report_character_profile'
    _description = 'Reporte de Ficha de Personaje'

    @api.model
    def _get_report_values(self, docids, data=None):
        docs = self.env['character.profile'].browse(docids)
        return {
            'doc_ids': docids,
            'doc_model': 'character.profile',
            'docs': docs,
            'get_gender': self._get_gender,
            'get_alignment': self._get_alignment,
        }

    def _get_gender(self, gender_code):
        genders = {
            'male': 'Masculino',
            'female': 'Femenino',
            'other': 'Otro'
        }
        return genders.get(gender_code, '')

    def _get_alignment(self, alignment_code):
        alignments = {
            'lg': 'Legal Bueno',
            'ng': 'Neutral Bueno',
            'cg': 'Caótico Bueno',
            'ln': 'Legal Neutral',
            'tn': 'Neutral',
            'cn': 'Caótico Neutral',
            'le': 'Legal Maligno',
            'ne': 'Neutral Maligno',
            'ce': 'Caótico Maligno',
        }
        return alignments.get(alignment_code, '')
