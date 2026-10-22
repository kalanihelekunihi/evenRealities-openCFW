/* Native retained crash record 0x47d9fc..0x47dc22. No source path string
 * survives; the "[CRASH]" messages and /log/hardfault.txt name the unit.
 *
 * Flow: the CmBacktrace fault path (0x5939a8..0x593afe) formats text into a
 * RAM staging buffer with crash_record_printf_47da78, then 0x5944bc commits it
 * with crash_record_commit_47dac0 into the record at RAM 0x20075048, which lies
 * just past the startup zero-init range [0x20004558,0x20075048) and therefore
 * survives the reset. On the next boot elog_async_ext_flieStore_Init (0x448e48,
 * via 0x448e2a with "/log") appends a valid record to <dir>/hardfault.txt with
 * crash_record_recover_to_file_47db02 and clears it, keeping the crash count. */
#include <stdint.h>
#include <stdarg.h>

#define CRASH_RECORD_MAGIC   0x43524153u /* 'CRAS' */
#define CRASH_TEXT_CAPACITY  0x1194u
#define CRASH_FILE_LIMIT     0x19001     /* > 100 KiB triggers delete */
#define CRASH_SAFE_MODE_AFTER 10u

typedef struct {
    uint32_t magic;          /* +0x00 CRASH_RECORD_MAGIC */
    uint32_t valid;          /* +0x04 1 once committed */
    uint32_t crash_count;    /* +0x08 preserved across clear */
    uint32_t length;         /* +0x0c text bytes, 1..0x1194 */
    uint32_t has_timestamp;  /* +0x10 0 -> "N/A" */
    uint32_t crc;            /* +0x14 CRC-32 of +0x00..+0x13 */
    char     text[CRASH_TEXT_CAPACITY]; /* +0x18 */
} g2_crash_record_t;
_Static_assert(sizeof(g2_crash_record_t) == 0x11acu, "crash record");

extern g2_crash_record_t g2_crash_record;           /* RAM 0x20075048 (retained) */
extern uint32_t g2_crash_staging_length;            /* RAM 0x200743a4 */
extern char g2_crash_staging_text[CRASH_TEXT_CAPACITY]; /* RAM 0x2005ce68 */
extern char g2_crash_path_buffer[0x80];             /* RAM 0x200e3b00 */
extern char g2_crash_header_buffer[0x200];          /* RAM 0x200e3b80 */
extern char g2_crash_footer_buffer[0x100];          /* RAM 0x200e3d80 */

extern uint32_t crc32_4d34c4(const void *data, uint32_t length, const uint32_t *seed); /* 0x4d34c4 */
extern void audio_uart_buffer_zero(void *, uint32_t, uint32_t); /* 0x43c0e4 */
extern void *audio_queue_copy_bytes(void *, const void *, uint32_t); /* 0x439be4 */
extern int32_t g2_log_vformat(char *, uint32_t, const char *, va_list); /* 0x44b76c vsnprintf */
extern int32_t g2_audio_dump_snprintf(char *, uint32_t, const char *, ...); /* 0x44b728 snprintf */
extern int32_t audio_ble_hci_boot_log_4733ee(const char *, ...); /* 0x4733ee raw log printf */
extern void *file_open(const char *path, const char *mode); /* 0x474550 */
extern int32_t file_close(void *file); /* 0x4745f4 */
extern int32_t file_seek(void *file, int32_t offset, int32_t origin); /* 0x474814 */
extern int32_t file_tell(void *file); /* 0x474870 */
extern int32_t file_remove(const char *path); /* 0x47498c */
extern uint32_t file_write(const void *buf, uint32_t size, uint32_t count, void *file); /* 0x474682 */
extern int32_t file_flush(void *file); /* 0x474910 */

static const char mode_read[] = "r";     /* code literal 0x47dc24 */
static const char mode_append[] = "a+";  /* code literal 0x47dc28 */
static const char ts_none[] = "N/A";     /* code literal 0x47dc2c */
static const char ts_available[] = "Available"; /* ROM 0x78a6ac */
static const char m_safe_mode[] = "[CRASH] Too many crashes (%u), entering safe mode\n"; /* ROM 0x72813c */
static const char f_path[] = "%s/hardfault.txt"; /* ROM 0x77eb18 */
static const char m_too_big[] =
    "[CRASH] hardfault.txt size exceeded 100KB, deleted and recreating\n"; /* ROM 0x7015e0 */
static const char m_open_fail[] = "[CRASH] Failed to open %s\n"; /* ROM 0x76a850 */
static const char f_header[] =
    "\n========================================\n===== CRASH #%u =====\nTimestamp: %s\n"
    "Data Length: %u bytes\nCRC32: 0x%08X\n----------------------------------------\n\n"; /* ROM 0x6d2ef8 */
static const char m_short_write[] = "[CRASH] Warning: only wrote %u/%u bytes\n"; /* ROM 0x73d3a4 */
static const char f_footer[] =
    "\n========================================\n===== END CRASH #%u =====\n"
    "========================================\n\n"; /* ROM 0x6d6e10 */
