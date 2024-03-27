# -*- coding: utf-8 -*-
import logging

from .test_lms_common import TestLmsCommon


class TestCourseMaterial(TestLmsCommon):

    def setUp(self):
        super(TestCourseMaterial, self).setUp()

    def details_of_material(self, case_number, data, video=False):
        logging.info('Test Case - %.2f : %s' % (case_number, data.name))
        logging.info('Record Id     : %d' % data.id)
        logging.info('Material Type : %s' % data.material_type)
        if video:
            logging.info('Document Url  : %s' % data.url)
            logging.info('Document Id   : %s' % data.document_id)

    def material_python_intro_course(self):
        data = self.env.ref(
            'openeducat_lms.material_python_intro_course')
        if not data:
            raise AssertionError(
                'Error in data, please check for '
                'demo data : openeducat_lms.material_python_intro_course')
        data.on_change_url()
        self.details_of_material(1.01, data, True)
        return data

    def material_python_words(self):
        data = self.env.ref(
            'openeducat_lms.material_python_words')
        if not data:
            raise AssertionError(
                'Error in data, please check for '
                'demo data : openeducat_lms.material_python_words')
        data.on_change_url()
        self.details_of_material(1.02, data, True)
        return data

    def material_python_anaconda_bundle(self):
        data = self.env.ref(
            'openeducat_lms.material_python_anaconda_bundle')
        if not data:
            raise AssertionError(
                'Error in data, please check for '
                'demo data : openeducat_lms.material_python_anaconda_bundle')
        data.on_change_url()
        self.details_of_material(1.03, data, True)
        return data

    def material_python_install(self):
        data = self.env.ref(
            'openeducat_lms.material_python_install')
        if not data:
            raise AssertionError(
                'Error in data, please check for '
                'demo data : openeducat_lms.material_python_install')
        data.on_change_url()
        self.details_of_material(1.04, data, True)
        return data

    def material_python_syntax_pdf(self):
        data = self.env.ref(
            'openeducat_lms.material_python_syntax_pdf')
        if not data:
            raise AssertionError(
                'Error in data, please check for '
                'demo data : openeducat_lms.material_python_syntax_pdf')
        data.on_change_url()
        self.details_of_material(1.05, data, True)
        return data

    def material_python_variable(self):
        data = self.env.ref(
            'openeducat_lms.material_python_variable')
        if not data:
            raise AssertionError(
                'Error in data, please check for '
                'demo data : openeducat_lms.material_python_variable')
        data.on_change_url()
        self.details_of_material(1.06, data, True)
        return data

    def material_python_string_number(self):
        data = self.env.ref(
            'openeducat_lms.material_python_string_number')
        if not data:
            raise AssertionError(
                'Error in data, please check for '
                'demo data : openeducat_lms.material_python_string_number')
        data.on_change_url()
        self.details_of_material(1.07, data, True)
        return data

    def material_python_functions(self):
        data = self.env.ref(
            'openeducat_lms.material_python_functions')
        if not data:
            raise AssertionError(
                'Error in data, please check for '
                'demo data : openeducat_lms.material_python_functions')
        data.on_change_url()
        self.details_of_material(1.08, data, True)
        return data

    def material_python_cnd_image(self):
        data = self.env.ref(
            'openeducat_lms.material_python_cnd_image')
        if not data:
            raise AssertionError(
                'Error in data, please check for '
                'demo data : openeducat_lms.material_python_cnd_image')
        data.on_change_url()
        self.details_of_material(1.09, data, True)
        return data

    def material_python_sequence_list(self):
        data = self.env.ref(
            'openeducat_lms.material_python_sequence_list')
        if not data:
            raise AssertionError(
                'Error in data, please check for '
                'demo data : openeducat_lms.material_python_sequence_list')
        data.on_change_url()
        self.details_of_material(1.10, data, True)
        return data

    def material_python_iteration(self):
        data = self.env.ref(
            'openeducat_lms.material_python_iteration')
        if not data:
            raise AssertionError(
                'Error in data, please check for '
                'demo data : openeducat_lms.material_python_iteration')
        data.on_change_url()
        self.details_of_material(1.11, data, True)
        return data

    def material_python_files(self):
        data = self.env.ref(
            'openeducat_lms.material_python_files')
        if not data:
            raise AssertionError(
                'Error in data, please check for '
                'demo data : openeducat_lms.material_python_files')
        data.on_change_url()
        self.details_of_material(1.12, data, True)
        return data

    def material_python_files_rw(self):
        data = self.env.ref(
            'openeducat_lms.material_python_files_rw')
        if not data:
            raise AssertionError(
                'Error in data, please check for '
                'demo data : openeducat_lms.material_python_files_rw')
        data.on_change_url()
        self.details_of_material(1.13, data, True)
        return data

    def material_french_video(self):
        data = self.env.ref(
            'openeducat_lms.material_french_video')
        if not data:
            raise AssertionError(
                'Error in data, please check for '
                'demo data : openeducat_lms.material_french_video')
        data.on_change_url()
        self.details_of_material(2.1, data, True)
        return data

    def material_french_pdf(self):
        data = self.env.ref('openeducat_lms.material_french_pdf')
        if not data:
            raise AssertionError(
                'Error in data, please check for '
                'demo data : openeducat_lms.material_french_pdf')
        self.details_of_material(2.2, data)
        return data

    def material_french_image(self):
        data = self.env.ref('openeducat_lms.material_french_image')
        if not data:
            raise AssertionError(
                'Error in data, please check for '
                'demo data : openeducat_lms.material_french_image')
        self.details_of_material(2.3, data)
        return data

    def material_sell_video(self):
        data = self.env.ref(
            'openeducat_lms.material_sell_video')
        if not data:
            raise AssertionError(
                'Error in data, please check for '
                'demo data : openeducat_lms.material_sell_video')
        data.on_change_url()
        self.details_of_material(3.1, data, True)
        return data

    def material_sell_pdf(self):
        data = self.env.ref('openeducat_lms.material_sell_pdf')
        if not data:
            raise AssertionError(
                'Error in data, please check for '
                'demo data : openeducat_lms.material_sell_pdf')
        self.details_of_material(3.2, data)
        return data

    def material_sell_image(self):
        data = self.env.ref('openeducat_lms.material_sell_image')
        if not data:
            raise AssertionError(
                'Error in data, please check for '
                'demo data : openeducat_lms.material_sell_image')
        self.details_of_material(3.3, data)
        return data
