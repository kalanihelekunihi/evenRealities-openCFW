/* OTA file export engine and frame entry points, stock
 * D:\01_workspace\s200_ap510b_iar_git\platform\protocols\ota_service\ota_service.c
 * (log tag "ota.service"; same translation unit as app/a-02-ota-service).
 * Native _exportFileParse 0x447f00..0x44865f (pool 0x448660..0x44866f),
 * semantic_OtaFrameDispatch 0x448670, semantic_OtaNotifyStatus4/3/5
 * 0x4486ec/0x44871a/0x44874c, OTA_SetInterface 0x4487e4..0x448843
 * (pools 0x4486e0, 0x448748, 0x448778, 0x4487a4, 0x4487d4, 0x448844..0x4488eb).
 *
 * Already reconstructed elsewhere (not repeated here): semantic_OtaResetExportState
 * 0x4486bc (ble/ble-slave), semantic_OtaCancelExport 0x448784 (ble/ble-ota),
 * semantic_OtaTransferActive 0x4487ac (ble/ble-role).
 *
 * Export protocol (frame command 0xC2/0xC3, first payload byte = sub-command):
 *   0 start  : path follows; CRC-32C of the whole file is computed and the
 *              10-byte info {0, 0, size LE32, crc LE32} goes out on 0xC2.
 *   1 next   : read the next <= 4 KiB chunk, send it on 0xC3, reply (0xC2, 1, 0).
 *   2 retry  : rewind the offset by the last chunk (or to 0 below 4 KiB), then read.
 *   3 result : log only.
 * The final chunk closes the file and replies (0xC2, 3, 0); a close error
 * replies (0xC2, 1, 10); a failed CRC pass replies (0xC2, 0, 3). */
#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

/* Shared OTA transfer object (RAM 0x20071ff0, cleared as 0x70 bytes); the
 * import engine uses +0x60/+0x68 differently. */
typedef struct {
    void *file;            /* +0x00 open file handle */
    uint8_t is_open;       /* +0x04 */
    char path[0x50];       /* +0x05 export path */
    uint8_t pad_55[3];     /* +0x55 */
    uint32_t file_size;    /* +0x58 */
    uint32_t file_crc;     /* +0x5c CRC-32C of the whole file */
    uint32_t last_len;     /* +0x60 bytes sent by the last chunk */
    uint32_t sent_total;   /* +0x64 _g_bleFileRecv.recvTotalLen (file offset) */
    uint32_t remain_len;   /* +0x68 _g_bleFileRecv.remainLen */
    uint8_t progress;      /* +0x6c percent */
    uint8_t export_active; /* +0x6d set once the start sub-command opened the file */
    uint8_t pad_6e[2];     /* +0x6e */
} g2_ota_export_t;
_Static_assert(sizeof(g2_ota_export_t) == 0x70, "stock OTA transfer object is 0x70 bytes");
_Static_assert(offsetof(g2_ota_export_t, remain_len) == 0x68, "remainLen at +0x68");

#define OTA_SESSION_SIZE 0x60u
#define OTA_SESSION_BUFFER 0x34u
#define OTA_CHUNK 0x1000u
#define OTA_FS_O_RDONLY 1u
#define OTA_CMD_CONTROL 0xc0u
#define OTA_CMD_RAW_DATA 0xc1u
#define OTA_CMD_EXPORT 0xc2u
#define OTA_CMD_EXPORT_DATA 0xc3u
#define OTA_INTERFACE_UART 1u

enum {
    OTA_EXPORT_START = 0u,
    OTA_EXPORT_NEXT = 1u,
    OTA_EXPORT_RETRY = 2u,
    OTA_EXPORT_RESULT_CHECK = 3u, /* eOTAExportFileCID_OTA_FILE_EXPORT_CMD_RESULT_CHECK */
};

