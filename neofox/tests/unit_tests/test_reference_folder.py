import os
import unittest
from unittest import TestCase

import neofox
import neofox.tests.unit_tests.tools as test_tools
from neofox.exceptions import NeofoxConfigurationException
from neofox.references.references import ReferenceFolder
from neofox.tests.unit_tests.fake_classes import FakeReferenceFolder


class TestReferenceFolder(TestCase):

    def setUp(self):
        os.environ[neofox.REFERENCE_FOLDER_ENV] = "."
        self.fake_reference_folder = FakeReferenceFolder()

    def test_not_provided_reference(self):
        del os.environ[neofox.REFERENCE_FOLDER_ENV]
        with self.assertRaises(NeofoxConfigurationException):
            ReferenceFolder()

    def test_empty_string_reference(self):
        os.environ[neofox.REFERENCE_FOLDER_ENV] = ""
        with self.assertRaises(NeofoxConfigurationException):
            ReferenceFolder()

    def test_non_existing_reference(self):
        os.environ[neofox.REFERENCE_FOLDER_ENV] = "/non_existing_folder"
        with self.assertRaises(NeofoxConfigurationException):
            ReferenceFolder()

    def test_all_resources_exist(self):
        test_tools._mock_file_existence(existing_files=self.fake_reference_folder.resources)
        ReferenceFolder()

    def test_one_resource_do_not_exist(self):
        test_tools._mock_file_existence(
            existing_files=self.fake_reference_folder.resources[1:len(self.fake_reference_folder.resources)],
            unexisting_files=[self.fake_reference_folder.resources[0]]
        )
        with self.assertRaises(NeofoxConfigurationException):
            ReferenceFolder()


if __name__ == "__main__":
    unittest.main()