static const char m_recovered[] = "[CRASH] Crash info #%u recovered to %s\n"; /* ROM 0x748b24 */

/* 0x47d9fc: header CRC (first 0x14 bytes only), 0 for an oversized record. */
uint32_t crash_record_crc_47d9fc(const g2_crash_record_t *record)
{
    if (record->length >= CRASH_TEXT_CAPACITY + 1u)
        return 0u;
    return crc32_4d34c4(record, 0x14u, 0);
}

uint32_t crash_record_is_valid_47da16(void)
{
    g2_crash_record_t *record = &g2_crash_record;
    if (record->magic != CRASH_RECORD_MAGIC)
        return 0u;
    if (record->valid != 1u)
        return 0u;
    if (record->length == 0u || record->length >= CRASH_TEXT_CAPACITY + 1u)
        return 0u;
    return crash_record_crc_47d9fc(record) == record->crc ? 1u : 0u;
}

/* 0x47da58: cold-boot init; garbage (no magic) is wiped including the count. */
void crash_record_init_47da58(void)
{
    g2_crash_record_t *record = &g2_crash_record;
    if (record->magic != CRASH_RECORD_MAGIC) {
        audio_uart_buffer_zero(record, sizeof(*record), 0u);
        record->crash_count = 0u;
    }
}

/* 0x47da78: append formatted text to the staging buffer, truncating at
 * 0x1193 characters and always leaving it NUL-terminated. */
void crash_record_printf_47da78(const char *format, ...)
{
    if (format != 0) {
        uint32_t room = 0x1193u - g2_crash_staging_length;
        if (room != 0u) {
            va_list args;
            int32_t written;
            va_start(args, format);
            written = g2_log_vformat(g2_crash_staging_text + g2_crash_staging_length,
                                     room + 1u, format, args);
            va_end(args);
            if (written >= 1) {
                if (room < (uint32_t)written)
                    g2_crash_staging_length = room + g2_crash_staging_length;
                else
                    g2_crash_staging_length = (uint32_t)written + g2_crash_staging_length;
            }
            g2_crash_staging_text[g2_crash_staging_length] = '\0';
        }
    }
}

void crash_record_commit_47dac0(void)
{
    g2_crash_record_t *record = &g2_crash_record;
    if (g2_crash_staging_length != 0u) {
        record->magic = CRASH_RECORD_MAGIC;
        record->valid = 1u;
        record->crash_count = record->crash_count + 1u;
        record->length = g2_crash_staging_length;
        record->has_timestamp = 0u;
        (void)audio_queue_copy_bytes(record->text, g2_crash_staging_text, g2_crash_staging_length);
        record->text[g2_crash_staging_length] = '\0';
        record->crc = crash_record_crc_47d9fc(record);
    }
}

uint32_t crash_record_recover_to_file_47db02(const char *log_dir)
{
    g2_crash_record_t *record = &g2_crash_record;
    char *path = g2_crash_path_buffer;
    void *file;
    uint32_t count;

    if (crash_record_is_valid_47da16() == 0u)
        return 0u;
    if (record->crash_count > CRASH_SAFE_MODE_AFTER)
        (void)audio_ble_hci_boot_log_4733ee(m_safe_mode, record->crash_count);

    (void)g2_audio_dump_snprintf(path, 0x80u, f_path, log_dir);
    file = file_open(path, mode_read);
    if (file != 0) {
        int32_t size;
        (void)file_seek(file, 0, 2);
        size = file_tell(file);
        (void)file_close(file);
        if (size >= CRASH_FILE_LIMIT) {
            (void)file_remove(path);
            (void)audio_ble_hci_boot_log_4733ee(m_too_big);
        }
    }

    file = file_open(path, mode_append);
    if (file == 0) {
        (void)audio_ble_hci_boot_log_4733ee(m_open_fail, path);
    } else {
        const char *timestamp = record->has_timestamp != 0u ? ts_available : ts_none;
        uint32_t length = record->length;
        uint32_t crc = record->crc;
        int32_t n = g2_audio_dump_snprintf(g2_crash_header_buffer, 0x200u, f_header,
                                           record->crash_count, timestamp, length, crc);
        uint32_t written;
        if (n >= 1)
            (void)file_write(g2_crash_header_buffer, 1u, (uint32_t)n, file);
        written = file_write(record->text, 1u, record->length, file);
        if (written != record->length)
            (void)audio_ble_hci_boot_log_4733ee(m_short_write, written, record->length);
        n = g2_audio_dump_snprintf(g2_crash_footer_buffer, 0x100u, f_footer, record->crash_count);
        if (n >= 1)
            (void)file_write(g2_crash_footer_buffer, 1u, (uint32_t)n, file);
        (void)file_flush(file);
        (void)file_close(file);
        (void)audio_ble_hci_boot_log_4733ee(m_recovered, record->crash_count, path);
    }

    count = record->crash_count;
    audio_uart_buffer_zero(record, sizeof(*record), 0u);
    record->crash_count = count;
    return 1u;
}
