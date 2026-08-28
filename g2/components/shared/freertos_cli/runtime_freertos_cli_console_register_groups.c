/* SPDX-License-Identifier: MIT */

#include "runtime_freertos_cli_console.h"

#if defined(__clang__) || defined(__GNUC__)
#define OPEN_CFW_FREERTOS_CLI_CONSOLE_NOINLINE __attribute__((noinline))
#else
#define OPEN_CFW_FREERTOS_CLI_CONSOLE_NOINLINE
#endif

OPEN_CFW_FREERTOS_CLI_CONSOLE_NOINLINE
void open_cfw_freertos_cli_console_register_groups(void)
{
    open_cfw_retained_freertos_cli_register_group_57e626();
    open_cfw_retained_freertos_cli_register_group_57e810();
    open_cfw_retained_freertos_cli_register_group_57ff40();
    open_cfw_retained_freertos_cli_register_group_580392();
    open_cfw_retained_freertos_cli_register_group_5807c0();
    open_cfw_retained_freertos_cli_register_group_580c04();
    open_cfw_retained_freertos_cli_register_group_580fec();
    open_cfw_retained_freertos_cli_register_group_5810d8();
    open_cfw_retained_freertos_cli_register_group_581136();
    open_cfw_retained_freertos_cli_register_group_581644();
    open_cfw_retained_freertos_cli_register_group_58183a();
    open_cfw_retained_freertos_cli_register_group_581960();
    open_cfw_retained_freertos_cli_register_group_581d60();
    open_cfw_retained_freertos_cli_register_group_5827d0();
    open_cfw_retained_freertos_cli_register_group_5836b8();
    open_cfw_retained_freertos_cli_register_group_583cec();
    open_cfw_retained_freertos_cli_register_group_583f74();
    open_cfw_retained_freertos_cli_register_group_5840f4();
    open_cfw_retained_freertos_cli_register_group_5841ee();
    open_cfw_retained_freertos_cli_register_group_584320();
    open_cfw_retained_freertos_cli_register_group_584430();
    open_cfw_retained_freertos_cli_register_group_584702();
}

#undef OPEN_CFW_FREERTOS_CLI_CONSOLE_NOINLINE