extern g2_ota_export_t g2_ota_transfer;             /* RAM 0x20071ff0 */
extern uint8_t audio_ble_ota_export_state[];        /* RAM 0x20072730, 0x60-byte session */
extern uint8_t g2_ota_cache_buffer[];               /* RAM 0x2034bc10, 4 KiB chunk buffer */
extern uint32_t g2_ota_start_tick;                  /* RAM 0x20074844 */
extern uint32_t g2_ota_data_start_tick;             /* RAM 0x20074848 */
extern uint32_t g2_ota_last_tick;                   /* RAM 0x2007484c */
/* RAM 0x20074ff3: OTA interface, 0 = BLE (replies go out over BLE), 1 = UART. */
extern volatile uint8_t audio_ble_ota_sync_enabled;

extern void _fileCmdParse(uint8_t cid, const uint8_t *data, uint32_t len);   /* 0x445660 */
extern void _fileRawDataParse(const uint8_t *data, uint16_t len);            /* 0x446d40 */
/* 0x447a60: file-local _fileCaculateCRC of this TU (a-02 keeps it static because
 * the EFS service has its own _fileCaculateCRC at 0x4567b8). */
extern uint8_t ota_file_calculate_crc_447a60(void **file, const char *path, uint32_t *size,
                                             uint32_t *crc);
extern const char *semantic_OtaSelectFlashOps(uint32_t flags);              /* 0x4448f4 */
extern void _evenOtaReplyToAPP(uint8_t cmd, uint8_t subcommand, uint8_t status); /* 0x444e08 */
extern void RPC_SystemTimeSync(void);                                       /* 0x44a2b2 */
extern void APP_ConnectParamOTASetFastMode(void);                           /* 0x4781f4 */
extern void audio_ble_param_reset_delayed_event(uint32_t delay);            /* 0x478252 */
extern uint32_t audio_event_loop_remove_delayed(void (*callback)(void));    /* 0x476ace */
extern uint32_t Thread_MsgTransport3TxByBle(uint8_t type, uint8_t command,
                                            const void *payload, uint16_t length); /* 0x475de0 */
extern uint32_t osKernelGetTickCount(void);                                 /* 0x4490cc */
extern void *file_open(const char *path, const char *mode);                 /* 0x474550 */
extern int32_t file_close(void *file);                                      /* 0x4745f4 */
extern uint32_t file_read(void *buffer, uint32_t size, uint32_t count, void *file); /* 0x474634 */
extern int32_t file_seek(void *file, int32_t offset, int32_t origin);       /* 0x474814 */
extern uint64_t audio_uart_ring_u64_div_47cc60(uint32_t low, uint32_t high,
                                               uint32_t divisor_low, uint32_t divisor_high);
extern void audio_uart_buffer_zero(void *dst, uint32_t len, uint32_t fill); /* 0x43c0e4 */
extern void audio_uart_checksum_copy(void *dst, const void *src, uint32_t len); /* 0x439be4 */
extern uint32_t audio_log_flags(void);                                      /* 0x43d0ce */
extern void audio_log_extended(uint8_t, const char *, const char *, const char *, uint32_t,
                               const char *, ...);                          /* 0x43d574 */
extern uint32_t compress_log_output(uint32_t, const char *, const char *, ...); /* 0x43ce9e */

static const char module_tag[] = "ota.service"; /* ROM 0x78b660 */
static const char source_file[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\platform\\protocols\\ota_service\\ota_service.c"; /* ROM 0x6e8f74 */
static const char export_fn[] = "_exportFileParse";   /* ROM 0x781700 */
static const char set_interface_fn[] = "OTA_SetInterface"; /* ROM 0x78173c */
static const char name_uart[] = "UART";               /* ROM 0x78de4c */
static const char name_ble[] = "BLE";                 /* pool word 0x44884c */

/* Every message is paired with a "[ota.service]"-prefixed compact copy; the
 * comments give plain / compact ROM addresses. */
#define OTA_LOG(fn, level, line, mask, fmt, ...) do { \
    if (audio_log_flags() & 2u) \
        audio_log_extended((level), module_tag, source_file, (fn), (line), fmt, ##__VA_ARGS__); \
    if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u)) \
        (void)compress_log_output((mask), "[ota.service]" fmt, "[ota.service]" fmt, ##__VA_ARGS__); \
} while (0)

