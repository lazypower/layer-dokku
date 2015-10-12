#!/bin/bash

source `which charms.reactive.sh`

@when 'docker.available'
@when_not 'dokku.available'
function install_dokku() {
  # We waited for docker to install so we dont race with it.
  # Dokku will also upgrade if the shipping version of docker is incompat
  status-set maintenance 'installing dokku'
  configure_dokku
  DOKKU_TAG=v0.4.1 scripts/dokku.sh
  open-port 80
  open-port 443
  charms.reactive.set-state 'dokku.available'
}

function configure_dokku(){
    # Setup the configuration for Dokku via debconf prior to installation
    VHOST=$(config-get vhost_enable)
    HOSTNM=$(config-get hostname)
    KEY_FILE=$(config-get key_file)

    if [ ! -z "${VHOST}" ]; then
        echo "dokku dokku/vhost_enable boolean $VHOST" | debconf-set-selections
    fi
    if [ ! -z "${HOSTNM}" ]; then
        echo "dokku dokku/hostname string $HOSTNM" | debconf-set-selections
    fi
    if [ ! -z "${KEY_FILE}" ]; then
        echo "$KEY_FILE" >> $CHARM_DIR/dokku_key.pub
        echo "dokku dokku/key_file string $CHARM_DIR/dokku_key.pub" | debconf-set-selections
    fi

}

reactive_handler_main
