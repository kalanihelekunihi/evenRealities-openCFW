/* SPDX-License-Identifier: MIT
 * Main 0x47075c mx25u25643g_sector_erase control path. Hardware helpers,
 * controller state and diagnostic output are independently owned lowers.
 */
#include <stdint.h>

extern volatile uint32_t g2_norflash_controller_handle_20074544;
extern void g2_norflash_lock_46f65e(void);
extern void g2_norflash_unlock_46f674(void);
extern void g2_norflash_enter_470f68(void);
extern void g2_norflash_exit_470e90(void);
extern uint32_t g2_norflash_wait_idle_4703ba(void);
extern uint32_t g2_norflash_write_enable_470670(void);
extern uint32_t g2_norflash_erase_command_47021c(uint32_t command,
                                                   uint32_t address,
                                                   uint32_t count,
                                                   uint32_t mode,
                                                   uint32_t extra);
extern uint32_t g2_norflash_write_disable_4706e0(void);
extern void g2_norflash_diagnostic_4733ee(const char *, ...);
extern uint32_t g2_flashdb_candidate_flags(void);
extern void g2_flashdb_candidate_log(uint8_t, const char *, const char *,
                                      const char *, uint32_t, const char *, ...);
extern uint32_t audio_log_simple(uint32_t, const char *, const char *, ...);

static const char module[] = "drv.norflash";
static const char file[] = "D:\\01_workspace\\s200_ap510b_iar_git\\driver\\flash\\drv_mx25u25643g.c";
static const char function[] = "mx25u25643g_sector_erase";
static const char alignment[] = "Error: Address must be 4KB aligned\n";
static const char alignment_short[] = "[drv.norflash]Error: Address must be 4KB aligned\n";
static const char before_wren[] = "SE wait_idle(before WREN) timeout: addr=0x%08X\n";
static const char enable_failed[] = "SE write_enable failed: addr=0x%08X, st=%d\n";
static const char command_failed[] = "SE erase command failed: addr=0x%08X, st=%d\n";
static const char after_erase[] = "SE wait_idle(after erase) timeout: addr=0x%08X\n";
static const char disable_failed[] = "SE write_disable failed: addr=0x%08X, st=%d\n";

uint32_t g2_norflash_erase_lower_47075c(uint32_t address)
{
    if (g2_norflash_controller_handle_20074544 == 0u) return 2u;
    if ((address & 0xfffu) != 0u) {
        if (g2_flashdb_candidate_flags() & 2u)
            g2_flashdb_candidate_log(2u, module, file, function, 1038u,
                                     alignment);
        if (g2_flashdb_candidate_flags() & 1u ||
            (g2_flashdb_candidate_flags() & 4u))
            (void)audio_log_simple(0x08000000u, alignment_short,
                                   alignment_short);
        return 6u;
    }
    if (address >= 0x02000000u) return 5u;

    g2_norflash_lock_46f65e();
    g2_norflash_enter_470f68();
    uint32_t result;
    if (g2_norflash_wait_idle_4703ba() != 0u) {
        g2_norflash_diagnostic_4733ee(before_wren, address);
        result = 3u;
    } else {
        result = g2_norflash_write_enable_470670();
        if (result != 0u) {
            g2_norflash_diagnostic_4733ee(enable_failed, address, result);
        } else {
            result = g2_norflash_erase_command_47021c(32u, address, 1u,
                                                       0u, 0u);
            if (result != 0u) {
                g2_norflash_diagnostic_4733ee(command_failed, address,
                                              result);
            } else if (g2_norflash_wait_idle_4703ba() != 0u) {
                g2_norflash_diagnostic_4733ee(after_erase, address);
                result = 4u;
            } else {
                result = g2_norflash_write_disable_4706e0();
                if (result != 0u)
                    g2_norflash_diagnostic_4733ee(disable_failed, address,
                                                  result);
            }
        }
    }
    g2_norflash_exit_470e90();
    g2_norflash_unlock_46f674();
    return result;
}
