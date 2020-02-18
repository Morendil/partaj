"""Django settings for partaj project.

Uses django-configurations to manage environments inheritance and the loading of some
config from the environment

"""

import json
import os

from django.utils.translation import gettext_lazy as _

from configurations import Configuration, values


BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def get_release():
    """
    Get the current release of the application.

    By release, we mean the release from the version.json file à la Mozilla [1]
    (if any). If this file has not been found, it defaults to "NA".
    [1]
    https://github.com/mozilla-services/Dockerflow/blob/master/docs/version_object.md
    """
    # Try to get the current release from the version.json file generated by the
    # CI during the Docker image build
    try:
        with open(os.path.join(BASE_DIR, "version.json")) as version:
            return json.load(version)["version"]
    except FileNotFoundError:
        return "NA"  # Default: not available


class Base(Configuration):
    """Base configuration every configuration (aka environment) should inherit from.

    It depends on an environment variable that SHOULD be defined:
    - DJANGO_SECRET_KEY

    You may also want to override default configuration by setting the following
    environment variables:
    - DJANGO_DEBUG
    """

    DATA_DIR = values.Value(os.path.join("/", "data"))

    # Static files (CSS, JavaScript, Images)
    STATICFILES_DIRS = (os.path.join(BASE_DIR, "static"),)
    STATIC_URL = "/static/"
    ABSOLUTE_STATIC_URL = STATIC_URL
    MEDIA_URL = "/media/"

    SECRET_KEY = values.SecretValue()

    DEBUG = values.BooleanValue(False)

    DATABASES = {
        "default": {
            "ENGINE": values.Value(
                "django.db.backends.postgresql_psycopg2",
                environ_name="DATABASE_ENGINE",
                environ_prefix=None,
            ),
            "NAME": values.Value(
                "partaj", environ_name="POSTGRES_DB", environ_prefix=None
            ),
            "USER": values.Value(
                "admin", environ_name="POSTGRES_USER", environ_prefix=None
            ),
            "PASSWORD": values.Value(
                "admin", environ_name="POSTGRES_PASSWORD", environ_prefix=None
            ),
            "HOST": values.Value(
                "db", environ_name="POSTGRES_HOST", environ_prefix=None
            ),
            "PORT": values.Value(
                5432, environ_name="POSTGRES_PORT", environ_prefix=None
            ),
        }
    }

    ALLOWED_HOSTS = []

    SITE_ID = 1

    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    X_FRAME_OPTIONS = "DENY"
    SILENCED_SYSTEM_CHECKS = values.ListValue([])

    # Application definition
    INSTALLED_APPS = [
        "partaj.core.apps.CoreConfig",
        "django.contrib.admin",
        "django.contrib.auth",
        "django.contrib.contenttypes",
        "django.contrib.sessions",
        "django.contrib.messages",
        "django.contrib.staticfiles",
        "django_extensions",
        "dockerflow.django",
    ]

    MIDDLEWARE = [
        "django.middleware.security.SecurityMiddleware",
        "django.contrib.sessions.middleware.SessionMiddleware",
        "django.middleware.common.CommonMiddleware",
        "django.middleware.csrf.CsrfViewMiddleware",
        "django.contrib.auth.middleware.AuthenticationMiddleware",
        "django.contrib.messages.middleware.MessageMiddleware",
        "django.middleware.clickjacking.XFrameOptionsMiddleware",
        "dockerflow.django.middleware.DockerflowMiddleware",
    ]

    ROOT_URLCONF = "partaj.urls"

    TEMPLATES = [
        {
            "BACKEND": "django.template.backends.django.DjangoTemplates",
            "DIRS": [],
            "APP_DIRS": True,
            "OPTIONS": {
                "context_processors": [
                    "django.template.context_processors.debug",
                    "django.template.context_processors.request",
                    "django.contrib.auth.context_processors.auth",
                    "django.contrib.messages.context_processors.messages",
                ]
            },
        }
    ]

    WSGI_APPLICATION = "partaj.wsgi.application"

    # Password validation
    # https://docs.djangoproject.com/en/2.0/ref/settings/#auth-password-validators
    AUTH_PASSWORD_VALIDATORS = [
        {
            "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"
        },
        {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
        {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
        {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
    ]

    # Internationalization
    # https://docs.djangoproject.com/en/2.0/topics/i18n/

    # Django sets `LANGUAGES` by default with all supported languages. Let's save it to a
    # different setting before overriding it with the languages active in Partaj. We can use it
    # for example for the choice of time text tracks languages which should not be limited to
    # the few languages active in Partaj.
    # pylint: disable=no-member
    ALL_LANGUAGES = Configuration.LANGUAGES

    LANGUAGE_CODE = "en-us"

    # Careful! Languages should be ordered by priority, as this tuple is used to get
    # fallback/default languages throughout the app.
    # Use "en" as default as it is the language that is most likely to be spoken by any visitor
    # when their preferred language, whatever it is, is unavailable
    LANGUAGES = [("en", _("english")), ("fr", _("french"))]
    LANGUAGES_DICT = dict(LANGUAGES)

    # Internationalization
    TIME_ZONE = "UTC"
    USE_I18N = True
    USE_L10N = True
    USE_TZ = True

    # Logging
    LOGGING = values.DictValue(
        {
            "version": 1,
            "disable_existing_loggers": False,
            "handlers": {
                "console": {
                    "class": "logging.StreamHandler",
                    "stream": "ext://sys.stdout",
                }
            },
            "loggers": {
                "partaj": {"handlers": ["console"], "level": "INFO", "propagate": True}
            },
        }
    )

    # pylint: disable=invalid-name
    @property
    def RELEASE(self):
        """
        Return the release information.

        Delegate to the module function to enable easier testing.
        """
        return get_release()

    # pylint: disable=invalid-name
    @property
    def ENVIRONMENT(self):
        """Environment in which the application is launched."""
        return self.__class__.__name__.lower()


class Development(Base):
    """Development environment settings.

    We set ``DEBUG`` to ``True`` by default, configure the server to respond to all hosts,
    and use a local sqlite database by default.
    """

    ALLOWED_HOSTS = ["*"]
    DEBUG = values.BooleanValue(True)
    CACHES = {"default": {"BACKEND": "django.core.cache.backends.dummy.DummyCache"}}

    LOGGING = values.DictValue(
        {
            "version": 1,
            "disable_existing_loggers": False,
            "handlers": {
                "console": {
                    "class": "logging.StreamHandler",
                    "stream": "ext://sys.stdout",
                }
            },
            "loggers": {
                "partaj": {"handlers": ["console"], "level": "DEBUG", "propagate": True}
            },
        }
    )


class Test(Base):
    """Test environment settings."""


class Production(Base):
    """Production environment settings.

    You must define the DJANGO_ALLOWED_HOSTS environment variable in Production
    configuration (and derived configurations):

    DJANGO_ALLOWED_HOSTS="foo.com,foo.fr"
    """

    # Postgresql config that maps to Clever-Cloud environment variablees
    DATABASES = {
        "default": {
            "ENGINE": values.Value(
                "django.db.backends.postgresql_psycopg2",
                environ_name="DATABASE_ENGINE",
                environ_prefix=None,
            ),
            "NAME": values.Value(
                "partaj", environ_name="POSTGRESQL_ADDON_DB", environ_prefix=None
            ),
            "USER": values.Value(
                "admin", environ_name="POSTGRESQL_ADDON_USER", environ_prefix=None
            ),
            "PASSWORD": values.Value(
                "admin", environ_name="POSTGRESQL_ADDON_PASSWORD", environ_prefix=None
            ),
            "HOST": values.Value(
                "db", environ_name="POSTGRESQL_ADDON_HOST", environ_prefix=None
            ),
            "PORT": values.Value(
                5432, environ_name="POSTGRESQL_ADDON_PORT", environ_prefix=None
            ),
        }
    }

    # Actual allowed hosts are specified directly through an environment variable
    ALLOWED_HOSTS = values.ListValue(None)

    # For static files in production, we want to use a backend that includes a hash in
    # the filename, that is calculated from the file content, so that browsers always
    # get the updated version of each file.
    STATICFILES_STORAGE = values.Value(
        "partaj.core.storage.ConfigurableManifestS3Boto3Storage"
    )

    # The mapping between the names of the original files and the names of the files distributed
    # by the backend is stored in a file.
    # The best practice is to allow this manifest file's name to change for each deployment so
    # that several versions of the app can run in parallel without interfering with each other.
    # We make it configurable so that it can be versioned with a deployment stamp in your CI/CD:
    STATICFILES_MANIFEST_NAME = values.Value("staticfiles.json")

    # pattern matching files to ignore when hashing file names and exclude from the
    # static files manifest
    STATIC_POSTPROCESS_IGNORE_REGEX = values.Value(r"^js\/[0-9]*\..*\.index\.js$")

    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
