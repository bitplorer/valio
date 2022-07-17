# Copyright (c) 2022 Valio
# 
# This software is released under the MIT License.
# https://opensource.org/licenses/MIT


import typing
import unittest
from dataclasses import dataclass

from toml import load
from valio import (PatternValidator, ReassignValidator, RequiredValidator,
                   TypeValidator, __version__)
from valio.validator.validators import MultipleValidator


class TestVersion(unittest.TestCase):
    
    def test_version(self):
        self.assertEqual(load('pyproject.toml')['tool']['poetry']['version'], __version__)
        
        

class TestTypeValidator(unittest.TestCase):
    
    def setUp(self) -> None:
        self.validator = TypeValidator()
        self.debug_validator = TypeValidator(debug=True)
        
        def type_class_common_validator(typ, tp=None, tp_debug=None):
            @dataclass
            class TypeClass(object):
                tp: typing.Union[typ, TypeValidator, None] = self.validator
                tp_debug: typing.Union[typ, TypeValidator, None] = self.debug_validator
            return TypeClass(tp, tp_debug)

        def type_class(typ, tp=None, tp_debug=None):
            @dataclass
            class TypeClass(object):
                tp: typing.Union[typ, TypeValidator, None] = TypeValidator()
                tp_debug: typing.Union[typ, TypeValidator, None] = TypeValidator(debug=True)
            return TypeClass(tp, tp_debug)
        
        self.type_class = type_class
        self.type_class_common_validator = type_class_common_validator

    def test_type_class_validator(self):
        # typ = int, integer case
        self.assertIsNone(self.type_class(typ=int).tp)
        self.assertIsNone(self.type_class(typ=int).tp_debug)
        # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++ #
        # with debug = False; the error is passed silently and value becomes   #
        # None                                                                 #
        # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++ #
        self.assertIsNone(self.type_class(typ=int, tp="-1").tp)
        # ____________________________________________________________________ #
        
        # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++ #
        # below assertEqual is passed because both isinstance(True, int) and   #
        # isinstance(False, int) are True                                      #
        # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++ #
        self.assertEqual(self.type_class(typ=int, tp=True).tp, True)
        self.assertEqual(self.type_class(typ=int, tp=False).tp, False)
        self.assertEqual(self.type_class(typ=int, tp_debug=True).tp_debug, True)
        self.assertEqual(self.type_class(typ=int, tp_debug=False).tp_debug, False)
        # ____________________________________________________________________ # 
        
        with self.assertRaises(TypeError):
            self.type_class(typ=int, tp_debug="-1")
        
        self.assertEqual(self.type_class(typ=int, tp=~1).tp, ~1)
        self.assertEqual(self.type_class(typ=int, tp_debug=~1).tp_debug, ~1)
        # typ = bool, boolean case
        self.assertIsNone(self.type_class(typ=bool).tp)
        self.assertIsNone(self.type_class(typ=bool).tp_debug)
        self.assertIsNone(self.type_class(typ=bool, tp="-1").tp)
        with self.assertRaises(TypeError):
            self.type_class(typ=bool, tp_debug="-1")
        self.assertEqual(self.type_class(typ=bool, tp_debug=True).tp_debug, True)
        self.assertEqual(self.type_class(typ=bool, tp_debug=bool(~1)).tp_debug, bool(~1))
        self.assertEqual(self.type_class(typ=bool, tp_debug=False).tp_debug, False)
        # typ = Union[str, int]
        self.assertEqual(self.type_class(typ=typing.Union[str, int], tp="a").tp, "a")
        
        #      ____ COMMON VALIDATORS ARE REASSIGNED HERE BELOW ____
        # The expected behaviour is that common validators if re-assigned 
        # to a variable accross classes, works only if the variable in the 
        # reassigned class has same annotations or subclass of prior assigned 
        # annotation.
        # Below validation works with reassignment because issubclasss(bool, int)
        #
        # typ = int, integer case
        self.assertIsNone(self.type_class_common_validator(typ=int).tp)
        self.assertIsNone(self.type_class_common_validator(typ=int).tp_debug)
        # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++ #
        # with debug = False; the error is passed silently and value becomes   #
        # None                                                                 #
        # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++ #
        self.assertIsNone(self.type_class_common_validator(typ=int, tp="-1").tp)
        # ____________________________________________________________________ #
        
        # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++ #
        # below assertEqual is passed because both isinstance(True, int) and   #
        # isinstance(False, int) are True                                      #
        # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++ #
        self.assertEqual(self.type_class_common_validator(typ=int, tp=True).tp, True)
        self.assertEqual(self.type_class_common_validator(typ=int, tp=False).tp, False)
        self.assertEqual(self.type_class_common_validator(typ=int, tp_debug=True).tp_debug, True)
        self.assertEqual(self.type_class_common_validator(typ=int, tp_debug=False).tp_debug, False)
        # ____________________________________________________________________ # 
        
        with self.assertRaises(TypeError):
            self.type_class_common_validator(typ=int, tp_debug="-1")
        
        self.assertEqual(self.type_class_common_validator(typ=int, tp=~1).tp, ~1)
        self.assertEqual(self.type_class_common_validator(typ=int, tp_debug=~1).tp_debug, ~1)
        # typ = bool, boolean case
        self.assertIsNone(self.type_class_common_validator(typ=bool).tp)
        self.assertIsNone(self.type_class_common_validator(typ=bool).tp_debug)
        self.assertIsNone(self.type_class_common_validator(typ=bool, tp="-1").tp)
        with self.assertRaises(TypeError):
            self.type_class_common_validator(typ=bool, tp_debug="-1")
        self.assertEqual(self.type_class_common_validator(typ=bool, tp_debug=True).tp_debug, True)
        self.assertEqual(self.type_class_common_validator(typ=bool, tp_debug=bool(~1)).tp_debug, bool(~1))
        self.assertEqual(self.type_class_common_validator(typ=bool, tp_debug=False).tp_debug, False)
        
        #     ____________________________________________________________
        
        # CASE: typ = Union[str, int],
        # below case here fails because prior to reassignment of self.validator
        # it was annotated as 'bool' due to above test case and now when we reassign
        # the self.validator it checks if new annotation is same as 'bool'[in this case]
        # or is subclass of 'bool' [in this case], as the new tupe is Union[str, int] it fails
        with self.assertRaises(RuntimeError):
            self.assertEqual(self.type_class_common_validator(typ=typing.Union[str, int], tp="a").tp, "a")


