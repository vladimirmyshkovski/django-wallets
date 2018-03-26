=============================
Django wallets
=============================

.. image:: https://badge.fury.io/py/django-wallets.svg
    :target: https://badge.fury.io/py/django-wallets

.. image:: https://travis-ci.org/narnikgamarnikus/django-wallets.svg?branch=master
    :target: https://travis-ci.org/narnikgamarnikus/django-wallets

.. image:: https://codecov.io/gh/narnikgamarnikus/django-wallets/branch/master/graph/badge.svg
    :target: https://codecov.io/gh/narnikgamarnikus/django-wallets

BTC, LTC, DASH, DOGE wallets for each user with withdraw with webhook

Documentation
-------------

The full documentation is at https://django-wallets.readthedocs.io.

Quickstart
----------

Install Django wallets::

    pip install django-wallets

Add it to your `INSTALLED_APPS`:

.. code-block:: python

    INSTALLED_APPS = (
        ...
        'wallets.apps.WalletsConfig',
        ...
    )

Add Django wallets's URL patterns:

.. code-block:: python

    from wallets import urls as wallets_urls


    urlpatterns = [
        ...
        url(r'^', include(wallets_urls)),
        ...
    ]

Features
--------

* TODO

Running Tests
-------------

Does the code actually work?

::

    source <YOURVIRTUALENV>/bin/activate
    (myenv) $ pip install tox
    (myenv) $ tox

Credits
-------

Tools used in rendering this package:

*  Cookiecutter_
*  `cookiecutter-djangopackage`_

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`cookiecutter-djangopackage`: https://github.com/pydanny/cookiecutter-djangopackage
