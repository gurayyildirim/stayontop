import unittest
import time
from stayontop import stayontop


__author__ = 'ygurasl'


test_global_yml = """
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
"""

test_current_date_yml = """
{current_date}:
   weekend_on:
       projects:
           - PUSHAPP
   keep_running:
       instances:
           - sapdsips01.acme.com
   keep_stopped:
       instances:
           - saprs01.acme.com
"""

class test_stayontop(unittest.TestCase):

    def setUp(self):
        lt = time.localtime()
        today = "{0}.{1}.{2}".format(lt.tm_mday, lt.tm_mon, lt.tm_year)
        self.test_yml = test_global_yml + test_current_date_yml.format(current_date=today)
        self.config = stayontop.Config(self.test_yml)
        # print(self.config.config)
        stayontop.config = self.config
        self.day = lt.tm_wday
        self.hour = lt.tm_hour

    def test_config_global(self):
        gconfig = stayontop.Config(test_global_yml, only_global=True)
        self.assertEqual(['BI', 'CRM', 'PUSHAPP'], gconfig.get('restricted'))
        self.assertEqual(['sybase.acme.com', 'hana01.acme.com'], gconfig.get('keep_running'))
        self.assertEqual(['sybase.acme.com', 'hanadyn.acme.com', 'apush.acme.com'], gconfig.get('keep_stopped'))
        self.assertEqual(['BI'], gconfig.get('weekend_on'))
        self.assertEqual('SYS', stayontop.config.get('aws_boto_profile'))

    def test_config_agregate(self):
        self.assertEqual('SYS', stayontop.config.get('aws_boto_profile'))
        self.assertEqual(['BI', 'CRM', 'PUSHAPP'], stayontop.config.get('restricted'))
        self.assertEqual(['PUSHAPP'], stayontop.config.get('weekend_on'))
        self.assertEqual(['sapdsips01.acme.com', 'sybase.acme.com', 'hana01.acme.com'],
                         stayontop.config.get('keep_running'))
        self.assertEqual(['saprs01.acme.com', 'sybase.acme.com', 'hanadyn.acme.com', 'apush.acme.com'],
                         stayontop.config.get('keep_stopped'))
        self.assertEqual(False, stayontop.config.get('is_holiday'))

    def test_is_weekend(self):
        self.assertEqual(stayontop.is_weekend(), self.day in (5, 6))

    def test_is_working_hours(self):
        working_hours = 7 <= self.hour < 19
        weekend = self.day in (5, 6)
        # test is_holiday flag
        stayontop.config.set('is_holiday', False)
        self.assertEqual(stayontop.is_working_hours(ignore_weekend=True), working_hours)
        stayontop.config.set('is_holiday', True)
        self.assertEqual(stayontop.is_working_hours(ignore_weekend=True), False)
        stayontop.config.set('is_holiday', False)
        self.assertEqual(stayontop.is_working_hours(), not weekend and working_hours)

    def test_will_instance_run(self):
        # no project tag
        instance_tags = eval("""{u'Name': u'veripark-poc-mgmt', u'poc': u'yes'}""")
        self.assertEqual(None, stayontop.will_instance_run(instance_tags))
        # not in restricted projects
        instance_tags = eval("""{u'project': u'SAP', u'role': u'platformservices', u'Name': u'sapdsips.acme.com'}""")
        self.assertEqual(None, stayontop.will_instance_run(instance_tags))
        # in restricted projects but not in keep_running
        instance_tags = eval("""{u'project': u'CRM', u'Name': u'web.acme.com'}""")
        next_state = 'running' if stayontop.is_working_hours() else 'stopped'
        self.assertEqual(next_state, stayontop.will_instance_run(instance_tags))
        # in restricted projects and in keep_running
        instance_tags = eval("""{u'project': u'CRM', u'Name': u'hana01.acme.com'}""")
        self.assertEqual('running', stayontop.will_instance_run(instance_tags))
        # in restricted projects and in keep_stopped
        instance_tags = eval("""{u'project': u'CRM', u'Name': u'hanadyn.acme.com'}""")
        self.assertEqual('stopped', stayontop.will_instance_run(instance_tags))
        # in restricted projects and both in keep_stopped and keep_running
        instance_tags = eval("""{u'project': u'CRM', u'Name': u'sybase.acme.com'}""")
        self.assertEqual('stopped', stayontop.will_instance_run(instance_tags))
        # project is both in restricted and weekend on
        instance_tags = eval("""{u'project': u'PUSHAPP', u'Name': u'push01.acme.com'}""")
        self.assertEqual('running' if stayontop.is_working_hours() else 'stopped', stayontop.will_instance_run(instance_tags))
        # project is both in restricted and weekend on, instance in keep_stopped
        instance_tags = eval("""{u'project': u'PUSHAPP', u'Name': u'apush.acme.com'}""")
        self.assertEqual('stopped', stayontop.will_instance_run(instance_tags))


if __name__ == '__main__':
    unittest.main()

