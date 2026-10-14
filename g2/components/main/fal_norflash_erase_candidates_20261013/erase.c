/* SPDX-License-Identifier: MIT
 * Main 0x540f84 FAL erase adapter. The physical 4 KiB erase lower at
 * 0x47075c remains an independent source body.
 */
#include <stdint.h>

extern uint32_t g2_norflash_erase_lower_47075c(uint32_t offset);
extern uint32_t g2_flashdb_candidate_flags(void);
extern void g2_flashdb_candidate_log(uint8_t, const char *, const char *,
                                      const char *, uint32_t, const char *, ...);
extern uint32_t audio_log_simple(uint32_t, const char *, const char *, ...);

static const char module[] = "db.api";
static const char file[] = "D:\\01_workspace\\s200_ap510b_iar_git\\platform\\service\\flashDB\\db_api\\service_db_api.c";
static const char function[] = "_flashDBErase";
static const char bad_offset[] = "Offset address 0x%08lX is not 4K aligned!";
static const char bad_offset_short[] = "[db.api]Offset address 0x%08lX is not 4K aligned!";
static const char bad_size[] = "invalid erase size=0x%x\r\n";
static const char bad_size_short[] = "[db.api]invalid erase size=0x%x\r\n";
static const char failed[] = "Erase failed at address 0x%08lX";
static const char failed_short[] = "[db.api]Erase failed at address 0x%08lX";

static void log_offset(int32_t offset)
{
    if (g2_flashdb_candidate_flags() & 2u)
        g2_flashdb_candidate_log(1u, module, file, function, 98u,
                                 bad_offset, (uint32_t)offset);
    if (g2_flashdb_candidate_flags() & 1u ||
        (g2_flashdb_candidate_flags() & 4u))
        (void)audio_log_simple(0x04400000u, bad_offset_short,
                               bad_offset_short, (uint32_t)offset);
}

static void log_size(uint32_t size)
{
    if (g2_flashdb_candidate_flags() & 2u)
        g2_flashdb_candidate_log(1u, module, file, function, 105u,
                                 bad_size, size);
    if (g2_flashdb_candidate_flags() & 1u ||
        (g2_flashdb_candidate_flags() & 4u))
        (void)audio_log_simple(0x04400000u, bad_size_short,
                               bad_size_short, size);
}

static void log_failure(uint32_t offset)
{
    if (g2_flashdb_candidate_flags() & 2u)
        g2_flashdb_candidate_log(1u, module, file, function, 114u,
                                 failed, offset);
    if (g2_flashdb_candidate_flags() & 1u ||
        (g2_flashdb_candidate_flags() & 4u))
        (void)audio_log_simple(0x04400000u, failed_short,
                               failed_short, offset);
}

int g2_norflash_erase_540f84(int32_t offset, uint32_t size)
{
    if (((uint32_t)offset & 0xfffu) != 0u || offset >= 0x02000001) {
        log_offset(offset);
        return 0;
    }
    if ((size & 0xfffu) != 0u) {
        log_size(size);
        size = ((size >> 12) + 1u) << 12;
    }
    uint32_t current = (uint32_t)offset;
    while (size != 0u) {
        if (g2_norflash_erase_lower_47075c(current) != 0u) {
            log_failure(current);
            return 0;
        }
        if (size < 4097u) return (int)size;
        size -= 4096u;
        current += 4096u;
    }
    return 0;
}
