/* OTA import engine, stock D:\01_workspace\s200_ap510b_iar_git\platform\protocols\ota_service\ota_service.c
 * (log tag "ota.service").
 * Native _fileCmdParse 0x445660..0x446c5e, _fileRawDataParse 0x446d40..0x447a1a,
 * _fileCaculateCRC 0x447a60..0x447e94; literal pools follow each body.
 *
 * Frames reach these through the 0xAA transport dispatcher 0x448670:
 * 0xC0 -> _fileCmdParse(data[0], data + 1, len - 1), 0xC1 -> _fileRawDataParse(data, len).
 * Replies go out through _evenOtaReplyToAPP(cmd, subcommand, status).
 *
 * The 0x70-byte transfer object (RAM 0x20071ff0) and the 0x60-byte session
 * object (RAM 0x20072730) are shared with the export engine _exportFileParse
 * 0x447f00, which is the only caller of _fileCaculateCRC; the EFS service has
 * its own _fileCaculateCRC at 0x4567b8, so this one carries the address-suffixed
 * name ota_file_calculate_crc_447a60 (called by _exportFileParse in a-03). */
#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

/* OTA flash backend vtable; RAM pointer 0x2000301c, MRAM default 0x2000038c. */
typedef struct {
    uint32_t sector_size;                /* +0x00 cache / program granule */
    void *reserved_04;                   /* +0x04 */
    void *reserved_08;                   /* +0x08 */
    void (*finish)(void);                /* +0x0c called after a firmware result check */
    void (*lock)(void);                  /* +0x10 used by semantic_OtaBufferedFlashWrite */
    void (*unlock)(void);                /* +0x14 */
    void *reserved_18;                   /* +0x18 */
    int32_t (*program)(uint32_t, const uint8_t *, uint32_t); /* +0x1c */
} g2_ota_flash_ops_t;

/* Write-back cache in front of the flash backend (RAM 0x20003020). */
typedef struct {
    uint8_t *buffer;                     /* +0x0 */
    uint16_t fill;                       /* +0x4 */
} g2_ota_write_cache_t;

/* Shared OTA transfer object (RAM 0x20071ff0, cleared as 0x70 bytes). */
typedef struct {
    void *file;                          /* +0x00 open file handle */
    uint8_t is_open;                     /* +0x04 */
    char path[0x50];                     /* +0x05 target path from the header */
    uint8_t pad_55[3];                   /* +0x55 */
    uint32_t file_size;                  /* +0x58 header fwLength */
    uint32_t calc_crc;                   /* +0x5c running CRC-32C (0x47cbc4) */
    uint32_t reserved_60;                /* +0x60 */
    uint32_t recv_total;                 /* +0x64 bytes accepted */
    uint32_t reserved_68;                /* +0x68 */
    uint8_t progress;                    /* +0x6c percent */
    uint8_t started;                     /* +0x6d set by subcommand 2 */
    uint8_t pad_6e[2];                   /* +0x6e */
} g2_ota_transfer_t;
_Static_assert(sizeof(g2_ota_transfer_t) == 0x70, "stock OTA transfer object is 0x70 bytes");
_Static_assert(offsetof(g2_ota_transfer_t, recv_total) == 0x64, "recvTotalLen at +0x64");

/* Shared OTA session object (RAM 0x20072730, cleared as 0x60 bytes). Bytes
 * +0x04..+0x33 are a verbatim copy of the first 0x30 header bytes. */
typedef struct {
    uint8_t state;                       /* +0x00 1 = header accepted */
    uint8_t pad_01[3];                   /* +0x01 */
    uint32_t encrypted;                  /* +0x04 header +0x00 */
    uint32_t fw_start_addr;              /* +0x08 header +0x04 */
    uint32_t fw_length;                  /* +0x0c header +0x08 */
    uint32_t fw_crc;                     /* +0x10 header +0x0c */
    uint8_t header_reserved[0x10];       /* +0x14 header +0x10..+0x1f */
    uint32_t version;                    /* +0x24 header +0x20 */
    uint32_t fw_data_type;               /* +0x28 header +0x24, eOTATransmitType_* */
    uint32_t storage_type;               /* +0x2c header +0x28: 0 MRAM, 1 external XIP, 3 file */
    uint32_t image_id;                   /* +0x30 header +0x2c */
    uint8_t *buffer;                     /* +0x34 = RAM 0x2034bc10 */
    uint32_t fw_addr;                    /* +0x38 program address / flash offset */
    uint32_t offset;                     /* +0x3c bytes written this session */
    uint8_t image_head[0x20];            /* +0x40 first 32 image bytes */
} g2_ota_session_t;
_Static_assert(sizeof(g2_ota_session_t) == 0x60, "stock OTA session object is 0x60 bytes");
_Static_assert(offsetof(g2_ota_session_t, fw_data_type) == 0x28, "fwDataType at +0x28");

enum {
    OTA_CID_START = 0u,                  /* eOTATransmitCID_OTA_TRANSMIT_START */
    OTA_CID_INFORMATION = 1u,            /* eOTATransmitCID_OTA_TRANSMIT_INFORMATION */
    OTA_CID_DATA_BEGIN = 2u,             /* unnamed in the logs; arms raw-data parsing */
    OTA_CID_RESULT_CHECK = 3u,           /* eOTATransmitCID_OTA_TRANSMIT_RESULT_CHECK */
};

enum {
    OTA_TYPE_GLASSES_FIRMWARE = 0u,
    OTA_TYPE_BOOTLOADER = 1u,
    OTA_TYPE_FONT = 2u,
    OTA_TYPE_TOUCH_BIN = 3u,
    OTA_TYPE_AUDIO_BIN = 4u,
    OTA_TYPE_BLE9305_BIN = 5u,
    OTA_TYPE_BOX = 6u,
    OTA_TYPE_OTHER_BIN = 7u,
};

enum { OTA_STORAGE_MRAM = 0u, OTA_STORAGE_EXTERNAL_FLASH = 1u, OTA_STORAGE_FILE = 3u };

#define OTA_CMD_CONTROL 0xc0u
#define OTA_CMD_RAW_DATA 0xc1u
#define OTA_HEADER_LENGTH 0x80u          /* 0x30 header words + 0x50 path */
#define OTA_CHUNK 0x1000u
#define OTA_FS_O_RDONLY 1u               /* littlefs flags fed to semantic_OtaSelectFlashOps */
#define OTA_FS_O_RDWR 3u
#define OTA_FS_O_CREAT 0x100u
#define OTA_LFS_ERR_NOENT (-2)
#define OTA_BOOTLOADER_FLAG_UPDATE 0x55555555u

