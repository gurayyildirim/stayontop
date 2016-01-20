#!/bin/env python

import boto.ec2
import time
import yaml
import sys
import getopt
import colorama

__author__ = 'ygurasl'


"""
.boto file must be filled as a prerequisite

$ cat $HOME/.boto
[Credentials]
aws_access_key_id = <accesskey>
aws_secret_access_key = <secret key>

[profile fms]
aws_access_key_id = <accesskey>
aws_secret_access_key = <secret key>

"""

class Weekdays:
    monday = 0
    tuesday = 1
    wednesday = 2
    thursday = 3
    friday = 4
    saturday = 5
    sunday = 6


class Config:
    """
      Merges today and global keep_running and keep_stopped instances
      today weekend_on config overrides global
    """
    def __init__(self, configfile, only_global=False):

        lt = time.localtime()
        today = "{0}.{1}.{2}".format(lt.tm_mday, lt.tm_mon, lt.tm_year)

        try:
            with open(configfile) as f:
                config_all = yaml.load(f)
        except IOError:
            config_all = yaml.load(configfile)
            if not isinstance(config_all, dict) or config_all == configfile:
                print("config file {file} can't be found or parsed".format(file=configfile))
                raise Exception
        config = config_all['global'].copy()
        if today in config_all.keys() and not only_global:
            today_config = config_all[today]
            config.update(today_config)
            # merge today and global keep_running and keep_stopped configs
            config['keep_running']['instances'] += config_all['global']['keep_running']['instances'] if 'keep_running' in config_all['global'].keys() else []
            config['keep_stopped']['instances'] += config_all['global']['keep_stopped']['instances'] if 'keep_stopped' in config_all['global'].keys() else []

        config['keep_running'] = config['keep_running']['instances'] if 'keep_running' in config.keys() else []
        config['keep_stopped'] = config['keep_stopped']['instances'] if 'keep_stopped' in config.keys() else []
        config['is_holiday'] = config['is_holiday'] if 'is_holiday' in config.keys() else False
        config['weekend_on'] = config['weekend_on']['projects'] if 'weekend_on' in config.keys() else []
        config['restricted'] = config['restricted']['projects'] if 'restricted' in config.keys() else []

        self.config = config

    def __repr__(self):
        return "Parsed config: " + str(self.config)

    def get(self, key):
        return self.config[key] if key in self.config.keys() else None

    def set(self, key, value):
        self.config[key] = value


def is_weekend():
    weekend = [Weekdays.saturday, Weekdays.sunday]
    lt = time.localtime()
    day = lt.tm_wday

    return day in weekend


def is_working_hours(ignore_weekend=False):
    lt = time.localtime()
    hour = lt.tm_hour

    is_holiday = config.get('is_holiday')
    if (is_weekend() and not ignore_weekend) or is_holiday:
        return False
    return 7 <= hour < 19


def friendly_print(instance_name, instance_state, instance_next_state, enable_color=True):
    pcolor = ""
    if instance_next_state == 'running' and instance_state == 'stopped':
        pcolor = colorama.Back.GREEN
    elif instance_next_state == 'stopped' and instance_state == 'running':
        pcolor = colorama.Back.RED

    message = "\t{0}: {1} -> {2}".format(instance_name, instance_state, instance_next_state)
    if enable_color:
        message = pcolor + message + colorama.Style.RESET_ALL
    print(message)


def will_instance_run(instance_tags):

    """
    input: instance_tags (as in aws tags)
    output:  instance state running or stopped

    Get a config file showing global and date specific configs
    According to configs return next state for the instance
    Will it be running or stopped?

    return value: true if "running", false if "stopped"

    """

    instance_name = instance_tags['Name']
    instance_project = instance_tags['project'] if 'project' in instance_tags else None
    project_on_weekend = instance_project in config.get('weekend_on')

    if instance_project not in config.get('restricted'):
        return None
    if instance_name in config.get('keep_stopped'):
        return 'stopped'
    elif instance_name in config.get('keep_running'):
        return 'running'
    elif is_working_hours(ignore_weekend=project_on_weekend):
        return 'running'
    
    return 'stopped'


def stayontop_main():
    aws_boto_profile = config.get('aws_boto_profile')
    conn = boto.ec2.connect_to_region("eu-west-1", profile_name=aws_boto_profile)
    reservations = conn.get_all_reservations()

    for res in reservations:
        for instance in res.instances:
                project = instance.tags['project'] if 'project' in instance.tags else None
                restricted_projects = config.get('restricted')
                environment = instance.tags['Environment'] if 'Environment' in instance.tags.keys() else ''
                name = instance.tags['Name']

                if project in restricted_projects:
                    next_state = will_instance_run(instance.tags)
                    friendly_print(name, instance.state, next_state, enable_color=color)
                    if instance.state == 'running' and next_state == 'stopped':
                        if not dryrun:
                            print("....Stopping....")
                            instance.stop()
                    elif instance.state == 'stopped' and next_state == 'running':
                        if not dryrun:
                            print("....Starting....")
                            instance.start()


def command_line_main():
    global config
    global color
    global dryrun
    try:
        optlist, args = getopt.getopt(sys.argv[1:], '', ['dryrun', 'color='])
        configfile = args[0]
        dryrun = False
        color = True
        for lp in optlist:
            key, value = lp
            if key == '--dryrun':
                dryrun = True
            elif key == '--color' and value == 'no':
                color = False
    except getopt.GetoptError:
        print("Usage: stayontop.py [--dryrun] [--color=no] project.yml")
        sys.exit(-1)
    config = Config(configfile)
    print(config)
    stayontop_main()
    if dryrun: print("Nothing is changed(dryrun mode)")

if __name__ == "__main__":
   command_line_main()
