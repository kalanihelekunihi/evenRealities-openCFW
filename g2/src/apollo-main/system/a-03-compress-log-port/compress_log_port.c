/* Compact-log file port, stock
 * D:\01_workspace\s200_ap510b_iar_git\platform\service\compress_log\port\compress_log_port.c
 * (log tag "clog.port"). Native 0x44a474..0x44a9ad, literal pool 0x44a9b4..0x44aa2b
 * (mode strings "rb"/"wb" at 0x44a790/0x44a794, "r+b"/"w+b" at 0x44a8fc/0x44a900).
 *
 * The compact-log ring core (system/log/p-03-compress-log) hands 4 KiB blocks to
 * compress_log_sync_to_files, which appends them to a rotation of five files
 * /log/compress_log_<0..4>.bin of at most 0x7d000 bytes each. Every file starts
 * with a "Software_Version: 2.2.6.10\n" header. The rotation state lives in a
 * 12-byte manager record mirrored to /log/compress_manager.bin.
 * compress_log_export_active 0x44a9ae is system/glue/log_policy_provider.c. */
#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

#define CLOG_MANAGER_MAGIC 0x4c4d4752u /* 'RGML' */
#define CLOG_FILE_COUNT 5u
#define CLOG_FILE_LIMIT 0x7d000u
#define CLOG_PATH_SIZE 0x30u
#define CLOG_HEADER_SIZE 0x28u
#define CLOG_EXPORT_TIMEOUT_MS 120000u

/* Rotation manager, RAM 0x20073f9c, persisted verbatim (12 bytes). */
typedef struct {
    uint32_t magic;    /* +0 CLOG_MANAGER_MAGIC */
    uint8_t current;   /* +4 index being appended to */
    uint8_t oldest;    /* +5 oldest index still on flash */
    uint8_t count;     /* +6 number of files present (0..5) */
    uint8_t pad;       /* +7 */
    uint32_t offset;   /* +8 write offset inside the current file */
} g2_clog_manager_t;
_Static_assert(sizeof(g2_clog_manager_t) == 12u, "compress_manager.bin record");

extern g2_clog_manager_t g2_clog_manager;        /* RAM 0x20073f9c */
extern volatile uint8_t g2_clog_manager_loaded;  /* RAM 0x20074fa0 */
extern volatile uint8_t audio_log_policy_byte;   /* RAM 0x20074fa1 export in progress */

extern int32_t g2_audio_dump_snprintf(char *buf, uint32_t size, const char *fmt, ...); /* 0x44b728 */
extern void *file_open(const char *path, const char *mode);                 /* 0x474550 */
extern int32_t file_close(void *file);                                      /* 0x4745f4 */
extern uint32_t file_read(void *buffer, uint32_t size, uint32_t count, void *file); /* 0x474634 */
extern uint32_t file_write(const void *buf, uint32_t size, uint32_t count, void *file); /* 0x474682 */
extern int32_t file_seek(void *file, int32_t offset, int32_t origin);       /* 0x474814 */
extern int32_t file_remove(const char *path);                               /* 0x47498c */
extern void audio_event_loop_push_delayed(void (*callback)(void), uint32_t argument,
                                          uint32_t delay);                  /* 0x47697e */
extern uint32_t audio_event_loop_remove_delayed(void (*callback)(void));    /* 0x476ace */
extern uint32_t audio_log_flags(void);                                      /* 0x43d0ce */
extern void audio_log_extended(uint8_t, const char *, const char *, const char *, uint32_t,
                               const char *, ...);                          /* 0x43d574 */
extern uint32_t compress_log_output(uint32_t, const char *, const char *, ...); /* 0x43ce9e */

