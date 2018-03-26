=====
Usage
=====

To use Django wallets in a project, add it to your `INSTALLED_APPS`:

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
