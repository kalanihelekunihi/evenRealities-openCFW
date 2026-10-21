/* SPDX-License-Identifier: MIT
 * Readable reconstruction of locked 0x420800/0x420890 NOR address-mode code.
 * Status, command, WREN/WRDI, delay, and logging are explicit providers.
 */
#include "xip_address_mode.h"

#include <stdint.h>

#define ACTIVE_HANDLE_SLOT UINT32_C(0x200270dc)

extern uint32_t opencfw_provider_4205f4(uint32_t instruction,
    uint32_t address, uint32_t send_address, void *buffer, uint32_t length);
extern uint32_t opencfw_provider_42069e(uint32_t instruction,
    uint32_t address, uint32_t send_address, void *buffer, uint32_t length);
extern uint32_t opencfw_provider_420984(void);
extern uint32_t opencfw_provider_4209c4(void);
extern uint32_t opencfw_bl_nor_read_delay(void);
extern void opencfw_bl_log(uint32_t level, const char *module,
    const char *file, const char *function, uint32_t line,
    const char *format, ...);

static const char log_module[] = "drv.norflash";
static const char log_file[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\driver\\flash\\drv_mx25u25643g.c";
static const char address_mode_function[] = "mx25u25643g_enter_4byte_mode";
static const char status_mode_function[] = "mx25u25643g_is_4byte_mode";
static const char busy_message[] = "Device is busy\n";
static const char mode_read_message[] = "Read 4byte mode failed\n";
static const char three_byte_message[] = "43G is 3byte device address mode\n";
static const char wren_message[] =
    "Write enable failed before entering 4-byte mode\n";
static const char enter_message[] = "Failed to enter 4-byte mode\n";
static const char verify_message[] = "Failed to verify 4-byte mode\n";
static const char wrdi_message[] = "exit write enable fail\n";

static void log_at(const char *function, uint32_t line, const char *message)
{
    opencfw_bl_log(2u, log_module, log_file, function, line, message);
}

__attribute__((noinline)) uint32_t opencfw_provider_420800(uint32_t unused0, uint32_t unused1,
                                uint32_t unused2, uint32_t unused3)
{
    uint8_t local[5] = {0u, 0u, 0u, 0u, 0u};
    uint32_t result;
    (void)unused0;
    (void)unused1;
    (void)unused2;
    (void)unused3;

    result = opencfw_provider_4205f4(0x15u, 0u, 0u, local, 1u);
    if (result != 0u) {
        log_at(status_mode_function, 0x3b0u, mode_read_message);
        return result;
    }
    /* Stock LSL #26 tests input bit 5 (and not bit 6). */
    if ((local[0] & 0x20u) != 0u)
        return 1u;

    log_at(status_mode_function, 0x3b8u, three_byte_message);
    return 0u;
}

uint32_t opencfw_provider_420890(void)
{
    volatile const uint32_t *const active_handle =
        (volatile const uint32_t *)(uintptr_t)ACTIVE_HANDLE_SLOT;
    uint32_t result;

    if (*active_handle == 0u)
        return 2u;

    result = opencfw_bl_nor_read_delay();
    if (result != 0u) {
        log_at(address_mode_function, 0x3c8u, busy_message);
        return 3u;
    }

    result = opencfw_provider_420984();
    if (result != 0u) {
        log_at(address_mode_function, 0x3cfu, wren_message);
        return result;
    }

    result = opencfw_provider_42069e(0xb7u, 0u, 0u, 0, 0u);
    if (result != 0u) {
        log_at(address_mode_function, 0x3d6u, enter_message);
        return result;
    }

    (void)opencfw_bl_nor_read_delay();
    result = opencfw_provider_420800(0u, 0u, 0u, 0u);
    if (result == 0u) {
        log_at(address_mode_function, 0x3deu, verify_message);
        return 1u;
    }

    result = opencfw_provider_4209c4();
    if (result != 0u)
        log_at(address_mode_function, 0x3e4u, wrdi_message);
    return result;
}
