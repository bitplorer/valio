# Copyright (c) 2022 Valio
# 
# This software is released under the MIT License.
# https://opensource.org/licenses/MIT



import typing
import unittest
from dataclasses import dataclass
from typing import Union

from valio.descriptor import Property


class PropertyClass(Property):
    pre_set_param = None
    post_set_param = None
    pre_get_param = None
    post_get_param = None
    pre_del_param = None
    post_del_param = None
    
    def pre_set(self, obj, value):
        if self.pre_set_param is None:
            self.pre_set_param = "assigned pre_set_param"
        return super().pre_set(obj, value)
    
    def post_set(self, obj, value):
        if self.post_set_param is None:
            self.post_set_param = "assigned post_set_param"
        return super().post_set(obj, value)
    
    def pre_get(self, obj, value):
        if self.pre_get_param is None:
            self.pre_get_param = "assigned pre_get_param"
        return super().pre_get(obj, value)
    
    def post_get(self, obj, value):
        if self.post_get_param is None:
            self.post_get_param = "assigned post_get_param"
        return super().post_get(obj, value)
    
    def pre_delete(self, obj, value):
        if self.pre_del_param is None:
            self.pre_del_param = "assigned pre_del_param"
        return super().pre_delete(obj, value)
    
    def post_delete(self, obj, value):
        if self.post_del_param is None:
            self.post_del_param = "assigned post_del_param"
        return super().post_delete(obj, value)
    
    
