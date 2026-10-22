/* OTA flash staging helpers, stock
 * D:\01_workspace\s200_ap510b_iar_git\platform\protocols\ota_service\ota_service.c
 * (log tag "ota.service"). Native 0x4448f4..0x444e08 and 0x444f26..0x44557a
 * (_RPC_SystemOtaStatusSync 0x444e90 lives in ble/ble-ota/display_ble_ota_cancel_sync.c);
 * literal pools 0x444934..0x44494b, 0x444c96, 0x444de6, 0x445108..0x44510f,
 * 0x445424..0x44565f.
 *
 * These are the lower half of the OTA import engine whose parsers
 * (_fileCmdParse 0x445660, _fileRawDataParse 0x446d40) are reconstructed in
 * app/a-02-ota-service. Image data goes through a one-page write-back cache
 * (RAM 0x20003020) to the active flash backend vtable (pointer RAM 0x2000301c):
 * MRAM backend 0x2000038c, external-flash backend 0x20003028. Every programmed
 * page is read back in 4 KiB chunks and compared (_verifyFlashContent). */
#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

/* Flash backend vtable (RAM 0x2000038c MRAM, 0x20003028 external flash). */
typedef struct {
    uint32_t write_size;                                              /* +0x00 program page / cache size */
    uint32_t erase_size;                                              /* +0x04 erase step */
    int32_t (*init)(void);                                            /* +0x08 nonzero = failure */
    int32_t (*deinit)(void);                                          /* +0x0c */
    int32_t (*lock)(void);                                            /* +0x10 nonzero = failure */
    int32_t (*unlock)(void);                                          /* +0x14 */
    int32_t (*read)(void *dst, uint32_t address, uint32_t length);    /* +0x18 */
    int32_t (*program)(uint32_t address, const void *src, uint32_t length); /* +0x1c 0 = ok */
    int32_t (*erase)(uint32_t address);                               /* +0x20 one erase_size unit */
} g2_ota_flash_ops_t;
_Static_assert(offsetof(g2_ota_flash_ops_t, erase) == 0x20, "erase slot at +0x20");

/* One-page write-back cache (RAM 0x20003020). */
typedef struct {
    uint8_t *buffer;                     /* +0x0 = RAM 0x2034bc10 */
    uint16_t fill;                       /* +0x4 bytes pending */
} g2_ota_write_cache_t;

/* Shared OTA transfer object (RAM 0x20071ff0, 0x70 bytes). */
typedef struct {
    void *file;                          /* +0x00 */
    uint8_t is_open;                     /* +0x04 */
    char path[0x50];                     /* +0x05 */
    uint8_t pad_55[3];
    uint32_t file_size;                  /* +0x58 */
    uint32_t calc_crc;                   /* +0x5c */
    uint32_t reserved_60;                /* +0x60 */
    uint32_t recv_total;                 /* +0x64 */
    uint32_t reserved_68;                /* +0x68 */
    uint8_t progress;                    /* +0x6c */
    uint8_t started;                     /* +0x6d */
    uint8_t pad_6e[2];
} g2_ota_transfer_t;
_Static_assert(sizeof(g2_ota_transfer_t) == 0x70, "stock OTA transfer object is 0x70 bytes");
_Static_assert(offsetof(g2_ota_transfer_t, recv_total) == 0x64, "recvTotalLen at +0x64");

/* Shared OTA session object (RAM 0x20072730, 0x60 bytes); +0x04..+0x33 is the
 * received image header. */