extern g2_ota_transfer_t g2_ota_transfer;                 /* RAM 0x20071ff0 */
extern uint8_t audio_ble_ota_export_state[];              /* RAM 0x20072730, session object */
#define g2_ota_session (*(g2_ota_session_t *)(void *)audio_ble_ota_export_state)
extern uint32_t g2_ota_start_tick;                        /* RAM 0x20074844 */
extern uint32_t g2_ota_data_start_tick;                   /* RAM 0x20074848 */
extern uint32_t g2_ota_last_tick;                         /* RAM 0x2007484c */
extern volatile uint8_t audio_ble_ota_sync_enabled;       /* RAM 0x20074ff3 */
extern uint8_t g2_ota_crc_failed;                         /* RAM 0x20075007 */
extern const g2_ota_flash_ops_t *g2_ota_flash_ops;        /* RAM 0x2000301c */
extern g2_ota_write_cache_t g2_ota_write_cache;           /* RAM 0x20003020 */
extern const g2_ota_flash_ops_t g2_ota_mram_flash_ops;    /* RAM 0x2000038c */
extern uint8_t g2_ota_cache_buffer[];                     /* RAM 0x2034bc10 */
extern uint8_t g2_ota_verify_buffer[OTA_CHUNK];           /* RAM 0x2034cc20 */

extern const char *semantic_OtaSelectFlashOps(uint32_t flags);   /* 0x4448f4 lfs flags -> fopen mode */
extern int32_t semantic_OtaFileSize(void *file);                 /* 0x44494c */
extern uint8_t _evenOtaSetFwAddr(void);                          /* 0x4449c4 */
extern uint8_t semantic_OtaBufferedFlashWrite(uint16_t len, const uint8_t *data,
                                              uint32_t address, uint8_t last); /* 0x444c9c */
extern void semantic_OtaCommitDescriptor(void);                  /* 0x444df0 */
extern void _evenOtaReplyToAPP(uint8_t cmd, uint8_t subcommand, uint8_t status); /* 0x444e08 */
extern void _RPC_SystemOtaStatusSync(uint8_t active);            /* 0x444e90 */
extern uint32_t semantic_OtaParseHexAddress(const char *text);   /* 0x444f26 */
extern int32_t _evenOtaBootloaderWriteFile2MRAM(const char *path, uint32_t address); /* 0x444f60 */
extern int32_t _otaFsHealthCheckAndHeal(void);                   /* 0x44545c */
extern void RPC_SystemTimeSync(void);                            /* 0x44a2b2 */
extern void APP_ConnectParamOTASetFastMode(void);                /* 0x4781f4 */
extern void APP_EvenOtaDisconnect(void);                         /* 0x4bdd18 */
extern void audio_ble_comm_link_delayed(void);                   /* 0x4b81b8 */
extern void audio_ble_ota_export_mode_set(uint32_t requested);   /* 0x478860 OTA_FileSystemSetBootloaderFlag */
extern uint32_t audio_event_loop_remove_delayed(void (*callback)(void)); /* 0x476ace */
extern void audio_event_loop_push_delayed(void (*callback)(void), uint32_t argument, uint32_t delay); /* 0x47697e */
extern uint32_t osKernelGetTickCount(void);                      /* 0x4490cc */
extern void *file_open(const char *path, const char *mode);      /* 0x474550 */
extern int32_t file_close(void *file);                           /* 0x4745f4 */
extern uint32_t file_read(void *buffer, uint32_t size, uint32_t count, void *file); /* 0x474634 */
extern uint32_t file_write(const void *buf, uint32_t size, uint32_t count, void *file); /* 0x474682 */
extern int32_t file_seek(void *file, int32_t offset, int32_t origin); /* 0x474814 */
extern int32_t file_remove(const char *path);                    /* 0x47498c */
extern uint32_t g2_norflash_erase_lower_47075c(uint32_t address); /* 0x47075c 4 KiB sector */
extern int32_t norflash_write_4709c0(int32_t address, const uint8_t *buffer, uint32_t size);
extern int32_t g2_norflash_read_lower_4709c8(int32_t address, uint8_t *buffer, uint32_t size);
extern void file_crc32c_update_47cbc4(const uint8_t *data, uint32_t length, uint32_t *crc);
extern uint64_t audio_uart_ring_u64_div_47cc60(uint32_t low, uint32_t high,
                                               uint32_t divisor_low, uint32_t divisor_high); /* __aeabi_uldivmod */
extern void *aeabi_memset_43c0e4(void *dst, uint32_t len, int32_t value);
extern void *audio_queue_copy_bytes(void *dst, const void *src, uint32_t len); /* 0x439be4 memcpy */
extern uint32_t g2_log_module_length(const char *text);          /* 0x44a43c strlen */
extern int32_t audio_ble_hci_vendor_compare_44b610(const void *a, const void *b, uint32_t len); /* strncmp */
extern int32_t g2_lfs_memcmp(const void *a, const void *b, uint32_t length); /* 0x4751c8 */
extern uint32_t audio_log_flags(void);                           /* 0x43d0ce */
extern void audio_log_extended(uint8_t, const char *, const char *, const char *, uint32_t, const char *, ...); /* 0x43d574 */
extern uint32_t compress_log_output(uint32_t, const char *, const char *, ...); /* 0x43ce9e */

static const char module_tag[] = "ota.service"; /* ROM 0x78b660 */
static const char source_file[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\platform\\protocols\\ota_service\\ota_service.c"; /* ROM 0x6e8f74 */
static const char cmd_parse_fn[] = "_fileCmdParse";      /* ROM 0x787bb0 */
static const char raw_parse_fn[] = "_fileRawDataParse";  /* ROM 0x7816c4 */
static const char crc_fn[] = "_fileCaculateCRC";         /* ROM 0x7816d8 */
static const char path_firmware[] = "ota/s200_firmware_ota.bin";  /* ROM 0x76f25c */
static const char path_bootloader[] = "ota/s200_bootloader.bin";  /* ROM 0x779dfc */
static const char path_touch[] = "firmware/touch.bin";            /* ROM 0x78164c */
static const char path_codec[] = "firmware/codec.bin";            /* ROM 0x781660 */
static const char path_em9305[] = "firmware/ble_em9305.bin";      /* ROM 0x779e14 */
static const char path_box[] = "firmware/box.bin";                /* ROM 0x781674 */

/* Stock pairs every message with a "[ota.service]"-prefixed compact copy; the
 * ROM comments give plain / compact addresses. */
#define OTA_LOG(fn, level, line, mask, fmt, ...) do { \
    if (audio_log_flags() & 2u) \
        audio_log_extended((level), module_tag, source_file, (fn), (line), fmt, ##__VA_ARGS__); \
    if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u)) \
        (void)compress_log_output((mask), "[ota.service]" fmt, "[ota.service]" fmt, ##__VA_ARGS__); \
} while (0)

