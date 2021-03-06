# Copyright (c) 2017 LINE Corporation
# These sources are released under the terms of the MIT license: see LICENSE

import json
from unittest import mock
from django.contrib.auth.models import User
from django.test import TestCase, override_settings
from django.urls import reverse

from promgen import models
from promgen.tests import TEST_ALERT, TEST_IMPORT, TEST_REPLACE, TEST_SETTINGS


class RouteTests(TestCase):
    longMessage = True

    def setUp(self):
        self.client.force_login(User.objects.create_user(id=999, username="Foo"), 'django.contrib.auth.backends.ModelBackend')

    @override_settings(PROMGEN=TEST_SETTINGS)
    @override_settings(CELERY_TASK_ALWAYS_EAGER=True)
    def test_alert(self):
        response = self.client.post(reverse('alert'), data=json.dumps(TEST_ALERT), content_type='application/json')
        self.assertEqual(response.status_code, 200)

    @override_settings(PROMGEN=TEST_SETTINGS)
    @override_settings(CELERY_TASK_ALWAYS_EAGER=True)
    @mock.patch('promgen.signals._trigger_write_config')
    @mock.patch('promgen.prometheus.reload_prometheus')
    def test_import(self, mock_write, mock_reload):
        response = self.client.post(reverse('import'), {
            'config': json.dumps(TEST_IMPORT)
        })

        self.assertEqual(response.status_code, 302, 'Redirect to imported object')
        self.assertEqual(models.Service.objects.count(), 1, 'Import one service')
        self.assertEqual(models.Project.objects.count(), 2, 'Import two projects')
        self.assertEqual(models.Exporter.objects.count(), 2, 'Import two exporters')
        self.assertEqual(models.Host.objects.count(), 3, 'Import three hosts')
        self.assertEqual(models.Farm.objects.filter(source='pmc').count(), 1, 'One PMC Farm')
        self.assertEqual(models.Farm.objects.filter(source='other').count(), 1, 'One other Farm')

    @override_settings(PROMGEN=TEST_SETTINGS)
    @override_settings(CELERY_TASK_ALWAYS_EAGER=True)
    @mock.patch('promgen.signals._trigger_write_config')
    @mock.patch('promgen.prometheus.reload_prometheus')
    def test_replace(self, mock_write, mock_reload):
        response = self.client.post(reverse('import'), {
            'config': json.dumps(TEST_IMPORT)
        })
        self.assertEqual(response.status_code, 302, 'Redirect to imported object')

        response = self.client.post(reverse('import'), {
            'config': json.dumps(TEST_REPLACE)
        })
        self.assertEqual(response.status_code, 302, 'Redirect to imported object (2)')

        self.assertEqual(models.Service.objects.count(), 1, 'Import one service')
        self.assertEqual(models.Project.objects.count(), 2, 'Import two projects')
        self.assertEqual(models.Exporter.objects.count(), 2, 'Import two exporters')
        self.assertEqual(models.Farm.objects.count(), 3, 'Original two farms and one new farm')
        self.assertEqual(models.Host.objects.count(), 5, 'Original 3 hosts and two new ones')

    def test_service(self):
        response = self.client.get(reverse('service-list'))
        self.assertEqual(response.status_code, 200)

    def test_project(self):
        shard = models.Shard.objects.create(name='Shard Test')
        service = models.Service.objects.create(name='Service Test', shard=shard)
        project = models.Project.objects.create(name='Project Test', service=service)

        response = self.client.get(reverse('project-detail', kwargs={'pk': project.pk}))
        self.assertEqual(response.status_code, 200)

    def test_farms(self):
        response = self.client.get(reverse('farm-list'))
        self.assertEqual(response.status_code, 200)

    def test_hosts(self):
        response = self.client.get(reverse('host-list'))
        self.assertEqual(response.status_code, 200)