typedef struct {
    uint8_t state;                       /* +0x00 */
    uint8_t pad_01[3];
    uint32_t encrypted;                  /* +0x04 */
    uint32_t fw_start_addr;              /* +0x08 */
    uint32_t fw_length;                  /* +0x0c */
    uint32_t fw_crc;                     /* +0x10 */
    uint8_t header_reserved[0x10];       /* +0x14 */
    uint32_t version;                    /* +0x24 */
    uint32_t fw_data_type;               /* +0x28 1 = bootloader */
    uint32_t storage_type;               /* +0x2c 0 MRAM, 1 external flash, 3 file */
    uint32_t image_id;                   /* +0x30 */
    uint8_t *buffer;                     /* +0x34 */
    uint32_t fw_addr;                    /* +0x38 program address */
    uint32_t offset;                     /* +0x3c */
    uint8_t image_head[0x20];            /* +0x40 first image bytes; +0x50 = OTA image magic */
} g2_ota_session_t;
_Static_assert(sizeof(g2_ota_session_t) == 0x60, "stock OTA session object is 0x60 bytes");
_Static_assert(offsetof(g2_ota_session_t, fw_addr) == 0x38, "fw_addr at +0x38");
_Static_assert(offsetof(g2_ota_session_t, image_head) + 0x10 == 0x50, "OTA magic at +0x50");

#define OTA_STORAGE_MRAM 0u
#define OTA_STORAGE_EXTERNAL_FLASH 1u
#define OTA_STORAGE_FILE 3u
#define OTA_TYPE_BOOTLOADER 1u
#define OTA_MRAM_APP_ADDR 0x605000u      /* staging area, ends at MRAM top 0x800000 */
#define OTA_MRAM_AREA_SIZE 0x1fb000u
#define OTA_MAX_IMAGE_SIZE 0x1f4000u     /* 2,048,000 bytes */
#define OTA_MRAM_BOOTLOADER_ADDR 0x410000u
#define OTA_CHUNK 0x1000u
#define AM_HAL_MRAM_PROGRAM_KEY 0x12344321u
#define OTA_LFS_O_RDONLY 1u
#define OTA_LFS_O_WRONLY 2u
#define OTA_LFS_O_RDWR 3u
#define OTA_LFS_O_CREAT 0x100u
#define OTA_LFS_O_TRUNC 0x400u
#define OTA_LFS_O_APPEND 0x800u
#define OTA_PROBE_PATTERN 0x5aa5a55au
#define FILE_SEEK_SET 0
#define FILE_SEEK_END 2

extern const g2_ota_flash_ops_t *g2_ota_flash_ops;        /* RAM 0x2000301c */
extern g2_ota_write_cache_t g2_ota_write_cache;           /* RAM 0x20003020 */
extern const g2_ota_flash_ops_t g2_ota_mram_flash_ops;    /* RAM 0x2000038c */
extern const g2_ota_flash_ops_t g2_ota_xip_flash_ops;     /* RAM 0x20003028 */
extern g2_ota_transfer_t g2_ota_transfer;                 /* RAM 0x20071ff0 */
extern uint8_t audio_ble_ota_export_state[];              /* RAM 0x20072730, session object */
#define g2_ota_session (*(g2_ota_session_t *)(void *)audio_ble_ota_export_state)
extern uint8_t g2_ota_verify_buffer[OTA_CHUNK];           /* RAM 0x2034cc20 */
extern volatile uint8_t audio_ble_ota_sync_enabled;       /* RAM 0x20074ff3, nonzero = suppress replies */

extern uint32_t audio_log_flags(void); /* 0x43d0ce */
extern void audio_log_extended(uint8_t, const char *, const char *, const char *, uint32_t, const char *, ...); /* 0x43d574 */
extern uint32_t compress_log_output(uint32_t, const char *, const char *, ...); /* 0x43ce9e */
extern void audio_uart_buffer_zero(void *dst, uint32_t len, uint32_t fill); /* 0x43c0e4 memset */
extern uint32_t g2_log_candidate_find_token(const uint8_t *haystack, const uint8_t *needle); /* 0x44b63a strstr */
extern uint32_t osKernelGetTickCount(void); /* 0x4490cc */
extern void *file_open(const char *path, const char *mode); /* 0x474550 */
extern int32_t file_close(void *file); /* 0x4745f4 */
extern uint32_t file_read(void *buffer, uint32_t size, uint32_t count, void *file); /* 0x474634 */
extern uint32_t file_write(const void *buf, uint32_t size, uint32_t count, void *file); /* 0x474682 */
extern int32_t file_seek(void *file, int32_t offset, int32_t origin); /* 0x474814 */
extern int32_t file_tell(void *file); /* 0x474870 */
extern int32_t file_remove(const char *path); /* 0x47498c */
extern void *file_heap_allocate(uint32_t size); /* 0x474cd2 */
extern void file_heap_free(void *buffer); /* 0x474d16 */
extern void audio_ble_privacy_cache_maintenance(const uint32_t *range, uint8_t clean); /* 0x475014 am_hal_cachectrl_dcache_invalidate */
extern int32_t g2_lfs_memcmp(const void *a, const void *b, uint32_t length); /* 0x4751c8 memcmp */
extern uint32_t am_hal_ota_add_475230(uint32_t key, uint8_t magic, uint32_t *image); /* 0x475230 */
extern uint32_t Thread_MsgTransport3TxByBle(uint8_t type, uint8_t command, const void *payload, uint16_t length); /* 0x475de0 */
extern int32_t audio_ble_parse_version(const char *s, const char *fmt, ...); /* 0x475fc0 sscanf */
extern int littlefs_format_4761d2(void); /* 0x4761d2 */

