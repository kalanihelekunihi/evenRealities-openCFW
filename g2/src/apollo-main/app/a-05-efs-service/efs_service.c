/* EFS (even file service) import/export engine, stock
 * D:\01_workspace\s200_ap510b_iar_git\platform\protocols\efs_service\efs_service.c
 * (log tag "efs.service").
 * Native rows: _efsFileCmdParse 0x456c0c..0x4579ba, _efsFileRawDataParse
 * 0x457a54..0x458018, _efsExportFileParse 0x4580c0..0x458b5c,
 * semantic_EfsFrameDispatch 0x458b60, semantic_EfsNotifyStatus4/2/5
 * 0x458bac/0x458bd2/0x458bf8, semantic_EfsTransferActive 0x458c1e,
 * EFS_CancelExport 0x458c5e..0x458d34. Literal pools 0x4578e8..0x457a54,
 * 0x458018..0x4580c0, 0x4586f8..0x458700, 0x458a2c.., 0x458c34..0x458c48,
 * 0x458d34..0x458df0 (plus mid-body words 0x457560 / 0x4575dc).
 *
 * The rest of this object lives elsewhere: _evenEfsReplyToAPP 0x456722,
 * _fileCaculateCRC 0x4567b8 and the path/mode helpers 0x456580..0x456722
 * (segment a-04), semantic_EfsServiceInit 0x458c48 (app/efs-service).
 *
 * Frames arrive through semantic_EfsFrameDispatch (service 0x400):
 * 0xC4 -> _efsFileCmdParse(data[0], data + 1, len - 1),
 * 0xC5 -> _efsFileRawDataParse(data, len),
 * 0xC6/0xC7 -> _efsExportFileParse(data[0], data + 1, len - 1).
 * Replies are {subcommand, status} through _evenEfsReplyToAPP. Observed
 * statuses: 0 ok, 1 rejected, 2 CRC/read failure, 3 file I/O failure,
 * 6 result check failed, 8 cancelled by the device.
 *
 * Stock quirks kept as found: an OTHER_FILE (0xAA) import opens the target
 * file but raw chunks are only logged (never written) and its result check
 * sends no reply; export accepts any whitelist path without validation. */
#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>
#include "g2_efs_service.h"

/* Shared transfer object _g_bleEfsFileTrans (RAM 0x20071cc8, cleared as 0x78 bytes). */
typedef struct {
    void *file;            /* +0x00 open file handle */
    uint8_t is_open;       /* +0x04 */
    char path[0x50];       /* +0x05 target path; export forces path[0x4f] = 0 */
    uint8_t pad_55[3];     /* +0x55 */
    uint32_t file_type;    /* +0x58 eEvenFileServiceType_* */
    uint32_t file_size;    /* +0x5c */
    uint32_t rx_crc;       /* +0x60 CRC-32C announced by the phone */
    uint32_t calc_crc;     /* +0x64 running CRC-32C (file_crc32c_update_47cbc4) */
    uint32_t chunk_len;    /* +0x68 last export read length */
    uint32_t recv_total;   /* +0x6c recvTotalLen */
    uint32_t remain_len;   /* +0x70 export remainLen */
    uint8_t progress;      /* +0x74 percent */
    uint8_t is_start;      /* +0x75 isStart */
    uint8_t pad_76[2];     /* +0x76 */
} g2_efs_transfer_t;
_Static_assert(sizeof(g2_efs_transfer_t) == 0x78u, "stock EFS transfer object is 0x78 bytes");
_Static_assert(offsetof(g2_efs_transfer_t, file_type) == 0x58u, "fileType at +0x58");
_Static_assert(offsetof(g2_efs_transfer_t, is_start) == 0x75u, "isStart at +0x75");

/* Import start header (payload after the subcommand byte; not word aligned). */
typedef struct __attribute__((packed)) {
    uint32_t file_type;    /* +0x00 */
    uint32_t file_size;    /* +0x04 */
    uint32_t file_crc;     /* +0x08 */
    char path[0x50];       /* +0x0c */
} g2_efs_import_header_t;

/* Export start header (payload after the subcommand byte). */
typedef struct __attribute__((packed)) {
    uint32_t file_type;    /* +0x00 */
    char path[0x50];       /* +0x04 */
} g2_efs_export_header_t;

enum {
    EFS_SEND_START = 0u,          /* eEvenFileSendServiceCID_EVEN_FILE_SERVICE_CMD_SEND_START */
    EFS_SEND_DATA_BEGIN = 1u,     /* arms raw-data parsing */
    EFS_SEND_RESULT_CHECK = 2u,   /* eEvenFileSendServiceCID_EVEN_FILE_SERVICE_CMD_SEND_RESULT_CHECK */
};

enum {
    EFS_EXPORT_START = 0u,        /* eEvenFileExportServiceCID_..._CMD_EXPORT_START */
    EFS_EXPORT_NEXT = 1u,         /* phone response to the previous chunk, send the next */
    EFS_EXPORT_RESULT_CHECK = 2u, /* ..._CMD_EXPORT_RESULT_CHECK */
    EFS_EXPORT_CANCEL = 3u,       /* ..._CMD_EXPORT_CANCEL */
};

#define EFS_CHUNK 0x1000u
#define EFS_ANDROID_MSG_MAX 0x2137u   /* Android JSON buffer size */
#define EFS_FS_O_RDONLY 1u            /* littlefs flags fed to the fopen-mode helper */
#define EFS_FS_O_RDWR 3u
#define EFS_FS_O_CREAT 0x100u
#define EFS_LFS_ERR_NOENT (-2)
#define EFS_NOTIF_EVT_WHITELIST_UPDATED 2u

extern uint8_t audio_efs_transfer_state[];           /* RAM 0x20071cc8, g2_efs_transfer_t */
#define g_efs (*(g2_efs_transfer_t *)(void *)audio_efs_transfer_state)
extern uint8_t *g2_efs_android_msg_buffer;           /* RAM 0x20074554 */
extern uint32_t g2_efs_start_tick;                   /* RAM 0x20074558 start / export start */
extern uint32_t g2_efs_data_tick;                    /* RAM 0x2007455c data begin / chunk send */
extern uint32_t g2_efs_last_tick;                    /* RAM 0x20074560 */
extern volatile uint8_t g2_efs_export_active;        /* RAM 0x20074fbc */
extern uint8_t g2_efs_export_buffer[EFS_CHUNK];      /* RAM 0x2035adf8 */
extern uint8_t g2_efs_verify_buffer[EFS_CHUNK];      /* RAM 0x2035be08 */

