from conans import ConanFile
import os

# FIXME: This is a workaround for setting CONAN_BASH_PATH


class Msys2WrapperConan(ConanFile):
    name = "msys2-wrapper"

    requires = "msys2/20200517"

    def package_info(self):
        self.env_info.CONAN_BASH_PATH = os.path.join(self.deps_env_info["msys2"].MSYS_BIN, "bash")