static int32_t close_export_file(g2_ota_export_t *xfer)
{
    int32_t err;
    if (xfer->file == NULL) {
        err = 0;
    } else {
        err = file_close(xfer->file);
        xfer->file = NULL;
    }
    return err;
}

static void reset_session(void)
{
    audio_uart_buffer_zero(audio_ble_ota_export_state, OTA_SESSION_SIZE, 0u);
    audio_ble_ota_export_state[0] = 0u;
    uint8_t *buffer = g2_ota_cache_buffer;
    audio_uart_checksum_copy(audio_ble_ota_export_state + OTA_SESSION_BUFFER, &buffer, sizeof buffer);
}

static void put_le32(uint8_t *out, uint32_t value)
{
    out[0] = (uint8_t)value;
    out[1] = (uint8_t)(value >> 8);
    out[2] = (uint8_t)(value >> 16);
    out[3] = (uint8_t)(value >> 24);
}

static void export_start(g2_ota_export_t *xfer, const uint8_t *data, uint32_t len)
{
    int32_t err = -1;

    g2_ota_start_tick = osKernelGetTickCount();
    OTA_LOG(export_fn, 4u, 0x6bau, 0x10400000u,
            "eOTATransmitCID_OTA_TRANSMIT_START = %d ms", g2_ota_start_tick); /* ROM 0x740d38 / 0x720e88 */
    if (audio_ble_ota_sync_enabled == 0u) {
        (void)audio_event_loop_remove_delayed(RPC_SystemTimeSync);
        APP_ConnectParamOTASetFastMode();
    }
    if (xfer->is_open == 1u) {
        OTA_LOG(export_fn, 2u, 0x6c2u, 0x08000000u,
                "file is open, close file first"); /* ROM 0x762c30 / 0x740d64 */
        int32_t close_err = close_export_file(xfer);
        if (close_err < 0) {
            OTA_LOG(export_fn, 1u, 0x6c5u, 0x04800000u,
                    "ERR-Close failed %s : %d", xfer->path, close_err); /* ROM 0x76f128 / 0x74bdc4 */
            return;
        }
    }
    audio_uart_buffer_zero(xfer, sizeof *xfer, 0u);
    reset_session();
    audio_uart_checksum_copy(xfer->path, data, len);
    OTA_LOG(export_fn, 4u, 0x6d1u, 0x10400000u,
            "export filePath = %s", xfer->path); /* ROM 0x779e8c / 0x757548 */

    if (ota_file_calculate_crc_447a60(&xfer->file, xfer->path, &xfer->file_size, &xfer->file_crc) == 0u) {
        _evenOtaReplyToAPP(OTA_CMD_EXPORT, 0u, 3u);
        return;
    }

    uint8_t info[10];
    audio_uart_buffer_zero(info, sizeof info, 0u);
    info[0] = 0u;
    info[1] = 0u;
    put_le32(&info[2], xfer->file_size);
    put_le32(&info[6], xfer->file_crc);
    xfer->remain_len = xfer->file_size;
    if (audio_ble_ota_sync_enabled == 0u)
        (void)Thread_MsgTransport3TxByBle(1u, OTA_CMD_EXPORT, info, sizeof info);

    xfer->file = file_open(xfer->path, semantic_OtaSelectFlashOps(OTA_FS_O_RDONLY));
    if (xfer->file == NULL) {
        xfer->is_open = 0u;
    } else {
        err = 0;
        xfer->is_open = 1u;
    }
    if (err < 0) {
        OTA_LOG(export_fn, 1u, 0x6edu, 0x04800000u,
                "ERR-Open failed %s : %d", xfer->path, err); /* ROM 0x779d3c / 0x74bd9c */
    } else {
        xfer->export_active = 1u;
    }
}

