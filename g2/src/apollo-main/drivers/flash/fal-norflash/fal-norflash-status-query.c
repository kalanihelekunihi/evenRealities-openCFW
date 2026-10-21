/* SPDX-License-Identifier: MIT
 * Main 0x4702d8: MX25U busy-status command and status-bit reduction.
 * The command executor at 0x470168 remains an independent lower contract.
 */
#include <stdint.h>

extern uint32_t g2_norflash_command_470168(uint32_t command,
                                             uint32_t address,
                                             uint32_t mode,
                                             uint8_t *response,
                                             uint32_t count);
extern uint32_t g2_flashdb_candidate_flags(void);
extern void g2_flashdb_candidate_log(uint8_t, const char *, const char *,
                                      const char *, uint32_t, const char *, ...);
extern uint32_t audio_log_simple(uint32_t, const char *, const char *, ...);

static const char module[] = "drv.norflash";
static const char file[] = "D:\\01_workspace\\s200_ap510b_iar_git\\driver\\flash\\drv_mx25u25643g.c";
static const char function[] = "mx25u25643g_is_busy";
static const char failed[] = "Read busy status failed\n";
static const char failed_short[] = "[drv.norflash]Read busy status failed\n";

uint32_t g2_norflash_status_busy_4702d8(void)
{
    uint8_t response[5] = {0};
    uint32_t result = g2_norflash_command_470168(5u, 0u, 0u,
                                                   response, 1u);
    if (result != 0u) {
        if (g2_flashdb_candidate_flags() & 2u)
            g2_flashdb_candidate_log(2u, module, file, function, 886u,
                                     failed);
        if (g2_flashdb_candidate_flags() & 1u ||
            (g2_flashdb_candidate_flags() & 4u))
            (void)audio_log_simple(0x08000000u, failed_short,
                                   failed_short);
        return result;
    }
    return (response[0] & 1u) != 0u;
}