#define OTA_FILE_CLOSE(slot, err) do { \
    if (*(slot) == NULL) { (err) = 0; } \
    else { (err) = file_close(*(slot)); *(slot) = NULL; } \
} while (0)

/* Accept one verified chunk: CRC, counters, ACK and progress percentage. */
#define OTA_CHUNK_ACCEPT(xfer, session, data, len) do { \
    file_crc32c_update_47cbc4((data), (len), &(xfer)->calc_crc); \
    (session)->offset += (len); \
    (xfer)->recv_total += (len); \
    _evenOtaReplyToAPP(OTA_CMD_RAW_DATA, 2u, 0u); \
    if ((xfer)->file_size != 0u) { \
        uint64_t scaled = (uint64_t)(xfer)->recv_total * 100u; \
        (xfer)->progress = (uint8_t)audio_uart_ring_u64_div_47cc60((uint32_t)scaled, \
            (uint32_t)(scaled >> 32), (xfer)->file_size, 0u); \
    } \
} while (0)

/* Speed log after an MRAM or file chunk: KiB/s for this packet against the
 * subcommand-2 tick, and overall against the start tick. */
#define OTA_SPEED_LOG(line, xfer, len) do { \
    g2_ota_last_tick = osKernelGetTickCount(); \
    OTA_LOG(raw_parse_fn, 4u, (line), 0x11000000u, \
            "OTA update %d%% eclipse time: %d ms speed : %d(%d) KB/S", /* ROM 0x720f30 / 0x6fbbf4 */ \
            (xfer)->progress, g2_ota_last_tick - g2_ota_start_tick, \
            (((uint32_t)(len) * 1000u) >> 10) / (g2_ota_last_tick - g2_ota_data_start_tick), \
            (((xfer)->recv_total * 1000u) >> 10) / (g2_ota_last_tick - g2_ota_start_tick)); \
} while (0)

