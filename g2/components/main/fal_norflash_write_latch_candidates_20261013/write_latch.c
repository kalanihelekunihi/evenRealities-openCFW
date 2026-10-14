/* SPDX-License-Identifier: MIT
 * Main 0x470670/0x4706e0: write-enable and write-disable command wrappers.
 * The MX25U command executor at 0x47021c remains a lower contract.
 */
#include <stdint.h>

extern uint32_t g2_norflash_erase_command_47021c(uint32_t command,
                                                   uint32_t address,
                                                   uint32_t count,
                                                   uint32_t mode,
                                                   uint32_t extra);
extern uint32_t g2_flashdb_candidate_flags(void);
extern void g2_flashdb_candidate_log(uint8_t, const char *, const char *,
                                      const char *, uint32_t, const char *, ...);
extern uint32_t audio_log_simple(uint32_t, const char *, const char *, ...);

static const char module[] = "drv.norflash";
static const char file[] = "D:\\01_workspace\\s200_ap510b_iar_git\\driver\\flash\\drv_mx25u25643g.c";
static const char enable_function[] = "mx25u25643g_enable_write_enable";
static const char disable_function[] = "mx25u25643g_enable_write_disable";
static const char failed[] = "Write enable failed before sector erase\n";
static const char failed_short[] =
    "[drv.norflash]Write enable failed before sector erase\n";

static void report_failure(uint8_t level, const char *function,
                           uint32_t line, uint32_t token)
{
    if (g2_flashdb_candidate_flags() & 2u)
        g2_flashdb_candidate_log(level, module, file, function, line,
                                 failed);
    if (g2_flashdb_candidate_flags() & 1u ||
        (g2_flashdb_candidate_flags() & 4u))
        (void)audio_log_simple(token, failed_short, failed_short);
}

uint32_t g2_norflash_write_enable_470670(void)
{
    uint32_t result = g2_norflash_erase_command_47021c(6u, 0u, 0u,
                                                         0u, 0u);
    if (result != 0u)
        report_failure(1u, enable_function, 1010u, 0x04000000u);
    return result;
}

uint32_t g2_norflash_write_disable_4706e0(void)
{
    uint32_t result = g2_norflash_erase_command_47021c(4u, 0u, 0u,
                                                         0u, 0u);
    if (result != 0u)
        report_failure(2u, disable_function, 1022u, 0x08000000u);
    return result;
}
