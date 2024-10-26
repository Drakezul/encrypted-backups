import unittest
import os
import shutil

from backup import encrypt as enc

ARCHIVE_FILE_ENDING = ".7z"

def encrypt(source, destination):
    enc(source, destination, "test")


class BackupTests(unittest.TestCase):

    def get_destination_path(self, path):
        return os.path.abspath(os.path.join(self.destination, path))
    
    def destination_exists(self, path):
        os.path.exists(self.get_destination_path(path))

    def TestEmptyLeaf(self):
        encrypt(self.source, self.destination)
        self.assertFalse(self.destination_exists(self.dir1_3_empty))

    def TestLeafFiles(self):
        encrypt(self.source, self.destination)
        for leaf_file in self.leaf_files:
            # leaf file at destination
            file_path = os.path.join(self.destination, leaf_file)
            self.assertFalse(os.path.exists(file_path))
            self.assertFalse(os.path.exists(file_path + ARCHIVE_FILE_ENDING))
            folder_as_archive = os.path.dirname(os.path.abspath(leaf_file)) + ARCHIVE_FILE_ENDING
            # parent folder archive should exist
            self.assertTrue(os.path.exists(folder_as_archive))

    def TestLeafDirectories(self):
        encrypt(self.source, self.destination)
        for leaf_dir in self.leaf_directories:
            leaf_dir_archive = leaf_dir + ARCHIVE_FILE_ENDING
            if len(os.listdir(leaf_dir)) == 0:
                self.assertFalse(self.destination_exists(leaf_dir_archive))
                self.assertFalse(self.destination_exists(leaf_dir))
            else:
                self.assertTrue(self.destination_exists(leaf_dir_archive))
                self.assertFalse(self.destination_exists(leaf_dir))

    def setUp(self):
        self.generated_base = "generated_test_data"
        if os.path.exists(self.generated_base):
            shutil.rmtree(self.generated_base)

        self.source = os.path.join(self.generated_base, "source")
        self.dir1 = os.path.join(self.source, "Dir1")
        self.dir1_1 = os.path.join(self.dir1, "Dir1_1")
        self.dir1_1_1 = os.path.join(self.dir1, "Dir1_1_1")
        self.dir1_2 = os.path.join(self.dir1, "Dir1_1")
        self.dir1_3_empty = os.path.join(self.dir1, "Dir1_3_empty")
        self.dir2 = os.path.join(self.source, "Dir2")
        self.destination = os.path.join(self.source, "destination")

        subdirs = [
            self.source,
            self.dir1,
            self.dir1_1,
            self.dir1_1_1,
            self.dir1_2,
            self.dir1_3_empty,
            self.dir2,
            self.destination,
        ]

        self.leaf_directories = [
            self.dir1_1_1,
            self.dir1_2,
            self.dir1_3_empty,
            self.dir2,
        ]

        for subdir in subdirs:
            os.makedirs(subdir, exist_ok=True)

        self.f1 = os.path.join(self.source, "F1.txt")
        self.f1_1 = os.path.join(self.dir1, "F1_1.txt")
        self.f1_1_1 = os.path.join(self.dir1_1, "F1_1_1.txt")
        self.f1_1_2 = os.path.join(self.dir1_1, "F1_1_2.txt")

        self.f1_1_1_1 = os.path.join(self.dir1_1_1, "F1_1_1_1.txt")
        self.f1_1_1_2 = os.path.join(self.dir1_1_1, "F1_1_1_2.txt")

        self.f1_2_1 = os.path.join(self.dir1_2, "F1_2_1.txt")

        self.f2 = os.path.join(self.source, "F2.txt")
        self.f2_1 = os.path.join(self.dir2, "F2_1.txt")
        self.f2_2 = os.path.join(self.dir2, "F2_2.txt")

        self.f3 = os.path.join(self.source, "F3.txt")

        files = [
            self.f1,
            self.f1_1,
            self.f1_1_1,
            self.f1_1_2,
            self.f1_1_1_1,
            self.f1_1_1_2,
            self.f1_2_1,
            self.f2,
            self.f3,
        ]
        self.leaf_files = [
            self.f1_1_1_1,
            self.f1_1_1_2,
            self.f1_2_1,
            self.f2_1,
            self.f2_2,
        ]

        for file in files:
            with open(file, "w") as f:
                f.write(os.path.basename(file))
        return super().setUp()

    def tearDown(self):
        shutil.rmtree(self.generated_base)
        return super().tearDown()
