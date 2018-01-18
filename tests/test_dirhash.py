import unittest
import dirhash
from uuid import uuid4
from tempfile import TemporaryDirectory
from os.path import join
from os import scandir
from shutil import copytree


class Tests(unittest.TestCase):
    def setUp(self):
        # Perform any setup that should occur
        # before every test
        pass

    def tearDown(self):
        # Perform any tear down that should
        # occur after every test
        pass

    def testPass(self):
        self.assertEqual(True, True)

    def testVersionAvailable(self):
        x = getattr(dirhash, "__version__", None)
        self.assertTrue(x is not None)

    def testSame(self):
        with TemporaryDirectory() as containing_dir:
            dir1 = TemporaryDirectory(dir=containing_dir)
            dir2 = TemporaryDirectory(dir=containing_dir)
            # Create two directories with the same contents but different file names
            for x in range(10):
                with open(join(dir1.name, uuid4().hex), 'w') as f:
                    f.write(uuid4().hex)
            for x in scandir(dir1.name):
                with open(x.path) as src:
                    with open(join(dir2.name, uuid4().hex), 'w') as dst:
                        dst.write(src.read())
            # Check that they're equal
            h1 = dirhash.hash_dir(dir1.name)[0].hexdigest()
            h2 = dirhash.hash_dir(dir2.name)[0].hexdigest()
            self.assertEqual(h1, h2)

    def testDifferent(self):
        with TemporaryDirectory() as containing_dir:
            dir1 = TemporaryDirectory(dir=containing_dir)
            dir2 = TemporaryDirectory(dir=containing_dir)
            # Create two directories with the different contents and different file names
            for x in range(10):
                with open(join(dir1.name, uuid4().hex), 'w') as f:
                    f.write(uuid4().hex)
            for x in scandir(dir1.name):
                with open(join(dir1.name, uuid4().hex), 'w') as f:
                    f.write(uuid4().hex)
            # Check that they're not equal
            h1 = dirhash.hash_dir(dir1.name)[0].hexdigest()
            h2 = dirhash.hash_dir(dir2.name)[0].hexdigest()
            self.assertNotEqual(h1, h2)

    def testRecursionSame(self):
        with TemporaryDirectory() as containing_dir:
            dir1 = TemporaryDirectory(dir=containing_dir)
            dir11 = TemporaryDirectory(dir=dir1.name)
            for x in range(10):
                with open(join(dir1.name, uuid4().hex), 'w') as f:
                    f.write(uuid4().hex)
            for x in range(10):
                with open(join(dir11.name, uuid4().hex), 'w') as f:
                    f.write(uuid4().hex)
            dir2name = join(containing_dir, uuid4().hex)
            copytree(dir1.name, dir2name)
            h1 = dirhash.hash_dir(dir1.name)[0].hexdigest()
            h2 = dirhash.hash_dir(dir2name)[0].hexdigest()
            self.assertEqual(h1, h2)

    def testRecursionDifferent(self):
        with TemporaryDirectory() as containing_dir:
            dir1 = TemporaryDirectory(dir=containing_dir)
            dir11 = TemporaryDirectory(dir=dir1.name)
            for x in range(10):
                with open(join(dir1.name, uuid4().hex), 'w') as f:
                    f.write(uuid4().hex)
            for x in range(10):
                with open(join(dir11.name, uuid4().hex), 'w') as f:
                    f.write(uuid4().hex)
            dir2name = join(containing_dir, uuid4().hex)
            copytree(dir1.name, dir2name)
            # Add another file to the subdir in dir2
            with open(join(dir2name, dir11.name, uuid4().hex), 'w') as f:
                f.write(uuid4().hex)
            h1 = dirhash.hash_dir(dir1.name)[0].hexdigest()
            h2 = dirhash.hash_dir(dir2name)[0].hexdigest()
            self.assertNotEqual(h1, h2)


if __name__ == "__main__":
    unittest.main()