extern void _evenEfsReplyToAPP(uint8_t command, uint8_t subcommand, uint8_t status); /* 0x456722 */
extern uint32_t _fileCaculateCRC(void **file, const char *path, uint32_t *size, uint32_t *crc); /* 0x4567b8 */
extern uint8_t efs_is_tracepoint_path_456580(const char *path); /* "/log/tp/tp_<n>.bin" */
extern uint8_t efs_is_logger_path_456606(const char *path);     /* "/log/hardfault.txt" or "/log/compress_log_<n>.bin" */
extern const char *efs_fopen_mode_45669a(uint32_t lfs_flags);   /* lfs flags -> "r"/"w"/"a"/"r+"/"a+"/"w+" */
extern int32_t efs_file_size_4566d8(void *file);                /* size via seek-end, position restored */
extern uint32_t Thread_MsgEfsTxByBle(uint8_t type, uint8_t command, const void *payload, uint16_t length); /* 0x475dfa */
extern uint32_t Thread_MsgEfsNotifyByBle(uint8_t type, uint8_t command, const void *payload, uint16_t length); /* 0x475e6c */
extern void APP_ConnectParamOTASetFastMode(void);                /* 0x4781f4 */
extern uint32_t audio_event_loop_remove_delayed(void (*callback)(void)); /* fw_event_loop_remove_delayed 0x476ace */
extern void audio_ble_comm_link_delayed(void);                   /* 0x4b81b8 APP_BleConnectTimeoutCheckEvt */
extern void audio_ble_param_reset_delayed_event(uint32_t delay_ms); /* ble_param_reset_delayed_event 0x478252 */
extern void compress_log_export_notify(uint8_t exporting);       /* 0x44a904 */
extern int32_t audio_tracepoint_prepare_pull_48ec9e(void);
extern uint8_t *svc_android_notify_buffer_48e0a8(void);          /* returns RAM 0x20354c78 */
extern void SVC_ANDROID_ParseNotification(const char *json);     /* 0x48e72c */
extern void Thread_SendEvtToNotifTask(uint32_t event);           /* 0x48e3e2 */
extern uint32_t osKernelGetTickCount(void);                      /* 0x4490cc */
extern int32_t osDelay(uint32_t ticks);                          /* 0x449376 */
extern void *file_open(const char *path, const char *mode);      /* 0x474550 */
extern int32_t file_close(void *file);                           /* 0x4745f4 */
extern uint32_t file_read(void *buffer, uint32_t size, uint32_t count, void *file); /* 0x474634 */
extern uint32_t file_write(const void *buf, uint32_t size, uint32_t count, void *file); /* 0x474682 */
extern int32_t file_seek(void *file, int32_t offset, int32_t origin); /* 0x474814 */
extern int32_t file_remove(const char *path);                    /* 0x47498c */
extern void file_crc32c_update_47cbc4(const uint8_t *data, uint32_t length, uint32_t *crc);
extern void audio_uart_buffer_zero(void *dst, uint32_t len, uint32_t fill); /* 0x43c0e4 memset */
extern void *audio_settings_copy_text(void *dst, const void *src, uint32_t len); /* 0x44b5a0 strncpy */
extern void *audio_queue_copy_bytes(void *dst, const void *src, uint32_t len); /* 0x439be4 memcpy */
extern uint32_t g2_log_module_length(const char *text);          /* 0x44a43c strlen */
extern int32_t audio_l2c_strncmp(const char *a, const char *b, uint32_t count); /* 0x44b610 */
extern int32_t g2_lfs_memcmp(const void *a, const void *b, uint32_t length); /* 0x4751c8 */
extern uint32_t audio_log_flags(void);                           /* 0x43d0ce */
extern void audio_log_extended(uint8_t, const char *, const char *, const char *, uint32_t, const char *, ...); /* 0x43d574 */
extern uint32_t compress_log_output(uint32_t, const char *, const char *, ...); /* 0x43ce9e */

