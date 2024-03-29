"""
Let's upgrade TLJH
"""
import os
import json
import logging
import subprocess

import sh
from tljh import utils
from tljh.hooks import hookimpl
from tljh.user import ensure_group
from tljh.conda import fix_permissions

from tljh.config import (
    USER_ENV_PREFIX
)


"""
Adding a custom logging class so I know when jetpack is running
See: https://stackoverflow.com/a/56944256/868724
"""


class CustomFormatter(logging.Formatter):
    """Logging Formatter to add colors and count warning / errors"""

    grey = "\x1b[38;21m"
    blue = '\033[94m'
    yellow = "\x1b[33;21m"
    red = "\x1b[31;21m"
    bold_red = "\x1b[31;1m"
    reset = "\x1b[0m"
    format = "[%(name)s] %(message)s (%(filename)s:%(lineno)d)"

    FORMATS = {
        logging.DEBUG: grey + format + reset,
        logging.INFO: blue + format + reset,
        logging.WARNING: yellow + format + reset,
        logging.ERROR: red + format + reset,
        logging.CRITICAL: bold_red + format + reset
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)


logger = logging.getLogger("tljh-jetpack")
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setFormatter(CustomFormatter())
logger.addHandler(ch)


@hookimpl
def tljh_extra_user_conda_packages():
    logger.info('Installing R and essentials via conda-forge...')
    return [
        'r-base',
        'r-essentials',
        'r-irkernel'
    ]


@hookimpl
def tljh_extra_user_pip_packages():
    logger.info('Installing data science libraries...')
    return [
        'dask[complete]',
        'scikit-learn',
        'fastparquet',
        'python-snappy',
        'pyarrow',
        'psycopg2',
        'beautifulsoup4',
        'jupyterlab==1.0.4'
    ]


@hookimpl
def tljh_extra_apt_packages():
    """
    Install additional apt packages
    """
    logger.info('Installing postgresql bindings for ubuntu...')
    return [
        'postgresql-10',
        'postgresql-10-postgis-2.4',
        'postgresql-10-postgis-scripts',
    ]


def _give_group_access(path, group='jupyterhub-admins', recursive=False):
    """
    Give group access to path. Defaults to `jupyterhub-admins` and 777
    """
    # Cribbed from https://github.com/kafonek/tljh-shared-directory/blob/master/tljh_shared_directory.py
    ensure_group(group)

    if recursive:
        sh.chown(f'root:{group}', '-R', path)
        sh.chmod('g+w', '-R', path) # https://superuser.com/a/695186/234265
    else:
        sh.chown(f'root:{group}', path)
        sh.chmod('g+w', path)


def _install_additional_jupyterlab_extensions():
    """
    Install the JupyterLab extensions we want.
    """
    # in order to add/remove extensions we'll want to make sure all admin users
    # have permissions to the directory stored in /opt/tljh/user/share/jupyter/lab/extensions
    logger.info('Changing extensions ownership...')
    jupyter_shared_path = os.path.join(
        USER_ENV_PREFIX, 'share', 'jupyter')
    _give_group_access(jupyter_shared_path, recursive=True)

    logger.info('Installing additional jupyterlab extensions...')

    extensions = [
        '@jupyterlab/git',
        'dask-labextension',
        '@jupyter-widgets/jupyterlab-manager'
    ]
    utils.run_subprocess([
        os.path.join(USER_ENV_PREFIX, 'bin/jupyter'),
        'labextension',
        'install'
    ] + extensions)

    # the dask extension will throw an error if a cluster is running
    # so to prevent confusion we'll disable it starting out
    utils.run_subprocess([
        os.path.join(USER_ENV_PREFIX, 'bin/jupyter'),
        'labextension',
        'disable',
        'dask-labextension'
    ])

    for directory in ['settings', 'extensions', 'staging', 'schemas']:
        _give_group_access(os.path.join(jupyter_shared_path, 'lab', directory, '.'), recursive=True)

    # extensions also modify a settings file so we'll need to add access there, too
    _give_group_access(os.path.join(jupyter_shared_path, 'lab', '.'), recursive=True)
    _give_group_access(os.path.join(jupyter_shared_path, 'lab', 'settings', 'page_config.json'))
    _give_group_access(os.path.join(jupyter_shared_path, 'lab', 'staging', 'build', '.'), recursive=True)
    _give_group_access(os.path.join(jupyter_shared_path, 'lab', 'schemas', '@jupyterlab', '.'), recursive=True)
    _give_group_access(os.path.join(jupyter_shared_path, 'lab', 'schemas', 'dask-labextension', '.'), recursive=True)
    _give_group_access(os.path.join(jupyter_shared_path, 'lab', 'schemas', '@jupyter-widgets', '.'), recursive=True)


@hookimpl
def tljh_config_post_install(config):
    config['default_app'] = 'jupyterlab'  # I don't think this works


@hookimpl
def tljh_custom_jupyterhub_config(c):
    """
    Make sure Jupyterlab has JupyterHub management console
    """
    logger.info('Add JupyterHub to Jupyterlab environment')
    c.Spawner.cmd = ['jupyter-labhub']


@hookimpl
def tljh_post_install():
    """
    What to run post install
    """
    _install_additional_jupyterlab_extensions()