class TestRequiredValidator(unittest.TestCase):
    
    def setUp(self) -> None:
        required_validator = typing.Union[str, RequiredValidator, None]
        self.required_validator: RequiredValidator = RequiredValidator
        self.required_empty: RequiredValidator = RequiredValidator()
        self.required_none: RequiredValidator = RequiredValidator(required=None)
        self.required_true: RequiredValidator = RequiredValidator(required=True, default="q")
        self.required_false: RequiredValidator = RequiredValidator(required=False)
        self.required_empty_debug_true: RequiredValidator = RequiredValidator(debug=True)
        self.required_none_debug_true: RequiredValidator = RequiredValidator(required=None, debug=True)
        self.required_true_debug_true: RequiredValidator = RequiredValidator(required=True, debug=True)
        self.required_false_debug_true: RequiredValidator = RequiredValidator(required=False, debug=True)
        
        @dataclass
        class TestRequiredClass(object):
            required_empty: required_validator = self.required_empty
            required_none: required_validator = self.required_none
            required_true: required_validator = self.required_true
            required_false: required_validator = self.required_false
            required_empty_debug_true: required_validator = self.required_empty_debug_true
            required_none_debug_true: required_validator = self.required_none_debug_true
            required_true_debug_true: required_validator = self.required_true_debug_true
            required_false_debug_true: required_validator = self.required_false_debug_true
            
        self.class_required = TestRequiredClass
        
    def test_required_is_valid(self):
        self.assertEqual(self.required_validator().required, None)
        self.assertEqual(self.required_validator(required=None).required, None) 
        self.required_validator()
        self.required_validator(required=None)
        self.assertEqual(self.required_validator(required=True).required, True)
        self.assertEqual(self.required_validator(required=False).required, False)

    def test_required_is_invalid(self):
        # reasign value of invalid type
        with self.assertRaises(TypeError):
            self.required_validator(required="True")
        
        with self.assertRaises(TypeError):
            self.required_validator(required="False")
            
        with self.assertRaises(TypeError):
            self.required_validator(required=list)
            
        with self.assertRaises(TypeError):
            self.required_validator(required=TypeValidator(debug=True))
    
    def test_required_class(self):
        with self.assertRaises(ValueError):
            self.class_required(required_true_debug_true=None)
        self.class_required(required_true_debug_true="OK")
        
        @dataclass
        class RequiredEmptyDebugNone(object):
            value: RequiredValidator = RequiredValidator(debug=None)
        
        @dataclass
        class RequiredNoneDebugNone(object):
            value: RequiredValidator = RequiredValidator(required=None, debug=None)
            
        @dataclass
        class RequiredTrueDebugNone(object):
            value: RequiredValidator = RequiredValidator(required=True, debug=None)
        
        @dataclass
        class RequiredFalseDebugNone(object):
            value: RequiredValidator = RequiredValidator(required=False, debug=None)
        
        # value empty
        self.assertIsNone(RequiredEmptyDebugNone().value)
        self.assertIsNone(RequiredNoneDebugNone().value)
        self.assertIsNone(RequiredTrueDebugNone().value)
        self.assertIsNone(RequiredFalseDebugNone().value)
        
        # value is None
        self.assertIsNone(RequiredEmptyDebugNone(value=None).value)
        self.assertIsNone(RequiredNoneDebugNone(value=None).value)
        self.assertIsNone(RequiredTrueDebugNone(value=None).value)
        self.assertIsNone(RequiredFalseDebugNone(value=None).value)
        
        # value is False
        self.assertEqual(RequiredEmptyDebugNone(value=False).value, False)
        self.assertEqual(RequiredNoneDebugNone(value=False).value, False)
        self.assertEqual(RequiredTrueDebugNone(value=False).value, False)
        self.assertEqual(RequiredFalseDebugNone(value=False).value, False)
        
        # value is True
        self.assertEqual(RequiredEmptyDebugNone(value=True).value, True)
        self.assertEqual(RequiredNoneDebugNone(value=True).value, True)
        self.assertEqual(RequiredTrueDebugNone(value=True).value, True)
        self.assertEqual(RequiredFalseDebugNone(value=True).value, True)


        @dataclass
        class RequiredEmptyDebugFalse(object):
            value: RequiredValidator = RequiredValidator(debug=False)
        
        @dataclass
        class RequiredNoneDebugFalse(object):
            value: RequiredValidator = RequiredValidator(required=None, debug=False)
            
        @dataclass
        class RequiredTrueDebugFalse(object):
            value: RequiredValidator = RequiredValidator(required=True, debug=False)
        
        @dataclass
        class RequiredFalseDebugFalse(object):
            value: RequiredValidator = RequiredValidator(required=False, debug=False)
            
        
        # value is None
        self.assertIsNone(RequiredEmptyDebugFalse(value=None).value)
        self.assertIsNone(RequiredNoneDebugFalse(value=None).value)
        self.assertIsNone(RequiredTrueDebugFalse(value=None).value)
        self.assertIsNone(RequiredFalseDebugFalse(value=None).value)
        
        # value is False
        self.assertEqual(RequiredEmptyDebugFalse(value=False).value, False)
        self.assertEqual(RequiredNoneDebugFalse(value=False).value, False)
        self.assertEqual(RequiredTrueDebugFalse(value=False).value, False)
        self.assertEqual(RequiredFalseDebugFalse(value=False).value, False)
        
        # value is True
        self.assertEqual(RequiredEmptyDebugFalse(value=True).value, True)
        self.assertEqual(RequiredNoneDebugFalse(value=True).value, True)
        self.assertEqual(RequiredTrueDebugFalse(value=True).value, True)
        self.assertEqual(RequiredFalseDebugFalse(value=True).value, True)
        
        @dataclass
        class RequiredEmptyDebugTrue(object):
            value: RequiredValidator = RequiredValidator(debug=True)
        
        @dataclass
        class RequiredNoneDebugTrue(object):
            value: RequiredValidator = RequiredValidator(required=None, debug=True)
            
        @dataclass
        class RequiredTrueDebugTrue(object):
            value: RequiredValidator = RequiredValidator(required=True, debug=True)
        
        @dataclass
        class RequiredFalseDebugTrue(object):
            value: RequiredValidator = RequiredValidator(required=False, debug=True)
            
        
        # value is None
        self.assertIsNone(RequiredEmptyDebugTrue(value=None).value)
        self.assertIsNone(RequiredNoneDebugTrue(value=None).value)
        with self.assertRaises(ValueError):
            RequiredTrueDebugTrue(value=None).value
        self.assertIsNone(RequiredFalseDebugTrue(value=None).value)
        
        # value is False
        self.assertEqual(RequiredEmptyDebugTrue(value=False).value, False)
        self.assertEqual(RequiredNoneDebugTrue(value=False).value, False)
        self.assertEqual(RequiredTrueDebugTrue(value=False).value, False)
        self.assertEqual(RequiredFalseDebugTrue(value=False).value, False)
        
        # value is True
        self.assertEqual(RequiredEmptyDebugTrue(value=True).value, True)
        self.assertEqual(RequiredNoneDebugTrue(value=True).value, True)
        self.assertEqual(RequiredTrueDebugTrue(value=True).value, True)
        self.assertEqual(RequiredFalseDebugTrue(value=True).value, True)
        

