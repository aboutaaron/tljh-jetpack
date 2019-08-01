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

logger = logging.getLogger("tljh")

@hookimpl
def tljh_extra_user_conda_packages():
  logger.info('[JETPACK] Installing R and essentials via conda-forge...')
  return [
    'r-base',
    'r-essentials',
    'r-irkernel',
    'voila',
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
  Add postgres support
  """
  # logger.info('[JETPACK] Installing postgresql bindings for ubuntu...')
  # return [
  #   'libpg-dev'
  # ]
  pass


def install_additional_jupyterlab_extensions():
    """
    Install the JupyterLab extensions we want.
    """
    logger.info('[JETPACK] Installing additional jupyterlab extensions...')
    extensions = [
        '@jupyterlab/hub-extension',
        '@jupyterlab/git',
        '@jupyterlab/google-drive',
        '@jupyterlab/shortcutui',
        'dask-labextension',
        '@jupyter-voila/jupyterlab-preview',
        '@jupyterlab/commenting-extension'
        '@jupyter-widgets/jupyterlab-manager'
    ]
    utils.run_subprocess([
        os.path.join(USER_ENV_PREFIX, 'bin/jupyter'),
        'labextension',
        'install'
    ] + extensions)


def enable_R_kernel():
  """
  TODO: Enable R kernel in jupyter programmatically
  """
  logger.info('[JETPACK] Enabling R kernel in jupyter...')
  pass


def enable_shared_directory():
  """
  Enable shared directory between users
  See: https://github.com/kafonek/tljh-shared-directory

  Configure /srv/scratch and change configs/mods
  """
  logger.info('[JETPACK] Adding shared-directory plugin...')
  ### mkdir -p /srv/scratch
  ### sudo chown  root:jupyterhub-users /srv/scratch
  ### sudo chmod 777 /srv/scratch
  ### sudo chmod g+s /srv/scratch
  ### sudo ln -s /srv/scratch /etc/skel/scratch
  sh.mkdir('/srv/scratch', '-p')
  # jupyterhub-users doesn't get created until a user logs in
  # make sure it's created before changing permissions on directory
  ensure_group('jupyterhub-users')
  sh.chown('root:jupyterhub-users', '/srv/scratch')
  sh.chmod('777', '/srv/scratch')
  sh.chmod('g+s', '/srv/scratch')
  sh.ln('-s', '/srv/scratch', '/etc/skel/scratch')

@hookimpl
def tljh_config_post_install(config):
  enable_shared_directory()
  install_additional_jupyterlab_extensions()
