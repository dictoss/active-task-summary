from django.test import TestCase


class TestLib(TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass


class TestViews(TestCase):
    fixtures = ['test_views.json']

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_login_top(self):
        self.assertTrue(True)

    def test_manage(self):
        self.assertTrue(True)

    def test_manage_chpasswd(self):
        self.assertTrue(True)

    def test_summary(self):
        self.assertTrue(True)

    def test_summary_project(self):
        self.assertTrue(True)

    def test_summary_job(self):
        self.assertTrue(True)

    def test_summary_user(self):
        self.assertTrue(True)

    def test_regist(self):
        self.assertTrue(True)
