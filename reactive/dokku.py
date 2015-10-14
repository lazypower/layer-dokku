#!/usr/bin/env python

from shlex import split
from subprocess import check_call

from charms.reactive import set_state
from charms.reactive import when
from charms.reactive import when_not

from charmhelpers.core.hookenv import open_port
from charmhelpers.core.hookenv import config
from charmhelpers.core import hookenv


@when('docker.available')
@when_not('dokku.available')
def install_dokku():
    hookenv.status_set('maintenance', 'Installing Dokku')
    cmd = ['scripts/dokku.sh']
    configure_dokku()
    check_call(cmd)
    open_ports()
    set_state('dokku.available')
    hookenv.status_set('active', 'Dokku Installed')


def open_ports():
    open_port(80)
    open_port(443)
    open_port(22)


def configure_dokku():
    cfg = config()
    vhost = cfg.get('vhost_enable')
    hostname = cfg.get('hostname')
    key_file = cfg.get('key_file')

    if vhost:
        debconf_function("dokku dokku/vhost_enable boolean {}".format(vhost))

    if hostname:
        debconf_function("dokku dokku/hostname string {}".format(hostname))

    if key_file:
        with open('dokku_key.pub') as f:
            f.write(key_file)
        debconf_function('dokku dokku/key_file string {}/dokku_key.pub'.format(CHARM_DIR))  # noqa


def debconf_function(arg):
    cmd = "echo '{}' | debconf-set-selections".format(arg)
    check_call(split(cmd))
