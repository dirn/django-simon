django-simon
============

Simon_ is a library to help make working with MongoDB easier.
django-imon was created to make it even easier to use Simon_ with your
Django applications.

.. _Simon: http://simon.readthedocs.org/


Installation
------------

To install the latest stable version of django-simon::

    $ pip install django-simon

or, if you must::

    $ easy_install django-simon

To install the latest development version::

    $ git clone git@github.com:dirn/django-simon.git
    $ cd django-simon
    $ python setup.py install

In addition to django-simon, this will also install:

- Django (1.2 or later)
- PyMongo (2.1 or later)
- Simon


Quickstart
----------

After installing django-simon, import it somewhere in your Django
project, like in your ``models.py`` file.

.. code-block:: python

    from django_simon import simonize()

    simonize()

:meth:`~django_simon.simonize` will establish a connection to the
database that will be used as the default database for any
:class:`~simon.Model` classes that you define.


Configuration
-------------

:meth:`~django_simon.simonize` looks for the following in your Django
project's settings:

===================== ==================================================
``MONGO_URI``         A `MongoDB URI`_ connection string specifying the
                      database connection.
``MONGO_HOST``        The hostname or IP address of the MongoDB server.
                      default: 'localhost'
``MONGO_PORT``        The port of the MongoDB server. default: 27017
``MONGO_DNAME``       The name of the database on ``MONGO_HOST``.
                      Default: ``app.name``
``MONGO_USERNAME``    The username for authentication.
``MONGO_PASSWORD``    The password for authentication.
``MONGO_REPLICA_SET`` The name of the replica set.
===================== ==================================================

.. _MongoDB URI: http://docs.mongodb.org/manual/reference/connection-string/

The ``MONGO_URI`` setting will be used before checking any other
settings. If it's not present, the others will be used.

By default, :meth:`~django_simon.simonize` will use ``MONGO`` as the
prefix for all settings. This can be overridden by using the ``prefix``
argument.

Specifying a value for ``prefix`` will allow for the use of multiple
databases.

.. code-block:: python

    # settings.py

    MONGO_URI = 'mongodb://localhost/mongo'
    SIMON_URI = 'mongodb://localhost/simon'

    # models.py

    simonize()
    simonize(prefix='SIMON')

This will allow for the use of the ``mongo`` and ``simon`` databases on
``localhost``. ``mongo`` will be available to models through the aliases
``default`` and ``mongo``. ``simon`` will be available through the alias
``simon``. This alias can be changed by using the ``alias`` argument.

.. code-block:: python

    simonize(prefix='SIMON', alias='other-database')


API
---

.. automodule:: django_simon
   :members:

Full details of how to query using :meth:`~django_simon.get_list_or_404`
and :meth:`~django_simon.get_object_or_404` can be found in the
:meth:`Simon API <simon.Model.get>`.


Further Reading
---------------

For more information, check out the `Simon docs`_ and the
`MongoDB docs`_.

.. _MongoDB docs: http://www.mongodb.org/display/DOCS/Home
.. _Simon docs: http://simon.readthedocs.org/
