cmake_minimum_required(VERSION 3.7)
list(APPEND CMAKE_MODULE_PATH "${CMAKE_CURRENT_LIST_DIR}")

set(CMAKE_SYSTEM_NAME PlayStation)
set(CMAKE_SYSTEM_PROCESSOR mipsel)

set(CMAKE_C_COMPILER ee-gcc)
set(CMAKE_CXX_COMPILER ee-gcc)
set(CMAKE_CXX_COMPILER ee-gcc)
set(CMAKE_STRIP ee-strip)
set(CMAKE_AR ee-ar)

set(CMAKE_EXECUTABLE_SUFFIX ".elf")

set(CMAKE_AS_FLAGS_INIT "-G0")
set(CMAKE_C_FLAGS_INIT "-G0")
set(CMAKE_CXX_FLAGS_INIT "-G0")

set(CMAKE_EXE_LINKER_FLAGS_INIT "-L$ENV{PS2SDK}/ee/lib")
set(CMAKE_MODULE_LINKER_FLAGS_INIT "-L$ENV{PS2SDK}/ee/lib")
set(CMAKE_SHARED_LINKER_FLAGS_INIT "-L$ENV{PS2SDK}/ee/lib")

set(CMAKE_FIND_ROOT_PATH "${PS2DEV}/ee;${PS2SDK}/ee")
set(CMAKE_FIND_ROOT_PATH_MODE_PROGRAM NEVER)
set(CMAKE_FIND_ROOT_PATH_MODE_LIBRARY ONLY)
set(CMAKE_FIND_ROOT_PATH_MODE_INCLUDE ONLY)

set(PS2 1)
set(EE 1)

function(add_erl_executable TARGET)
    separate_arguments(cflags NATIVE_COMMAND "${CMAKE_C_FLAGS}")
    separate_arguments(linkflags NATIVE_COMMAND "${CMAKE_EXE_LINKER_FLAGS}")
    set(ofile "$<TARGET_FILE_DIR:${TARGET}>/${TARGET}.erl")
    add_custom_command(OUTPUT "${TARGET}.erl"
        COMMAND "${CMAKE_C_COMPILER}" -mno-crt0 -o "${ofile}" $<TARGET_OBJECTS:${TARGET}> ${cflags} ${linkflags} -Wl,-r -Wl,-d
        COMMAND "${CMAKE_STRIP}" --strip-unneeded -R .mdebug.eabi64 -R .reginfo -R .comment "${ofile}"
        DEPENDS ${TARGET}
    )
    add_custom_target(aa ALL
        DEPENDS "${TARGET}.erl"
    )
endfunction()
