/* SPDX-License-Identifier: MIT
 * Main 0x540ed4 FAL read callback. The physical read lower at 0x4709c8 is
 * deliberately a separate source body; this owns the product adapter.
 */
#include <stdint.h>

extern int g2_norflash_read_lower_4709c8(int32_t, uint8_t *, uint32_t);
extern uint32_t g2_flashdb_candidate_flags(void);
extern void g2_flashdb_candidate_log(uint8_t, const char *, const char *,
                                      const char *, uint32_t, const char *, ...);
extern uint32_t audio_log_simple(uint32_t, const char *, const char *, ...);

static const char module[] = "db.api";
static const char file[] = "D:\\01_workspace\\s200_ap510b_iar_git\\platform\\service\\flashDB\\db_api\\service_db_api.c";
static const char function[] = "_flashDBRead";
static const char message[] = "read failed";
static const char short_message[] = "[db.api]read failed";

int g2_norflash_read_540ed4(int32_t offset, uint8_t *buffer, uint32_t size)
{
    if (g2_norflash_read_lower_4709c8(offset, buffer, size) == 0)
        return (int)size;
    if (g2_flashdb_candidate_flags() & 2u)
        g2_flashdb_candidate_log(1u, module, file, function, 75u, message);
    if (g2_flashdb_candidate_flags() & 1u ||
        (g2_flashdb_candidate_flags() & 4u))
        (void)audio_log_simple(0x04000000u, short_message, short_message);
    return 0;
}
