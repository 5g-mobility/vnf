#!/usr/bin/env python3
# Copyright 2020 David Garcia
# See LICENSE file for licensing details.
#
# Further developed by Orlando Macedo 2021
# email: orlando.macedo15@ua.pt

import sys
import subprocess

sys.path.append("lib")

from ops.main import main
from ops.charm import CharmBase

from ops.model import (
    ActiveStatus,
    MaintenanceStatus,
    BlockedStatus,
    WaitingStatus,
    ModelError,
)

class NativeCharm(CharmBase):
    def __init__(self, framework, key):
        super().__init__(framework, key)

        # Register all of the events we want to observe
        # Charm events
        self.framework.observe(self.on.config_changed, self.on_config_changed)
        self.framework.observe(self.on.install, self.on_install)
        self.framework.observe(self.on.start, self.on_start)
        # Charm actions (primitives)
        self.framework.observe(self.on.touch_action, self.on_touch_action)

        # Personalized actions ip-static-vm
        self.framework.observe(self.on.update_time_action, self.on_update_time_action)
        self.framework.observe(self.on.run_app_action, self.on_run_app_action)

        # specific vars
        self.github_dir = "~/github-code/"

    def on_config_changed(self, event):
        """Handle changes in configuration"""
        self.model.unit.status = ActiveStatus()

    def on_install(self, event):
        self.model.unit.status = ActiveStatus()

    def on_start(self, event):
        """Called when the charm is being installed"""
        self.model.unit.status = ActiveStatus()

    def on_touch_action(self, event):
        """Touch a file."""

        filename = event.params["filename"]

        try:
            subprocess.run(["touch", filename], check=True)
            event.set_results({"created": True, "filename": filename})
        except subprocess.CalledProcessError as e:
            event.fail("Action failed: {}".format(e))

        self.model.unit.status = ActiveStatus()

    ########################
    # Personalized methods #
    ########################

    def on_update_time_action(self, event):
        """ Synchronize the time of the VM with the time o ntp UA server """
        try:
            self.unit.status = MaintenanceStatus("Synchronizing")

            subprocess.run("while ! ping -c 1 -W 1 0.0.0.0; do echo \"waiting\"; sleep 1; done", shell=True, check=True)

            subprocess.run(["sudo", "apt", "install", "-y", "ntp"], check=True)
            subprocess.run(["sudo", "service", "ntp", "stop"], check=True)
            subprocess.run(["sudo", "rm", "/etc/ntp.conf"], check=True)
            
            subprocess.run(["sudo", "cp", "{}cv_app/ntp.conf".format(self.github_dir), "/etc/"], check=True)

            subprocess.run(["sudo", "timedatectl", "set-timezone", "Europe/Lisbon"], check=True)
            subprocess.run(["sudo", "timedatectl", "set-ntp", "true"], check=True)
            subprocess.run(["sudo", "service", "ntp", "restart"], check=True)

        except subprocess.CalledProcessError as e:
            event.fail("Action failed: {}".format(e))
        
        self.unit.status = ActiveStatus("Time was synchronized")

    def on_run_app_action(self, event):
        """ Build and run application on the VM associated with the VNF service """
        try:
            app_name = event.params["app-name"]
            
            self.unit.status = MaintenanceStatus("Building and running application {}".format(app_name))

            subprocess.run(["sudo", "chown", "root:ubuntu", "/var/run/docker.sock"], check=True)
            subprocess.run(["sudo", "chown", "-R", "root:ubuntu", "/var/run/docker"], check=True)
            
            subprocess.run(["sudo", "service", "ntp", "restart"], check=True)
            
            subprocess.run(["export", "RABBITMQ_IP=$(python3 {}cv_app/ip_static_vm.py)".format(self.github_dir),
                    "&&", "docker-compose", "-f", "{}{}/docker-compose.yml up -d".format(self.github_dir, app_name)], check=True)

            self.unit.status = ActiveStatus("{} running successfully".format(app_name))
        except subprocess.CalledProcessError as e:
            event.fail("Action failed: {}".format(e))

if __name__ == "__main__":
    main(NativeCharm)
