/* SPDX-License-Identifier: MIT
 * Main 0x4709c8 NOR read control path. Transfer, wait and clock operations
 * remain separate source-owned lowers; this preserves their call ordering.
 */
#include <stdint.h>

extern volatile uint32_t g2_norflash_controller_handle_20074544;
extern void g2_norflash_lock_46f65e(void);
extern void g2_norflash_unlock_46f674(void);
extern void g2_norflash_enter_470f68(void);
extern void g2_norflash_exit_470e90(void);
extern uint32_t g2_norflash_wait_idle_4703ba(void);
extern uint32_t g2_norflash_command_470168(uint32_t, uint32_t, uint32_t,
                                           uint8_t *, uint32_t);
extern void g2_norflash_diagnostic_4733ee(const char *, ...);
extern uint32_t g2_flashdb_candidate_flags(void);
extern void g2_flashdb_candidate_log(uint8_t, const char *, const char *,
                                      const char *, uint32_t, const char *, ...);
extern uint32_t audio_log_simple(uint32_t, const char *, const char *, ...);

static const char module[] = "drv.norflash";
static const char file[] = "D:\\01_workspace\\s200_ap510b_iar_git\\driver\\flash\\drv_mx25u25643g.c";
static const char function[] = "mx25u25643g_read_data";
static const char busy[] = "Device is busy\n";
static const char read_failed[] = "Read data failed\n";
static const char read_failed_short[] = "[drv.norflash]Read data failed\n";

int32_t g2_norflash_read_lower_4709c8(int32_t address, uint8_t *buffer,
                                       uint32_t size)
{
    if (g2_norflash_controller_handle_20074544 == 0u || buffer == 0 ||
        size == 0u)
        return 6u;
    if ((uint32_t)address >= UINT32_C(0x02000000))
        return 5u;

    g2_norflash_lock_46f65e();
    g2_norflash_enter_470f68();
    uint32_t result;
    if (g2_norflash_wait_idle_4703ba() != 0u) {
        g2_norflash_diagnostic_4733ee(busy);
        result = 3u;
    } else {
        result = g2_norflash_command_470168(3u, (uint32_t)address, 1u,
                                           buffer, size);
        if (result == 0u) {
            (void)g2_norflash_wait_idle_4703ba();
        } else {
            if (g2_flashdb_candidate_flags() & 2u)
                g2_flashdb_candidate_log(2u, module, file, function, 1286u,
                                         read_failed);
            if (g2_flashdb_candidate_flags() & 1u ||
                (g2_flashdb_candidate_flags() & 4u))
                (void)audio_log_simple(0x08000000u, read_failed_short,
                                       read_failed_short);
        }
    }
    g2_norflash_exit_470e90();
    g2_norflash_unlock_46f674();
    return (int32_t)result;
}
