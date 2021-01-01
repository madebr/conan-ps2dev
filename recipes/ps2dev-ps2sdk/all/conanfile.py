from conans import AutoToolsBuildEnvironment, ConanFile, tools
from conans.errors import ConanInvalidConfiguration
import glob
import os


class Ps2devPs2sdkdevConan(ConanFile):
    name = "ps2dev-ps2sdk"
    license = "AFL-2.0"
    url = "https://www.github.com/madebr/conan-ps2dev"
    description = "PS2SDK is a collection of Open Source libraries used for developing applications on Sony's PlayStation 2 (PS2)."
    topics = "ps2", "sdk", "library", "sony", "playstation", "ps2"
    settings = "os", "arch", "compiler"

    _make_args = None
    _autotools = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def configure(self):
        if self.settings.os != "Playstation2":
            raise ConanInvalidConfiguration("ps2dev-ps2sdk can only be built for playstation2")
        if self.settings.arch != "mips":
            raise ConanInvalidConfiguration("ps2dev-ps2sdk can only be built for the mips processor")
        if self.settings.compiler != "gcc":
            raise ConanInvalidConfiguration("ps2dev-ps2sdk can only be built using the gcc compiler")

    def build_requirements(self):
        if tools.os_info.is_windows and not tools.get_env("CONAN_BASH_PATH"):
            self.build_requires("msys2/20200517")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename(glob.glob("ps2sdk-*")[0], self._source_subfolder)

    @property
    def _ps2sdk_path(self):
        return os.path.join(self.package_folder).replace("\\", "/")

    def _configure_autotools_args(self):
        if self._autotools:
            return self._autotools, self._make_args
        self._autotools = AutoToolsBuildEnvironment(self, win_bash=tools.os_info.is_windows)
        self._make_args = [
            "PS2SDK={}".format(self._ps2sdk_path),
            "-j1",
        ]
        return self._autotools, self._make_args

    def build(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)
        autotools, make_args = self._configure_autotools_args()
        with tools.chdir(self._source_subfolder):
            with tools.environment_append(autotools.vars):
                autotools.make(args=make_args)

    def package(self):
        self.copy("LICENSE", src=self._source_subfolder, dst="licenses")
        autotools, make_args = self._configure_autotools_args()
        with tools.chdir(self._source_subfolder):
            with tools.environment_append(autotools.vars):
                autotools.install(args=make_args)

        for libdir in self._rel_libdirs:
            tools.remove_files_by_mask(os.path.join(self.package_folder, libdir), "*.erl")

        tools.rmdir(os.path.join(self._ps2sdk_path, "samples"))
        tools.rmdir(os.path.join(self._ps2sdk_path, "ports"))

    def package_id(self):
        del self.info.settings.compiler

    @property
    def _rel_libdirs(self):
        return [
            os.path.join(self._ps2sdk_path, "ee", "lib"),
            os.path.join(self._ps2sdk_path, "iop", "lib"),
        ]

    @property
    def _linker_flags(self):
        return " ".join("-L{}".format(os.path.join(self.package_folder, lib).replace("\\", "/")) for lib in self._rel_libdirs)

    def package_info(self):
        self.cpp_info.includedirs = [
            os.path.join(self._ps2sdk_path, "common", "include"),
            os.path.join(self._ps2sdk_path, "ee", "include"),
            os.path.join(self._ps2sdk_path, "iop", "include"),
        ]

        ps2sdk = self._ps2sdk_path
        self.output.info("Settings PS2SDK environment variable: {}".format(ps2sdk))
        self.env_info.PS2SDK = ps2sdk
        self.user_info.PS2SDK = ps2sdk

        self.user_info.link_flags = self._linker_flags
