#!/bin/sh
# Adapted from my script doing this over and over
# See: https://gist.github.com/aboutaaron/6933b9ba0d742167c61ca50cbee114d3#uninstalling-and-removing-the-littlest-jupyter-hub-from-a-server
echo "Attempting to uninstall TLJH from your environment..."
echo "[WARNING] This script will run the following commands using sudo:"
echo
echo "  Remove traefik.service from systemd"
echo "  Remove jupyterhub.service from systemd"
echo "  Remove associated files from /etc/systemd/system"
echo "  Remove code stored in /opt/tljh"
echo "  Remove symlink in /usr/bin/tljh-config"
echo
read -p "Are you sure you want to do this? Do you trust me? [Y/n]" response
echo

response=${response,,}
if [[ $response =~ ^(yes|y| ) ]] || [[ -z $response ]]; then
  echo "Attempting to remove TLJH from your server..."
  sudo systemctl disable traefik.service
  sudo systemctl stop traefik.service
  sudo rm /etc/systemd/system/traefik.service

  sudo systemctl disable jupyterhub.service
  sudo systemctl stop jupyterhub.service
  sudo rm /etc/systemd/system/jupyterhub.service

  sudo rm -rf /opt/tljh/
  sudo rm /usr/bin/tljh-config

  echo "For the final step, manually remove any user created by TLJH on your system. Here's a list of possible users:"
  cat /etc/passwd | grep jupyter
  echo
  echo "If you want to remove the users try userdel:"
  echo "  sudo userdel -r jupyter-USERNAME"
  exit 0
else
  echo "Leaving TLJH setup as is...exiting"
  exit 0
fi
