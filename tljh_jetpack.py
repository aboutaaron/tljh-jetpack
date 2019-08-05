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
    format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s (%(filename)s:%(lineno)d)"

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
  logger.info('[JETPACK] Installing R and essentials via conda-forge...')
  return [
    'r-base',
    'r-essentials',
    'r-irkernel'
  ]


@hookimpl
def tljh_extra_user_pip_packages():
  logger.info('[JETPACK] Installing data science libraries...')
  return [
    'dask[complete]',
    'scikit-learn',
    # 'psycopg2',
    'beautifulsoup4',
    'jupyterlab==1.0.4'
  ]


@hookimpl
def tljh_extra_apt_packages():
  """
  CURRENTLY NOT IN USE

  Add postgres support
  """
  # logger.info('[JETPACK] Installing postgresql bindings for ubuntu...')
  # return [
  #   'libpg-dev'
  # ]
  pass


def _install_additional_jupyterlab_extensions():
    """
    Install the JupyterLab extensions we want.
    """
    logger.info('[JETPACK] Installing additional jupyterlab extensions...')
    extensions = [
        '@jupyterlab/git',
        'dask-labextension',
        '@jupyterlab/hub-extension',
        '@jupyter-widgets/jupyterlab-manager'
    ]
    utils.run_subprocess([
        os.path.join(USER_ENV_PREFIX, 'bin/jupyter'),
        'labextension',
        'install'
    ] + extensions)


@hookimpl
def tljh_config_post_install(config):
  config['default_app'] = 'jupyterlab'  # I don't think this works


@hookimpl
def tljh_custom_jupyterhub_config(c):
  """
  Make sure Jupyterlab has JupyterHub management console
  """
  logger.info('[JETPACK] Add JupyterHub to Jupyterlab environment')
  c.Spawner.cmd = ['jupyter-labhub']
  print(c)


@hookimpl
def tljh_post_install():
  """
  What to run post install
  """
  _install_additional_jupyterlab_extensions()