static const char module_tag[] = "efs.service"; /* ROM 0x78a94c */
static const char source_file[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\platform\\protocols\\efs_service\\efs_service.c"; /* ROM 0x6e772c */
static const char fn_cmd[] = "_efsFileCmdParse";         /* ROM 0x77f1f8 */
static const char fn_raw[] = "_efsFileRawDataParse";     /* ROM 0x77703c */
static const char fn_export[] = "_efsExportFileParse";   /* ROM 0x77f248 */
static const char fn_cancel[] = "EFS_CancelExport";      /* ROM 0x77f270 */
static const char path_whitelist[] = "user/notify_whitelist.json"; /* ROM 0x76b538 */

/* Plain / "[efs.service]"-prefixed compact message pairs (ROM plain, compact). */
static const char s_send_start[] = "eEvenFileSendServiceCID_EVEN_FILE_SERVICE_CMD_SEND_START = %d ms"; /* 0x702614 */
static const char c_send_start[] = "[efs.service]eEvenFileSendServiceCID_EVEN_FILE_SERVICE_CMD_SEND_START = %d ms"; /* 0x6ece38 */
static const char s_is_open[] = "file is open, close file first"; /* 0x75fad0 */
static const char c_is_open[] = "[efs.service]file is open, close file first"; /* 0x73e89c */
static const char s_close_failed[] = "ERR-Close failed %s : %d"; /* 0x76b4e4 */
static const char c_close_failed[] = "[efs.service]ERR-Close failed %s : %d"; /* 0x749c7c */
static const char s_file_type[] = "fileType = 0x%x"; /* 0x785d50 */
static const char c_file_type[] = "[efs.service]fileType = 0x%x"; /* 0x75faf0 */
static const char s_file_size[] = "fileSize = 0x%x"; /* 0x785d60 */
static const char c_file_size[] = "[efs.service]fileSize = 0x%x"; /* 0x75fb10 */
static const char s_rx_crc[] = "rxFileCrc = 0x%x"; /* 0x77f20c */
static const char c_rx_crc[] = "[efs.service]rxFileCrc = 0x%x"; /* 0x75fb30 */
static const char s_file_path[] = "filePath = %s"; /* 0x785d70 */
static const char c_file_path[] = "[efs.service]filePath = %s"; /* 0x76b51c */
static const char s_type_whitelist[] = "eEvenFileServiceType_NOTIFICATION_JSON_WHITELIST"; /* 0x72931c */
static const char c_type_whitelist[] = "[efs.service]eEvenFileServiceType_NOTIFICATION_JSON_WHITELIST"; /* 0x70b1e4 */
static const char s_type_android_size[] =
    "eEvenFileServiceType_ANDROID_MSG_JSON_NOTIFICATION, fileSize = %d(%d)"; /* 0x6fa0f4 */
static const char c_type_android_size[] =
    "[efs.service]eEvenFileServiceType_ANDROID_MSG_JSON_NOTIFICATION, fileSize = %d(%d)"; /* 0x6e7780 */
static const char s_too_large[] = "fileSize is too large"; /* 0x777024 */
static const char c_too_large[] = "[efs.service]fileSize is too large"; /* 0x754140 */
static const char s_type_other[] = "eEvenFileServiceType_OTHER_FILE"; /* 0x75fb50 */
static const char c_type_other[] = "[efs.service]eEvenFileServiceType_OTHER_FILE"; /* 0x733b54 */
static const char s_export_only[] = "fileType 0x%x is export only"; /* 0x75fb70 */
static const char c_export_only[] = "[efs.service]fileType 0x%x is export only"; /* 0x73e8c8 */
static const char s_target_path[] = "pTargetPath = %s"; /* 0x77f220 */
static const char c_target_path[] = "[efs.service]pTargetPath = %s"; /* 0x75fb90 */
static const char s_delete_failed[] = "ERR-Delete failed %s : %d"; /* 0x76b554 */
static const char c_delete_failed[] = "[efs.service]ERR-Delete failed %s : %d"; /* 0x749ca4 */
static const char s_old_deleted[] = "Old file deleted"; /* 0x77f234 */
static const char c_old_deleted[] = "[efs.service]Old file deleted"; /* 0x75fbb0 */
static const char s_open_failed[] = "ERR-Open failed %s : %d"; /* 0x776ff4 */
static const char c_open_failed[] = "[efs.service]ERR-Open failed %s : %d"; /* 0x749c54 */
static const char s_opened_write[] = "file opened for writing: %s"; /* 0x76b570 */
static const char c_opened_write[] = "[efs.service]file opened for writing: %s"; /* 0x73e8f4 */
static const char s_result_check[] = "eEvenFileSendServiceCID_EVEN_FILE_SERVICE_CMD_SEND_RESULT_CHECK"; /* 0x70b224 */
static const char c_result_check[] = "[efs.service]eEvenFileSendServiceCID_EVEN_FILE_SERVICE_CMD_SEND_RESULT_CHECK"; /* 0x6ece88 */
static const char s_calc_crc[] = "calc bin crc 0x%x, rxFileCrc = 0x%x"; /* 0x754164 */
static const char c_calc_crc[] = "[efs.service]calc bin crc 0x%x, rxFileCrc = 0x%x"; /* 0x729350 */
static const char s_recv_size[] = "recvTotalLen = %d,fileSize = %d"; /* 0x75fbd0 */
static const char c_recv_size[] = "[efs.service]recvTotalLen = %d,fileSize = %d"; /* 0x733b84 */
static const char s_type_android[] = "eEvenFileServiceType_ANDROID_MSG_JSON_NOTIFICATION"; /* 0x7293b8 */
static const char c_type_android[] = "[efs.service]eEvenFileServiceType_ANDROID_MSG_JSON_NOTIFICATION"; /* 0x70b2a4 */
static const char s_rx_calc_crc[] = "rxFileCrc = 0x%x, calcFileCrc = 0x%x"; /* 0x749cf4 */
static const char c_rx_calc_crc[] = "[efs.service]rxFileCrc = 0x%x, calcFileCrc = 0x%x"; /* 0x7293ec */
static const char s_size_recv[] = "fileSize = %d, recvTotalLen = %d"; /* 0x7541d0 */
static const char c_size_recv[] = "[efs.service]fileSize = %d, recvTotalLen = %d"; /* 0x733c44 */
static const char s_rsp_success[] = "eEvenFileServiceRsp_EVEN_FILE_SERVICE_RSP_SUCCESS"; /* 0x729384 */
static const char c_rsp_success[] = "[efs.service]eEvenFileServiceRsp_EVEN_FILE_SERVICE_RSP_SUCCESS"; /* 0x70b264 */
static const char s_rsp_check_fail[] = "eEvenFileServiceRsp_EVEN_FILE_SERVICE_RSP_RESULT_CHECK_FAIL"; /* 0x714a58 */
static const char c_rsp_check_fail[] = "[efs.service]eEvenFileServiceRsp_EVEN_FILE_SERVICE_RSP_RESULT_CHECK_FAIL"; /* 0x6f31d4 */
static const char s_wl_saved[] = "[WHITELIST] Whitelist file saved to: %s"; /* 0x749ccc */
static const char c_wl_saved[] = "[efs.service][WHITELIST] Whitelist file saved to: %s"; /* 0x71e808 */
static const char s_wl_verify_failed[] = "[WHITELIST] Whitelist file verification FAILED"; /* 0x733bb4 */
static const char c_wl_verify_failed[] = "[efs.service][WHITELIST] Whitelist file verification FAILED"; /* 0x714a1c */
static const char s_wl_crc[] = "[WHITELIST] CRC mismatch detected"; /* 0x754188 */
static const char c_wl_crc[] = "[efs.service][WHITELIST] CRC mismatch detected"; /* 0x733be4 */
static const char s_wl_size[] = "[WHITELIST] Size mismatch detected"; /* 0x7541ac */
static const char c_wl_size[] = "[efs.service][WHITELIST] Size mismatch detected"; /* 0x733c14 */
static const char s_not_open[] = "ERR:file is not open, [%s]"; /* 0x76b58c */
static const char c_not_open[] = "[efs.service]ERR:file is not open, [%s]"; /* 0x749d1c */
static const char s_wl_write_ok[] = "[WHITELIST] Write & verify OK: %d bytes at offset %d"; /* 0x71e840 */
static const char c_wl_write_ok[] = "[efs.service][WHITELIST] Write & verify OK: %d bytes at offset %d"; /* 0x702658 */
static const char s_wl_mismatch[] = "[WHITELIST] Write verify failed - data mismatch"; /* 0x733c74 */
static const char c_wl_mismatch[] = "[efs.service][WHITELIST] Write verify failed - data mismatch"; /* 0x70b2e4 */
static const char s_read_short[] = "File read failed: expected %d, actual %d"; /* 0x73e920 */
static const char c_read_short[] = "[efs.service]File read failed: expected %d, actual %d"; /* 0x71e878 */
static const char s_write_short[] = "File write failed: expected %d, actual %d"; /* 0x73e94c */
static const char c_write_short[] = "[efs.service]File write failed: expected %d, actual %d"; /* 0x71e8b0 */
static const char s_recv_len[] = "_g_bleEfsFileTrans.recvTotalLen = %d, len = %d"; /* 0x733ca4 */
static const char c_recv_len[] = "[efs.service]_g_bleEfsFileTrans.recvTotalLen = %d, len = %d"; /* 0x714a94 */
static const char s_update_speed[] = "EFS update %d%% eclipse time: %d ms speed : %d(%d) KB/S"; /* 0x71e8e8 */
static const char c_update_speed[] = "[efs.service]EFS update %d%% eclipse time: %d ms speed : %d(%d) KB/S"; /* 0x6fa13c */
static const char s_wl_write_failed[] = "[WHITELIST] Write failed at offset %d"; /* 0x749d44 */
static const char c_wl_write_failed[] = "[efs.service][WHITELIST] Write failed at offset %d"; /* 0x729420 */
static const char s_export_start[] = "eEvenFileExportServiceCID_EVEN_FILE_SERVICE_CMD_EXPORT_START = %d ms"; /* 0x6fa184 */
static const char c_export_start[] = "[efs.service]eEvenFileExportServiceCID_EVEN_FILE_SERVICE_CMD_EXPORT_START = %d ms"; /* 0x6e77d4 */
static const char s_type_other_path[] = "eEvenFileServiceType_OTHER_FILE %s"; /* 0x7541f4 */
static const char c_type_other_path[] = "[efs.service]eEvenFileServiceType_OTHER_FILE %s"; /* 0x733cd4 */
static const char s_type_logger[] = "eEvenFileServiceType_LOGGER_FILE %s"; /* 0x754218 */
static const char c_type_logger[] = "[efs.service]eEvenFileServiceType_LOGGER_FILE %s"; /* 0x729454 */
static const char s_bad_logger[] = "invalid logger export path: %s"; /* 0x75fbf0 */
static const char c_bad_logger[] = "[efs.service]invalid logger export path: %s"; /* 0x73e978 */
static const char s_type_trace[] = "eEvenFileServiceType_TRACEPOINT_FILE %s"; /* 0x749d6c */
static const char c_type_trace[] = "[efs.service]eEvenFileServiceType_TRACEPOINT_FILE %s"; /* 0x71e920 */
static const char s_bad_trace[] = "invalid tracepoint export path: %s"; /* 0x75423c */
static const char c_bad_trace[] = "[efs.service]invalid tracepoint export path: %s"; /* 0x733d04 */
static const char s_tp_prepare[] = "tracepoint prepare pull failed before export: %d"; /* 0x729488 */
static const char c_tp_prepare[] = "[efs.service]tracepoint prepare pull failed before export: %d"; /* 0x70b324 */
static const char s_crc_failed[] = "Failed to read/calculate CRC"; /* 0x75fc10 */
static const char c_crc_failed[] = "[efs.service]Failed to read/calculate CRC"; /* 0x73e9a4 */
static const char s_is_start[] = "_g_bleEfsFileTrans.isStart = %d"; /* 0x75fc30 */
static const char c_is_start[] = "[efs.service]_g_bleEfsFileTrans.isStart = %d"; /* 0x733d34 */
static const char s_export_resp[] = "ERR-Export failed response %d"; /* 0x75fc50 */
static const char c_export_resp[] = "[efs.service]ERR-Export failed response %d"; /* 0x73e9d0 */
static const char s_read_len[] = "readLen = %d, _g_bleEfsFileTrans.remainLen = %d"; /* 0x733d64 */
static const char c_read_len[] = "[efs.service]readLen = %d, _g_bleEfsFileTrans.remainLen = %d"; /* 0x70b364 */
static const char s_read_failed[] = "ERR-Read failed %d"; /* 0x77f25c */
static const char c_read_failed[] = "[efs.service]ERR-Read failed %d"; /* 0x75fc70 */
static const char s_read_result[] = "readResult = %d"; /* 0x785d80 */
static const char c_read_result[] = "[efs.service]readResult = %d"; /* 0x75fc90 */
static const char s_export_speed[] = "export file %d%% eclipse time: %d ms speed : %d KB/S"; /* 0x71e958 */
static const char c_export_speed[] = "[efs.service]export file %d%% eclipse time: %d ms speed : %d KB/S"; /* 0x70269c */
static const char s_export_total[] = "recvTotalLen = %d, fileSize = %d, crc = 0x%x"; /* 0x733d94 */
static const char c_export_total[] = "[efs.service]recvTotalLen = %d, fileSize = %d, crc = 0x%x"; /* 0x714ad0 */
static const char s_export_result[] =
    "eEvenFileExportServiceCID_EVEN_FILE_SERVICE_CMD_EXPORT_RESULT_CHECK response = %d"; /* 0x6e7828 */
static const char c_export_result[] =
    "[efs.service]eEvenFileExportServiceCID_EVEN_FILE_SERVICE_CMD_EXPORT_RESULT_CHECK response = %d"; /* 0x6dd1d4 */
static const char s_export_cancel[] =
    "eEvenFileExportServiceCID_EVEN_FILE_SERVICE_CMD_EXPORT_CANCEL, stop export"; /* 0x6f3220 */
static const char c_export_cancel[] =
    "[efs.service]eEvenFileExportServiceCID_EVEN_FILE_SERVICE_CMD_EXPORT_CANCEL, stop export"; /* 0x6e3040 */
static const char s_cancel[] = "EFS cancel export: device local startup, cancel export and notify APP"; /* 0x6fa1cc */
static const char c_cancel[] =
    "[efs.service]EFS cancel export: device local startup, cancel export and notify APP"; /* 0x6e787c */

/* compress_log_output record code: level << 26 | argument count << 22. */
#define EFS_LOG_CODE(level, nargs) (((uint32_t)(level) << 26) | ((uint32_t)(nargs) << 22))

#define EFS_LOG(fn, level, line, nargs, plain, compact, ...) do { \
    if (audio_log_flags() & 2u) \
        audio_log_extended((level), module_tag, source_file, (fn), (line), (plain), ##__VA_ARGS__); \
    if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u)) \
        (void)compress_log_output(EFS_LOG_CODE((level), (nargs)), (compact), (compact), ##__VA_ARGS__); \
} while (0)

