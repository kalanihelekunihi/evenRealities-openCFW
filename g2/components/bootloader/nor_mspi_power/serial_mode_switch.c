/* SPDX-License-Identifier: MIT
 * Source reconstruction of locked NOR status-register mode switch 0x420c5c.
 * Transfer, WREN, delay, and logging remain separate providers.
 */
#include "serial_mode_switch.h"

#include <stdint.h>

#define ACTIVE_HANDLE_SLOT UINT32_C(0x200270dc)

extern uint32_t opencfw_provider_4205f4(uint32_t instruction,
    uint32_t address, uint32_t send_address, void *buffer, uint32_t length);
extern uint32_t opencfw_provider_42069e(uint32_t instruction,
    uint32_t address, uint32_t send_address, void *buffer, uint32_t length);
extern uint32_t opencfw_provider_420984(void);
extern uint32_t opencfw_bl_nor_read_delay(void);
extern void opencfw_bl_log(uint32_t level, const char *module,
    const char *file, const char *function, uint32_t line,
    const char *format, ...);

static const char log_module[] = "drv.norflash";
static const char log_file[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\driver\\flash\\drv_mx25u25643g.c";
static const char log_function[] = "mx25u25643g_quad_enable";
static const char status_read_failed[] = "Failed to read status register 2\n";
static const char mode_already_set[] = "QE bit already in desired state\n";
static const char write_enable_failed[] = "Write enable failed before setting QE\n";
static const char status_write_failed[] = "Failed to write status register 2\n";
static const char verify_failed[] = "Failed to verify QE bit\n";
static const char mode_failed_format[] = "Failed to %s QE bit\n";
static const char set_mode[] = "set";
static const char clear_mode[] = "clear";

static void log_line(uint32_t line, const char *message)
{
    opencfw_bl_log(2u, log_module, log_file, log_function, line, message);
}

uint32_t opencfw_provider_420c5c(uint32_t mode)
{
    volatile const uint32_t *const active_handle =
        (volatile const uint32_t *)(uintptr_t)ACTIVE_HANDLE_SLOT;
    uint8_t status[4] = {0u, 0u, 0u, 0u};
    uint32_t result;
    const uint8_t mode_byte = (uint8_t)mode;

    if (*active_handle == 0u)
        return 2u;

    (void)opencfw_bl_nor_read_delay();
    result = opencfw_provider_4205f4(5u, 0u, 0u, status, 1u);
    if (result != 0u) {
        log_line(0x521u, status_read_failed);
        return result;
    }

    if (((status[0] >> 6) & 1u) == mode_byte && (status[0] & 0x3cu) == 0u) {
        log_line(0x52au, mode_already_set);
        return 0u;
    }

    result = opencfw_provider_420984();
    if (result != 0u) {
        log_line(0x531u, write_enable_failed);
        return result;
    }

    if (mode_byte == 0u)
        status[0] &= 0xbfu;
    else
        status[0] |= 0x40u;
    status[0] &= 0xc3u;

    result = opencfw_provider_42069e(1u, 0u, 0u, status, 1u);
    if (result != 0u) {
        log_line(0x540u, status_write_failed);
        return result;
    }

    (void)opencfw_bl_nor_read_delay();
    result = opencfw_provider_4205f4(5u, 0u, 0u, status, 1u);
    if (result != 0u) {
        log_line(0x54au, verify_failed);
        return result;
    }

    if (((status[0] >> 6) & 1u) == mode_byte)
        return 0u;

    opencfw_bl_log(2u, log_module, log_file, log_function, 0x550u,
        mode_failed_format, mode_byte != 0u ? set_mode : clear_mode);
    return 1u;
}