/* Read and send the next chunk (sub-commands 1 and 2). */
static void export_next_chunk(g2_ota_export_t *xfer)
{
    if (xfer->export_active == 0u)
        return;

    g2_ota_data_start_tick = osKernelGetTickCount();
    uint32_t want = OTA_CHUNK;
    audio_uart_buffer_zero(g2_ota_cache_buffer, OTA_CHUNK, 0u);
    if (xfer->remain_len < OTA_CHUNK)
        want = xfer->remain_len;
    OTA_LOG(export_fn, 4u, 0x70bu, 0x10800000u,
            "readLen = %d, _g_bleFileRecv.remainLen = %d", want, xfer->remain_len); /* ROM 0x741050 / 0x717398 */

    uint32_t got = file_read(g2_ota_cache_buffer, 1u, want, xfer->file);
    if (got != want) {
        OTA_LOG(export_fn, 1u, 0x70eu, 0x04400000u, "ERR-Read failed %d", got); /* ROM 0x781714 / 0x762db0 */
        int32_t err = close_export_file(xfer);
        if (err < 0) {
            OTA_LOG(export_fn, 1u, 0x711u, 0x04800000u,
                    "ERR-Close failed %s : %d", xfer->path, err); /* ROM 0x76f128 / 0x74bdc4 */
            _evenOtaReplyToAPP(OTA_CMD_EXPORT, 1u, 10u);
        }
        return;
    }

    OTA_LOG(export_fn, 4u, 0x716u, 0x10400000u, "readResult = %d", got); /* ROM 0x787c30 / 0x762dd0 */
    xfer->sent_total += got;
    xfer->last_len = got;
    xfer->remain_len = xfer->file_size - xfer->sent_total;
    if (audio_ble_ota_sync_enabled == 0u)
        (void)Thread_MsgTransport3TxByBle(1u, OTA_CMD_EXPORT_DATA, g2_ota_cache_buffer, (uint16_t)got);
    _evenOtaReplyToAPP(OTA_CMD_EXPORT, 1u, 0u);
    if (xfer->file_size != 0u) {
        uint64_t scaled = (uint64_t)xfer->sent_total * 100u;
        xfer->progress = (uint8_t)audio_uart_ring_u64_div_47cc60((uint32_t)scaled, (uint32_t)(scaled >> 32),
                                                                 xfer->file_size, 0u);
    }
    g2_ota_last_tick = osKernelGetTickCount();
    OTA_LOG(export_fn, 4u, 0x726u, 0x10c00000u,
            "export file %d%% eclipse time: %d ms speed : %d KB/S", /* ROM 0x721160 / 0x7045b0 */
            xfer->progress, g2_ota_last_tick - g2_ota_start_tick,
            ((xfer->sent_total * 1000u) >> 10) / (g2_ota_last_tick - g2_ota_start_tick));
    OTA_LOG(export_fn, 4u, 0x729u, 0x10c00000u,
            "recvTotalLen = %d, fileSize = %d, crc = 0x%x", /* ROM 0x736554 / 0x7173d4 */
            xfer->sent_total, xfer->file_size, xfer->file_crc);

    if (xfer->sent_total < xfer->file_size)
        return;

    xfer->export_active = 0u;
    OTA_LOG(export_fn, 3u, 0x72cu, 0x0c400000u, "file tx SUCCESS %s", xfer->path); /* ROM 0x781728 / 0x762df0 */
    int32_t err = close_export_file(xfer);
    if (err < 0) {
        OTA_LOG(export_fn, 1u, 0x72fu, 0x04800000u,
                "ERR-Close failed %s : %d", xfer->path, err); /* ROM 0x76f128 / 0x74bdc4 */
        _evenOtaReplyToAPP(OTA_CMD_EXPORT, 1u, 10u);
    } else {
        xfer->is_open = 0u;
        audio_uart_buffer_zero(xfer, sizeof *xfer, 0u);
        _evenOtaReplyToAPP(OTA_CMD_EXPORT, 3u, 0u);
        if (audio_ble_ota_sync_enabled == 0u)
            audio_ble_param_reset_delayed_event(2000u);
    }
}

