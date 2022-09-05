import os
import sys
import inspect

import unittest
from unittest.mock import Mock
from unittest.mock import patch


currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir)
import slice

class TestSlice(unittest.TestCase):
    #@patch('slice.Service')
    def test_service_set_replicas(self):
        mock_object = Mock()
        service = slice.Service(mock_object, mock_object, mock_object)
        service.setReplicas(4)

        assert service.replicas == 4

    def test_function_set_replicas(self):
        mock_object = Mock()
        function = slice.Function(mock_object, mock_object, mock_object, mock_object)
        function.setReplicas(4)

        assert function.replicas == 4


#testslice = TestSlice()
#testslice.test_set_replicas()

if __name__ == '__main__':
    unittest.main()