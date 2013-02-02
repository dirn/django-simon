__version__ = '0.1.0'

from django.conf import settings
from django.http import Http404
from pymongo import uri_parser
from simon import connection

__all__ = ('simonize', 'get_list_or_404', 'get_object_or_404')


def simonize(prefix='MONGO', alias=None):
    """Automatically creates a connection for Simon models.

    :param prefix: (optional) the prefix of the settings
    :type prefix: str
    :param alias: (optional) the alias to use for the database
                  connection
    :type alias: str

    .. versionadded:: 0.1.0
    """

    def key(name):
        """Prepends the prefix to the key name."""

        return '{0}_{1}'.format(prefix, name)

    if hasattr(settings, key('URI')):
        parsed = uri_parser.parse_uri(getattr(settings, key('URI')))
        if not parsed.get('database'):
            message = '{0} does not contain a database name.'
            message = message.format(key('URI'))
            raise ValueError(message)

        host = getattr(settings, key('URI'))
        name = parsed['database']

        username = parsed['username']
        password = parsed['password']

        replica_set = parsed['options'].get('replicaset', None)
    else:
        name = getattr(settings, key('DBNAME'), None)
        if not name:
            message = '{0} does not contain a database name.'
            message = message.format(key('DBNAME'))
            raise ValueError(message)

        host = getattr(settings, key('HOST'), 'localhost')
        port = getattr(settings, key('PORT'), 27017)

        username = getattr(settings, key('USERNAME'), None)
        password = getattr(settings, key('PASSWORD'), None)

        replica_set = getattr(settings, key('REPLICA_SET'), None)

        host = '{0}:{1}'.format(host, port)

    connection.connect(host, name=name, alias=alias, username=username,
                       password=password, replicaSet=replica_set)


def get_list_or_404(model, *qs, **fields):
    """Finds and returns a single document, or raises a 404 exception.

    This method will find documents within the specified model. If the
    specified query matches no documents, a ``404 Not Found`` exception
    will be raised.

    :param model: the model class.
    :type model: :class:`simon.Model`
    :param \*qs: logical queries.
    :type \*qs: :class:`simon.query.Q`
    :param \*\*fields: keyword arguments specifying the query.
    :type \*\*fields: kwargs
    :returns: :class:`~simon.query.QuerySet` -- a query set of model
              instances.

    .. versionadded: 0.1.0
    """

    result = model.find(*qs, **fields)
    if not result:
        raise Http404
    return result


def get_object_or_404(model, *qs, **fields):
    """Finds and returns a single document, or raises a 404 exception.

    This method will find a single document within the specified
    model. If the specified query matches zero or multiple documents,
    a ``404 Not Found`` exception will be raised.

    :param model: the model class.
    :type model: :class:`simon.Model`
    :param \*qs: logical queries.
    :type \*qs: :class:`simon.query.Q`
    :param \*\*fields: keyword arguments specifying the query.
    :type \*\*fields: kwargs
    :returns: :class:`~simon.Model` -- an instance of a model.

    .. versionadded: 0.1.0
    """

    try:
        return model.get(*qs, **fields)
    except (model.NoDocumentFound, model.MultipleDocumentsFound):
        raise Http404
