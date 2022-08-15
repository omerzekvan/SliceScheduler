import os
import sys
import inspect

import unittest
from unittest.mock import patch


currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir)
import slice

class TestSlice(unittest.TestCase):
    #@patch('slice.Service')
    def test_set_replicas(self):
        service = slice.Service(1, 2, 3)
        service.setReplicas(4)

        assert service.replicas == 4


#testslice = TestSlice()
#testslice.test_set_replicas()

if __name__ == '__main__':
    unittest.main()