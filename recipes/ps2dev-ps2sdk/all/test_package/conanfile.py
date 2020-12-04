from conans import CMake, ConanFile, tools
import os


class TestPackage(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    generators = "cmake"

    def build(self):
        with tools.environment_append({"PS2SDK": self.deps_user_info["ps2dev-ps2sdk"].PS2SDK}):
            cmake = CMake(self)
            cmake.verbose = True

            cmake.definitions["CMAKE_TOOLCHAIN_FILE"] = os.path.join(self.source_folder, "ee-toolchain.cmake").replace("\\", "/")
            cmake.configure()
            cmake.build()

    def test(self):
        pass
