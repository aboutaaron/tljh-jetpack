# The Littlest Jupyterhub Jetpack :rocket:

Plugin to upgrade TLJH

## Quickstart

```bash
curl https://raw.githubusercontent.com/jupyterhub/the-littlest-jupyterhub/master/bootstrap/bootstrap.py \
 | sudo python3 - \
  --admin admin-USER \
  --plugin git+https://github.com/aboutaaron/tljh-jetpack
```


## Uninstall TLJH + Jetpack

Need a restart? tljh-jetpack includes a bash script that tries to remove everything for you.

**Warning**: THIS WILL TOTALLY REMOVE TLJH FROM YOUR SERVER. ONLY DO THIS IS YOU WANT TO RESET THE WORLD. YOU'VE BEEN WARNED!

```bash
curl https://raw.githubusercontent.com/aboutaaron/tljh-jetpack/master/uninstall_tljh.sh | bash
```
