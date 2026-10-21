/* SPDX-License-Identifier: MIT
 * Main 0x4708a8 NOR page-program control loop. Hardware command and wait
 * helpers remain independently source-owned lower contracts.
 */
#include <stdint.h>

extern volatile uint32_t g2_norflash_controller_handle_20074544;
extern void g2_norflash_lock_46f65e(void);
extern void g2_norflash_unlock_46f674(void);
extern void g2_norflash_enter_470f68(void);
extern void g2_norflash_exit_470e90(void);
extern uint32_t g2_norflash_wait_idle_4703ba(void);
extern uint32_t g2_norflash_write_enable_470670(void);
extern uint32_t g2_norflash_erase_command_47021c(uint32_t, uint32_t,
                                                  uint32_t, uint32_t,
                                                  uint32_t);
extern uint32_t g2_norflash_wait_status_470368(uint32_t);
extern uint32_t g2_norflash_write_disable_4706e0(void);
extern void g2_norflash_diagnostic_4733ee(const char *, ...);

static const char invalid[] = "PP invalid arg: handle=%p, buf=%p, len=%u\n";
static const char range[] = "PP out of range: addr=0x%08X, total=0x%08X\n";
static const char before_wren[] =
    "PP wait_idle(before WREN) timeout: addr=0x%08X, len=%u\n";
static const char enable_failed[] =
    "PP write_enable failed: addr=0x%08X, len=%u, st=%d\n";
static const char program_failed[] =
    "PP program failed: addr=0x%08X, len=%u, st=%d\n";
static const char after_program[] =
    "PP wait_idle(after PP) timeout: addr=0x%08X, len=%u\n";
static const char disable_failed[] =
    "PP write_disable failed: addr=0x%08X, len=%u, st=%d\n";

int32_t g2_norflash_write_lower_4708a8(int32_t initial_address,
                                         const uint8_t *initial_buffer,
                                         uint32_t initial_size)
{
    const uint32_t controller = g2_norflash_controller_handle_20074544;
    if (controller == 0u || initial_buffer == 0 || initial_size == 0u) {
        g2_norflash_diagnostic_4733ee(invalid, controller, initial_buffer,
                                      initial_size);
        return 6;
    }
    uint32_t address = (uint32_t)initial_address;
    if (address >= UINT32_C(0x02000000)) {
        g2_norflash_diagnostic_4733ee(range, address,
                                      UINT32_C(0x02000000));
        return 5;
    }

    g2_norflash_lock_46f65e();
    g2_norflash_enter_470f68();
    const uint8_t *buffer = initial_buffer;
    uint32_t remaining = initial_size;
    uint32_t offset = address & 0xffu;
    uint32_t result = 0u;
    while (remaining != 0u) {
        uint32_t chunk = 0x100u - offset;
        if (remaining <= chunk)
            chunk = remaining;
        if (g2_norflash_wait_idle_4703ba() != 0u) {
            g2_norflash_diagnostic_4733ee(before_wren, address, chunk);
            result = 4u;
            break;
        }
        result = g2_norflash_write_enable_470670();
        if (result != 0u) {
            g2_norflash_diagnostic_4733ee(enable_failed, address, chunk,
                                          result);
            break;
        }
        result = g2_norflash_erase_command_47021c(
            2u, address, 1u, (uint32_t)(uintptr_t)buffer, chunk);
        if (result != 0u) {
            g2_norflash_diagnostic_4733ee(program_failed, address, chunk,
                                          result);
            break;
        }
        if (g2_norflash_wait_status_470368(10u) != 0u) {
            g2_norflash_diagnostic_4733ee(after_program, address, chunk);
            result = 4u;
            break;
        }
        result = g2_norflash_write_disable_4706e0();
        if (result != 0u) {
            g2_norflash_diagnostic_4733ee(disable_failed, address, chunk,
                                          result);
            break;
        }
        remaining -= chunk;
        address += chunk;
        buffer += chunk;
        offset = 0u;
    }
    g2_norflash_exit_470e90();
    g2_norflash_unlock_46f674();
    return (int32_t)result;
}