void _fileCmdParse(uint8_t cid, const uint8_t *data, uint32_t len)
{
    g2_ota_transfer_t *const xfer = &g2_ota_transfer;
    g2_ota_session_t *const session = &g2_ota_session;
    const char *const path = xfer->path;
    const char *target;
    uint8_t reply[2];
    int32_t ret = -1;
    int32_t err;

    (void)aeabi_memset_43c0e4(reply, sizeof reply, 0);

    if (cid == OTA_CID_START) {
        g2_ota_start_tick = osKernelGetTickCount();
        _RPC_SystemOtaStatusSync(1u);
        OTA_LOG(cmd_parse_fn, 4u, 0x40bu, 0x10400000u,
                "eOTATransmitCID_OTA_TRANSMIT_START = %d ms", g2_ota_start_tick); /* ROM 0x740d38 / 0x720e88 */
        if (audio_ble_ota_sync_enabled == 0u) {
            (void)audio_event_loop_remove_delayed(RPC_SystemTimeSync);
            APP_ConnectParamOTASetFastMode();
            (void)audio_event_loop_remove_delayed(audio_ble_comm_link_delayed);
        }
        if (xfer->is_open == 1u) {
            OTA_LOG(cmd_parse_fn, 2u, 0x413u, 0x08000000u,
                    "file is open, close file first"); /* ROM 0x762c30 / 0x740d64 */
            OTA_FILE_CLOSE(&xfer->file, err);
            if (err < 0) {
                OTA_LOG(cmd_parse_fn, 1u, 0x416u, 0x04800000u,
                        "ERR-Close failed %s : %d", path, err); /* ROM 0x76f128 / 0x74bdc4 */
                _evenOtaReplyToAPP(OTA_CMD_CONTROL, 0u, 10u);
                return;
            }
        }
        (void)aeabi_memset_43c0e4(xfer, sizeof *xfer, 0);
        (void)aeabi_memset_43c0e4(session, sizeof *session, 0);
        if (_otaFsHealthCheckAndHeal() != 0) {
            OTA_LOG(cmd_parse_fn, 1u, 0x421u, 0x04000000u,
                    "OTA: fs heal failed, refuse this OTA"); /* ROM 0x74bedc / 0x72b8e4 */
            _evenOtaReplyToAPP(OTA_CMD_CONTROL, 0u, 10u);
            return;
        }
        session->state = 0u;
        session->buffer = g2_ota_cache_buffer;
        _evenOtaReplyToAPP(OTA_CMD_CONTROL, 0u, 0u);
        return;
    }

    if (cid == OTA_CID_DATA_BEGIN) {
        xfer->started = 1u;
        g2_ota_data_start_tick = osKernelGetTickCount();
        return;
    }

    if (cid == OTA_CID_RESULT_CHECK) {
        OTA_LOG(cmd_parse_fn, 4u, 0x4cfu, 0x10000000u,
                "eOTATransmitCID_OTA_TRANSMIT_RESULT_CHECK"); /* ROM 0x740e98 / 0x720ef8 */
        OTA_LOG(cmd_parse_fn, 4u, 0x4d0u, 0x10800000u,
                "calc bin crc 0x%x(0x%x)", xfer->calc_crc, session->fw_crc); /* ROM 0x779e2c / 0x74bf7c */
        switch (session->fw_data_type) {
        case OTA_TYPE_GLASSES_FIRMWARE:
            OTA_LOG(cmd_parse_fn, 4u, 0x4d3u, 0x10000000u,
                    "eOTATransmitType_GLASSES_FIRMWARE"); /* ROM 0x75744c / 0x736374 */
            if (session->storage_type == OTA_STORAGE_MRAM) {
                if (xfer->calc_crc == session->fw_crc) {
                    _evenOtaReplyToAPP(OTA_CMD_CONTROL, 3u, 8u);
                    OTA_LOG(cmd_parse_fn, 4u, 0x4d8u, 0x10000000u,
                            "crc verify success"); /* ROM 0x78169c / 0x762d30 */
                    g2_ota_crc_failed = 0u;
                    semantic_OtaCommitDescriptor();
                    if (audio_ble_ota_sync_enabled == 0u) {
                        (void)audio_event_loop_remove_delayed(APP_EvenOtaDisconnect);
                        audio_event_loop_push_delayed(APP_EvenOtaDisconnect, 0u, 3000u);
                    }
                    _evenOtaReplyToAPP(OTA_CMD_CONTROL, 4u, 9u);
                } else {
                    OTA_LOG(cmd_parse_fn, 1u, 0x4e3u, 0x04000000u,
                            "crc verify failed"); /* ROM 0x7816b0 / 0x762d50 */
                    g2_ota_crc_failed = 1u;
                    _evenOtaReplyToAPP(OTA_CMD_CONTROL, 3u, 7u);
                }
                if (g2_ota_flash_ops->finish != NULL)
                    g2_ota_flash_ops->finish();
                session->state = 0u;
                xfer->calc_crc = 0u;
                g2_ota_flash_ops = &g2_ota_mram_flash_ops;
            } else if (session->storage_type == OTA_STORAGE_EXTERNAL_FLASH) {
                OTA_LOG(cmd_parse_fn, 4u, 0x4eeu, 0x10800000u,
                        "External flash CRC verification: calculated=0x%x, expected=0x%x", /* ROM 0x70d6e4 / 0x6eec88 */
                        xfer->calc_crc, session->fw_crc);
                if (xfer->calc_crc == session->fw_crc) {
                    _evenOtaReplyToAPP(OTA_CMD_CONTROL, 3u, 8u);
                    OTA_LOG(cmd_parse_fn, 4u, 0x4f2u, 0x10000000u,
                            "External flash crc verify success"); /* ROM 0x757470 / 0x7363a4 */
                    g2_ota_crc_failed = 0u;
                    _evenOtaReplyToAPP(OTA_CMD_CONTROL, 4u, 9u);
                } else {
                    OTA_LOG(cmd_parse_fn, 1u, 0x4f6u, 0x04000000u,
                            "External flash crc verify failed"); /* ROM 0x757494 / 0x7363d4 */
                    g2_ota_crc_failed = 1u;
                    _evenOtaReplyToAPP(OTA_CMD_CONTROL, 3u, 7u);
                }
                session->state = 0u;
                xfer->calc_crc = 0u;
            }
            break;
        case OTA_TYPE_FONT:
            OTA_LOG(cmd_parse_fn, 4u, 0x507u, 0x10000000u, "eOTATransmitType_FONT"); /* ROM 0x779e44 / 0x7574b8 */
            break;
        case OTA_TYPE_BOOTLOADER:
            OTA_LOG(cmd_parse_fn, 4u, 0x502u, 0x10000000u, "eOTATransmitType_BOOTLOADER"); /* ROM 0x76f2cc / 0x740ec4 */
            break;
        case OTA_TYPE_AUDIO_BIN:
            OTA_LOG(cmd_parse_fn, 4u, 0x511u, 0x10000000u, "eOTATransmitType_AUDIO_BIN"); /* ROM 0x76f304 / 0x74bfcc */
            break;
        case OTA_TYPE_TOUCH_BIN:
            OTA_LOG(cmd_parse_fn, 4u, 0x50cu, 0x10000000u, "eOTATransmitType_TOUCH_BIN"); /* ROM 0x76f2e8 / 0x74bfa4 */
            break;
        case OTA_TYPE_BOX:
            OTA_LOG(cmd_parse_fn, 4u, 0x51bu, 0x10000000u, "eOTATransmitType_BOX"); /* ROM 0x779e5c / 0x7574dc */
            break;
        case OTA_TYPE_BLE9305_BIN:
            OTA_LOG(cmd_parse_fn, 4u, 0x516u, 0x10000000u, "eOTATransmitType_BLE9305_BIN"); /* ROM 0x762d70 / 0x740ef0 */
            break;
        default:
            break;
        }

        /* A glasses-firmware image on external flash falls through to this
         * second check as well, so stock replies twice for it. */
        if (session->storage_type != OTA_STORAGE_FILE) {
            if (session->storage_type != OTA_STORAGE_EXTERNAL_FLASH)
                return;
            if (xfer->calc_crc == session->fw_crc) {
                g2_ota_crc_failed = 0u;
                OTA_LOG(cmd_parse_fn, 4u, 0x555u, 0x10000000u,
                        "eOTATransmitType_EXTERNAL_FLASH crc verify success"); /* ROM 0x72ba1c / 0x70d764 */
                _evenOtaReplyToAPP(OTA_CMD_CONTROL, 3u, 8u);
            } else {
                g2_ota_crc_failed = 1u;
                OTA_LOG(cmd_parse_fn, 4u, 0x55au, 0x10000000u,
                        "eOTATransmitType_EXTERNAL_FLASH crc verify failed"); /* ROM 0x72ba50 / 0x70d7a4 */
                _evenOtaReplyToAPP(OTA_CMD_CONTROL, 3u, 7u);
            }
            (void)aeabi_memset_43c0e4(xfer, sizeof *xfer, 0);
            session->offset = 0u;
            xfer->recv_total = 0u;
            return;
        }

        if (xfer->is_open != 1u) {
            OTA_LOG(cmd_parse_fn, 1u, 0x52du, 0x04400000u,
                    "ERR-File not opened, cannot close %s", path); /* ROM 0x74bff4 / 0x72b9e8 */
            _evenOtaReplyToAPP(OTA_CMD_CONTROL, 3u, 7u);
            return;
        }
        OTA_FILE_CLOSE(&xfer->file, err);
        if (err < 0) {
            OTA_LOG(cmd_parse_fn, 1u, 0x527u, 0x04800000u,
                    "ERR-Close failed %s : %d", path, err); /* ROM 0x76f128 / 0x74bdc4 */
            _evenOtaReplyToAPP(OTA_CMD_CONTROL, 3u, 7u);
            return;
        }
        xfer->is_open = 0u;
        OTA_LOG(cmd_parse_fn, 4u, 0x531u, 0x10c00000u,
                "offset = %d, recvTotalLen = %d,fileSize = %d", /* ROM 0x736404 / 0x717230 */
                session->offset, xfer->recv_total, xfer->file_size);
        if (xfer->calc_crc == session->fw_crc) {
            g2_ota_crc_failed = 0u;
            _evenOtaReplyToAPP(OTA_CMD_CONTROL, 3u, 8u);
            if (session->fw_data_type == OTA_TYPE_GLASSES_FIRMWARE) {
                audio_ble_ota_export_mode_set(OTA_BOOTLOADER_FLAG_UPDATE);
                _evenOtaReplyToAPP(OTA_CMD_CONTROL, 4u, 9u);
                if (audio_ble_ota_sync_enabled == 0u) {
                    (void)audio_event_loop_remove_delayed(APP_EvenOtaDisconnect);
                    audio_event_loop_push_delayed(APP_EvenOtaDisconnect, 0u, 3000u);
                }
                _RPC_SystemOtaStatusSync(0u);
            } else if (session->fw_data_type == OTA_TYPE_BOOTLOADER) {
                int32_t status = _evenOtaBootloaderWriteFile2MRAM(path, session->fw_addr);
                if (status != 0) {
                    OTA_LOG(cmd_parse_fn, 1u, 0x544u, 0x04400000u,
                            "ERR-Write bootloader to internal MRAM failed %d", status); /* ROM 0x736434 / 0x70d724 */
                    _evenOtaReplyToAPP(OTA_CMD_CONTROL, 3u, 7u);
                    return;
                }
            }
        } else {
            g2_ota_crc_failed = 1u;
            (void)file_remove(path);
            _evenOtaReplyToAPP(OTA_CMD_CONTROL, 3u, 7u);
        }
        (void)aeabi_memset_43c0e4(xfer, sizeof *xfer, 0);
        session->offset = 0u;
        xfer->recv_total = 0u;
        return;
    }

    if (cid != OTA_CID_INFORMATION)
        return;

    OTA_LOG(cmd_parse_fn, 4u, 0x430u, 0x10400000u,
            "eOTATransmitCID_OTA_TRANSMIT_INFORMATION = %d", len); /* ROM 0x736284 / 0x717014 */
    xfer->recv_total = 0u;
    if (len != OTA_HEADER_LENGTH) {
        OTA_LOG(cmd_parse_fn, 4u, 0x434u, 0x10000000u, "header too short\n"); /* ROM 0x7815e8 / 0x762c50 */
        _evenOtaReplyToAPP(OTA_CMD_CONTROL, 1u, 1u);
        return;
    }
    xfer->calc_crc = 0u;
    (void)audio_queue_copy_bytes(&session->encrypted, data, 0x30u);
    (void)audio_queue_copy_bytes(xfer->path, data + 0x30, sizeof xfer->path);
    xfer->file_size = session->fw_length;
    OTA_LOG(cmd_parse_fn, 4u, 0x441u, 0x10000000u,
            "============= fw header start ==============="); /* ROM 0x7362b4 / 0x717050 */
    OTA_LOG(cmd_parse_fn, 4u, 0x442u, 0x10400000u, "encrypted = 0x%x", session->encrypted); /* ROM 0x7815fc / 0x762c70 */
    OTA_LOG(cmd_parse_fn, 4u, 0x443u, 0x10400000u, "version = 0x%x", session->version); /* ROM 0x787bc0 / 0x76f1ec */
    OTA_LOG(cmd_parse_fn, 4u, 0x444u, 0x10400000u, "fwLength = 0x%x", session->fw_length); /* ROM 0x787bd0 / 0x762c90 */
    OTA_LOG(cmd_parse_fn, 4u, 0x445u, 0x10400000u, "fwCrc = 0x%x", session->fw_crc); /* ROM 0x787be0 / 0x76f208 */
    OTA_LOG(cmd_parse_fn, 4u, 0x446u, 0x10400000u, "fwStartAddr = 0x%x", session->fw_start_addr); /* ROM 0x781610 / 0x762cb0 */
    OTA_LOG(cmd_parse_fn, 4u, 0x447u, 0x10400000u, "fwDataType = 0x%x", session->fw_data_type); /* ROM 0x781624 / 0x762cd0 */
    OTA_LOG(cmd_parse_fn, 4u, 0x448u, 0x10400000u, "storageType = 0x%x", session->storage_type); /* ROM 0x781638 / 0x762cf0 */
    OTA_LOG(cmd_parse_fn, 4u, 0x449u, 0x10400000u, "imageId = 0x%x", session->image_id); /* ROM 0x787bf0 / 0x76f224 */
    OTA_LOG(cmd_parse_fn, 4u, 0x44au, 0x10400000u, "filePath = %s", path); /* ROM 0x787c00 / 0x76f240 */
    OTA_LOG(cmd_parse_fn, 4u, 0x44bu, 0x10000000u,
            "============= fw header end ==============="); /* ROM 0x740d90 / 0x71708c */

    switch (session->fw_data_type) {
    case OTA_TYPE_GLASSES_FIRMWARE:
        target = path_firmware;
        OTA_LOG(cmd_parse_fn, 4u, 0x451u, 0x10400000u,
                "eOTATransmitType_GLASSES_FIRMWARE pTargetPath = %s", target); /* ROM 0x72b918 / 0x70d664 */
        session->fw_addr = 0u;
        session->offset = 0u;
        xfer->recv_total = 0u;
        if (session->storage_type == OTA_STORAGE_MRAM) {
            uint8_t ok;
            g2_ota_write_cache.fill = 0u;
            ok = _evenOtaSetFwAddr();
            OTA_LOG(cmd_parse_fn, 4u, 0x458u, 0x10800000u,
                    "OTA process start from beginning addr 0x%x, bResult = %d", /* ROM 0x7170c8 / 0x6fbbac */
                    session->fw_addr, ok);
            if (ok == 0u) {
                _evenOtaReplyToAPP(OTA_CMD_CONTROL, 1u, 1u);
                session->state = 0u;
                return;
            }
        }
        break;
    case OTA_TYPE_FONT:
        target = path;
        (void)_evenOtaSetFwAddr();
        OTA_LOG(cmd_parse_fn, 4u, 0x46cu, 0x10400000u,
                "eOTATransmitType_FONT pTargetPath = %s", path); /* ROM 0x74bf04 / 0x72b94c */
        break;
    case OTA_TYPE_BOOTLOADER:
        target = path_bootloader;
        (void)_evenOtaSetFwAddr();
        OTA_LOG(cmd_parse_fn, 4u, 0x465u, 0x10400000u,
                "eOTATransmitType_BOOTLOADER pTargetPath = %s", target); /* ROM 0x7362e4 / 0x717104 */
        break;
    case OTA_TYPE_AUDIO_BIN:
        target = path_codec;
        OTA_LOG(cmd_parse_fn, 4u, 0x478u, 0x10400000u,
                "eOTATransmitType_AUDIO_BIN pTargetPath = %s", target); /* ROM 0x740de8 / 0x71717c */
        break;
    case OTA_TYPE_TOUCH_BIN:
        target = path_touch;
        OTA_LOG(cmd_parse_fn, 4u, 0x472u, 0x10400000u,
                "eOTATransmitType_TOUCH_BIN pTargetPath = %s", target); /* ROM 0x740dbc / 0x717140 */
        break;
    case OTA_TYPE_BOX:
        target = path_box;
        OTA_LOG(cmd_parse_fn, 4u, 0x484u, 0x10400000u,
                "eOTATransmitType_BOX pTargetPath = %s", target); /* ROM 0x74bf2c / 0x72b980 */
        break;
    case OTA_TYPE_BLE9305_BIN:
        target = path_em9305;
        OTA_LOG(cmd_parse_fn, 4u, 0x47eu, 0x10400000u,
                "eOTATransmitType_BLE9305_BIN pTargetPath = %s", target); /* ROM 0x736314 / 0x7171b8 */
        break;
    case OTA_TYPE_OTHER_BIN:
        target = path;
        OTA_LOG(cmd_parse_fn, 4u, 0x48au, 0x10400000u,
                "eOTATransmitType_OTHER_BIN pTargetPath = %s", path); /* ROM 0x740e14 / 0x7171f4 */
        break;
    default:
        target = path;
        OTA_LOG(cmd_parse_fn, 4u, 0x490u, 0x10400000u,
                "other type pTargetPath = %s", path); /* ROM 0x76f278 / 0x740e40 */
        break;
    }

    if (session->storage_type == OTA_STORAGE_FILE) {
        /* The header path must start with the per-type target; font, other
         * and unknown types compare the path with itself. */
        if (target == NULL ||
            audio_ble_hci_vendor_compare_44b610(path, target, g2_log_module_length(target)) != 0) {
            OTA_LOG(cmd_parse_fn, 1u, 0x4b0u, 0x04400000u, "path error %s", path); /* ROM 0x787c10 / 0x76f2b0 */
            _evenOtaReplyToAPP(OTA_CMD_CONTROL, 1u, 1u);
            return;
        }
        OTA_LOG(cmd_parse_fn, 4u, 0x496u, 0x10400000u, "pTargetPath = %s", path); /* ROM 0x781688 / 0x762d10 */
        err = file_remove(path);
        if (err < 0 && err != OTA_LFS_ERR_NOENT)
            OTA_LOG(cmd_parse_fn, 1u, 0x49au, 0x04800000u,
                    "ERR-Delete failed %s : %d", path, err); /* ROM 0x76f294 / 0x74bf54 */

        /* Create (or truncate) the file, close it, then reopen read/write. */
        xfer->file = file_open(path, semantic_OtaSelectFlashOps(OTA_FS_O_CREAT | OTA_FS_O_RDWR));
        if (xfer->file == NULL) {
            err = ret;
            xfer->is_open = 0u;
        } else {
            err = 0;
            xfer->is_open = 1u;
        }
        if (err < 0) {
            OTA_LOG(cmd_parse_fn, 1u, 0x49eu, 0x04800000u,
                    "ERR-Open failed %s : %d", path, err); /* ROM 0x779d3c / 0x74bd9c */
            _evenOtaReplyToAPP(OTA_CMD_CONTROL, 1u, 6u);
            return;
        }
        OTA_FILE_CLOSE(&xfer->file, err);
        if (err < 0) {
            OTA_LOG(cmd_parse_fn, 1u, 0x4a4u, 0x04800000u,
                    "ERR-Close failed %s : %d", path, err); /* ROM 0x76f128 / 0x74bdc4 */
            _evenOtaReplyToAPP(OTA_CMD_CONTROL, 1u, 6u);
            return;
        }
        xfer->file = file_open(path, semantic_OtaSelectFlashOps(OTA_FS_O_RDWR));
        if (xfer->file == NULL) {
            xfer->is_open = 0u;
        } else {
            ret = 0;
            xfer->is_open = 1u;
        }
        if (ret < 0) {
            OTA_LOG(cmd_parse_fn, 1u, 0x4abu, 0x04800000u,
                    "ERR-Open failed %s : %d", path, ret); /* ROM 0x779d3c / 0x74bd9c */
            _evenOtaReplyToAPP(OTA_CMD_CONTROL, 1u, 6u);
            return;
        }
    } else if (session->storage_type == OTA_STORAGE_EXTERNAL_FLASH) {
        /* The path carries the XIP address as "0x..."; accept 0x80000000..0x82000000. */
        uint32_t xip_addr = semantic_OtaParseHexAddress(path);
        if (xip_addr + 0x80000000u >= 0x02000001u) {
            OTA_LOG(cmd_parse_fn, 1u, 0x4b9u, 0x04400000u,
                    "ERR-Find hex from string failed %s", path); /* ROM 0x757428 / 0x736344 */
            _evenOtaReplyToAPP(OTA_CMD_CONTROL, 1u, 1u);
            return;
        }
        session->fw_addr = xip_addr & 0x7fffffffu;
        OTA_LOG(cmd_parse_fn, 2u, 0x4beu, 0x08800000u,
                "xipAddr = 0x%x, newFwFlashInfo.addr = 0x%x", /* ROM 0x740e6c / 0x720ec0 */
                xip_addr, session->fw_addr);
    }

    session->state = 1u;
    OTA_LOG(cmd_parse_fn, 4u, 0x4c2u, 0x10000000u,
            "eOTATransmitCID_OTA_TRANSMIT_INFORMATION success"); /* ROM 0x72b9b4 / 0x70d6a4 */
    _evenOtaReplyToAPP(OTA_CMD_CONTROL, 1u, 0u);
}

