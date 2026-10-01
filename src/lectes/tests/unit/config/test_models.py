from unittest_extensions import args, TestCase

from lectes.config.models import Rule
from lectes.engine.models import Regex


def rule(name, regex):
    return Rule(name=name, regex=Regex(regex))


class TestConfig(TestCase):
    def test_rules_with_different_regex_not_equal(self):
        self.assertNotEqual(rule("X", "a"), rule("X", "b"))

    def test_rules_with_different_name_not_equal(self):
        self.assertNotEqual(rule("X", "a"), rule("Y", "a"))

    def test_rule_usable_as_dict_key(self):
        self.assertEqual({rule("X", "a"): 1}[rule("X", "a")], 1)