class TestPatternValidator(unittest.TestCase):
    
    def setUp(self) -> None:
        self.word_1_or_more = r'\w+' 
        
    
    def test_pattern(self):
        @dataclass
        class PatternEmptyDebugNone(object):
            value: str | PatternValidator = PatternValidator()
            
        @dataclass
        class PatternEmptyDebugTrue(object):
            value: str | PatternValidator = PatternValidator(debug=True)
            
        @dataclass
        class PatternEmptyDebugFalse(object):
            value: str | PatternValidator = PatternValidator(debug=False)
        
        self.assertEqual(PatternEmptyDebugNone(value="1").value, "1")
        self.assertEqual(PatternEmptyDebugTrue(value="1").value, "1")  
        self.assertEqual(PatternEmptyDebugFalse(value="1").value, "1")
        @dataclass
        class PatternAndDebugNone(object):
            value: str | PatternValidator = PatternValidator(pattern=self.word_1_or_more)
            
        @dataclass
        class PatternAndDebugTrue(object):
            value: str | PatternValidator = PatternValidator(pattern=self.word_1_or_more, debug=True)
        
        @dataclass
        class PatternAndDebugFalse(object):
            value: str | PatternValidator = PatternValidator(pattern=self.word_1_or_more, debug=False)

        # value = None
        self.assertEqual(PatternAndDebugNone(value=None).value, None)
        self.assertEqual(PatternAndDebugFalse(value=None).value, None)
        self.assertEqual(PatternAndDebugTrue(value=None).value, None)
        
        # value = ""
        self.assertEqual(PatternAndDebugNone(value="").value, None)
        self.assertEqual(PatternAndDebugFalse(value="").value, None)
        with self.assertRaises(ValueError):
            PatternAndDebugTrue(value="").value
        
        # value = "a string"
        self.assertEqual(PatternAndDebugNone(value="a string").value, "a string")
        self.assertEqual(PatternAndDebugFalse(value="a string").value, "a string")
        self.assertEqual(PatternAndDebugTrue(value="a string").value, "a string")
        
