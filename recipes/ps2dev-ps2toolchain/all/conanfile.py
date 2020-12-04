from conans import AutoToolsBuildEnvironment, ConanFile, tools
from conans.errors import ConanInvalidConfiguration
import glob
import os


class Ps2devPs2ToolchainConan(ConanFile):
    name = "ps2dev-ps2toolchain"
    license = "GPL-2.0", "BSD-2-Clause"
    url = "https://www.github.com/conan-io/conan-center-index"
    description = "binutils+gcc+newlib toolchain for Sony(R) PlayStation 2"
    topics = "ps2", "toolchain", "binutils", "gcc", "newlib", "sony", "playstation", "ps2"
    settings = "os", "arch", "compiler", "build_type"

    exports_sources = "patches/*"

    def source(self):
        for sources in self.conan_data["sources"][self.version]:
            tools.get(**sources)
        tools.rename(glob.glob("ps2toolchain-*")[0], "ps2toolchain")
        tools.rename(glob.glob("binutils-*")[0], "binutils")
        tools.rename(glob.glob("gcc-*")[0], "gcc")
        tools.rename(glob.glob("newlib-*")[0], "newlib")

    def build_requirements(self):
        if tools.os_info.is_windows and not tools.get_env("CONAN_BASH_PATH"):
            self.build_requires("msys2/20200517")

    def package_id(self):
        del self.info.settings.compiler

    @property
    def _ps2toolchain_path(self):
        return os.path.join(self.package_folder, "bin")

    def _build_install_binutils(self, target):
        autotools = AutoToolsBuildEnvironment(self, win_bash=tools.os_info.is_windows)
        conf_args = [
            "--prefix={}".format(os.path.join(self._ps2toolchain_path, target).replace("\\", "/")),
            "--disable-build-warnings",
            "--target={}".format(target),
        ]
        autotools.flags.extend(["-DSTDC_HEADERS", "-D_FORTIFY_SOURCE=0"])

        host = tools.get_gnu_triplet(str(self.settings.os), str(self.settings.arch), str(self.settings.compiler))
        build = tools.get_gnu_triplet(tools.detected_os(), tools.detected_architecture(), "gcc")
        if tools.os_info.is_windows:
            build = "{}-w64-mingw32".format({
                "x86": "i686",
            }.get(str(tools.detected_architecture()), str(tools.detected_architecture())))
        if self.settings.os == "Windows":
            host = "{}-w64-mingw32".format({
                "x86": "i686",
            }.get(str(self.settings.arch), str(self.settings.arch)))

        build_folder = os.path.join("build_binutils_{}".format(target))
        tools.mkdir(build_folder)
        with tools.chdir(build_folder):
            self.output.info("Building binutils for target={}".format(target))
            autotools.configure(args=conf_args, configure_dir=os.path.join(self.build_folder, "binutils"), build=build, host=host)
            autotools.make()
            autotools.install()

    def _build_install_gcc(self, target, stage):
        autotools = AutoToolsBuildEnvironment(self, win_bash=tools.os_info.is_windows)
        conf_args = [
            "--prefix={}".format(os.path.join(self._ps2toolchain_path, target).replace("\\", "/")),
            "--disable-build-warnings",
            "--target={}".format(target),
            "--with-newlib",
        ]
        env = {}
        if stage == 1:
            conf_args.extend([
                "--enable-languages=c",
                "--without-headers",
            ])
        else:
            conf_args.extend([
                "--enable-languages=c,c++",
                "--with-headers={}".format(tools.unix_path(os.path.join(self._ps2toolchain_path, target, target, "include"))),
            ])
            ff = lambda a: not a.startswith("-m")
            env.update({
                "CFLAGS_FOR_BUILD": " ".join(autotools.flags),
                "CXXFLAGS_FOR_BUILD": " ".join(autotools.cxx_flags),
                "LDFLAGS_FOR_BUILD": " ".join(autotools.link_flags),
                "CFLAGS_FOR_TARGET": " ".join(filter(ff, autotools.flags)),
                "CXXFLAGS_FOR_TARGET": " ".join(filter(ff, autotools.cxx_flags)),
                "LDFLAGS_FOR_TARGET": " ".join(filter(ff, autotools.link_flags)),
            })
            autotools.flags = []
            autotools.cxx_flags = []
            autotools.link_flags = []

        autotools.flags.append("-DSTDC_HEADERS")

        host = tools.get_gnu_triplet(str(self.settings.os), str(self.settings.arch), str(self.settings.compiler))
        build =  tools.get_gnu_triplet(tools.detected_os(), tools.detected_architecture())
        if tools.os_info.is_windows:
            build = "{}-w64-mingw32".format({
                "x86": "i686"
            }.get(str(tools.detected_architecture()), str(tools.detected_architecture())))
        if self.settings.os == "Windows":
            host = "{}-w64-mingw32".format({
                "x86": "i686"
            }.get(str(self.settings.arch), str(self.settings.arch)))

        # Apple needs to pretend to be linux
        if tools.os_info.is_macos:
            build = "{}-linux-gnu".format({
                "x86": "i686"
            }.get(str(tools.detected_architecture()), str(tools.detected_architecture())))
        if tools.is_apple_os(self.settings.os):
            host = "{}-linux-gnu".format({
                "x86": "i686"
            }.get(str(self.settings.arch), str(self.settings.arch)))

        build_folder = os.path.join("build_gcc_stage{}_{}".format(stage, target))
        tools.mkdir(build_folder)
        with tools.chdir(build_folder):
            with tools.environment_append(env):
                with tools.environment_append({"PATH": [os.path.join(self._ps2toolchain_path, target, "bin")]}):
                    self.output.info("Building gcc stage1 for target={}".format(target))
                    autotools.configure(args=conf_args, configure_dir=os.path.join(self.build_folder, "gcc"), build=build, host=host)
                    autotools.make()
                    autotools.install()

    def _build_install_newlib(self, target):
        ff = lambda a: not a.startswith("-m")
        autotools = AutoToolsBuildEnvironment(self, win_bash=tools.os_info.is_windows)
        conf_args = [
            "--prefix={}".format(os.path.join(self._ps2toolchain_path, target).replace("\\", "/")),
            "--target={}".format(target),
        ]

        autotools.flags = list(filter(ff, autotools.flags))
        autotools.cxx_flags = list(filter(ff, autotools.cxx_flags))
        autotools.link_flags = list(filter(ff, autotools.link_flags))

        host = tools.get_gnu_triplet(str(self.settings.os), str(self.settings.arch), str(self.settings.compiler))
        build =  tools.get_gnu_triplet(tools.detected_os(), tools.detected_architecture())
        if tools.os_info.is_windows:
            build = "{}-w64-mingw32".format({
                "x86": "i686"
            }.get(str(self.settings.arch), str(self.settings.arch)))
        if self.settings.os == "Windows":
            host = "{}-w64-mingw32".format({
                "x86": "i686"
            }.get(str(self.settings.arch), str(self.settings.arch)))

        env = {
            "PATH": [os.path.join(self._ps2toolchain_path, target, "bin")],
            "CPPFLAGS_FOR_TARGET": "-G0",
        }

        self.output.info("env={}".format(env))

        build_folder = os.path.join("build_newlib_{}".format(target))
        tools.mkdir(build_folder)
        with tools.chdir(build_folder):
            with tools.environment_append(env):
                self.output.info("Building newlib for target={}".format(target))
                autotools.configure(args=conf_args, configure_dir=os.path.join(self.build_folder, "newlib"), build=build, host=host)
                autotools.make(args=["-j1"])
                autotools.install()

    def build(self):
        if tools.cross_building(self.settings, skip_x64_x86=True):
            raise ConanInvalidConfiguration("This recipe does not support cross building")

        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)

        for target in ("ee", "iop", "dvp"):
            self._build_install_binutils(target)
        for target in ("ee", "iop"):
            self._build_install_gcc(target, 1)
        self._build_install_newlib("ee")
        self._build_install_gcc("ee", 2)

    def package(self):
        self.copy("LICENSE", src="ps2toolchain", dst=os.path.join("licenses", "ps2toolchain"))
        self.copy("COPYING", src="binutils", dst=os.path.join("licenses", "binutils"))
        self.copy("COPYING", src="gcc", dst=os.path.join("licenses", "gcc"))
        self.copy("COPYING", src="newlib", dst=os.path.join("licenses", "newlib"))
        if not os.path.isdir(os.path.join(self.package_folder, "bin")):
            raise Exception("This recipe does not support the '-kb' option of 'conan create'")
        for target in ("ee", "iop", "dvp"):
            tools.rmdir(os.path.join(self._ps2toolchain_path, target, "info"))
            tools.rmdir(os.path.join(self._ps2toolchain_path, target, "man"))
            tools.rmdir(os.path.join(self._ps2toolchain_path, target, "share"))
            tools.remove_files_by_mask(os.path.join(self.package_folder, "bin", target, target, "lib"), "*.la")

    def package_info(self):
        for target in ("ee", "iop", "dvp"):
            bin_path = os.path.join(self._ps2toolchain_path, target, "bin")
            self.output.info("Extending PATH environment variable: {}".format(bin_path))
            self.env_info.PATH.append(bin_path)

        ps2dev = self._ps2toolchain_path
        self.output.info("Settings PS2DEV environment variable: {}".format(ps2dev))
        self.env_info.PS2DEV = ps2dev
        self.user_info.PS2DEV = ps2dev
