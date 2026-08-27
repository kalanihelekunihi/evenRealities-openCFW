/* SPDX-License-Identifier: GPL-3.0-or-later */

typedef unsigned int open_cfw_bootloader_u32;

#ifndef OPEN_CFW_BOOTLOADER_CRITICAL_CONTEXT
extern open_cfw_bootloader_u32 open_cfw_bootloader_critical_context(void);
#define OPEN_CFW_BOOTLOADER_CRITICAL_CONTEXT() \
    open_cfw_bootloader_critical_context()
#endif

#ifndef OPEN_CFW_BOOTLOADER_RUNTIME_TRANSFER_CRITICAL_418FE8
extern void open_cfw_bootloader_runtime_transfer_critical_418fe8(
    open_cfw_bootloader_u32 argument_0,
    open_cfw_bootloader_u32 argument_1,
    int argument_2,
    open_cfw_bootloader_u32 argument_3,
    int *result,
    open_cfw_bootloader_u32 *schedule_required
);
#define OPEN_CFW_BOOTLOADER_RUNTIME_TRANSFER_CRITICAL_418FE8(...) \
    open_cfw_bootloader_runtime_transfer_critical_418fe8(__VA_ARGS__)
#endif

#ifndef OPEN_CFW_BOOTLOADER_RUNTIME_TRANSFER_NORMAL_418E70
extern void open_cfw_bootloader_runtime_transfer_normal_418e70(
    open_cfw_bootloader_u32 argument_0,
    open_cfw_bootloader_u32 argument_1,
    int argument_2,
    open_cfw_bootloader_u32 argument_3,
    int *result
);
#define OPEN_CFW_BOOTLOADER_RUNTIME_TRANSFER_NORMAL_418E70(...) \
    open_cfw_bootloader_runtime_transfer_normal_418e70(__VA_ARGS__)
#endif

#ifndef OPEN_CFW_BOOTLOADER_PENDSV_SET
#define OPEN_CFW_BOOTLOADER_PENDSV_SET() \
    (*(volatile open_cfw_bootloader_u32 *)0xE000ED04U = 0x10000000U)
#endif

__attribute__((used, noinline))
int open_cfw_bootloader_runtime_transfer_41623a(
    open_cfw_bootloader_u32 argument_0,
    int argument_1
)
{
    int result = -1;

    if (argument_0 == 0U || argument_1 < 0) {
        return -4;
    }

    if (OPEN_CFW_BOOTLOADER_CRITICAL_CONTEXT() != 0U) {
        open_cfw_bootloader_u32 schedule_required = 0U;

        OPEN_CFW_BOOTLOADER_RUNTIME_TRANSFER_CRITICAL_418FE8(
            argument_0, 0U, argument_1, 1U, (int *)0, &schedule_required
        );
        OPEN_CFW_BOOTLOADER_RUNTIME_TRANSFER_CRITICAL_418FE8(
            argument_0, 0U, 0, 0U, &result,
            (open_cfw_bootloader_u32 *)0
        );
        if (schedule_required != 0U) {
            OPEN_CFW_BOOTLOADER_PENDSV_SET();
        }
    } else {
        OPEN_CFW_BOOTLOADER_RUNTIME_TRANSFER_NORMAL_418E70(
            argument_0, 0U, argument_1, 1U, (int *)0
        );
        OPEN_CFW_BOOTLOADER_RUNTIME_TRANSFER_NORMAL_418E70(
            argument_0, 0U, 0, 0U, &result
        );
    }

    return result;
}