void _fileRawDataParse(const uint8_t *data, uint16_t len)
{
    g2_ota_transfer_t *const xfer = &g2_ota_transfer;
    g2_ota_session_t *const session = &g2_ota_session;
    uint8_t readback[OTA_CHUNK];

    if (xfer->started != 1u)
        return;

    switch (session->fw_data_type) {
    case OTA_TYPE_GLASSES_FIRMWARE:
        OTA_LOG(raw_parse_fn, 4u, 0x574u, 0x10000000u,
                "eOTATransmitType_GLASSES_FIRMWARE"); /* ROM 0x75744c / 0x736374 */
        if (session->offset == 0u)
            (void)audio_queue_copy_bytes(session->image_head, data, sizeof session->image_head);
        if (session->storage_type == OTA_STORAGE_MRAM) {
            if (session->state != 1u || session->fw_addr == 0u) {
                OTA_LOG(raw_parse_fn, 1u, 0x583u, 0x04800000u,
                        "OTA raw data dropped: session not ready (state=%d, addr=0x%x)", /* ROM 0x70d7e4 / 0x6f4eec */
                        session->state, session->fw_addr);
                _evenOtaReplyToAPP(OTA_CMD_RAW_DATA, 2u, 6u);
                return;
            }
            if (semantic_OtaBufferedFlashWrite(len, data, session->offset + session->fw_addr,
                                               (uint8_t)(len + session->offset == session->fw_length)) == 1u) {
                OTA_CHUNK_ACCEPT(xfer, session, data, len);
                OTA_SPEED_LOG(0x59du, xfer, len);
            } else {
                _evenOtaReplyToAPP(OTA_CMD_RAW_DATA, 2u, 6u);
            }
        }
        break;
    case OTA_TYPE_FONT:
        OTA_LOG(raw_parse_fn, 4u, 0x5adu, 0x10000000u, "eOTATransmitType_FONT"); /* ROM 0x779e44 / 0x7574b8 */
        break;
    case OTA_TYPE_BOOTLOADER:
        OTA_LOG(raw_parse_fn, 4u, 0x5a8u, 0x10000000u, "eOTATransmitType_BOOTLOADER"); /* ROM 0x76f2cc / 0x740ec4 */
        break;
    case OTA_TYPE_AUDIO_BIN:
        OTA_LOG(raw_parse_fn, 4u, 0x5b7u, 0x10000000u, "eOTATransmitType_AUDIO_BIN"); /* ROM 0x76f304 / 0x74bfcc */
        break;
    case OTA_TYPE_TOUCH_BIN:
        OTA_LOG(raw_parse_fn, 4u, 0x5b2u, 0x10000000u, "eOTATransmitType_TOUCH_BIN"); /* ROM 0x76f2e8 / 0x74bfa4 */
        break;
    case OTA_TYPE_BOX:
        OTA_LOG(raw_parse_fn, 4u, 0x5c1u, 0x10000000u, "eOTATransmitType_BOX_BIN"); /* ROM 0x76f320 / 0x74c01c */
        break;
    case OTA_TYPE_BLE9305_BIN:
        OTA_LOG(raw_parse_fn, 4u, 0x5bcu, 0x10000000u, "eOTATransmitType_BLE9305_BIN"); /* ROM 0x762d70 / 0x740ef0 */
        break;
    default:
        break;
    }

    if (session->storage_type == OTA_STORAGE_FILE) {
        bool verified;
        uint32_t count;
        int32_t err;

        (void)osKernelGetTickCount();
        count = file_write(data, 1u, len, xfer->file);
        if (count == len) {
            /* Read the chunk back from where it was written and compare. */
            (void)file_seek(xfer->file, (int32_t)xfer->recv_total, 0);
            count = file_read(g2_ota_verify_buffer, 1u, len, xfer->file);
            if (count == len) {
                verified = g2_lfs_memcmp(g2_ota_verify_buffer, data, len) == 0;
            } else {
                verified = false;
                OTA_LOG(raw_parse_fn, 1u, 0x5d6u, 0x04800000u,
                        "File read failed: expected %d, actual %d", len, count); /* ROM 0x740f1c / 0x720f68 */
            }
        } else {
            verified = false;
            OTA_LOG(raw_parse_fn, 1u, 0x5dau, 0x04800000u,
                    "File write failed: expected %d, actual %d", len, count); /* ROM 0x740f48 / 0x720fa0 */
        }
        (void)osKernelGetTickCount();
        if (verified) {
            OTA_CHUNK_ACCEPT(xfer, session, data, len);
            OTA_SPEED_LOG(0x5ecu, xfer, len);
            return;
        }
        OTA_LOG(raw_parse_fn, 1u, 0x5f0u, 0x04000000u, "OTA read data != write data"); /* ROM 0x76f33c / 0x740f74 */
        if (xfer->is_open == 1u) {
            OTA_FILE_CLOSE(&xfer->file, err);
            if (err < 0)
                OTA_LOG(raw_parse_fn, 1u, 0x5f7u, 0x04800000u,
                        "ERR-Close failed after write err %s : %d", xfer->path, err); /* ROM 0x740fa0 / 0x720fd8 */
            xfer->is_open = 0u;
        }
        err = file_remove(xfer->path);
        if (err < 0 && err != OTA_LFS_ERR_NOENT)
            OTA_LOG(raw_parse_fn, 1u, 0x5feu, 0x04800000u,
                    "ERR-Delete failed after write err %s : %d", xfer->path, err); /* ROM 0x740fcc / 0x721010 */
        session->state = 0u;
        xfer->recv_total = 0u;
        session->offset = 0u;
        xfer->calc_crc = 0u;
        _evenOtaReplyToAPP(OTA_CMD_RAW_DATA, 2u, 6u);
    } else if (session->storage_type == OTA_STORAGE_EXTERNAL_FLASH) {
        uint32_t start_tick = osKernelGetTickCount();
        uint32_t address = session->offset + session->fw_addr;
        uint32_t sector = address & ~(OTA_CHUNK - 1u);
        uint32_t last_sector = (len + address) & ~(OTA_CHUNK - 1u);
        uint32_t erased = 0u;
        uint32_t erase_status;
        int32_t status;

        OTA_LOG(raw_parse_fn, 4u, 0x60eu, 0x10c00000u,
                "XIP data start at 0x%x, offset = %x, len = %x", /* ROM 0x736464 / 0x71726c */
                address, session->offset, len);
        /* Erase the 4 KiB sector this packet starts on (only when aligned:
         * a mid-sector start was erased with the previous packet) and every
         * further sector boundary up to and including the end address. */
        if ((address & (OTA_CHUNK - 1u)) == 0u) {
            OTA_LOG(raw_parse_fn, 4u, 0x61bu, 0x10400000u,
                    "Target address is 4K aligned, erasing sector at 0x%x", address); /* ROM 0x721048 / 0x7044e4 */
            erase_status = g2_norflash_erase_lower_47075c(address);
            if (erase_status != 0u) {
                OTA_LOG(raw_parse_fn, 1u, 0x61eu, 0x04800000u,
                        "External flash sector erase failed at 0x%x, result=%d", /* ROM 0x721080 / 0x704528 */
                        address, erase_status);
                _evenOtaReplyToAPP(OTA_CMD_RAW_DATA, 2u, 6u);
                return;
            }
            OTA_LOG(raw_parse_fn, 4u, 0x622u, 0x10400000u,
                    "Successfully erased sector at 0x%x", address); /* ROM 0x757500 / 0x736494 */
            erased = 1u;
        }
        if (sector < last_sector) {
            for (sector += OTA_CHUNK; sector <= last_sector; sector += OTA_CHUNK) {
                OTA_LOG(raw_parse_fn, 4u, 0x62bu, 0x10400000u,
                        "Target address crosses 4K boundary, erasing sector at 0x%x", sector); /* ROM 0x7172a8 / 0x6fbc3c */
                erase_status = g2_norflash_erase_lower_47075c(sector);
                if (erase_status != 0u) {
                    OTA_LOG(raw_parse_fn, 1u, 0x62eu, 0x04800000u,
                            "External flash sector erase failed at 0x%x, result=%d", /* ROM 0x721080 / 0x704528 */
                            sector, erase_status);
                    _evenOtaReplyToAPP(OTA_CMD_RAW_DATA, 2u, 6u);
                    return;
                }
                OTA_LOG(raw_parse_fn, 4u, 0x632u, 0x10400000u,
                        "Successfully erased sector at 0x%x", sector); /* ROM 0x757500 / 0x736494 */
                erased++;
            }
        }
        if (erased == 0u)
            OTA_LOG(raw_parse_fn, 4u, 0x639u, 0x10000000u,
                    "No sectors need to be erased for this packet"); /* ROM 0x7364c4 / 0x7172e4 */
        else
            OTA_LOG(raw_parse_fn, 4u, 0x63bu, 0x10400000u,
                    "Total erased %d sectors for this packet", erased); /* ROM 0x74c044 / 0x7210b8 */

        status = norflash_write_4709c0((int32_t)address, data, len);
        if (status != 0) {
            OTA_LOG(raw_parse_fn, 1u, 0x641u, 0x04800000u,
                    "External flash write failed at 0x%x, result=%d", address, status); /* ROM 0x7364f4 / 0x717320 */
            _evenOtaReplyToAPP(OTA_CMD_RAW_DATA, 2u, 6u);
            return;
        }
        status = g2_norflash_read_lower_4709c8((int32_t)address, readback, len);
        if (status != 0) {
            OTA_LOG(raw_parse_fn, 1u, 0x64au, 0x04800000u,
                    "External flash read verify failed at 0x%x, result=%d", address, status); /* ROM 0x7210f0 / 0x70456c */
            _evenOtaReplyToAPP(OTA_CMD_RAW_DATA, 2u, 6u);
            return;
        }
        if (g2_lfs_memcmp(readback, data, len) != 0) {
            OTA_LOG(raw_parse_fn, 1u, 0x651u, 0x04400000u,
                    "External flash write verify failed at 0x%x", address); /* ROM 0x740ff8 / 0x721128 */
            _evenOtaReplyToAPP(OTA_CMD_RAW_DATA, 2u, 6u);
            return;
        }
        {
            uint32_t end_tick = osKernelGetTickCount();
            uint32_t elapsed;
            OTA_CHUNK_ACCEPT(xfer, session, data, len);
            elapsed = end_tick - start_tick;
            OTA_LOG(raw_parse_fn, 4u, 0x66au, 0x11000000u,
                    "External flash OTA update %d%% eclipse time: %d ms speed : %d(%d) KB/S", /* ROM 0x6fbc84 / 0x6e901c */
                    xfer->progress, elapsed, (((uint32_t)len * 1000u) >> 10) / elapsed,
                    ((xfer->recv_total * 1000u) >> 10) / elapsed);
        }
    }
}

