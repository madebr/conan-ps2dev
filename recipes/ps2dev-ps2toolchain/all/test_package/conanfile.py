from conans import ConanFile, tools
import os


class TestPackage(ConanFile):
    settings = "os", "arch", "compiler", "build_type"

    def build(self):
        if not tools.cross_building(self.settings, skip_x64_x86=True):
            self.run("ee-gcc -c '{}/ee.c' -o ee.o".format(self.source_folder), run_environment=True)
        if not tools.cross_building(self.settings, skip_x64_x86=True):
            self.run("iop-gcc -c '{}/iop.c' -o iop.o".format(self.source_folder), run_environment=True)

    def test(self):
        if not tools.cross_building(self.settings, skip_x64_x86=True):
            if not os.path.isfile("ee.o"):
                raise Exception("ee.o not created")
            if not os.path.isfile("iop.o"):
                raise Exception("iop.o not created")
