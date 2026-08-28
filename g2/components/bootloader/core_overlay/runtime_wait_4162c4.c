/* SPDX-License-Identifier: MIT */

typedef unsigned int open_cfw_bootloader_u32;

#ifndef OPEN_CFW_BOOTLOADER_CRITICAL_CONTEXT
extern open_cfw_bootloader_u32 open_cfw_bootloader_critical_context(void);
#define OPEN_CFW_BOOTLOADER_CRITICAL_CONTEXT() \
    open_cfw_bootloader_critical_context()
#endif

#ifndef OPEN_CFW_BOOTLOADER_RUNTIME_TICK_41835A
extern open_cfw_bootloader_u32 open_cfw_bootloader_runtime_tick_41835a(void);
#define OPEN_CFW_BOOTLOADER_RUNTIME_TICK_41835A() \
    open_cfw_bootloader_runtime_tick_41835a()
#endif

#ifndef OPEN_CFW_BOOTLOADER_RUNTIME_WAIT_418DAC
extern int open_cfw_bootloader_runtime_wait_418dac(
    open_cfw_bootloader_u32 argument_0,
    open_cfw_bootloader_u32 argument_1,
    open_cfw_bootloader_u32 clear_mask,
    open_cfw_bootloader_u32 *observed,
    open_cfw_bootloader_u32 timeout
);
#define OPEN_CFW_BOOTLOADER_RUNTIME_WAIT_418DAC(...) \
    open_cfw_bootloader_runtime_wait_418dac(__VA_ARGS__)
#endif

__attribute__((used, noinline))
int open_cfw_bootloader_runtime_wait_4162c4(
    open_cfw_bootloader_u32 mask,
    open_cfw_bootloader_u32 options,
    open_cfw_bootloader_u32 timeout
)
{
    open_cfw_bootloader_u32 clear_mask;
    open_cfw_bootloader_u32 remaining = timeout;
    open_cfw_bootloader_u32 started;
    int result = 0;
    int status;

    if (OPEN_CFW_BOOTLOADER_CRITICAL_CONTEXT() != 0U) {
        return -6;
    }
    if ((int)mask < 0) {
        return -4;
    }

    clear_mask = (options & 2U) != 0U ? 0U : mask;
    started = OPEN_CFW_BOOTLOADER_RUNTIME_TICK_41835A();

    do {
        open_cfw_bootloader_u32 observed = 0U;

        status = OPEN_CFW_BOOTLOADER_RUNTIME_WAIT_418DAC(
            0U, 0U, clear_mask, &observed, remaining
        );
        if (status == 1) {
            result = (int)(((open_cfw_bootloader_u32)result & mask) | observed);
            if ((options & 1U) != 0U) {
                if (((open_cfw_bootloader_u32)result & mask) == mask) {
                    return result;
                }
            } else if (((open_cfw_bootloader_u32)result & mask) != 0U) {
                return result;
            }

            if (timeout == 0U) {
                return -3;
            }
            {
                open_cfw_bootloader_u32 elapsed =
                    OPEN_CFW_BOOTLOADER_RUNTIME_TICK_41835A() - started;
                remaining = timeout >= elapsed ? timeout - elapsed : 0U;
            }
        } else {
            result = timeout == 0U ? -3 : -2;
        }
    } while (status != 0);

    return result;
}