class TestPropertyClass(unittest.TestCase):
    
    def setUp(self) -> None:
        self.property_unassigned: PropertyClass = PropertyClass()
        self.property_assigned = PropertyClass()
        self.property_assigned_with_default = PropertyClass(default="default value")
        self.property_assigned_with_debug = PropertyClass(debug=True)
        self.property_assigned_with_doc = PropertyClass(doc="Testing Doc")
        
        @dataclass
        class PropertyAssignedClass(object):
            activity: typing.Union[str, PropertyClass, None] = self.property_assigned
            default: typing.Union[str, PropertyClass, None] = self.property_assigned_with_default
            debugging: typing.Union[str, PropertyClass, None] = self.property_assigned_with_debug
            document: typing.Union[str, PropertyClass, None] = self.property_assigned_with_doc
            
        self.property_assigned_class = PropertyAssignedClass(activity="testing", debugging="debug value")
    
    def test_property_instance_type(self):
        self.assertIsInstance(self.property_unassigned, PropertyClass)
        self.assertIsInstance(self.property_assigned, PropertyClass)
        self.assertIsInstance(self.property_assigned_with_default, PropertyClass)
        self.assertIsInstance(self.property_assigned_with_debug, PropertyClass)
        self.assertIsInstance(self.property_assigned_with_doc, PropertyClass)
    
    def test_property_assigned_class(self):
        self.assertIsNotNone(self.property_assigned_class.activity)
        self.assertEqual(self.property_assigned_class.activity, 'testing')
        self.assertIsNotNone(self.property_assigned_class.default)
        self.assertEqual(self.property_assigned_class.default, "default value")
        self.assertIsNotNone(self.property_assigned_class.debugging)
        self.assertEqual(self.property_assigned_class.debugging, "debug value")
        self.assertIsNone(self.property_assigned_class.document)
        self.assertIsNotNone(self.property_assigned_class.__doc__)
        self.assertEqual(self.property_assigned_class.__doc__, 'Class: PropertyAssignedClass\n\t:param typing.Union[str, __main__.PropertyClass, NoneType] activity:\n\t:param typing.Union[str, __main__.PropertyClass, NoneType] default:\n\t:param typing.Union[str, __main__.PropertyClass, NoneType] debugging:\n\t:param typing.Union[str, __main__.PropertyClass, NoneType] document: Testing Doc')

    def test_unassigned_property_name_is_none(self):
        self.assertIsNone(self.property_unassigned.name)
        
    def test_assigned_property_name_is_not_none(self):
        self.assertIsNotNone(self.property_assigned.name)
        self.assertEqual(self.property_assigned.name, "activity")
        self.assertIsNotNone(self.property_assigned_with_default.name)
        self.assertEqual(self.property_assigned_with_default.name, "default")
        self.assertIsNotNone(self.property_assigned_with_debug.name)
        self.assertEqual(self.property_assigned_with_debug.name, "debugging")
        self.assertIsNotNone(self.property_assigned_with_doc.name)
        self.assertEqual(self.property_assigned_with_doc.name, "document")
        
    def test_assigned_property_parameter(self):
        self.assertEqual(self.property_assigned_with_debug.debug, True)
        self.assertEqual(self.property_assigned_with_default.default, "default value")
        self.assertEqual(self.property_assigned_with_doc.doc, "Testing Doc")
        
    def test_unassigned_property_pre_set_param_is_none(self):
        self.assertIsNone(self.property_unassigned.pre_set_param)
    
    def test_assigned_property_pre_set_param_is_not_none(self):
        self.assertIsNotNone(self.property_assigned.pre_set_param)
        self.assertEqual(self.property_assigned.pre_set_param, "assigned pre_set_param")
        
    def test_unassigned_property_post_set_param_is_none(self):
        self.assertIsNone(self.property_unassigned.post_set_param)
        
    def test_assigned_property_post_set_param_is_not_none(self):
        self.assertIsNotNone(self.property_assigned.post_set_param)
        self.assertEqual(self.property_assigned.post_set_param, "assigned post_set_param")
    
    def test_unassigned_property_pre_get_param_is_none(self):
        self.assertIsNone(self.property_unassigned.pre_get_param)
        
    def test_assigned_property_pre_get_param_is_not_none(self):
        self.assertIsNone(self.property_assigned.pre_get_param)
        # get property from property_assigned_class to call __get__
        _ =  self.property_assigned_class.activity
        self.assertIsNotNone(self.property_assigned.pre_get_param)
        self.assertEqual(self.property_assigned.pre_get_param, "assigned pre_get_param")
    
    def test_unassigned_property_post_get_param_is_none(self):
        self.assertIsNone(self.property_unassigned.post_get_param)
    
    def test_assigned_property_post_get_param_is_not_none(self):
        self.assertIsNone(self.property_assigned.post_get_param)
        # get property from property_assigned_class to call __get__
        _ =  self.property_assigned_class.activity
        self.assertIsNotNone(self.property_assigned.post_get_param)
        self.assertEqual(self.property_assigned.post_get_param, "assigned post_get_param")
        
    def test_unassigned_property_pre_del_param_is_none(self):
        self.assertIsNone(self.property_unassigned.pre_del_param)
        
    def test_assigned_property_pre_del_param_is_not_none(self):
        self.assertIsNone(self.property_assigned.pre_del_param)
        # del property from property_assigned_class to call __del__
        del self.property_assigned_class.activity
        self.assertIsNotNone(self.property_assigned.pre_del_param)
        self.assertEqual(self.property_assigned.pre_del_param, "assigned pre_del_param")
    
    def test_unassigned_property_post_del_param_is_none(self):
        self.assertIsNone(self.property_unassigned.post_del_param)
        
    def test_assigned_property_post_del_param_is_not_none(self):
        self.assertIsNone(self.property_assigned.post_del_param)
        # del property from property_assigned_class to call __del__
        del self.property_assigned_class.activity
        self.assertIsNotNone(self.property_assigned.post_del_param)
        self.assertEqual(self.property_assigned.post_del_param, "assigned post_del_param")
 

        
@dataclass
class TestClass(object):
    prop: Union[str, Property] = Property()
    debug_prop: Union[str, Property] = Property(debug=True)
    

class TestClassProperty(unittest.TestCase):
    
    def setUp(self) -> None:
        self.test_class: TestClass = TestClass(prop="Banker")
    
    def test_class_set_property(self):
        self.test_class.prop = "Chef"
        self.assertEqual(self.test_class.prop, "Chef")
        
    def test_class_get_property(self):
        self.assertEqual(self.test_class.prop, "Banker")
        self.assertEqual(self.test_class.debug_prop, None)
        
    def test_class_delete_property(self):
        self.assertIsNotNone(self.test_class.prop)
        del self.test_class.prop
        self.assertIsNone(self.test_class.prop)
        
        
if __name__ == '__main__':
    unittest.main()
        
        