/* Stock open/close idiom (inlined at every site): ret is 0 on success, -1 on
 * open failure, the file_close result on close. */
#define EFS_FILE_OPEN(ret, path, flags) do { \
    (ret) = -1; \
    g_efs.file = file_open((path), efs_fopen_mode_45669a(flags)); \
    if (g_efs.file == NULL) { g_efs.is_open = 0u; } \
    else { (ret) = 0; g_efs.is_open = 1u; } \
} while (0)

#define EFS_FILE_CLOSE(ret) do { \
    if (g_efs.file == NULL) { (ret) = 0; } \
    else { (ret) = file_close(g_efs.file); g_efs.file = NULL; } \
} while (0)

static void efs_update_progress(void)
{
    if (g_efs.file_size != 0u)
        g_efs.progress = (uint8_t)(((uint64_t)g_efs.recv_total * 100u) / g_efs.file_size);
}

/* Import control (0xC4). */
void _efsFileCmdParse(uint8_t subcommand, const uint8_t *data, uint16_t length)
{
    const g2_efs_import_header_t *hdr = (const g2_efs_import_header_t *)(const void *)data;
    uint8_t unused_reply[2];
    const char *target;
    int32_t ret;
    int32_t err;

    (void)length;
    audio_uart_buffer_zero(unused_reply, 2u, 0u);

    if (subcommand == EFS_SEND_START) {
        g2_efs_start_tick = osKernelGetTickCount();
        EFS_LOG(fn_cmd, 4u, 0x15bu, 1u, s_send_start, c_send_start, g2_efs_start_tick);
        APP_ConnectParamOTASetFastMode();
        (void)audio_event_loop_remove_delayed(audio_ble_comm_link_delayed);
        if (g_efs.is_open == 1u) {
            EFS_LOG(fn_cmd, 2u, 0x160u, 0u, s_is_open, c_is_open);
            EFS_FILE_CLOSE(err);
            if (err < 0) {
                EFS_LOG(fn_cmd, 1u, 0x163u, 2u, s_close_failed, c_close_failed, g_efs.path, err);
                _evenEfsReplyToAPP(G2_EFS_CMD_IMPORT_CONTROL, EFS_SEND_START, 1u);
                return;
            }
        }
        audio_uart_buffer_zero(&g_efs, sizeof(g_efs), 0u);
        g_efs.file_type = hdr->file_type;
        g_efs.file_size = hdr->file_size;
        g_efs.rx_crc = hdr->file_crc;
        (void)audio_settings_copy_text(g_efs.path, hdr->path, sizeof(g_efs.path));
        EFS_LOG(fn_cmd, 4u, 0x16fu, 1u, s_file_type, c_file_type, g_efs.file_type);
        EFS_LOG(fn_cmd, 4u, 0x170u, 1u, s_file_size, c_file_size, g_efs.file_size);
        EFS_LOG(fn_cmd, 4u, 0x171u, 1u, s_rx_crc, c_rx_crc, g_efs.rx_crc);
        EFS_LOG(fn_cmd, 4u, 0x172u, 1u, s_file_path, c_file_path, g_efs.path);

        switch (g_efs.file_type) {
        case G2_EFS_TYPE_NOTIFICATION_JSON_WHITELIST:
            EFS_LOG(fn_cmd, 4u, 0x176u, 0u, s_type_whitelist, c_type_whitelist);
            /* Copies only the 26 name bytes over the received path. */
            target = path_whitelist;
            (void)audio_settings_copy_text(g_efs.path, path_whitelist, 0x1au);
            break;
        case G2_EFS_TYPE_ANDROID_MSG_JSON_NOTIFICATION:
            EFS_LOG(fn_cmd, 4u, 0x17du, 2u, s_type_android_size, c_type_android_size,
                    g_efs.file_size, EFS_ANDROID_MSG_MAX);
            if (g_efs.file_size >= EFS_ANDROID_MSG_MAX) {
                EFS_LOG(fn_cmd, 1u, 0x183u, 0u, s_too_large, c_too_large);
                _evenEfsReplyToAPP(G2_EFS_CMD_IMPORT_CONTROL, EFS_SEND_START, 1u);
                return;
            }
            g2_efs_android_msg_buffer = svc_android_notify_buffer_48e0a8();
            audio_uart_buffer_zero(g2_efs_android_msg_buffer, EFS_ANDROID_MSG_MAX, 0u);
            target = NULL;
            break;
        case G2_EFS_TYPE_OTHER_FILE:
            EFS_LOG(fn_cmd, 4u, 0x18bu, 0u, s_type_other, c_type_other);
            target = g_efs.path;
            break;
        case G2_EFS_TYPE_LOGGER_FILE:
        case G2_EFS_TYPE_TRACEPOINT_FILE:
            EFS_LOG(fn_cmd, 2u, 0x192u, 1u, s_export_only, c_export_only, g_efs.file_type);
            _evenEfsReplyToAPP(G2_EFS_CMD_IMPORT_CONTROL, EFS_SEND_START, 1u);
            return;
        default:
            return;
        }

        if (target != NULL &&
            audio_l2c_strncmp(g_efs.path, target, g2_log_module_length(target)) == 0) {
            EFS_LOG(fn_cmd, 3u, 0x19eu, 1u, s_target_path, c_target_path, g_efs.path);
            ret = file_remove(g_efs.path);
            if (ret < 0 && ret != EFS_LFS_ERR_NOENT) {
                EFS_LOG(fn_cmd, 1u, 0x1a2u, 2u, s_delete_failed, c_delete_failed, g_efs.path, ret);
            } else if (ret == 0) {
                EFS_LOG(fn_cmd, 4u, 0x1a4u, 0u, s_old_deleted, c_old_deleted);
            }
            /* Create the file, close it, then reopen read/write for the chunks. */
            EFS_FILE_OPEN(ret, g_efs.path, EFS_FS_O_CREAT | EFS_FS_O_RDWR);
            if (ret < 0) {
                EFS_LOG(fn_cmd, 1u, 0x1a8u, 2u, s_open_failed, c_open_failed, g_efs.path, ret);
                _evenEfsReplyToAPP(G2_EFS_CMD_IMPORT_CONTROL, EFS_SEND_START, 3u);
                return;
            }
            EFS_FILE_CLOSE(ret);
            if (ret < 0) {
                EFS_LOG(fn_cmd, 1u, 0x1aeu, 2u, s_close_failed, c_close_failed, g_efs.path, ret);
                _evenEfsReplyToAPP(G2_EFS_CMD_IMPORT_CONTROL, EFS_SEND_START, 3u);
                return;
            }
            EFS_FILE_OPEN(ret, g_efs.path, EFS_FS_O_RDWR);
            if (ret < 0) {
                EFS_LOG(fn_cmd, 1u, 0x1b5u, 2u, s_open_failed, c_open_failed, g_efs.path, ret);
                _evenEfsReplyToAPP(G2_EFS_CMD_IMPORT_CONTROL, EFS_SEND_START, 3u);
                return;
            }
            EFS_LOG(fn_cmd, 4u, 0x1b9u, 1u, s_opened_write, c_opened_write, g_efs.path);
        }
        _evenEfsReplyToAPP(G2_EFS_CMD_IMPORT_CONTROL, EFS_SEND_START, 0u);
        return;
    }

    if (subcommand == EFS_SEND_DATA_BEGIN) {
        g_efs.is_start = 1u;
        g2_efs_data_tick = osKernelGetTickCount();
        return;
    }
    if (subcommand != EFS_SEND_RESULT_CHECK)
        return;

    EFS_LOG(fn_cmd, 4u, 0x1c9u, 0u, s_result_check, c_result_check);
    EFS_LOG(fn_cmd, 4u, 0x1cau, 2u, s_calc_crc, c_calc_crc, g_efs.calc_crc, g_efs.rx_crc);
    EFS_LOG(fn_cmd, 4u, 0x1cbu, 2u, s_recv_size, c_recv_size, g_efs.recv_total, g_efs.file_size);

    switch (g_efs.file_type) {
    case G2_EFS_TYPE_NOTIFICATION_JSON_WHITELIST:
        EFS_LOG(fn_cmd, 4u, 0x1ceu, 0u, s_type_whitelist, c_type_whitelist);
        if (g_efs.is_open == 0u) {
            EFS_FILE_OPEN(ret, g_efs.path, EFS_FS_O_RDWR);
            if (ret < 0) {
                EFS_LOG(fn_cmd, 1u, 0x1d2u, 2u, s_open_failed, c_open_failed, g_efs.path, ret);
                _evenEfsReplyToAPP(G2_EFS_CMD_IMPORT_CONTROL, EFS_SEND_RESULT_CHECK, 6u);
                return;
            }
        }
        (void)efs_file_size_4566d8(g_efs.file);
        EFS_FILE_CLOSE(err);
        if (err < 0) {
            EFS_LOG(fn_cmd, 1u, 0x1dau, 2u, s_close_failed, c_close_failed, g_efs.path, err);
            _evenEfsReplyToAPP(G2_EFS_CMD_IMPORT_CONTROL, EFS_SEND_RESULT_CHECK, 6u);
            return;
        }
        if (g_efs.rx_crc == g_efs.calc_crc && g_efs.file_size == g_efs.recv_total) {
            EFS_LOG(fn_cmd, 4u, 0x1e0u, 0u, s_rsp_success, c_rsp_success);
            EFS_LOG(fn_cmd, 4u, 0x1e1u, 1u, s_wl_saved, c_wl_saved, g_efs.path);
            _evenEfsReplyToAPP(G2_EFS_CMD_IMPORT_CONTROL, EFS_SEND_RESULT_CHECK, 0u);
            Thread_SendEvtToNotifTask(EFS_NOTIF_EVT_WHITELIST_UPDATED);
        } else {
            EFS_LOG(fn_cmd, 1u, 0x1e5u, 0u, s_wl_verify_failed, c_wl_verify_failed);
            if (g_efs.rx_crc != g_efs.calc_crc)
                EFS_LOG(fn_cmd, 1u, 0x1e7u, 0u, s_wl_crc, c_wl_crc);
            if (g_efs.file_size != g_efs.recv_total)
                EFS_LOG(fn_cmd, 1u, 0x1eau, 0u, s_wl_size, c_wl_size);
            (void)file_remove(g_efs.path);
            EFS_LOG(fn_cmd, 4u, 0x1edu, 0u, s_rsp_check_fail, c_rsp_check_fail);
            _evenEfsReplyToAPP(G2_EFS_CMD_IMPORT_CONTROL, EFS_SEND_RESULT_CHECK, 6u);
        }
        audio_ble_param_reset_delayed_event(2000u);
        audio_uart_buffer_zero(&g_efs, sizeof(g_efs), 0u);
        return;
    case G2_EFS_TYPE_ANDROID_MSG_JSON_NOTIFICATION:
        EFS_LOG(fn_cmd, 4u, 0x1f6u, 0u, s_type_android, c_type_android);
        EFS_LOG(fn_cmd, 4u, 0x1f7u, 2u, s_rx_calc_crc, c_rx_calc_crc, g_efs.rx_crc, g_efs.calc_crc);
        EFS_LOG(fn_cmd, 4u, 0x1f8u, 2u, s_size_recv, c_size_recv, g_efs.file_size, g_efs.recv_total);
        if (g_efs.rx_crc == g_efs.calc_crc && g_efs.file_size == g_efs.recv_total) {
            EFS_LOG(fn_cmd, 4u, 0x1fau, 0u, s_rsp_success, c_rsp_success);
            _evenEfsReplyToAPP(G2_EFS_CMD_IMPORT_CONTROL, EFS_SEND_RESULT_CHECK, 0u);
            SVC_ANDROID_ParseNotification((const char *)g2_efs_android_msg_buffer);
        } else {
            EFS_LOG(fn_cmd, 4u, 0x1feu, 0u, s_rsp_check_fail, c_rsp_check_fail);
            _evenEfsReplyToAPP(G2_EFS_CMD_IMPORT_CONTROL, EFS_SEND_RESULT_CHECK, 6u);
        }
        audio_ble_param_reset_delayed_event(2000u);
        audio_uart_buffer_zero(&g_efs, sizeof(g_efs), 0u);
        return;
    case G2_EFS_TYPE_OTHER_FILE:
        EFS_LOG(fn_cmd, 4u, 0x207u, 0u, s_type_other, c_type_other);
        return;
    default:
        return;
    }
}