static const char module_tag[] = "clog.port"; /* ROM 0x78a64c */
static const char source_file[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\platform\\service\\compress_log\\port\\compress_log_port.c"; /* ROM 0x6dfcd4 */
static const char path_format[] = "/log/compress_log_%d.bin";    /* ROM 0x76a134 */
static const char manager_path[] = "/log/compress_manager.bin";  /* ROM 0x76a150 */
static const char version_format[] = "Software_Version: %s\n";  /* ROM 0x775aac */
static const char software_version[] = "2.2.6.10";              /* ROM 0x78a640 */
static const char mode_read[] = "rb";        /* code 0x44a790 */
static const char mode_write[] = "wb";       /* code 0x44a794 */
static const char mode_update[] = "r+b";     /* code 0x44a8fc */
static const char mode_create[] = "w+b";     /* code 0x44a900 */
static const char header_fn[] = "_write_file_version_header";            /* ROM 0x76a16c */
static const char sync_fn[] = "compress_log_sync_to_files";              /* ROM 0x76a188 */
static const char timeout_fn[] = "compress_log_export_timeout_callback"; /* ROM 0x748444 */
static const char notify_fn[] = "compress_log_export_notify";            /* ROM 0x76a1a4 */

#define CLOG_LOG(fn, level, line, mask, fmt, ...) do { \
    if (audio_log_flags() & 2u) \
        audio_log_extended((level), module_tag, source_file, (fn), (line), fmt, ##__VA_ARGS__); \
    if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u)) \
        (void)compress_log_output((mask), "[clog.port]" fmt, "[clog.port]" fmt, ##__VA_ARGS__); \
} while (0)

void compress_log_path_format(uint8_t index, char *buffer, uint32_t size)
{
    (void)g2_audio_dump_snprintf(buffer, size, path_format, index);
}

bool compress_log_file_exists(uint8_t index)
{
    char path[CLOG_PATH_SIZE];
    compress_log_path_format(index, path, sizeof path);
    void *file = file_open(path, mode_read);
    if (file == NULL)
        return false;
    (void)file_close(file);
    return true;
}

int32_t compress_log_manager_save(void)
{
    void *file = file_open(manager_path, mode_write);
    if (file == NULL)
        return -1;
    g2_clog_manager.magic = CLOG_MANAGER_MAGIC;
    uint32_t written = file_write(&g2_clog_manager, sizeof g2_clog_manager, 1u, file);
    (void)file_close(file);
    return written == 1u ? 0 : -1;
}

/* Re-derive oldest/count from the files actually present. */
void compress_log_manager_reconcile(void)
{
    g2_clog_manager_t *const m = &g2_clog_manager;
    if (m->count == 0u)
        return;
    if (!compress_log_file_exists(m->current))
        m->offset = 0u;

    uint8_t present = 0u;
    bool found = false;
    uint8_t oldest = m->oldest;
    for (uint8_t i = 0u; i < m->count; i++) {
        uint8_t index = (uint8_t)(((uint32_t)m->oldest + i) % CLOG_FILE_COUNT);
        if (compress_log_file_exists(index)) {
            if (!found) {
                oldest = index;
                found = true;
            }
            present++;
        }
    }
    if (present == m->count && oldest == m->oldest)
        return;
    m->oldest = oldest;
    m->count = present;
    (void)compress_log_manager_save();
}

static void manager_reset(g2_clog_manager_t *m)
{
    m->magic = CLOG_MANAGER_MAGIC;
    m->current = 0u;
    m->oldest = 0u;
    m->count = 0u;
    m->offset = 0u;
}

int32_t compress_log_manager_load(void)
{
    g2_clog_manager_t *const m = &g2_clog_manager;
    void *file = file_open(manager_path, mode_read);
    if (file == NULL) {
        manager_reset(m);
        g2_clog_manager_loaded = 1u;
        return 0;
    }
    uint32_t got = file_read(m, sizeof *m, 1u, file);
    (void)file_close(file);
    if (got != 1u || m->magic != CLOG_MANAGER_MAGIC)
        manager_reset(m);
    if (m->current >= CLOG_FILE_COUNT)
        m->current = 0u;
    if (m->oldest >= CLOG_FILE_COUNT)
        m->oldest = 0u;
    if (m->count > CLOG_FILE_COUNT)
        m->count = 0u;
    if (m->offset >= CLOG_FILE_LIMIT + 1u)
        m->offset = 0u;
    g2_clog_manager_loaded = 1u;
    compress_log_manager_reconcile();
    return 0;
}

void compress_log_file_remove(uint8_t index)
{
    char path[CLOG_PATH_SIZE];
    compress_log_path_format(index, path, sizeof path);
    (void)file_remove(path);
}

/* Rewrite the version line at offset 0; returns its length, 0 on failure. */
uint32_t _write_file_version_header(void *file)
{
    char header[CLOG_HEADER_SIZE];
    if (file == NULL)
        return 0u;
    int32_t length = g2_audio_dump_snprintf(header, sizeof header, version_format, software_version);
    if ((uint32_t)length - 1u >= CLOG_HEADER_SIZE - 1u) {
        CLOG_LOG(header_fn, 2u, 0xadu, 0x08400000u,
                 "[FILE_HDR] write version header failed: header_len=%d", length); /* ROM 0x71cdc8 / 0x701008 */
        return 0u;
    }
    (void)file_seek(file, 0, 0);
    uint32_t written = file_write(header, 1u, (uint32_t)length, file);
    if (written != (uint32_t)length) {
        CLOG_LOG(header_fn, 2u, 0xb4u, 0x08800000u,
                 "[FILE_HDR] write version header failed: written=%u, expect=%d", /* ROM 0x709fe4 / 0x6f25f4 */
                 written, length);
        return 0u;
    }
    return written;
}