static const char ota_tag[] = "ota.service"; /* ROM 0x78b660 */
static const char ota_path[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\platform\\protocols\\ota_service\\ota_service.c"; /* ROM 0x6e8f74 */
static const char fn_set_fw_addr[] = "_evenOtaSetFwAddr"; /* ROM 0x781584 */
static const char fn_verify[] = "_verifyFlashContent"; /* ROM 0x781598 */
static const char fn_reply[] = "_evenOtaReplyToAPP"; /* ROM 0x7815ac */
static const char fn_write_mram[] = "_evenOtaBootloaderWriteFile2MRAM"; /* ROM 0x757398 */
static const char fn_probe[] = "_otaFsHealthProbe"; /* ROM 0x7815c0 */
static const char fn_heal[] = "_otaFsHealthCheckAndHeal"; /* ROM 0x76f1d0 */

static const char s_no_space[] = "not enough OTA space allocated = %d bytes, Desired = %d bytes"; /* ROM 0x70d564 */
static const char c_no_space[] = "[ota.service]not enough OTA space allocated = %d bytes, Desired = %d bytes"; /* ROM 0x6f4ea0 */
static const char s_overlap[] = "OTA descriptor area will be overlaped!!"; /* ROM 0x74bdec */
static const char c_overlap[] = "[ota.service]OTA descriptor area will be overlaped!!"; /* ROM 0x720e18 */
static const char s_max_size[] =
    "The maximum support size is %d bytes, while the upgrading image size is %d bytes"; /* ROM 0x6e8fc8 */
static const char c_max_size[] =
    "[ota.service]The maximum support size is %d bytes, while the upgrading image size is %d bytes"; /* ROM 0x6de074 */
static const char s_reconfigure[] = "Please try to reconfigure OTA_MAX_IMAGE_SIZE"; /* ROM 0x7361f4 */
static const char c_reconfigure[] = "[ota.service]Please try to reconfigure OTA_MAX_IMAGE_SIZE"; /* ROM 0x716fd8 */
static const char s_verify_fail[] = "flash write verify failed. address 0x%x. length %d"; /* ROM 0x72b848 */
static const char c_verify_fail[] = "[ota.service]flash write verify failed. address 0x%x. length %d"; /* ROM 0x70d5a4 */
static const char s_status[] = "status = %d"; /* ROM 0x78b66c */
static const char c_status[] = "[ota.service]status = %d"; /* ROM 0x76f144 */
static const char s_mode_w_plus[] = "w+"; /* ROM 0x444934 */
static const char s_mode_a_plus[] = "a+"; /* ROM 0x444938 */
static const char s_mode_r_plus[] = "r+"; /* ROM 0x44493c */
static const char s_mode_a[] = "a"; /* ROM 0x444940 */
static const char s_mode_w[] = "w"; /* ROM 0x444944 */
static const char s_mode_r[] = "r"; /* ROM 0x444948 */
static const char s_mode_wb[] = "wb"; /* ROM 0x445424 */
static const char s_mode_rb[] = "rb"; /* ROM 0x445428 */
static const char s_hex_lower[] = "0x"; /* ROM 0x445108 */
static const char s_hex_upper[] = "0X"; /* ROM 0x44510c */
static const char s_hex_format[] = "0x%x"; /* ROM 0x78de44 */
static const char s_mram_start[] = "Start write file to MRAM filePath = %s, addr = %x"; /* ROM 0x72b87c */
static const char c_mram_start[] = "[ota.service]Start write file to MRAM filePath = %s, addr = %x"; /* ROM 0x70d5e4 */
static const char s_size_zero[] = "ERR-File size is 0 %s"; /* ROM 0x779d54 */
static const char c_size_zero[] = "[ota.service]ERR-File size is 0 %s"; /* ROM 0x7573bc */
static const char s_mram_done[] = "Write file to MRAM success, time = %d ms"; /* ROM 0x740ce0 */
static const char c_mram_done[] = "[ota.service]Write file to MRAM success, time = %d ms"; /* ROM 0x720e50 */
static const char s_probe_alloc[] = "fs probe: alloc failed"; /* ROM 0x779d6c */
static const char c_probe_alloc[] = "[ota.service]fs probe: alloc failed"; /* ROM 0x7573e0 */
static const char s_probe_path[] = "ota/_health_probe.bin"; /* ROM 0x779d84 */
static const char s_probe_open_w[] = "fs probe: open w failed"; /* ROM 0x779d9c */
static const char c_probe_open_w[] = "[ota.service]fs probe: open w failed"; /* ROM 0x74be14 */
static const char s_probe_write[] = "fs probe: write %u != %u"; /* ROM 0x76f17c */
static const char c_probe_write[] = "[ota.service]fs probe: write %u != %u"; /* ROM 0x74be3c */
static const char s_probe_open_r[] = "fs probe: open r failed"; /* ROM 0x779db4 */
static const char c_probe_open_r[] = "[ota.service]fs probe: open r failed"; /* ROM 0x74be64 */
static const char s_probe_read[] = "fs probe: read %u != %u"; /* ROM 0x779dcc */
static const char c_probe_read[] = "[ota.service]fs probe: read %u != %u"; /* ROM 0x74be8c */
static const char s_probe_mismatch[] = "fs probe: data mismatch"; /* ROM 0x779de4 */
static const char c_probe_mismatch[] = "[ota.service]fs probe: data mismatch"; /* ROM 0x74beb4 */
static const char s_probe_pass[] = "fs probe: PASS"; /* ROM 0x787b90 */
static const char c_probe_pass[] = "[ota.service]fs probe: PASS"; /* ROM 0x76f198 */
static const char s_probe_fail[] = "fs probe: FAIL"; /* ROM 0x787ba0 */
static const char c_probe_fail[] = "[ota.service]fs probe: FAIL"; /* ROM 0x76f1b4 */
static const char s_fs_broken[] = "OTA: filesystem looks broken, format and recover"; /* ROM 0x72b8b0 */
static const char c_fs_broken[] = "[ota.service]OTA: filesystem looks broken, format and recover"; /* ROM 0x70d624 */
static const char s_format_failed[] = "OTA: littlefs_format failed %d"; /* ROM 0x762bf0 */
static const char c_format_failed[] = "[ota.service]OTA: littlefs_format failed %d"; /* ROM 0x740d0c */
static const char s_still_broken[] = "OTA: fs still broken after format"; /* ROM 0x757404 */
static const char c_still_broken[] = "[ota.service]OTA: fs still broken after format"; /* ROM 0x736254 */
static const char s_heal_done[] = "OTA: fs heal done"; /* ROM 0x7815d4 */
static const char c_heal_done[] = "[ota.service]OTA: fs heal done"; /* ROM 0x762c10 */

/* elog levels and compact-log words (level << 26 | argument count << 22). */
#define ELOG_E 1u
#define ELOG_W 2u
#define ELOG_I 3u
#define ELOG_D 4u
#define CLOG_E0 0x04000000u
#define CLOG_E1 0x04400000u
#define CLOG_E2 0x04800000u
#define CLOG_W0 0x08000000u
#define CLOG_I1 0x0c400000u
#define CLOG_I2 0x0c800000u
#define CLOG_D0 0x10000000u
#define CLOG_D1 0x10400000u

/* Stock log pair: extended elog line when flag bit 1 is set, compact record
 * when bit 0 or bit 2 is set. */
#define OTA_LOG(lvl, fn, line, text, word, compact, ...)                              \
    do {                                                                              \
        if (audio_log_flags() & 2u)                                                   \
            audio_log_extended((lvl), ota_tag, ota_path, (fn), (line), (text), ##__VA_ARGS__); \
        if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))                    \
            (void)compress_log_output((word), (compact), (compact), ##__VA_ARGS__);   \
    } while (0)

uint8_t semantic_OtaBufferedFlashWrite(uint16_t len, const uint8_t *data, uint32_t address, uint8_t last);
int32_t _verifyFlashContent(uint32_t address, const uint8_t *expected, uint32_t length,
                            const g2_ota_flash_ops_t *ops);
int32_t _otaFsHealthProbe(void);

/* littlefs open flags -> stdio mode. The RDWR test (mask 3) also matches
 * WRONLY, so the write-only branch is unreachable, as in stock. */
const char *semantic_OtaSelectFlashOps(uint32_t flags)
{
    if ((flags & OTA_LFS_O_RDWR) != 0u) {
        if ((flags & OTA_LFS_O_CREAT) != 0u)
            return (flags & OTA_LFS_O_TRUNC) != 0u ? s_mode_w_plus : s_mode_a_plus;
        return s_mode_r_plus;
    }
    if ((flags & OTA_LFS_O_WRONLY) != 0u) {
        if ((flags & OTA_LFS_O_APPEND) != 0u)
            return s_mode_a;
        if ((flags & OTA_LFS_O_CREAT) != 0u)
            return (flags & OTA_LFS_O_TRUNC) != 0u ? s_mode_w : s_mode_a;
        return s_mode_w;
    }
    return s_mode_r;
}

int32_t semantic_OtaFileSize(void *file)
{
    int32_t position;
    int32_t size;

    if (file == NULL)
        return -1;
    position = file_tell(file);
    if (position < 0)
        return -1;
    if (file_seek(file, 0, FILE_SEEK_END) != 0)
        return -1;
    size = file_tell(file);
    (void)file_seek(file, position, FILE_SEEK_SET);
    return size;
}

void semantic_OtaEraseRange(uint32_t address, uint32_t length)
{
    while (length != 0u) {
        (void)g2_ota_flash_ops->erase(address);
        if (g2_ota_flash_ops->erase_size >= length)
            break;
        length -= g2_ota_flash_ops->erase_size;
        address += g2_ota_flash_ops->erase_size;
    }
}

/* Select the backend for the received header and erase the image range.
 * A failed lock still erases and unlocks; only the result is cleared. */
uint8_t _evenOtaSetFwAddr(void)
{
    uint8_t ok;

    g2_ota_session.fw_addr = 0u;
    g2_ota_session.offset = 0u;
    g2_ota_transfer.recv_total = 0u;

    if (g2_ota_session.storage_type == OTA_STORAGE_MRAM) {
        if (OTA_MRAM_AREA_SIZE < g2_ota_session.fw_length) {
            OTA_LOG(ELOG_E, fn_set_fw_addr, 0x243u, s_no_space, CLOG_E2, c_no_space,
                    OTA_MRAM_AREA_SIZE, g2_ota_session.fw_length);
            return 0u;
        }
        if (g2_ota_session.fw_length >= OTA_MAX_IMAGE_SIZE + 1u) {
            OTA_LOG(ELOG_E, fn_set_fw_addr, 0x24au, s_overlap, CLOG_E0, c_overlap);
            OTA_LOG(ELOG_E, fn_set_fw_addr, 0x24cu, s_max_size, CLOG_E2, c_max_size,
                    OTA_MAX_IMAGE_SIZE, g2_ota_session.fw_length);
            OTA_LOG(ELOG_E, fn_set_fw_addr, 0x24du, s_reconfigure, CLOG_E0, c_reconfigure);
            return 0u;
        }
        g2_ota_flash_ops = &g2_ota_mram_flash_ops;
        g2_ota_session.fw_addr = OTA_MRAM_APP_ADDR;
        ok = 1u;
    } else if (g2_ota_session.storage_type == OTA_STORAGE_EXTERNAL_FLASH) {
        g2_ota_flash_ops = &g2_ota_xip_flash_ops;
        return 1u;
    } else if (g2_ota_session.storage_type == OTA_STORAGE_FILE &&
               g2_ota_session.fw_data_type == OTA_TYPE_BOOTLOADER) {
        g2_ota_flash_ops = &g2_ota_mram_flash_ops;
        g2_ota_session.fw_addr = OTA_MRAM_BOOTLOADER_ADDR;
        ok = 1u;
    } else {
        ok = 0u;
    }

    if (ok != 0u) {
        int32_t rc = g2_ota_flash_ops->init != NULL ? g2_ota_flash_ops->init() : 0;
        if (rc != 0)
            return 0u;
        rc = g2_ota_flash_ops->lock != NULL ? g2_ota_flash_ops->lock() : 0;
        if (rc != 0) {
            if (g2_ota_flash_ops->deinit != NULL)
                (void)g2_ota_flash_ops->deinit();
            ok = 0u;
        }
        semantic_OtaEraseRange(g2_ota_session.fw_addr, g2_ota_session.fw_length);
        if (g2_ota_flash_ops->unlock != NULL)
            (void)g2_ota_flash_ops->unlock();
    }
    return ok;
}

/* Read back `length` bytes in 4 KiB chunks after invalidating the D-cache;
 * returns the first nonzero memcmp result. */
int32_t _verifyFlashContent(uint32_t address, const uint8_t *expected, uint32_t length,
                            const g2_ota_flash_ops_t *ops)
{
    uint32_t done = 0u;
    uint32_t left = length;
    int32_t rc = 0;

    audio_ble_privacy_cache_maintenance(NULL, 1u);
    while (left != 0u) {
        uint32_t chunk = left >= OTA_CHUNK + 1u ? OTA_CHUNK : left;
        (void)ops->read(g2_ota_verify_buffer, address + done, chunk);
        rc = g2_lfs_memcmp(g2_ota_verify_buffer, expected + done, chunk);
        if (rc != 0) {
            OTA_LOG(ELOG_E, fn_verify, 0x2acu, s_verify_fail, CLOG_E2, c_verify_fail, address, length);
            break;
        }
        done += chunk;
        left -= chunk;
    }
    return rc;
}

/* Append to the page cache; program and verify each full page (or the
 * partial page when `last`). `address` is the absolute end of the data
 * already accepted, so the page start is address - cache fill and must be
 * page aligned inside the session image range. */
uint8_t semantic_OtaBufferedFlashWrite(uint16_t len, const uint8_t *data, uint32_t address, uint8_t last)
{
    uint8_t pages = 0u;
    uint8_t ok = 1u;
    uint32_t start;
    uint32_t base;
    uint32_t end;

    if (address < g2_ota_write_cache.fill)
        return 0u;
    start = address - g2_ota_write_cache.fill;
    base = g2_ota_session.fw_addr;
    end = ((g2_ota_flash_ops->write_size + g2_ota_session.fw_length - 1u) &
           ~(g2_ota_flash_ops->write_size - 1u)) + base;
    if (start < base || start >= end || (start & (g2_ota_flash_ops->write_size - 1u)) != 0u)
        return 0u;

    if (g2_ota_flash_ops->lock != NULL)
        (void)g2_ota_flash_ops->lock();
    while (len != 0u) {
        uint16_t room = (uint16_t)(g2_ota_flash_ops->write_size - g2_ota_write_cache.fill);
        uint16_t n = len < room ? len : room;
        for (uint16_t i = 0u; i < n; i++)
            g2_ota_write_cache.buffer[g2_ota_write_cache.fill++] = data[i];
        len = (uint16_t)(len - n);
        data += n;
        if (last != 0u || g2_ota_write_cache.fill == g2_ota_flash_ops->write_size) {
            uint32_t at = g2_ota_flash_ops->write_size * pages + start;
            if (g2_ota_flash_ops->program(at, g2_ota_write_cache.buffer, g2_ota_flash_ops->write_size) != 0 ||
                _verifyFlashContent(at, g2_ota_write_cache.buffer, g2_ota_write_cache.fill,
                                    g2_ota_flash_ops) != 0) {
                ok = 0u;
                break;
            }
            pages++;
            g2_ota_write_cache.fill = 0u;
            ok = 1u;
        }
    }
    if (g2_ota_flash_ops->unlock != NULL)
        (void)g2_ota_flash_ops->unlock();
    return ok;
}

/* Register the staged image with the boot ROM OTA descriptor list. */
void semantic_OtaCommitDescriptor(void)
{
    (void)am_hal_ota_add_475230(AM_HAL_MRAM_PROGRAM_KEY, g2_ota_session.image_head[0x10],
                                (uint32_t *)(uintptr_t)g2_ota_session.fw_addr);
}

/* Two-byte {subcommand, status} reply on BLE message type 1. */
void _evenOtaReplyToAPP(uint8_t cmd, uint8_t subcommand, uint8_t status)
{
    uint8_t payload[2];

    audio_uart_buffer_zero(payload, sizeof payload, 0u);
    payload[0] = subcommand;
    payload[1] = status;
    OTA_LOG(ELOG_D, fn_reply, 0x328u, s_status, CLOG_D1, c_status, (uint32_t)status);
    if (audio_ble_ota_sync_enabled == 0u)
        (void)Thread_MsgTransport3TxByBle(1u, cmd, payload, 2u);
}

/* "0x"/"0X"-prefixed hexadecimal address, 0 when absent or unparsable. */
uint32_t semantic_OtaParseHexAddress(const char *text)
{
    uint32_t value = 0u;

    if (g2_log_candidate_find_token((const uint8_t *)text, (const uint8_t *)s_hex_lower) == 0u &&
        g2_log_candidate_find_token((const uint8_t *)text, (const uint8_t *)s_hex_upper) == 0u)
        return 0u;
    if (audio_ble_parse_version(text, s_hex_format, &value) == 1)
        return value;
    return 0u;
}

/* Copy a file into MRAM through the page cache. An unopened file is not
 * rejected (its size reads as -1). The zero-size path returns file_close's
 * result when a handle was open. */
int32_t _evenOtaBootloaderWriteFile2MRAM(const char *path, uint32_t address)
{
    uint32_t started;
    int32_t size;

    OTA_LOG(ELOG_I, fn_write_mram, 0x358u, s_mram_start, CLOG_I2, c_mram_start, path, address);
    started = osKernelGetTickCount();
    g2_ota_transfer.file = file_open(path, semantic_OtaSelectFlashOps(OTA_LFS_O_RDONLY));
    g2_ota_transfer.is_open = g2_ota_transfer.file != NULL ? 1u : 0u;
    size = semantic_OtaFileSize(g2_ota_transfer.file);
    if (size == 0) {
        int32_t rc = 0;
        OTA_LOG(ELOG_E, fn_write_mram, 0x363u, s_size_zero, CLOG_E1, c_size_zero, path);
        if (g2_ota_transfer.file != NULL) {
            rc = file_close(g2_ota_transfer.file);
            g2_ota_transfer.file = NULL;
        }
        return rc;
    }
    for (uint32_t offset = 0u; offset < (uint32_t)size; offset += OTA_CHUNK) {
        uint32_t chunk = OTA_CHUNK;
        if ((uint32_t)size < chunk + offset)
            chunk = (uint32_t)size - offset;
        (void)file_read(g2_ota_verify_buffer, 1u, chunk, g2_ota_transfer.file);
        (void)semantic_OtaBufferedFlashWrite((uint16_t)chunk, g2_ota_verify_buffer, offset + address, 1u);
    }
    if (g2_ota_transfer.file != NULL) {
        (void)file_close(g2_ota_transfer.file);
        g2_ota_transfer.file = NULL;
    }
    if (audio_log_flags() & 2u)
        audio_log_extended(ELOG_I, ota_tag, ota_path, fn_write_mram, 0x381u, s_mram_done,
                           osKernelGetTickCount() - started);
    if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
        (void)compress_log_output(CLOG_I1, c_mram_done, c_mram_done, osKernelGetTickCount() - started);
    return 0;
}

/* Write, read back and compare a 4 KiB pattern file; 0 = filesystem healthy. */
int32_t _otaFsHealthProbe(void)
{
    int32_t rc = -1;
    void *file = NULL;
    uint32_t *pattern = file_heap_allocate(OTA_CHUNK);
    uint8_t *readback = file_heap_allocate(OTA_CHUNK);
    uint32_t n;

    if (pattern == NULL || readback == NULL) {
        OTA_LOG(ELOG_E, fn_probe, 0x3a7u, s_probe_alloc, CLOG_E0, c_probe_alloc);
        goto out;
    }
    for (uint32_t i = 0u; i < OTA_CHUNK / 4u; i++)
        pattern[i] = i ^ OTA_PROBE_PATTERN;
    (void)file_remove(s_probe_path);
    file = file_open(s_probe_path, s_mode_wb);
    if (file == NULL) {
        OTA_LOG(ELOG_E, fn_probe, 0x3b4u, s_probe_open_w, CLOG_E0, c_probe_open_w);
        goto out;
    }
    n = file_write(pattern, 1u, OTA_CHUNK, file);
    (void)file_close(file);
    file = NULL;
    if (n != OTA_CHUNK) {
        OTA_LOG(ELOG_E, fn_probe, 0x3bbu, s_probe_write, CLOG_E2, c_probe_write, n, OTA_CHUNK);
        goto out;
    }
    file = file_open(s_probe_path, s_mode_rb);
    if (file == NULL) {
        OTA_LOG(ELOG_E, fn_probe, 0x3c1u, s_probe_open_r, CLOG_E0, c_probe_open_r);
        goto out;
    }
    n = file_read(readback, 1u, OTA_CHUNK, file);
    (void)file_close(file);
    file = NULL;
    if (n != OTA_CHUNK) {
        OTA_LOG(ELOG_E, fn_probe, 0x3c8u, s_probe_read, CLOG_E2, c_probe_read, n, OTA_CHUNK);
        goto out;
    }
    if (g2_lfs_memcmp(pattern, readback, OTA_CHUNK) != 0) {
        OTA_LOG(ELOG_E, fn_probe, 0x3cdu, s_probe_mismatch, CLOG_E0, c_probe_mismatch);
        goto out;
    }
    rc = 0;
out:
    if (file != NULL)
        (void)file_close(file);
    (void)file_remove(s_probe_path);
    if (pattern != NULL)
        file_heap_free(pattern);
    if (readback != NULL)
        file_heap_free(readback);
    if (rc == 0)
        OTA_LOG(ELOG_D, fn_probe, 0x3dcu, s_probe_pass, CLOG_D0, c_probe_pass);
    else
        OTA_LOG(ELOG_W, fn_probe, 0x3deu, s_probe_fail, CLOG_W0, c_probe_fail);
    return rc;
}

/* Probe, and on failure format littlefs and probe again: 0 healthy, -1 not. */
int32_t _otaFsHealthCheckAndHeal(void)
{
    int rc;

    if (_otaFsHealthProbe() == 0)
        return 0;
    OTA_LOG(ELOG_W, fn_heal, 0x3efu, s_fs_broken, CLOG_W0, c_fs_broken);
    rc = littlefs_format_4761d2();
    if (rc != 0) {
        OTA_LOG(ELOG_E, fn_heal, 0x3f2u, s_format_failed, CLOG_E1, c_format_failed, rc);
        return -1;
    }
    if (_otaFsHealthProbe() != 0) {
        OTA_LOG(ELOG_E, fn_heal, 0x3f8u, s_still_broken, CLOG_E0, c_still_broken);
        return -1;
    }
    OTA_LOG(ELOG_W, fn_heal, 0x3fbu, s_heal_done, CLOG_W0, c_heal_done);
    return 0;
}