/* Import raw data (0xC5), accepted only while isStart == 1. */
void _efsFileRawDataParse(const uint8_t *data, uint16_t length)
{
    uint32_t len = length;
    uint32_t done;
    bool ok;

    if (g_efs.is_start != 1u)
        return;

    switch (g_efs.file_type) {
    case G2_EFS_TYPE_NOTIFICATION_JSON_WHITELIST:
        EFS_LOG(fn_raw, 4u, 0x21fu, 0u, s_type_whitelist, c_type_whitelist);
        if (g_efs.is_open == 0u) {
            EFS_LOG(fn_raw, 1u, 0x221u, 1u, s_not_open, c_not_open, g_efs.path);
            return;
        }
        (void)osKernelGetTickCount();
        /* Write, seek back to the chunk start and read it back for comparison. */
        done = file_write(data, 1u, len, g_efs.file);
        if (done == len) {
            (void)file_seek(g_efs.file, (int32_t)g_efs.recv_total, 0);
            done = file_read(g2_efs_verify_buffer, 1u, len, g_efs.file);
            if (done == len) {
                ok = g2_lfs_memcmp(g2_efs_verify_buffer, data, len) == 0;
                if (ok)
                    EFS_LOG(fn_raw, 4u, 0x22fu, 2u, s_wl_write_ok, c_wl_write_ok, len, g_efs.recv_total);
                else
                    EFS_LOG(fn_raw, 1u, 0x231u, 0u, s_wl_mismatch, c_wl_mismatch);
            } else {
                ok = false;
                EFS_LOG(fn_raw, 1u, 0x235u, 2u, s_read_short, c_read_short, len, done);
            }
        } else {
            ok = false;
            EFS_LOG(fn_raw, 1u, 0x239u, 2u, s_write_short, c_write_short, len, done);
        }
        (void)osKernelGetTickCount();
        if (!ok) {
            EFS_LOG(fn_raw, 1u, 0x24eu, 1u, s_wl_write_failed, c_wl_write_failed, g_efs.recv_total);
            _evenEfsReplyToAPP(G2_EFS_CMD_IMPORT_DATA, 1u, 3u);
            return;
        }
        file_crc32c_update_47cbc4(data, len, &g_efs.calc_crc);
        g_efs.recv_total += len;
        _evenEfsReplyToAPP(G2_EFS_CMD_IMPORT_DATA, 1u, 0u);
        efs_update_progress();
        EFS_LOG(fn_raw, 4u, 0x248u, 2u, s_recv_len, c_recv_len, g_efs.recv_total, len);
        g2_efs_last_tick = osKernelGetTickCount();
        EFS_LOG(fn_raw, 4u, 0x24au, 4u, s_update_speed, c_update_speed, g_efs.progress,
                g2_efs_last_tick - g2_efs_start_tick,
                ((len * 1000u) >> 10) / (g2_efs_last_tick - g2_efs_data_tick),
                ((g_efs.recv_total * 1000u) >> 10) / (g2_efs_last_tick - g2_efs_start_tick));
        return;
    case G2_EFS_TYPE_ANDROID_MSG_JSON_NOTIFICATION:
        EFS_LOG(fn_raw, 4u, 0x255u, 0u, s_type_android, c_type_android);
        (void)osKernelGetTickCount();
        /* No bound check here; the start header capped fileSize below 0x2137. */
        (void)audio_queue_copy_bytes(g2_efs_android_msg_buffer + g_efs.recv_total, data, len);
        file_crc32c_update_47cbc4(data, len, &g_efs.calc_crc);
        g_efs.recv_total += len;
        _evenEfsReplyToAPP(G2_EFS_CMD_IMPORT_DATA, 1u, 0u);
        efs_update_progress();
        EFS_LOG(fn_raw, 4u, 0x263u, 2u, s_recv_len, c_recv_len, g_efs.recv_total, len);
        g2_efs_last_tick = osKernelGetTickCount();
        EFS_LOG(fn_raw, 4u, 0x265u, 4u, s_update_speed, c_update_speed, g_efs.progress,
                g2_efs_last_tick - g2_efs_start_tick,
                ((len * 1000u) >> 10) / (g2_efs_last_tick - g2_efs_data_tick),
                ((g_efs.recv_total * 1000u) >> 10) / (g2_efs_last_tick - g2_efs_start_tick));
        return;
    case G2_EFS_TYPE_OTHER_FILE:
        EFS_LOG(fn_raw, 4u, 0x26cu, 0u, s_type_other, c_type_other);
        return;
    default:
        return;
    }
}

