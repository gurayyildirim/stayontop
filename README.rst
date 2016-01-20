stayontop
===========================================

Development instances on AWS EC2 need to be shutdown off-hours.

This small project tries to address this need providing a clear config file in yaml.

  - You can specify which instances must be stopped/running all the time.
  - By default all instances are set to be stopped off-hours
  - You can set all instances with a specific project tag to be open
  - Assumes office hours are between 07:00 - 19:00
  - Assumes EC2 instance tags: "project"
  - Assumes EC2 instance name matches  instance tag "Name"

A sample config file:

::

        global:
           restricted:
              projects:
                    - BI
                    - CRM
                    - PUSHAPP
           keep_running:
              instances:
                    - sybase.acme.com
                    - hana01.acme.com
           keep_stopped:
              instances:
                    - sybase.acme.com
                    - hanadyn.acme.com
                    - apush.acme.com
           weekend_on:
              projects:
                    - BI
           aws_boto_profile: SYS

Use case #1: Please keep FMS project stopped at weekends
   - Do not put it on weekend_on anywhere in the config
   - By default all projects are stopped unless stated otherwise
   - With the following config SAP project instances will be running during weekends

::

   global:
      weekend_on:
         projects:
              - SAP


Use case #2:  I want webdev01 instance to be running this night
::

   date_of_today:
      keep_running:
          instances:
             - webdev01


Use case #3:  Please keep webdev01 instance stopped on off-hours
    - Unless stated otherwise all instances are stopped on off-hours


Use case #4: Please keep dbdev01 instance stopped on working hours
::

    global:
        keep_stopped:
             instances:
                 - dbdev01


Use case #5:  Please keep dbdev01 instance stopped on 29.12.2015
   - Add the following to the config
   - Remove from the global config if necessary

::

     29.12.2015:
         keep_stopped:
              instances:
                  - dbdev01


Running
-----------------------

::

        $ git clone stayontop.git
        $ cd stayontop
        $ python setup.py install
      
        $ sudo -u jenkins /usr/bin/stayontop --dryrun project.yml
        Parsed config: {'restricted': ['sky'], 'weekend_on': [], 'keep_running': [], 'keep_stopped':[], 'is_holiday': False, 'aws_boto_profile': 'ecom'}``
                prj-front: running -> stopped
                prj-staged: running -> stopped
                prj-test: running -> stopped
        Nothing is changed(dryrun mode)

        $ sudo -u jenkins /usr/bin/stayontop project.yml
        Parsed config: {'restricted': ['sky'], 'weekend_on': [], 'keep_running': [], 'keep_stopped': [], 'is_holiday': False, 'aws_boto_profile': 'ecom'}
                prj-front: running -> stopped
                ....Stopping....
                prj-staged: running -> stopped
                ....Stopping....
                prj-test: running -> stopped
                ....Stopping....

        $ sudo -u jenkins /usr/bin/stayontop project.yml
        Parsed config: {'restricted': ['sky'], 'weekend_on': [], 'keep_running': [], 'keep_stopped':   [], 'is_holiday': False, 'aws_boto_profile': 'ecom'}
                prj-front: stopped -> stopped
                prj-staged: stopped -> stopped
                prj-test: stopped -> stopped

