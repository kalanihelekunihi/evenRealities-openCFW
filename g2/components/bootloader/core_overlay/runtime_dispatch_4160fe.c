/* SPDX-License-Identifier: MIT */

typedef unsigned int open_cfw_bootloader_u32;

struct open_cfw_bootloader_runtime_4160fe_options {
    open_cfw_bootloader_u32 argument_1;
    unsigned char flags;
    unsigned char reserved_05[3];
    open_cfw_bootloader_u32 path_a_argument_6;
    open_cfw_bootloader_u32 path_a_minimum;
    open_cfw_bootloader_u32 path_a_argument_5;
    open_cfw_bootloader_u32 scaled_argument_2;
    open_cfw_bootloader_u32 argument_4;
};

#ifndef OPEN_CFW_BOOTLOADER_CRITICAL_CONTEXT
extern open_cfw_bootloader_u32 open_cfw_bootloader_critical_context(void);
#define OPEN_CFW_BOOTLOADER_CRITICAL_CONTEXT() \
    open_cfw_bootloader_critical_context()
#endif

#ifndef OPEN_CFW_BOOTLOADER_RUNTIME_4160FE_PATH_A
extern open_cfw_bootloader_u32 open_cfw_bootloader_runtime_4160fe_path_a(
    open_cfw_bootloader_u32 argument_0,
    open_cfw_bootloader_u32 argument_1,
    open_cfw_bootloader_u32 argument_2,
    open_cfw_bootloader_u32 argument_3,
    open_cfw_bootloader_u32 argument_4,
    open_cfw_bootloader_u32 argument_5,
    open_cfw_bootloader_u32 argument_6
);
#define OPEN_CFW_BOOTLOADER_RUNTIME_4160FE_PATH_A(...) \
    open_cfw_bootloader_runtime_4160fe_path_a(__VA_ARGS__)
#endif

#ifndef OPEN_CFW_BOOTLOADER_RUNTIME_4160FE_PATH_B
extern int open_cfw_bootloader_runtime_4160fe_path_b(
    open_cfw_bootloader_u32 argument_0,
    open_cfw_bootloader_u32 argument_1,
    unsigned short argument_2,
    open_cfw_bootloader_u32 argument_3,
    open_cfw_bootloader_u32 argument_4,
    open_cfw_bootloader_u32 *result
);
#define OPEN_CFW_BOOTLOADER_RUNTIME_4160FE_PATH_B(...) \
    open_cfw_bootloader_runtime_4160fe_path_b(__VA_ARGS__)
#endif

__attribute__((used, noinline))
open_cfw_bootloader_u32 open_cfw_bootloader_runtime_dispatch_4160fe(
    open_cfw_bootloader_u32 argument_0,
    open_cfw_bootloader_u32 argument_3,
    const struct open_cfw_bootloader_runtime_4160fe_options *options
)
{
    open_cfw_bootloader_u32 result = 0U;
    open_cfw_bootloader_u32 argument_1 = 0U;
    open_cfw_bootloader_u32 argument_2 = 0x100U;
    open_cfw_bootloader_u32 argument_4 = 0x18U;
    int path = 0;

    if (OPEN_CFW_BOOTLOADER_CRITICAL_CONTEXT() != 0U || argument_0 == 0U) {
        return 0U;
    }

    if (options != (const struct open_cfw_bootloader_runtime_4160fe_options *)0) {
        if (options->argument_1 != 0U) {
            argument_1 = options->argument_1;
        }
        if (options->argument_4 != 0U) {
            argument_4 = options->argument_4;
        }
        if (argument_4 == 0U || argument_4 >= 0x39U ||
                (options->flags & 1U) == 0U) {
            return 0U;
        }
        if (options->scaled_argument_2 != 0U) {
            argument_2 = options->scaled_argument_2 >> 2;
        }

        if (options->path_a_argument_6 != 0U &&
                options->path_a_minimum >= 0x70U &&
                options->path_a_argument_5 != 0U &&
                options->scaled_argument_2 != 0U) {
            path = 1;
        } else if (options->path_a_argument_6 != 0U ||
                options->path_a_minimum != 0U ||
                options->path_a_argument_5 != 0U) {
            path = -1;
        }
    }

    if (path == 1) {
        return OPEN_CFW_BOOTLOADER_RUNTIME_4160FE_PATH_A(
            argument_0,
            argument_1,
            argument_2,
            argument_3,
            argument_4,
            options->path_a_argument_5,
            options->path_a_argument_6
        );
    }
    if (path != 0) {
        return 0U;
    }
    if (OPEN_CFW_BOOTLOADER_RUNTIME_4160FE_PATH_B(
            argument_0,
            argument_1,
            (unsigned short)argument_2,
            argument_3,
            argument_4,
            &result
        ) != 1) {
        return 0U;
    }
    return result;
}