/* Export control/data (0xC6/0xC7). data[0] is the phone's response byte for
 * subcommands 1 and 2. */
void _efsExportFileParse(uint8_t subcommand, const uint8_t *data, uint16_t length)
{
    const g2_efs_export_header_t *hdr = (const g2_efs_export_header_t *)(const void *)data;
    uint8_t unused_reply[2];
    uint8_t meta[10];
    uint8_t is_tracepoint = 0u;
    uint8_t response;
    uint32_t read_len;
    uint32_t done;
    int32_t ret = -1;
    int32_t err;

    (void)length;
    audio_uart_buffer_zero(unused_reply, 2u, 0u);
    response = data[0];

    if (subcommand == EFS_EXPORT_START) {
        g2_efs_start_tick = osKernelGetTickCount();
        EFS_LOG(fn_export, 4u, 0x288u, 1u, s_export_start, c_export_start, g2_efs_start_tick);
        compress_log_export_notify(1u);
        APP_ConnectParamOTASetFastMode();
        if (g_efs.is_open == 1u) {
            EFS_LOG(fn_export, 2u, 0x28du, 0u, s_is_open, c_is_open);
            EFS_FILE_CLOSE(err);
            if (err < 0) {
                EFS_LOG(fn_export, 1u, 0x290u, 2u, s_close_failed, c_close_failed, g_efs.path, err);
                goto cleanup;
            }
        }
        audio_uart_buffer_zero(&g_efs, sizeof(g_efs), 0u);
        g_efs.file_type = hdr->file_type;
        switch (g_efs.file_type) {
        case G2_EFS_TYPE_NOTIFICATION_JSON_WHITELIST:
            EFS_LOG(fn_export, 4u, 0x299u, 0u, s_type_whitelist, c_type_whitelist);
            (void)audio_settings_copy_text(g_efs.path, path_whitelist, 0x1au);
            break;
        case G2_EFS_TYPE_OTHER_FILE:
            (void)audio_settings_copy_text(g_efs.path, hdr->path, sizeof(g_efs.path));
            g_efs.path[sizeof(g_efs.path) - 1u] = '\0';
            EFS_LOG(fn_export, 4u, 0x2a2u, 1u, s_type_other_path, c_type_other_path, g_efs.path);
            is_tracepoint = efs_is_tracepoint_path_456580(g_efs.path);
            break;
        case G2_EFS_TYPE_LOGGER_FILE:
            (void)audio_settings_copy_text(g_efs.path, hdr->path, sizeof(g_efs.path));
            g_efs.path[sizeof(g_efs.path) - 1u] = '\0';
            EFS_LOG(fn_export, 4u, 0x2abu, 1u, s_type_logger, c_type_logger, g_efs.path);
            if (efs_is_logger_path_456606(g_efs.path) == 0u) {
                EFS_LOG(fn_export, 2u, 0x2adu, 1u, s_bad_logger, c_bad_logger, g_efs.path);
                _evenEfsReplyToAPP(G2_EFS_CMD_EXPORT_CONTROL, EFS_EXPORT_START, 1u);
                goto cleanup;
            }
            break;
        case G2_EFS_TYPE_TRACEPOINT_FILE:
            (void)audio_settings_copy_text(g_efs.path, hdr->path, sizeof(g_efs.path));
            g_efs.path[sizeof(g_efs.path) - 1u] = '\0';
            EFS_LOG(fn_export, 4u, 0x2b8u, 1u, s_type_trace, c_type_trace, g_efs.path);
            if (efs_is_tracepoint_path_456580(g_efs.path) == 0u) {
                EFS_LOG(fn_export, 2u, 0x2bau, 1u, s_bad_trace, c_bad_trace, g_efs.path);
                _evenEfsReplyToAPP(G2_EFS_CMD_EXPORT_CONTROL, EFS_EXPORT_START, 1u);
                goto cleanup;
            }
            is_tracepoint = 1u;
            break;
        default:
            /* Path stays empty; the CRC step below fails with status 2. */
            break;
        }
        if (is_tracepoint != 0u) {
            /* Flush/prepare the tracepoint store; failure is only logged. */
            err = audio_tracepoint_prepare_pull_48ec9e();
            if (err != 0)
                EFS_LOG(fn_export, 2u, 0x2cau, 1u, s_tp_prepare, c_tp_prepare, err);
        }
        if (_fileCaculateCRC(&g_efs.file, g_efs.path, &g_efs.file_size, &g_efs.calc_crc) == 0u) {
            EFS_LOG(fn_export, 1u, 0x2cfu, 0u, s_crc_failed, c_crc_failed);
            _evenEfsReplyToAPP(G2_EFS_CMD_EXPORT_CONTROL, EFS_EXPORT_START, 2u);
            goto cleanup;
        }
        /* Start reply: {0, 0, fileSize LE32, CRC-32C LE32}. */
        audio_uart_buffer_zero(meta, sizeof(meta), 0u);
        meta[0] = EFS_EXPORT_START;
        meta[1] = 0u;
        meta[2] = (uint8_t)g_efs.file_size;
        meta[3] = (uint8_t)(g_efs.file_size >> 8);
        meta[4] = (uint8_t)(g_efs.file_size >> 16);
        meta[5] = (uint8_t)(g_efs.file_size >> 24);
        meta[6] = (uint8_t)g_efs.calc_crc;
        meta[7] = (uint8_t)(g_efs.calc_crc >> 8);
        meta[8] = (uint8_t)(g_efs.calc_crc >> 16);
        meta[9] = (uint8_t)(g_efs.calc_crc >> 24);
        g_efs.remain_len = g_efs.file_size;
        (void)Thread_MsgEfsTxByBle(1u, G2_EFS_CMD_EXPORT_CONTROL, meta, sizeof(meta));
        EFS_FILE_OPEN(ret, g_efs.path, EFS_FS_O_RDONLY);
        if (ret < 0) {
            EFS_LOG(fn_export, 1u, 0x2e6u, 2u, s_open_failed, c_open_failed, g_efs.path, ret);
            goto cleanup;
        }
        g_efs.is_start = 1u;
        g2_efs_export_active = 1u;
        EFS_LOG(fn_export, 4u, 0x2ebu, 1u, s_is_start, c_is_start, g_efs.is_start);
        (void)osDelay(30u);
        response = 0u; /* fall through and send the first chunk */
    } else if (subcommand == EFS_EXPORT_RESULT_CHECK) {
        EFS_LOG(fn_export, 4u, 0x32cu, 1u, s_export_result, c_export_result, response);
        goto cleanup;
    } else if (subcommand > EFS_EXPORT_RESULT_CHECK) {
        if (subcommand != EFS_EXPORT_CANCEL)
            return;
        EFS_LOG(fn_export, 2u, 0x332u, 0u, s_export_cancel, c_export_cancel);
        _evenEfsReplyToAPP(G2_EFS_CMD_EXPORT_CONTROL, EFS_EXPORT_CANCEL, 0u);
        goto cleanup;
    }

    /* EFS_EXPORT_NEXT, or the first chunk right after a start. */
    if (g_efs.is_start == 0u)
        return;
    if (response != 0u) {
        EFS_LOG(fn_export, 1u, 0x2f7u, 1u, s_export_resp, c_export_resp, response);
        goto cleanup;
    }
    g2_efs_data_tick = osKernelGetTickCount();
    read_len = EFS_CHUNK;
    audio_uart_buffer_zero(g2_efs_export_buffer, EFS_CHUNK, 0u);
    if (g_efs.remain_len < EFS_CHUNK)
        read_len = g_efs.remain_len;
    EFS_LOG(fn_export, 4u, 0x2ffu, 2u, s_read_len, c_read_len, read_len, g_efs.remain_len);
    done = file_read(g2_efs_export_buffer, 1u, read_len, g_efs.file);
    if (done != read_len) {
        EFS_LOG(fn_export, 1u, 0x302u, 1u, s_read_failed, c_read_failed, done);
        EFS_FILE_CLOSE(err);
        if (err < 0)
            EFS_LOG(fn_export, 1u, 0x305u, 2u, s_close_failed, c_close_failed, g_efs.path, err);
        goto cleanup;
    }
    EFS_LOG(fn_export, 4u, 0x309u, 1u, s_read_result, c_read_result, done);
    g_efs.recv_total += done;
    g_efs.chunk_len = done;
    g_efs.remain_len = g_efs.file_size - g_efs.recv_total;
    (void)Thread_MsgEfsNotifyByBle(1u, G2_EFS_CMD_EXPORT_DATA, g2_efs_export_buffer, (uint16_t)done);
    efs_update_progress();
    g2_efs_last_tick = osKernelGetTickCount();
    EFS_LOG(fn_export, 4u, 0x315u, 3u, s_export_speed, c_export_speed, g_efs.progress,
            g2_efs_last_tick - g2_efs_start_tick,
            ((g_efs.recv_total * 1000u) >> 10) / (g2_efs_last_tick - g2_efs_start_tick));
    EFS_LOG(fn_export, 4u, 0x318u, 3u, s_export_total, c_export_total,
            g_efs.recv_total, g_efs.file_size, g_efs.calc_crc);
    if (g_efs.recv_total < g_efs.file_size)
        return;
    g_efs.is_start = 0u;
    EFS_FILE_CLOSE(err);
    if (err >= 0) {
        audio_uart_buffer_zero(&g_efs, sizeof(g_efs), 0u);
        g2_efs_export_active = 0u;
        compress_log_export_notify(0u);
        audio_ble_param_reset_delayed_event(2000u);
        return;
    }
    EFS_LOG(fn_export, 1u, 0x31du, 2u, s_close_failed, c_close_failed, g_efs.path, err);

cleanup:
    if (g_efs.is_open == 1u) {
        EFS_FILE_CLOSE(err);
        if (err < 0)
            EFS_LOG(fn_export, 1u, 0x342u, 2u, s_close_failed, c_close_failed, g_efs.path, err);
    }
    audio_uart_buffer_zero(&g_efs, sizeof(g_efs), 0u);
    g2_efs_export_active = 0u;
    compress_log_export_notify(0u);
    audio_ble_param_reset_delayed_event(2000u);
}