/* Advance to the next file, dropping the oldest once all five exist. */
void compress_log_rotate_file(void)
{
    g2_clog_manager_t *const m = &g2_clog_manager;
    char path[CLOG_PATH_SIZE];
    uint8_t next = (uint8_t)(((uint32_t)m->current + 1u) % CLOG_FILE_COUNT);

    if (m->count < CLOG_FILE_COUNT) {
        m->count++;
    } else {
        compress_log_file_remove(m->oldest);
        m->oldest = (uint8_t)(((uint32_t)m->oldest + 1u) % CLOG_FILE_COUNT);
    }
    m->current = next;
    m->offset = 0u;
    compress_log_path_format(next, path, sizeof path);
    void *file = file_open(path, mode_write);
    if (file != NULL) {
        uint32_t header = _write_file_version_header(file);
        if (header != 0u)
            m->offset = header;
        (void)file_close(file);
    }
    (void)compress_log_manager_save();
}

void compress_log_sync_to_files(const uint8_t *data, uint32_t len)
{
    g2_clog_manager_t *const m = &g2_clog_manager;
    char path[CLOG_PATH_SIZE];
    uint32_t done;
    uint32_t chunk;

    if (data == NULL || len == 0u)
        return;
    if (g2_clog_manager_loaded == 0u)
        (void)compress_log_manager_load();
    if (m->count == 0u)
        m->count = 1u;

    for (done = 0u; done < len; done += chunk) {
        uint32_t room = CLOG_FILE_LIMIT - m->offset;
        if (room == 0u) {
            compress_log_rotate_file();
            room = CLOG_FILE_LIMIT;
        }
        chunk = len - done;
        if (room < chunk)
            chunk = room;
        compress_log_path_format(m->current, path, sizeof path);
        void *file = file_open(path, mode_update);
        if (file == NULL) {
            file = file_open(path, mode_create);
            if (file == NULL)
                return;
            m->offset = 0u;
            uint32_t header = _write_file_version_header(file);
            if (header != 0u)
                m->offset = header;
            room = CLOG_FILE_LIMIT - m->offset;
            if (room < chunk)
                chunk = room;
        }
        (void)file_seek(file, (int32_t)m->offset, 0);
        uint32_t written = file_write(data + done, 1u, chunk, file);
        (void)file_close(file);
        if (written != chunk)
            break;
        m->offset += chunk;
        (void)compress_log_manager_save();
    }
    CLOG_LOG(sync_fn, 4u, 0x115u, 0x10400000u,
             "[SYNC] <<< sync_to_files done, total written=%u", done); /* ROM 0x7322c4 / 0x71339c */
}

void compress_log_export_timeout_callback(void)
{
    CLOG_LOG(timeout_fn, 2u, 0x157u, 0x08000000u,
             "[EXPORT] export timeout, reset sync flag"); /* ROM 0x73cb90 / 0x727984 */
    audio_log_policy_byte = 0u;
}

/* While an export runs the ring is not flushed to files; a 120 s timer
 * clears the flag if the host never ends the export. */
void compress_log_export_notify(uint8_t is_start_export)
{
    CLOG_LOG(notify_fn, 4u, 0x15du, 0x10400000u,
             "[EXPORT] export_notify called, is_start_export=%d", is_start_export); /* ROM 0x7279b8 / 0x70a024 */
    if (is_start_export == 1u) {
        CLOG_LOG(notify_fn, 4u, 0x171u, 0x10000000u,
                 "[EXPORT] start export, set 120s timeout"); /* ROM 0x74846c / 0x7279ec */
        (void)audio_event_loop_remove_delayed(compress_log_export_timeout_callback);
        audio_event_loop_push_delayed(compress_log_export_timeout_callback, 0u, CLOG_EXPORT_TIMEOUT_MS);
    } else {
        (void)audio_event_loop_remove_delayed(compress_log_export_timeout_callback);
    }
    audio_log_policy_byte = is_start_export;
}
