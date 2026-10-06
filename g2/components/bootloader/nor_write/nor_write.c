/* SPDX-License-Identifier: MIT
 * Source candidates for stock MX25U25643G program/sector-erase and adjacent
 * write-enable/write-disable entries. Lower setup, timing, status-poll and
 * MSPI/HAL services remain explicit providers from nor_read/runtime_helpers.
 */
#include "nor_write.h"
#include "../nor_commands/nor_commands.h"
#include "../nor_read/runtime_helpers.h"
#include <stddef.h>

#define ACTIVE_HANDLE_SLOT UINT32_C(0x200270dc)
#define ADDRESS_LIMIT      UINT32_C(0x02000000)
#define PAGE_SIZE          UINT32_C(0x100)
#define SECTOR_SIZE        UINT32_C(0x1000)
#define DRIVER_MODULE      UINT32_C(0x00433cd8)

enum {
    STATUS_INVALID_HANDLE = 2,
    STATUS_OUT_OF_RANGE = 5,
    STATUS_INVALID_ARGUMENT = 6,
    MX25_PAGE_PROGRAM = 0x02,
    MX25_SECTOR_ERASE = 0x20,
    MX25_WRITE_ENABLE = 0x06,
    MX25_WRITE_DISABLE = 0x04
};

extern void opencfw_bl_printf(const char *format, ...);
extern void opencfw_bl_log(uint32_t level, const char *module,
    const char *file, const char *function, uint32_t line,
    const char *format, ...);