int32_t semantic_EfsFrameDispatch(uint8_t command, const uint8_t *payload, uint16_t length)
{
    if (command == G2_EFS_CMD_IMPORT_CONTROL)
        _efsFileCmdParse(payload[0], payload + 1, (uint16_t)(length - 1u));
    else if (command == G2_EFS_CMD_IMPORT_DATA)
        _efsFileRawDataParse(payload, length);
    else if (command == G2_EFS_CMD_EXPORT_CONTROL || command == G2_EFS_CMD_EXPORT_DATA)
        _efsExportFileParse(payload[0], payload + 1, (uint16_t)(length - 1u));
    return 0;
}

void semantic_EfsNotifyStatus4(uint8_t command)
{
    uint8_t payload[2];

    if (command == G2_EFS_CMD_IMPORT_DATA) {
        payload[0] = 1u;
        payload[1] = 4u;
        (void)Thread_MsgEfsTxByBle(1u, command, payload, 2u);
    }
}

void semantic_EfsNotifyStatus2(uint8_t command)
{
    uint8_t payload[2];

    if (command == G2_EFS_CMD_IMPORT_DATA) {
        payload[0] = 1u;
        payload[1] = 2u;
        (void)Thread_MsgEfsTxByBle(1u, command, payload, 2u);
    }
}