void _exportFileParse(uint8_t cid, const uint8_t *data, uint32_t len)
{
    g2_ota_export_t *const xfer = &g2_ota_transfer;
    uint8_t unused_reply[2]; /* stock clears a 2-byte reply buffer it never uses */

    audio_uart_buffer_zero(unused_reply, sizeof unused_reply, 0u);
    switch (cid) {
    case OTA_EXPORT_START:
        export_start(xfer, data, len);
        break;
    case OTA_EXPORT_RETRY:
        OTA_LOG(export_fn, 4u, 0x6f5u, 0x10400000u,
                "file export req retry:%d", xfer->sent_total); /* ROM 0x76f390 / 0x74c06c */
        if (xfer->sent_total < OTA_CHUNK)
            xfer->sent_total = 0u;
        else
            xfer->sent_total -= xfer->last_len;
        (void)file_seek(xfer->file, (int32_t)xfer->sent_total, 0);
        export_next_chunk(xfer);
        break;
    case OTA_EXPORT_NEXT:
        export_next_chunk(xfer);
        break;
    case OTA_EXPORT_RESULT_CHECK:
        OTA_LOG(export_fn, 4u, 0x740u, 0x10000000u,
                "eOTAExportFileCID_OTA_FILE_EXPORT_CMD_RESULT_CHECK"); /* ROM 0x72ba84 / 0x70d824 */
        break;
    default:
        break;
    }
}

/* Transport entry for 0xC0..0xC3 frames; payload byte 0 is the sub-command
 * except for raw data. Always returns 0. */
uint32_t semantic_OtaFrameDispatch(uint8_t command, const uint8_t *data, uint16_t len)
{
    if (command == OTA_CMD_CONTROL)
        _fileCmdParse(data[0], data + 1, (uint32_t)len - 1u);
    else if (command == OTA_CMD_RAW_DATA)
        _fileRawDataParse(data, len);
    else if (command == OTA_CMD_EXPORT || command == OTA_CMD_EXPORT_DATA)
        _exportFileParse(data[0], data + 1, (uint32_t)len - 1u);
    return 0u;
}

/* The three status notifiers differ only in the second payload byte. */
static void notify_status(uint8_t command, uint8_t status)
{
    if (command == OTA_CMD_RAW_DATA) {
        uint8_t payload[2];
        payload[0] = 2u;
        payload[1] = status;
        if (audio_ble_ota_sync_enabled == 0u)
            (void)Thread_MsgTransport3TxByBle(1u, command, payload, sizeof payload);
    }
}

void semantic_OtaNotifyStatus4(uint8_t command)
{
    notify_status(command, 4u);
}

void semantic_OtaNotifyStatus3(uint8_t command)
{
    notify_status(command, 3u);
}

void semantic_OtaNotifyStatus5(uint8_t command)
{
    notify_status(command, 5u);
}

void OTA_SetInterface(uint8_t interface)
{
    audio_ble_ota_sync_enabled = interface;
    if (audio_log_flags() & 2u)
        audio_log_extended(4u, module_tag, source_file, set_interface_fn, 0x7c6u,
                           "OTA interface set to: %s", /* ROM 0x76f3ac */
                           interface == OTA_INTERFACE_UART ? name_uart : name_ble);
    if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
        (void)compress_log_output(0x10400000u, "[ota.service]OTA interface set to: %s", /* ROM 0x74c094 */
                                  "[ota.service]OTA interface set to: %s",
                                  interface == OTA_INTERFACE_UART ? name_uart : name_ble);
}
