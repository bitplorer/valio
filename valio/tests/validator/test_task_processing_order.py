# Copyright (c) 2022 Valio
#
# This software is released under the MIT License.
# https://opensource.org/licenses/MIT

import unittest
from dataclasses import dataclass

from valio.validator.validators import TaskValidator, Validator


class TestTaskValidatorProcessingOrder(unittest.TestCase):
    """Tasks run once per phase, after processing, on Validator and TaskValidator."""

    def _bind_phase(self, validator, namespace, log, add_name, task_add_name, label):
        def proc(instance, value):
            log.append((f"{label}_proc", value))
            if isinstance(value, str):
                return f"{value}-{label[0]}"
            return value

        def task(instance, value):
            log.append((f"{label}_task", value))

        getattr(validator, add_name)(proc, namespace=namespace)
        getattr(validator, task_add_name)(task, namespace=namespace)

    def test_validator_default_cache_runs_processing_then_task_once(self):
        log = []
        v = Validator(debug=True, logger=False)
        self._bind_phase(
            v, "Host", log, "add_pre_validator", "add_pre_validator_task", "pre"
        )

        @dataclass
        class Host(object):
            x: str = v

        host = Host(x="raw")
        self.assertEqual(host.x, "raw-p")
        self.assertEqual(log, [("pre_proc", "raw"), ("pre_task", "raw-p")])

    def test_validator_all_phases_run_task_once_after_processing(self):
        log = []
        v = Validator(debug=True, logger=False, cache_task=False)
        ns = "Host"
        phases = (
            ("add_pre_validator", "add_pre_validator_task", "pre"),
            ("add_post_validator", "add_post_validator_task", "post"),
            ("add_post_set", "add_post_set_task", "set"),
            ("add_pre_get", "add_pre_get_task", "pget"),
            ("add_post_get", "add_post_get_task", "gget"),
            ("add_pre_delete", "add_pre_delete_task", "pdel"),
            ("add_post_delete", "add_post_delete_task", "gdel"),
        )
        for add_name, task_add_name, label in phases:
            self._bind_phase(v, ns, log, add_name, task_add_name, label)

        @dataclass
        class Host(object):
            x: str = v

        host = Host(x="raw")
        _ = host.x
        del host.x

        self.assertEqual(
            log,
            [
                ("pre_proc", "raw"),
                ("pre_task", "raw-p"),
                ("post_proc", "raw-p"),
                ("post_task", "raw-p-p"),
                ("set_proc", "raw-p-p"),
                ("set_task", "raw-p-p-s"),
                ("pget_proc", "x"),
                ("pget_task", "x-p"),
                ("gget_proc", "x"),
                ("gget_task", "x-g"),
                ("pdel_proc", "x"),
                ("pdel_task", "x-p"),
                ("gdel_proc", "x"),
                ("gdel_task", "x-g"),
            ],
        )

    def test_plain_validator_processing_without_tasks(self):
        log = []
        v = Validator(debug=True, logger=False)

        def proc(instance, value):
            log.append(("proc", value))
            return value.upper()

        v.add_pre_validator(proc, namespace="Plain")

        @dataclass
        class Plain(object):
            x: str = v

        self.assertEqual(Plain(x="raw").x, "RAW")
        self.assertEqual(log, [("proc", "raw")])

    def test_taskvalidator_keeps_assigned_value_and_runs_task_once(self):
        log = []
        tv = TaskValidator(
            task_interval=None, cache_task=False, debug=True, logger=False
        )

        def task(instance, value):
            log.append(("task", value))

        tv.add_pre_validator_task(task, namespace="Solo")

        @dataclass
        class Solo(object):
            x: str = tv

        solo = Solo(x="raw")
        self.assertEqual(solo.x, "raw")
        self.assertEqual(log, [("task", "raw")])