class TestReassignValidator(unittest.TestCase):

    def setUp(self) -> None:
        self.reassign_validator: typing.Type[ReassignValidator] = ReassignValidator
        self.empty: ReassignValidator = ReassignValidator()
        self.reassign_true: ReassignValidator = ReassignValidator(reassign=True)
        self.reassign_false: ReassignValidator = ReassignValidator(reassign=False)
        self.reassign_none: ReassignValidator = ReassignValidator(reassign=None)
        self.reassign_empty_debug_true: ReassignValidator = ReassignValidator(debug=True)
        self.reassign_true_debug_true: ReassignValidator = ReassignValidator(reassign=True, debug=True)
        self.reassign_false_debug_true: ReassignValidator = ReassignValidator(reassign=False, debug=True)
        self.reassign_none_debug_true: ReassignValidator = ReassignValidator(reassign=None, debug=True)
        
        @dataclass
        class TestReassignClass(object):
            empty: typing.Union[str, ReassignValidator, None] =  self.empty
            true: typing.Union[str, ReassignValidator, None] =  self.reassign_true
            false: typing.Union[str, ReassignValidator, None] =  self.reassign_false
            none: typing.Union[str, ReassignValidator, None] =  self.reassign_none
            reassign_empty_with_debug: typing.Union[str, ReassignValidator, None] =  self.reassign_empty_debug_true
            reassign_true_with_debug: typing.Union[str, ReassignValidator, None] =  self.reassign_true_debug_true
            reassign_false_with_debug: typing.Union[str, ReassignValidator, None] =  self.reassign_false_debug_true
            reassign_none_with_debug: typing.Union[str, ReassignValidator, None] =  self.reassign_none_debug_true

        self.class_reassigned = TestReassignClass(
            empty="Reassign Empty Debug Empty", 
            true="Reassign True Debug Empty", 
            false="Reassign False Debug Empty", 
            none="Reassign None Debug Empty", 
            reassign_empty_with_debug="Reassign Empty Debug True", 
            reassign_true_with_debug="Reassign True Debug True", 
            reassign_false_with_debug="Reassign False Debug True", 
            reassign_none_with_debug="Reassign None Debug True"
            )
    
    def test_reassign_is_valid(self):
        self.assertEqual(self.reassign_validator().reassign, None)
        self.assertEqual(self.reassign_validator(reassign=None).reassign, None)
        self.reassign_validator()
        self.assertEqual(self.reassign_validator(reassign=True).reassign, True)    
        self.assertEqual(self.reassign_validator(reassign=False).reassign, False) 
        
    def test_reassign_is_invalid(self):
        # reasign value of invalid type
        with self.assertRaises(TypeError):
            self.reassign_validator(reassign="True")
        
        with self.assertRaises(TypeError):
            self.reassign_validator(reassign="False")
            
        with self.assertRaises(TypeError):
            self.reassign_validator(reassign=list)
            
        with self.assertRaises(TypeError):
            self.reassign_validator(reassign=TypeValidator(debug=True))
            
    def test_reassign_empty(self):
        self.assertIsNotNone(self.class_reassigned.empty)
        self.assertEqual(self.class_reassigned.empty, "Reassign Empty Debug Empty")
        self.assertGreater(self.empty.number_of_assignment, 0)
        self.assertEqual(self.empty.number_of_assignment, 1)
        self.assertGreater(self.empty.__dict__[id(self.class_reassigned)], 0)
        self.assertEqual(self.empty.__dict__[id(self.class_reassigned)], 1)
        self.class_reassigned.empty = "Reassigned"
        self.assertEqual(self.class_reassigned.empty, "Reassigned")
        self.assertGreater(self.empty.__dict__[id(self.class_reassigned)], 1)
        self.assertEqual(self.empty.__dict__[id(self.class_reassigned)], 2)
        
        # this should not fail because of TypeError as no Type Checks happen 
        # in ReassignValidator
        self.class_reassigned.empty = False  # notice empty type is 'str' but got set with 'bool'
        self.assertEqual(self.class_reassigned.empty, False)
        self.assertGreater(self.empty.number_of_assignment, 0)
        self.assertEqual(self.empty.number_of_assignment, 3)
        
    
    def test_reassign_none(self):
        self.assertIsNotNone(self.class_reassigned.none)
        self.assertEqual(self.class_reassigned.none, "Reassign None Debug Empty")
        self.assertGreater(self.reassign_none.number_of_assignment, 0)
        self.assertEqual(self.reassign_none.number_of_assignment, 1)
        self.class_reassigned.none = "Reassigned"
        self.assertEqual(self.class_reassigned.none, "Reassigned")
        self.assertGreater(self.reassign_none.number_of_assignment, 0)
        self.assertEqual(self.reassign_none.number_of_assignment, 2)
        
    def test_reassign_true(self):
        self.assertIsNotNone(self.class_reassigned.true)
        self.assertEqual(self.class_reassigned.true, "Reassign True Debug Empty")
        self.assertGreater(self.reassign_true.number_of_assignment, 0)
        self.assertEqual(self.reassign_true.number_of_assignment, 1)
        self.class_reassigned.true = "Reassigned"
        self.assertEqual(self.class_reassigned.true, "Reassigned")
        self.assertGreater(self.reassign_true.number_of_assignment, 0)
        self.assertEqual(self.reassign_true.number_of_assignment, 2)
        
    def test_reassign_false(self):
        self.assertIsNotNone(self.class_reassigned.false)
        self.assertEqual(self.class_reassigned.false, "Reassign False Debug Empty")
        self.assertGreater(self.reassign_false.number_of_assignment, 0)
        self.assertEqual(self.reassign_false.number_of_assignment, 1)
        self.class_reassigned.false = "Reassigned" # by default debug=None so no error raised but assignment fails by design
        self.assertNotEqual(self.class_reassigned.false, "Reassigned")
        self.assertEqual(self.class_reassigned.false, "Reassign False Debug Empty")
        self.assertGreater(self.reassign_false.number_of_assignment, 0)
        self.assertEqual(self.reassign_false.number_of_assignment, 1)
        
    def test_reassign_empty_with_debug(self):
        self.assertIsNotNone(self.class_reassigned.reassign_empty_with_debug)
        self.assertEqual(self.class_reassigned.reassign_empty_with_debug, "Reassign Empty Debug True")
        self.assertGreater(self.reassign_empty_debug_true.number_of_assignment, 0)
        self.assertEqual(self.reassign_empty_debug_true.number_of_assignment, 1)
        self.class_reassigned.reassign_empty_with_debug = "Reassigned"
        self.assertEqual(self.class_reassigned.reassign_empty_with_debug, "Reassigned")
        self.assertGreater(self.reassign_empty_debug_true.number_of_assignment, 0)
        self.assertEqual(self.reassign_empty_debug_true.number_of_assignment, 2)
        
        # this should not fail because of TypeError as no Type Checks happen 
        # in ReassignValidator
        self.class_reassigned.reassign_empty_with_debug = False  # notice debug_empty type is 'str' but got set with 'bool'
        self.assertEqual(self.class_reassigned.reassign_empty_with_debug, False)
        self.assertGreater(self.reassign_empty_debug_true.number_of_assignment, 0)
        self.assertEqual(self.reassign_empty_debug_true.number_of_assignment, 3)
        
    def test_reassign_none_with_debug(self):
        self.assertIsNotNone(self.class_reassigned.reassign_none_with_debug)
        self.assertEqual(self.class_reassigned.reassign_none_with_debug, "Reassign None Debug True")
        self.assertGreater(self.reassign_none_debug_true.number_of_assignment, 0)
        self.assertEqual(self.reassign_none_debug_true.number_of_assignment, 1)
        self.class_reassigned.reassign_none_with_debug = "Reassigned"
        self.assertEqual(self.class_reassigned.reassign_none_with_debug, "Reassigned")
        self.assertGreater(self.reassign_none_debug_true.number_of_assignment, 0)
        self.assertEqual(self.reassign_none_debug_true.number_of_assignment, 2)
        
        # this should not fail because of TypeError as no Type Checks happen 
        # in ReassignValidator
        self.class_reassigned.reassign_none_with_debug = False  # notice debug_none type is 'str' but got set with 'bool'
        self.assertEqual(self.class_reassigned.reassign_none_with_debug, False)
        self.assertGreater(self.reassign_none_debug_true.number_of_assignment, 0)
        self.assertEqual(self.reassign_none_debug_true.number_of_assignment, 3)
        
    def test_reassign_true_with_debug(self):
        self.assertIsNotNone(self.class_reassigned.reassign_true_with_debug)
        self.assertEqual(self.class_reassigned.reassign_true_with_debug, "Reassign True Debug True")
        self.assertGreater(self.reassign_true_debug_true.number_of_assignment, 0)
        self.assertEqual(self.reassign_true_debug_true.number_of_assignment, 1)
        self.class_reassigned.reassign_true_with_debug = "Reassigned"
        self.assertEqual(self.class_reassigned.reassign_true_with_debug, "Reassigned")
        self.assertGreater(self.reassign_true_debug_true.number_of_assignment, 0)
        self.assertEqual(self.reassign_true_debug_true.number_of_assignment, 2)
        
        # this should not fail because of TypeError as no Type Checks happen 
        # in ReassignValidator
        self.class_reassigned.reassign_true_with_debug = False  # <- notice no type validation, expects 'str' but set with 'bool'
        self.assertEqual(self.class_reassigned.reassign_true_with_debug, False)
        self.assertGreater(self.reassign_true_debug_true.number_of_assignment, 0)
        self.assertEqual(self.reassign_true_debug_true.number_of_assignment, 3)

    def test_reassign_false_with_debug(self):
        self.assertIsNotNone(self.class_reassigned.reassign_false_with_debug)
        self.assertEqual(self.class_reassigned.reassign_false_with_debug, "Reassign False Debug True")
        self.assertGreater(self.reassign_false_debug_true.number_of_assignment, 0)
        self.assertEqual(self.reassign_false_debug_true.number_of_assignment, 1)
        with self.assertRaises(AttributeError): 
            self.class_reassigned.reassign_false_with_debug = "Reassigned"
        self.assertNotEqual(self.class_reassigned.reassign_false_with_debug, "Reassigned")
        self.assertEqual(self.class_reassigned.reassign_false_with_debug, "Reassign False Debug True")
        self.assertGreater(self.reassign_false_debug_true.number_of_assignment, 0)
        self.assertEqual(self.reassign_false_debug_true.number_of_assignment, 1)
        
        # this should fail not because of TypeError as no Type Checks happen 
        # in ReassignValidator for values assigned but due to reassign_validation
        with self.assertRaises(AttributeError):
            # notice no type validation, expects 'str' but set with 'bool' error due to reassign_validation raising
            # AttributeError
            self.class_reassigned.reassign_false_with_debug = False  
        self.assertNotEqual(self.class_reassigned.reassign_false_with_debug, False)
        self.assertEqual(self.class_reassigned.reassign_false_with_debug, "Reassign False Debug True")
        self.assertGreater(self.reassign_false_debug_true.number_of_assignment, 0)
        self.assertEqual(self.reassign_false_debug_true.number_of_assignment, 1)
        
class TestMultipleValidator(unittest.TestCase):
    
    def setUp(self) -> None:
        self.multiple_of = 2
    
    def test_multiple_of_validator(self):
        @dataclass
        class MultipleEmptyDebugEmpty(object):
            value: int| MultipleValidator | None = MultipleValidator()
            
        @dataclass
        class MultipleEmptyDebugTrue(object):
            value: int| MultipleValidator | None = MultipleValidator(debug=True)
            
        @dataclass
        class MultipleEmptyDebugFalse(object):
            value: int| MultipleValidator | None = MultipleValidator(debug=False)
            
        self.assertEqual(MultipleEmptyDebugEmpty(value=None).value, None)
        self.assertEqual(MultipleEmptyDebugEmpty(value="Abc").value, 'Abc') # no typechecks
        self.assertEqual(MultipleEmptyDebugEmpty(value=1).value, 1)            

if __name__ == '__main__':
    unittest.main()
    