void semantic_EfsNotifyStatus5(uint8_t command)
{
    uint8_t payload[2];

    if (command == G2_EFS_CMD_IMPORT_DATA) {
        payload[0] = 1u;
        payload[1] = 5u;
        (void)Thread_MsgEfsTxByBle(1u, command, payload, 2u);
    }
}

uint8_t semantic_EfsTransferActive(void)
{
    return g_efs.is_start == 1u ? 1u : 0u;
}

void EFS_CancelExport(void)
{
    int32_t err;

    if (g2_efs_export_active == 0u)
        return;
    EFS_LOG(fn_cancel, 2u, 0x3a8u, 0u, s_cancel, c_cancel);
    _evenEfsReplyToAPP(G2_EFS_CMD_EXPORT_CONTROL, EFS_EXPORT_CANCEL, 8u);
    if (g_efs.is_open == 1u) {
        EFS_FILE_CLOSE(err);
        if (err < 0)
            EFS_LOG(fn_cancel, 1u, 0x3b3u, 2u, s_close_failed, c_close_failed, g_efs.path, err);
    }
    audio_uart_buffer_zero(&g_efs, sizeof(g_efs), 0u);
    g2_efs_export_active = 0u;
    compress_log_export_notify(0u);
    audio_ble_param_reset_delayed_event(2000u);
}
