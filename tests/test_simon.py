try:
    # Django >= 1.3 provides this in django.utils, but in order to
    # support Django 1.2, it's better to just do it the old fashioned
    # way
    import unittest2 as unittest
except ImportError:
    import unittest

from bson.objectid import ObjectId
from django.conf import settings
from django.http import Http404
try:
    from django.utils.functional import empty
except ImportError:
    # Django < 1.4 used None instead of empty
    empty = None
import django_simon
import mock
from pymongo.errors import InvalidURI
from simon.exceptions import MultipleDocumentsFound, NoDocumentFound

AN_OBJECT_ID_STR = '50d4dce70ea5fae6fb84e44b'
AN_OBJECT_ID = ObjectId(AN_OBJECT_ID_STR)


class TestSimon(unittest.TestCase):
    def tearDown(self):
        """ Kill the config """

        settings._wrapped = empty

    def test_simonize_alias(self):
        """Test the `simonize()` method with an alias."""

        settings.configure(MONGO_DBNAME='simon')

        with mock.patch('simon.connection.connect') as connect:
            django_simon.simonize(alias='test')

            connect.assert_called_with('localhost:27017', name='simon',
                                       alias='test', username=None,
                                       password=None, replica_set=None)

    def test_simonize_default(self):
        """Test the `simonize()` method with defaults."""

        settings.configure(MONGO_DBNAME='simon')

        with mock.patch('simon.connection.connect') as connect:
            django_simon.simonize()

            connect.assert_called_with('localhost:27017', name='simon',
                                       alias=None, username=None,
                                       password=None, replica_set=None)

    def test_simonize_invaliduri(self):
        """Test that `simonize()` raises `InvalidURI`."""

        settings.configure(MONGO_URI='localhost')

        with self.assertRaises(InvalidURI):
            django_simon.simonize()

    def test_simonize_mulitple(self):
        """Test the `simonize()` method with multiple calls."""

        mongo_uri = 'mongodb://localhost/mongo'
        simon_uri = 'mongodb://localhost/simon'
        settings.configure(MONGO_URI=mongo_uri, SIMON_URI=simon_uri)

        with mock.patch('simon.connection.connect') as connect:
            django_simon.simonize()

            connect.assert_called_with(mongo_uri, name='mongo', alias=None,
                                       username=None, password=None,
                                       replica_set=None)

            django_simon.simonize(prefix='SIMON')

            connect.assert_called_with(simon_uri, name='simon', alias=None,
                                       username=None, password=None,
                                       replica_set=None)

    def test_simonize_prefix(self):
        """Test the `simonize()` method with prefixed settings."""

        settings.configure(SIMON_HOST='simon.example.com', SIMON_PORT=1234,
                           SIMON_DBNAME='simon', SIMON_USERNAME='uname',
                           SIMON_PASSWORD='passwd',
                           SIMON_REPLICA_SET='simon-rs')

        with mock.patch('simon.connection.connect') as connect:
            django_simon.simonize(prefix='SIMON')

            connect.assert_called_with('simon.example.com:1234', name='simon',
                                       alias=None, username='uname',
                                       password='passwd',
                                       replica_set='simon-rs')

    def test_simonize_settings(self):
        """Test the `simonize()` method with individual settings."""

        settings.configure(MONGO_HOST='simon.example.com', MONGO_PORT=1234,
                           MONGO_DBNAME='simon', MONGO_USERNAME='uname',
                           MONGO_PASSWORD='passwd',
                           MONGO_REPLICA_SET='simon-rs')

        with mock.patch('simon.connection.connect') as connect:
            django_simon.simonize()

            connect.assert_called_with('simon.example.com:1234', name='simon',
                                       alias=None, username='uname',
                                       password='passwd',
                                       replica_set='simon-rs')

    def test_simonize_uri(self):
        """Test the `simonize()` method with a URI."""

        settings.configure(MONGO_URI='mongodb://localhost/simon')

        with mock.patch('simon.connection.connect') as connect:
            django_simon.simonize()

            connect.assert_called_with('mongodb://localhost/simon',
                                       name='simon', alias=None,
                                       username=None, password=None,
                                       replica_set=None)

    def test_simonize_uri_all(self):
        """Test the `simonize()` method with a URI with everything."""

        uri = 'mongodb://uname:passwd@localhost:1234/simon?replicaSet=simon-rs'
        settings.configure(MONGO_URI=uri)

        with mock.patch('simon.connection.connect') as connect:
            django_simon.simonize()

            connect.assert_called_with(uri, name='simon', alias=None,
                                       username='uname', password='passwd',
                                       replica_set='simon-rs')

    def test_simonize_uri_valueerror(self):
        """Test that `simonize()` raises `ValueError` with a URI."""

        settings.configure(MONGO_URI='mongodb://localhost')

        with self.assertRaises(ValueError) as e:
            django_simon.simonize()

        expected = 'MONGO_URI does not contain a database name.'
        actual = e.exception.message
        self.assertEqual(actual, expected)

    def test_simonize_valueerror(self):
        """Test that `simonize()` raises `ValueError`."""

        settings.configure()

        with self.assertRaises(ValueError) as e:
            django_simon.simonize()

        expected = 'MONGO_DBNAME does not contain a database name.'
        actual = e.exception.message
        self.assertEqual(actual, expected)


class TestMiscellaneous(unittest.TestCase):
    def test_get_list_or_404(self):
        """Test the `get_list_or_404()` method."""

        expected = [{'a': 1}]

        Model = mock.Mock()
        Model.find.return_value = expected

        actual = django_simon.get_list_or_404(Model, a=1)
        self.assertEqual(actual, expected)

    def test_get_list_or_404_http404(self):
        """Test that `get_list_or_404()` raises `Http404`."""

        Model = mock.Mock()
        Model.find.return_value = []

        with self.assertRaises(Http404):
            django_simon.get_list_or_404(Model, a=1)

    def test_get_object_or_404(self):
        """Test the `get_object_or_404()` method."""

        expected = {'a': 1}

        Model = mock.Mock()
        Model.get.return_value = expected

        actual = django_simon.get_object_or_404(Model, a=1)
        self.assertEqual(actual, expected)

    def test_get_object_or_404_http404_multiple(self):
        ("Test that `get_object_or_404()` raises `Http404` with "
         "`MultipleDocumentsFound`.")

        Model = mock.Mock()
        Model.MultipleDocumentsFound = MultipleDocumentsFound
        Model.get.side_effect = Model.MultipleDocumentsFound

        with self.assertRaises(Http404):
            django_simon.get_object_or_404(Model, a=1)

    def test_get_object_or_404_http404_none(self):
        ("Test that `get_object_or_404()` raises `Http404` with "
         "`NoDocumentFound`.")

        Model = mock.Mock()
        Model.NoDocumentFound = NoDocumentFound
        Model.get.side_effect = Model.NoDocumentFound

        with self.assertRaises(Http404):
            django_simon.get_object_or_404(Model, a=1)
