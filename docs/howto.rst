How To...
======================================================================

Build documentation
----------------------------------------------------------------------

Documentation can be written as rst files in `tat/docs`.


To build and serve docs, use the commands::
    
    docker-compose -f local.yml up docs



Changes to files in `docs/_source` will be picked up and reloaded automatically.

`Sphinx <https://www.sphinx-doc.org/>`_ is the tool used to build documentation.

Run a command in the container
----------------------------------------------------------------------
To run a command::
        
    docker-compose -f local.yml run --rm django

Examples::

    docker-compose -f local.yml run --rm django python manage.py migrate
    docker-compose -f local.yml run --rm django python manage.py createsuperuser

Get a Shell
----------------------------------------------------------------------
::
  
  docker-compose -f local.yml run --rm django python manage.py shell

Start a new app
----------------------------------------------------------------------
To start a new app:

#. Create the app with

   .. code-block:: bash

     docker-compose -f local.yml run --rm django

#. Move the app to tat/

   .. code-block:: bash

     mv new-app tat/new-app

#. edit tat/new-app/apps.py and change name

   .. code-block:: python

     name = "tat.new-app"

#. Add tat.new-app.apps.new-appConfig to LOCAL_APPS in config/settings/base.py

Do Database Migrations
----------------------------------------------------------------------
To view a migration for an app::

    docker-compose -f local.yml run --rm django python manage.py sqlmigrate <app name> <task number>

To create a migration:

#. Change models in models.py
#. Create migrations for changes
   
  .. code-block:: bash

    docker-compose -f local.yml run --rm django python manage.py makemigrations

#. Apply migrations

   .. code-block:: bash

     docker-compose -f local.yml run --rm django python manage.py migrate


Set up HTTPS locally
----------------------------------------------------------------------
Edit host to include::

    127.0.0.1 tat.local

Generate local certs::

    brew install mkcert
    mkcert --install
    mkcert tat.local
    mv tat.local-key.pem certs/tat.local.key
    mv tat.local.pem certs/tat.local.crt

Add nginx-proxy to local.yml::

    nginx-proxy:
      image: jwilder/nginx-proxy:alpine
      container_name: nginx-proxy
      ports:
        - "80:80"
        - "443:443"
      volumes:
        - /var/run/docker.sock:/tmp/docker.sock:ro
        - ./certs:/etc/nginx/certs
      restart: always
      depends_on:
        - django

Add new environment variables to local django environment ./.envs/.local/.django:: 

    # HTTPS
    # ------------------------------------------------------------------------------
    VIRTUAL_HOST=tat.local
    VIRTUAL_PORT=8000

Add new host name to config/settings/local.py::

    ALLOWED_HOSTS = ["localhost", "0.0.0.0", "127.0.0.1", "tat.local"]

Add certs to .gitignore::

    certs/*


Docstrings to Documentation
----------------------------------------------------------------------

The sphinx extension `apidoc <https://www.sphinx-doc.org/en/master/man/sphinx-apidoc.html/>`_ is used to automatically document code using signatures and docstrings.

Numpy or Google style docstrings will be picked up from project files and availble for documentation. See the `Napoleon <https://sphinxcontrib-napoleon.readthedocs.io/en/latest/>`_ extension for details.

For an in-use example, see the `page source <_sources/users.rst.txt>`_ for :ref:`users`.

To compile all docstrings automatically into documentation source files, use the command:
    ::
    
        make apidocs


This can be done in the docker container:
    :: 
        
        docker run --rm docs make apidocs

Create a Form
----------------------------------------------------------------------
Load the bulma_tags library and use the bulma filters::

  {% load bulma_tags %}

  {# Display a form #}

  <form action="/url/to/submit/" method="post">
     {% csrf_token %}
     {{ form|bulma }}
     <div class="field">
       <button type="submit" class="button is-primary">Login</button>
     </div>
     <input type="hidden" name="next" value="{{ next }}"/>
  </form>