static const char log_module[] = "drv.norflash";
static const char log_file[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\driver\\flash\\drv_mx25u25643g.c";
static const char wren_function[] = "mx25u25643g_enable_write_enable";
static const char wrdi_function[] = "mx25u25643g_enable_write_disable";
static const char wren_failure[] = "Write enable failed before sector erase\n";
static const char wrdi_failure[] = "Write enable failed before sector erase\n";
static const char erase_before_timeout[] =
    "SE wait_idle(before WREN) timeout: addr=0x%08X\n";
static const char erase_wren_failure[] =
    "SE write_enable failed: addr=0x%08X, st=%d\n";
static const char erase_command_failure[] =
    "SE erase command failed: addr=0x%08X, st=%d\n";
static const char erase_after_timeout[] =
    "SE wait_idle(after erase) timeout: addr=0x%08X\n";
static const char erase_wrdi_failure[] =
    "SE write_disable failed: addr=0x%08X, st=%d\n";
static const char program_invalid_args[] =
    "PP invalid arg: handle=%p, buf=%p, len=%u\n";
static const char program_out_of_range[] =
    "PP out of range: addr=0x%08X, total=0x%08X\n";
static const char program_before_timeout[] =
    "PP wait_idle(before WREN) timeout: addr=0x%08X, len=%u\n";
static const char program_wren_failure[] =
    "PP write_enable failed: addr=0x%08X, len=%u, st=%d\n";
static const char program_command_failure[] =
    "PP program failed: addr=0x%08X, len=%u, st=%d\n";
static const char program_after_timeout[] =
    "PP wait_idle(after PP) timeout: addr=0x%08X, len=%u\n";
static const char program_wrdi_failure[] =
    "PP write_disable failed: addr=0x%08X, len=%u, st=%d\n";

static uint32_t active_handle(void) {
    return *(volatile const uint32_t *)(uintptr_t)ACTIVE_HANDLE_SLOT;
}

uint32_t opencfw_provider_420984(void) {
    uint32_t status = opencfw_provider_42069e(
        MX25_WRITE_ENABLE, 0u, 0u, NULL, 0u);
    if (status != 0u) {
        opencfw_bl_log(1u, log_module, log_file, wren_function,
            0x3f2u, wren_failure);
    }
    return status;
}

uint32_t opencfw_provider_4209c4(void) {
    uint32_t status = opencfw_provider_42069e(
        MX25_WRITE_DISABLE, 0u, 0u, NULL, 0u);
    if (status != 0u) {
        opencfw_bl_log(2u, log_module, log_file, wrdi_function,
            0x3feu, wrdi_failure);
    }
    return status;
}

uint32_t opencfw_provider_420b0c(uint32_t address, const void *source,
                                uint32_t length) {
    uint32_t status = 0u;
    const uint32_t handle = active_handle();
    if (handle == 0u || source == NULL || length == 0u) {
        opencfw_bl_printf(program_invalid_args, handle, source, length);
        return STATUS_INVALID_ARGUMENT;
    }
    if (address >= ADDRESS_LIMIT) {
        opencfw_bl_printf(program_out_of_range, address, ADDRESS_LIMIT);
        return STATUS_OUT_OF_RANGE;
    }

    opencfw_bl_nor_read_before();
    opencfw_provider_420f10();

    uint32_t remaining = length;
    uint32_t page_offset = address & (PAGE_SIZE - 1u);
    const uint8_t *cursor = (const uint8_t *)source;
    while (remaining != 0u) {
        uint32_t count = PAGE_SIZE - page_offset;
        if (count > remaining) count = remaining;

        status = opencfw_bl_nor_read_delay();
        if (status != 0u) {
            opencfw_bl_printf(program_before_timeout, address, count);
            status = 4u;
            break;
        }

        status = opencfw_provider_420984();
        if (status != 0u) {
            opencfw_bl_printf(program_wren_failure, address, count, status);
            break;
        }

        status = opencfw_provider_42069e(MX25_PAGE_PROGRAM,
            address, 1u, (void *)cursor, count);
        if (status != 0u) {
            opencfw_bl_printf(program_command_failure, address, count, status);
            break;
        }

        status = opencfw_bl_nor_wait(10u);
        if (status != 0u) {
            opencfw_bl_printf(program_after_timeout, address, count);
            status = 4u;
            break;
        }

        status = opencfw_provider_4209c4();
        if (status != 0u) {
            opencfw_bl_printf(program_wrdi_failure, address, count, status);
            break;
        }

        remaining -= count;
        address += count;
        cursor += count;
        page_offset = 0u;
    }

    opencfw_bl_nor_read_configure(); /* stock restoration call at 0x420e8c */
    opencfw_bl_nor_read_after();
    return status;
}

uint32_t opencfw_provider_420a08(uint32_t address) {
    uint32_t status = 0u;
    if (active_handle() == 0u) return STATUS_INVALID_HANDLE;
    if ((address & (SECTOR_SIZE - 1u)) != 0u) {
        opencfw_bl_log(2u, log_module, log_file, "mx25u25643g_sector_erase",
            0x40eu, "Error: Address must be 4KB aligned\n");
        return STATUS_INVALID_ARGUMENT;
    }
    if (address >= ADDRESS_LIMIT) return STATUS_OUT_OF_RANGE;

    opencfw_bl_nor_read_before();
    opencfw_provider_420f10();

    status = opencfw_bl_nor_read_delay();
    if (status != 0u) {
        opencfw_bl_printf(erase_before_timeout, address);
        status = 3u;
        goto cleanup;
    }

    status = opencfw_provider_420984();
    if (status != 0u) {
        opencfw_bl_printf(erase_wren_failure, address, status);
        goto cleanup;
    }

    status = opencfw_provider_42069e(MX25_SECTOR_ERASE,
        address, 1u, NULL, 0u);
    if (status != 0u) {
        opencfw_bl_printf(erase_command_failure, address, status);
        goto cleanup;
    }

    status = opencfw_bl_nor_read_delay();
    if (status != 0u) {
        opencfw_bl_printf(erase_after_timeout, address);
        status = 4u;
        goto cleanup;
    }

    status = opencfw_provider_4209c4();
    if (status != 0u)
        opencfw_bl_printf(erase_wrdi_failure, address, status);

cleanup:
    opencfw_bl_nor_read_configure(); /* stock alias calls 0x420e8c */
    opencfw_bl_nor_read_after();
    return status;
}