/* Streams a whole file through the CRC-32C helper in 4 KiB chunks; 1 = ok.
 * The open flag it updates is the shared transfer object's, whatever slot the
 * caller passes (stock only passes &g2_ota_transfer.file). */
uint8_t ota_file_calculate_crc_447a60(void **file, const char *path, uint32_t *size,
                                                      uint32_t *crc)
{
    int32_t ret = -1;
    int32_t length;
    int32_t err;
    uint32_t count;
    uint32_t rest;

    *file = file_open(path, semantic_OtaSelectFlashOps(OTA_FS_O_RDONLY));
    if (*file == NULL) {
        g2_ota_transfer.is_open = 0u;
    } else {
        ret = 0;
        g2_ota_transfer.is_open = 1u;
    }
    if (ret < 0) {
        OTA_LOG(crc_fn, 1u, 0x677u, 0x04800000u,
                "ERR-Open failed %s : %d", path, ret); /* ROM 0x779d3c / 0x74bd9c */
        return 0u;
    }

    length = semantic_OtaFileSize(*file);
    if (length < 0) {
        OTA_LOG(crc_fn, 1u, 0x67du, 0x04800000u,
                "ERR-get size failed %s : %d", path, length); /* ROM 0x76f358 / 0x741024 */
        OTA_FILE_CLOSE(file, err);
        if (err < 0)
            OTA_LOG(crc_fn, 1u, 0x680u, 0x04800000u,
                    "ERR-Close failed %s : %d", path, err); /* ROM 0x76f128 / 0x74bdc4 */
        return 0u;
    }
    *size = (uint32_t)length;
    OTA_LOG(crc_fn, 4u, 0x686u, 0x10400000u, "File size: %ld bytes\n", *size); /* ROM 0x779e74 / 0x757524 */

    for (uint32_t i = 0u; i < (*size >> 12); i++) {
        count = file_read(g2_ota_verify_buffer, 1u, OTA_CHUNK, *file);
        if (count != OTA_CHUNK) {
            OTA_LOG(crc_fn, 1u, 0x68bu, 0x04400000u, "read failed %d", count); /* ROM 0x787c20 / 0x76f374 */
            OTA_FILE_CLOSE(file, err);
            if (err < 0)
                OTA_LOG(crc_fn, 1u, 0x68eu, 0x04800000u,
                        "ERR-Close failed %s : %d", path, err); /* ROM 0x76f128 / 0x74bdc4 */
            return 0u;
        }
        file_crc32c_update_47cbc4(g2_ota_verify_buffer, OTA_CHUNK, crc);
    }

    rest = *size & (OTA_CHUNK - 1u);
    if (rest != 0u) {
        count = file_read(g2_ota_verify_buffer, 1u, rest, *file);
        if (count != rest) {
            OTA_LOG(crc_fn, 1u, 0x699u, 0x04800000u,
                    "read failed %d(%d)", count, rest); /* ROM 0x7816ec / 0x762d90 */
            OTA_FILE_CLOSE(file, err);
            if (err < 0)
                OTA_LOG(crc_fn, 1u, 0x69cu, 0x04800000u,
                        "ERR-Close failed %s : %d", path, err); /* ROM 0x76f128 / 0x74bdc4 */
            return 0u;
        }
        file_crc32c_update_47cbc4(g2_ota_verify_buffer, rest, crc);
    }

    OTA_FILE_CLOSE(file, err);
    if (err < 0)
        OTA_LOG(crc_fn, 1u, 0x6a4u, 0x04800000u,
                "ERR-Close failed %s : %d", path, err); /* ROM 0x76f128 / 0x74bdc4 */
    OTA_LOG(crc_fn, 4u, 0x6a6u, 0x10c00000u,
            "filePath = %s, fileSize = %d, calc CRC = 0x%x", path, *size, *crc); /* ROM 0x736524 / 0x71735c */
    return 1u;
}
