from django.db import models
from django.test import TestCase
from sortedm2m.utils import execute_after_model_is_loaded


class AfterModelLoadingHelper(TestCase):
    def setUp(self):
        self.test_dict = {'executed': False}

    def tearDown(self):
        del self.test_dict

    def set_test_dict(self, model):
        self.test_dict['executed'] = True
        self.test_dict['model'] = model

    def test_model_is_loaded_before(self):
        class PreLoadedModel(models.Model):
            class Meta:
                app_label = 'after_model_loaded'

        execute_after_model_is_loaded(
            'after_model_loaded.PreLoadedModel',
            self.set_test_dict)

        self.assertTrue(self.test_dict['executed'])
        self.assertTrue('model' in self.test_dict)
        self.assertEqual(self.test_dict['model'], PreLoadedModel)

    def test_model_is_loaded_after(self):
        execute_after_model_is_loaded(
            'after_model_loaded.PostLoadedeModel',
            self.set_test_dict)

        self.assertFalse(self.test_dict['executed'])
        self.assertFalse('model' in self.test_dict)

        class PostLoadedeModel(models.Model):
            class Meta:
                app_label = 'after_model_loaded'

        self.assertTrue(self.test_dict['executed'])
        self.assertTrue('model' in self.test_dict)
        self.assertEqual(self.test_dict['model'], PostLoadedeModel)
