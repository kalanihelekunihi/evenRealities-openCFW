/* SPDX-License-Identifier: MIT
 * Main 0x540f2c FAL write callback. The physical write lower at 0x4708a8
 * is a distinct source body and remains an explicit import.
 */
#include <stdint.h>

extern int g2_norflash_write_lower_4708a8(int32_t, const uint8_t *, uint32_t);
extern uint32_t g2_flashdb_candidate_flags(void);
extern void g2_flashdb_candidate_log(uint8_t, const char *, const char *,
                                      const char *, uint32_t, const char *, ...);
extern uint32_t audio_log_simple(uint32_t, const char *, const char *, ...);

static const char module[] = "db.api";
static const char file[] = "D:\\01_workspace\\s200_ap510b_iar_git\\platform\\service\\flashDB\\db_api\\service_db_api.c";
static const char function[] = "_flashDBWrite";
static const char message[] = "write failed";
static const char short_message[] = "[db.api]write failed";

int g2_norflash_write_540f2c(int32_t offset, const uint8_t *buffer, uint32_t size)
{
    if (g2_norflash_write_lower_4708a8(offset, buffer, size) == 0)
        return (int)size;
    if (g2_flashdb_candidate_flags() & 2u)
        g2_flashdb_candidate_log(1u, module, file, function, 85u, message);
    if (g2_flashdb_candidate_flags() & 1u ||
        (g2_flashdb_candidate_flags() & 4u))
        (void)audio_log_simple(0x04000000u, short_message, short_message);
    return 0;
}
