/* Stock D:\01_workspace\s200_ap510b_iar_git\app\gui\logger\logger_setting.c
 * (log tag "logger.setting"), protobuf command handler.
 * Native rows: loggerSetting_common_data_handler 0x4592dc..0x45a386,
 * simplify_log_filename 0x45a3b4..0x45a462. Literal pools 0x459d58..0x459d60
 * (including the inline "%s" at 0x459d5c), 0x459f8c..0x459fa4,
 * 0x45a05c..0x45a074, 0x45a164..0x45a16c, 0x45a1c8..0x45a1d0,
 * 0x45a258..0x45a260, 0x45a2a8..0x45a2b0, 0x45a388..0x45a3b4,
 * 0x45a464..0x45a558.
 *
 * Sources: 0 = phone app (protobuf on BLE service 0x0f), 0x0b = file list
 * forwarded by the peer arm, 0x0c = peer delete result (already encoded).
 * The /log helpers live in app/a-05-logger-setting. */
#include <stdint.h>
#include <stddef.h>
#include "g2_logger_setting.h"

/* nanopb 0.4 stream ABI (32-bit). */
typedef struct {
    void *callback;
    void *state;
    uint32_t bytes_left;
    const char *errmsg;     /* +0x0c */
} logger_pb_istream_t;
_Static_assert(sizeof(logger_pb_istream_t) == 16u, "nanopb istream");

typedef struct {
    void *callback;
    void *state;
    uint32_t max_size;
    uint32_t bytes_written; /* +0x0c */
    const char *errmsg;
} logger_pb_ostream_t;
_Static_assert(sizeof(logger_pb_ostream_t) == 20u, "nanopb ostream");

#define LOGGER_LIST_NAMES 40u
#define LOGGER_NAME_LEN   0x20u

/* Decoded/encoded logger-setting message (descriptor ROM 0x777da4). */
typedef struct {
    uint8_t cmd;              /* +0x00 0 heart, 1 ble switch, 2 level, 4 list, 5 delete, 6 delete all */
    uint8_t magic_random;     /* +0x01 echoed in every reply */
    uint16_t which_payload;   /* +0x02 oneof tag: 3 switch, 4 level, 6 file list, 7 file name */
    union {
        uint32_t value;       /* +0x04 switch on/off, log level */
        struct {
            uint16_t count;   /* +0x04 */
            char names[LOGGER_LIST_NAMES][LOGGER_NAME_LEN]; /* +0x06 "R:3", "L:h" ... */
        } file_list;
        char file_name[LOGGER_NAME_LEN]; /* +0x04 .. +0x23 */
    } payload;
} logger_setting_msg_t;
_Static_assert(sizeof(logger_setting_msg_t) == 0x508u, "stock message is 0x508 bytes");

extern logger_setting_msg_t g2_logger_setting_rx_msg;   /* RAM 0x20377194 */
extern logger_setting_msg_t g2_logger_setting_tx_msg;   /* RAM 0x2037769c */
extern uint8_t g2_logger_setting_tx_encoded[0x578];     /* RAM 0x203766c0 */
extern volatile int32_t g2_master_file_list_stored_flag; /* RAM 0x200746ac */
extern g2_logger_file_list_t g2_logger_file_list;       /* RAM 0x2037b098 */
extern const uint8_t audio_uart_ble_log_pb_descriptor_777da4[]; /* ROM 0x777da4 */

extern void audio_uart_buffer_zero(void *dst, uint32_t len, uint32_t fill); /* 0x43c0e4 memset */
extern void *audio_queue_copy_bytes(void *, const void *, uint32_t);       /* 0x439be4 memcpy */
/* pb_istream_from_buffer / pb_ostream_from_buffer return the stream by value
 * (IAR copies the returned temporary with 0x439c04). */
extern logger_pb_istream_t audio_uart_pb_stream_init(const void *buf, uint32_t len); /* 0x48f49c */
extern uint32_t audio_uart_pb_decode(logger_pb_istream_t *, const void *, void *);   /* 0x490120 */
extern logger_pb_ostream_t audio_pb_ostream_from_buffer(void *buf, uint32_t size);   /* 0x4905f4 */
extern uint32_t audio_pb_encode(logger_pb_ostream_t *, const void *, const void *);  /* 0x490c32 */
extern int32_t Thread_MsgPbTxByBle(uint32_t, uint32_t, const void *, uint32_t);       /* 0x475b14 */
extern int32_t audio_uart_handshake_send(uint32_t channel, const void *bytes, uint32_t size,
                                         uint32_t flags, uint32_t command);         /* 0x465480 */
extern uint8_t audio_uart_device_role_get(void);        /* 0x45a568, 1 = R (master), 2 = L */
extern void audio_uart_task_delay(uint32_t ticks);      /* 0x454b4c */
extern void loggerSetting_set_ble_transmit(uint32_t enabled); /* 0x458df0 */
extern void elog_set_filter_lvl_43d3a6(uint8_t level);  /* 0x43d3a6 */
extern void audio_log_policy_set_43d0d4(uint8_t level); /* 0x43d0d4, byte RAM 0x20004544 */
extern void ble_state_skip_manual_start(uint32_t);      /* 0x478110 */
extern void svc_compress_log_force_sync_to_files(void); /* 0x43cf8c */
extern int32_t file_remove(const char *path);           /* 0x47498c */
extern void *audio_settings_copy_text(void *dst, const void *src, uint32_t len); /* 0x44b5a0 strncpy */
extern int32_t g2_audio_dump_snprintf(char *dst, uint32_t size, const char *format, ...); /* 0x44b728 */
extern int32_t audio_l2c_strncmp(const char *a, const char *b, uint32_t count); /* 0x44b610 */
extern int32_t audio_ble_parse_version(const char *s, const char *format, ...); /* 0x475fc0 sscanf */
extern int32_t audio_uart_font_path_compare(const char *a, const char *b); /* 0x46cacc strcmp */
extern uint32_t audio_log_flags(void);                  /* 0x43d0ce */
extern void audio_log_extended(uint8_t, const char *, const char *, const char *,
                               uint32_t, const char *, ...); /* 0x43d574 */
extern uint32_t compress_log_output(uint32_t, const char *, const char *, ...); /* 0x43ce9e */

int32_t simplify_log_filename(const char *filename, uint8_t role, char *out, uint32_t out_size);

static const char module_tag[] = "logger.setting"; /* ROM 0x786220 */
static const char source_file[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\app\\gui\\logger\\logger_setting.c"; /* ROM 0x7034f4 */
static const char fn_handler[] = "loggerSetting_common_data_handler"; /* ROM 0x755070 */
static const char fn_simplify[] = "simplify_log_filename";             /* ROM 0x777dec */
static const char none_text[] = "(none)";                               /* ROM 0x78d82c */
static const char fmt_s[] = "%s";                                       /* ROM 0x459d5c */
static const char prefix_l[] = "L:/log/";                               /* ROM 0x78d834 */
static const char prefix_r[] = "R:/log/";                               /* ROM 0x78d83c */
static const char dir_log[] = "/log";                                   /* ROM 0x78d81c */
static const char fmt_compress_log[] = "compress_log_%d.bin";           /* ROM 0x77f93c */
static const char fmt_role_index[] = "%c:%d";                           /* ROM 0x78d844 */
static const char name_hardfault[] = "hardfault.txt";                   /* ROM 0x786240 */
static const char fmt_role_hardfault[] = "%c:h";                        /* ROM 0x78d84c */

static const char e_recv[] = "loggerSetting_common_data_handler recv data len = %d"; /* 0x71f950 */
static const char c_recv[] = "[logger.setting]loggerSetting_common_data_handler recv data len = %d"; /* 0x6faf4c */
static const char e_decode[] = "loggerSetting_common_data_handler protobuf decode failed: %s\n"; /* 0x70c4a4 */
static const char c_decode[] = "[logger.setting]loggerSetting_common_data_handler protobuf decode failed: %s\n"; /* 0x6ed9c8 */
static const char e_cmd[] = "loggerSetting_common_data_handler cmd = %d, magicRandom = %d"; /* 0x70c4e4 */
static const char c_cmd[] = "[logger.setting]loggerSetting_common_data_handler cmd = %d, magicRandom = %d"; /* 0x6eda18 */
static const char e_heart[] = "loggerSetting_common_data_handler receive connect heart packet request from APP"; /* 0x6eda68 */
static const char c_heart[] = "[logger.setting]loggerSetting_common_data_handler receive connect heart packet request from APP"; /* 0x6dd6b4 */
static const char e_switch[] = "loggerSetting_common_data_handler receive ble logger switch set request from APP"; /* 0x6e83f8 */
static const char c_switch[] = "[logger.setting]loggerSetting_common_data_handler receive ble logger switch set request from APP"; /* 0x6dabec */
static const char e_level[] = "loggerSetting_common_data_handler receive ble logger level set request from APP"; /* 0x6edab8 */
static const char c_level[] = "[logger.setting]loggerSetting_common_data_handler receive ble logger level set request from APP"; /* 0x6dd714 */
static const char e_list_req[] = "loggerSetting_common_data_handler receive request file name request from APP"; /* 0x6edb08 */
static const char c_list_req[] = "[logger.setting]loggerSetting_common_data_handler receive request file name request from APP"; /* 0x6dd774 */
static const char e_scanned[] = "Successfully scanned %d files in /log directory"; /* 0x734c64 */
static const char c_scanned[] = "[logger.setting]Successfully scanned %d files in /log directory"; /* 0x70c524 */
static const char e_entry[] = "  [%d] %s - %d bytes (type: %d)"; /* 0x7605d0 */
static const char c_entry[] = "[logger.setting]  [%d] %s - %d bytes (type: %d)"; /* 0x734c94 */
static const char e_encode_list[] = "loggerSetting common data handler protobuf encode failed"; /* 0x715b38 */
static const char c_encode_list[] = "[logger.setting]loggerSetting common data handler protobuf encode failed"; /* 0x6f3f7c */
static const char e_list_sent[] = "loggerSetting common data handler send file list to slave success"; /* 0x70357c */
static const char c_list_sent[] = "[logger.setting]loggerSetting common data handler send file list to slave success"; /* 0x6e844c */
static const char e_stored[] = "master_file_list_stored_flag = %d"; /* 0x755094 */
static const char c_stored[] = "[logger.setting]master_file_list_stored_flag = %d"; /* 0x72a2f4 */
static const char e_scan_fail[] = "Failed to scan /log directory"; /* 0x7605f0 */
static const char c_scan_fail[] = "[logger.setting]Failed to scan /log directory"; /* 0x734cc4 */
static const char e_del_req[] = "receive delete file name request from APP"; /* 0x73f318 */
static const char c_del_req[] = "[logger.setting]receive delete file name request from APP"; /* 0x715b74 */
static const char e_not_slave[] = "not slave file path, current path: %s"; /* 0x74a6a4 */
static const char c_not_slave[] = "[logger.setting]not slave file path, current path: %s"; /* 0x71f988 */
static const char e_not_master[] = "not master file path, current path: %s"; /* 0x74a6cc */
static const char c_not_master[] = "[logger.setting]not master file path, current path: %s"; /* 0x71f9c0 */
static const char e_del[] = "loggerSetting delete file: %s"; /* 0x760610 */
static const char c_del[] = "[logger.setting]loggerSetting delete file: %s"; /* 0x734cf4 */
static const char e_del_fail[] = "loggerSetting delete file failed: %s"; /* 0x74a6f4 */
static const char c_del_fail[] = "[logger.setting]loggerSetting delete file failed: %s"; /* 0x71f9f8 */
static const char e_del_ok[] = "loggerSetting delete file success: %s"; /* 0x74a71c */
static const char c_del_ok[] = "[logger.setting]loggerSetting delete file success: %s"; /* 0x71fa30 */
static const char e_del_fwd[] = "loggerSetting slave send delete result to master: file=%s, len=%d"; /* 0x7035c0 */
static const char c_del_fwd[] = "[logger.setting]loggerSetting slave send delete result to master: file=%s, len=%d"; /* 0x6e84a0 */
static const char e_del_fwd_fail[] = "loggerSetting slave send delete result to master failed"; /* 0x71fa68 */
static const char c_del_fwd_fail[] = "[logger.setting]loggerSetting slave send delete result to master failed"; /* 0x6faf94 */
static const char e_del_all_req[] = "receive delete all logger file request from APP"; /* 0x734d24 */
static const char c_del_all_req[] = "[logger.setting]receive delete all logger file request from APP"; /* 0x70c564 */
static const char e_del_all_fail[] = "loggerSetting delete all logger file failed"; /* 0x73f344 */
static const char c_del_all_fail[] = "[logger.setting]loggerSetting delete all logger file failed"; /* 0x715bb0 */
static const char e_del_all_ok[] = "loggerSetting deleted %d files successfully"; /* 0x73f370 */
static const char c_del_all_ok[] = "[logger.setting]loggerSetting deleted %d files successfully"; /* 0x715bec */
static const char e_unknown_sync[] = "sync_info_data_handler: unknown cmd = %d"; /* 0x73f39c */
static const char c_unknown_sync[] = "[logger.setting]sync_info_data_handler: unknown cmd = %d"; /* 0x715c28 */
static const char e_peer_list[] = "loggerSetting_common_data_handler receive slave send file list to master request from APP"; /* 0x6e05d0 */
static const char c_peer_list[] = "[logger.setting]loggerSetting_common_data_handler receive slave send file list to master request from APP"; /* 0x6cab6c */
static const char e_peer_name[] = "loggerSetting_common_data_handler file name = %s"; /* 0x72a328 */
static const char c_peer_name[] = "[logger.setting]loggerSetting_common_data_handler file name = %s"; /* 0x703604 */
static const char e_encode[] = "loggerSetting protobuf encode failed"; /* 0x74a744 */
static const char c_encode[] = "[logger.setting]loggerSetting protobuf encode failed"; /* 0x71faa0 */
static const char e_to_master_fail[] = "loggerSetting send file list to master failed"; /* 0x734d54 */
static const char c_to_master_fail[] = "[logger.setting]loggerSetting send file list to master failed"; /* 0x70c5a4 */
static const char e_to_master_ok[] = "loggerSetting send file list to master success"; /* 0x734d84 */
static const char c_to_master_ok[] = "[logger.setting]loggerSetting send file list to master success"; /* 0x70c5e4 */
static const char e_not_stored[] = "loggerSetting_common_data_handler master file list not stored"; /* 0x70c624 */
static const char c_not_stored[] = "[logger.setting]loggerSetting_common_data_handler master file list not stored"; /* 0x6edb58 */
static const char e_unknown[] = "loggerSetting_common_data_handler: unknown cmd = %d"; /* 0x72a35c */
static const char c_unknown[] = "[logger.setting]loggerSetting_common_data_handler: unknown cmd = %d"; /* 0x703648 */
static const char e_peer_del[] = "master recv slave delete result, len = %d"; /* 0x73f3c8 */
static const char c_peer_del[] = "[logger.setting]master recv slave delete result, len = %d"; /* 0x715c64 */
static const char e_fwd_fail[] = "loggerSetting master forward slave delete result to APP failed"; /* 0x70c664 */
static const char c_fwd_fail[] = "[logger.setting]loggerSetting master forward slave delete result to APP failed"; /* 0x6edba8 */
static const char e_fwd_ok[] = "loggerSetting master forward slave delete result to APP success"; /* 0x70c6a4 */
static const char c_fwd_ok[] = "[logger.setting]loggerSetting master forward slave delete result to APP success"; /* 0x6edbf8 */
static const char e_simplify[] = "simple change log filename, filename = %s, role_status = %c"; /* 0x715ca0 */
static const char c_simplify[] = "[logger.setting]simple change log filename, filename = %s, role_status = %c"; /* 0x6f3fc8 */

/* Every stock call pairs an extended log (flags bit 1) with a compressed log
 * (flags bit 0 or 2) whose category is level << 26 | argument count << 22. */
static uint32_t extended_on(void)
{
    return (audio_log_flags() & 2u) != 0u;
}

static uint32_t compressed_on(void)
{
    return (audio_log_flags() & 1u) != 0u || (audio_log_flags() & 4u) != 0u;
}

static void log0(uint8_t level, uint32_t line, const char *e, const char *c)
{
    if (extended_on())
        audio_log_extended(level, module_tag, source_file, fn_handler, line, e);
    if (compressed_on())
        (void)compress_log_output((uint32_t)level << 26, c, c);
}

static void log1(uint8_t level, uint32_t line, const char *e, const char *c, uintptr_t a)
{
    if (extended_on())
        audio_log_extended(level, module_tag, source_file, fn_handler, line, e, a);
    if (compressed_on())
        (void)compress_log_output(((uint32_t)level << 26) | 0x00400000u, c, c, a);
}

static void log2(uint8_t level, uint32_t line, const char *e, const char *c,
                 uintptr_t a, uintptr_t b)
{
    if (extended_on())
        audio_log_extended(level, module_tag, source_file, fn_handler, line, e, a, b);
    if (compressed_on())
        (void)compress_log_output(((uint32_t)level << 26) | 0x00800000u, c, c, a, b);
}

static uint8_t log_role_letter(void)
{
    return audio_uart_device_role_get() == 1u ? (uint8_t)'R' : (uint8_t)'L';
}

/* Clears the reply buffers and stamps cmd / magicRandom / oneof tag. */
static logger_setting_msg_t *reply_begin(uint8_t cmd, uint8_t magic, uint16_t which)
{
    logger_setting_msg_t *tx = &g2_logger_setting_tx_msg;
    audio_uart_buffer_zero(tx, sizeof *tx, 0u);
    audio_uart_buffer_zero(g2_logger_setting_tx_encoded, sizeof g2_logger_setting_tx_encoded, 0u);
    tx->cmd = cmd;
    tx->magic_random = magic;
    tx->which_payload = which;
    return tx;
}

/* Returns 0 on encode failure, else 1 with the encoded length in *length. */
static uint32_t reply_encode(uint32_t *length)
{
    logger_pb_ostream_t stream = audio_pb_ostream_from_buffer(
        g2_logger_setting_tx_encoded, sizeof g2_logger_setting_tx_encoded);
    if (audio_pb_encode(&stream, audio_uart_ble_log_pb_descriptor_777da4,
                        &g2_logger_setting_tx_msg) == 0u)
        return 0u;
    *length = stream.bytes_written;
    return 1u;
}

static int32_t reply_send_app(uint32_t length)
{
    return Thread_MsgPbTxByBle(1u, 0x0fu, g2_logger_setting_tx_encoded, (uint16_t)length);
}

static uint32_t decode_request(const void *data, uint32_t length, uint32_t line)
{
    logger_setting_msg_t *rx = &g2_logger_setting_rx_msg;
    audio_uart_buffer_zero(rx, sizeof *rx, 0u);
    logger_pb_istream_t stream = audio_uart_pb_stream_init(data, length);
    if ((uint8_t)audio_uart_pb_decode(&stream, audio_uart_ble_log_pb_descriptor_777da4, rx) != 0u)
        return 1u;
    if (extended_on())
        audio_log_extended(1u, module_tag, source_file, fn_handler, line, e_decode,
                           stream.errmsg != 0 ? stream.errmsg : none_text);
    if (compressed_on())
        (void)compress_log_output(0x04400000u, c_decode, c_decode,
                                  stream.errmsg != 0 ? stream.errmsg : none_text);
    return 0u;
}

static int32_t app_ble_switch(uint8_t magic)
{
    const logger_setting_msg_t *rx = &g2_logger_setting_rx_msg;
    uint32_t length;
    log0(4u, 0xf1u, e_switch, c_switch);
    if (rx->which_payload != 3u)
        return 0;
    if (rx->payload.value == 1u) {
        loggerSetting_set_ble_transmit(1u);
        log0(4u, 0xf5u, e_switch, c_switch);
    } else {
        loggerSetting_set_ble_transmit(0u);
        log0(4u, 0xf8u, e_switch, c_switch);
    }
    (void)reply_begin(1u, magic, 3u);
    if (reply_encode(&length) == 0u)
        return 0;
    return reply_send_app(length);
}

static int32_t app_log_level(uint8_t magic)
{
    const logger_setting_msg_t *rx = &g2_logger_setting_rx_msg;
    uint32_t length;
    log0(4u, 0x113u, e_level, c_level);
    if (rx->which_payload != 4u)
        return 0;
    log0(4u, 0x115u, e_level, c_level);
    elog_set_filter_lvl_43d3a6((uint8_t)rx->payload.value);
    audio_log_policy_set_43d0d4((uint8_t)rx->payload.value);
    (void)reply_begin(2u, magic, 4u);
    if (reply_encode(&length) == 0u)
        return 0;
    return reply_send_app(length);
}

/* Builds the own-arm list; the L arm sends it to the R arm (command 0x0b),
 * the R arm keeps it until the peer list arrives (source 0x0b below). */
static int32_t app_file_list(uint8_t magic)
{
    g2_logger_file_list_t *list = &g2_logger_file_list;
    uint32_t length;
    log0(4u, 0x12du, e_list_req, c_list_req);
    ble_state_skip_manual_start(0u);
    svc_compress_log_force_sync_to_files();
    if (scan_log_files() != 0) {
        log0(1u, 0x170u, e_scan_fail, c_scan_fail);
        return 0;
    }
    log1(4u, 0x136u, e_scanned, c_scanned, list->count);
    for (uint32_t i = 0; i < list->count; i++) {
        const g2_logger_file_entry_t *entry = &list->files[i];
        if (extended_on())
            audio_log_extended(4u, module_tag, source_file, fn_handler, 0x13eu, e_entry,
                               i, entry->name, entry->size, entry->type);
        if (compressed_on())
            (void)compress_log_output(0x11000000u, c_entry, c_entry, i, entry->name,
                                      entry->size, entry->type);
    }
    logger_setting_msg_t *tx = reply_begin(4u, magic, 6u);
    tx->payload.file_list.count = (uint16_t)list->count;
    for (uint32_t i = 0; i < list->count; i++)
        (void)simplify_log_filename(list->files[i].name, log_role_letter(),
                                    tx->payload.file_list.names[i], LOGGER_NAME_LEN);
    if (audio_uart_device_role_get() == 2u) {
        if (reply_encode(&length) == 0u) {
            log0(1u, 0x158u, e_encode_list, c_encode_list);
            return 0;
        }
        audio_uart_task_delay(100u);
        (void)audio_uart_handshake_send(0x0fu, g2_logger_setting_tx_encoded,
                                        (uint16_t)length, 0u, 0x0bu);
        log0(4u, 0x161u, e_list_sent, c_list_sent);
        return 0;
    }
    g2_master_file_list_stored_flag = 1;
    log1(4u, 0x164u, e_stored, c_stored, (uint32_t)g2_master_file_list_stored_flag);
    return 0;
}

/* Accepts "L:/log/<name>" on the L arm and "R:/log/<name>" on the R arm. */
static int32_t app_delete_file(uint8_t magic)
{
    const logger_setting_msg_t *rx = &g2_logger_setting_rx_msg;
    char path[0x40];
    char name[LOGGER_NAME_LEN];
    const char *target = 0;
    uint32_t length;
    if (rx->which_payload != 7u)
        return 0;
    log0(3u, 0x179u, e_del_req, c_del_req);
    (void)audio_settings_copy_text(name, rx->payload.file_name, 0x1fu);
    name[0x1f] = 0;
    (void)g2_audio_dump_snprintf(path, sizeof path, fmt_s, name);
    if (audio_uart_device_role_get() == 2u) {
        if (audio_l2c_strncmp(path, prefix_l, 7u) != 0) {
            log1(4u, 0x186u, e_not_slave, c_not_slave, (uintptr_t)path);
            return 0;
        }
        target = path + 2;
    } else if (audio_uart_device_role_get() == 1u) {
        if (audio_l2c_strncmp(path, prefix_r, 7u) != 0) {
            log1(4u, 0x18cu, e_not_master, c_not_master, (uintptr_t)path);
            return 0;
        }
        target = path + 2;
    }
    log1(3u, 0x191u, e_del, c_del, (uintptr_t)target);
    if (file_remove(target) != 0)
        log1(1u, 0x194u, e_del_fail, c_del_fail, (uintptr_t)target);
    else
        log1(4u, 0x196u, e_del_ok, c_del_ok, (uintptr_t)target);
    logger_setting_msg_t *tx = reply_begin(5u, magic, 7u);
    (void)audio_settings_copy_text(tx->payload.file_name, name, 0x1fu);
    tx->payload.file_name[0x1f] = 0;
    if (reply_encode(&length) == 0u)
        return 0;
    if (audio_uart_device_role_get() == 2u) {
        log2(4u, 0x1a8u, e_del_fwd, c_del_fwd, (uintptr_t)name, length);
        int32_t result = audio_uart_handshake_send(0x0fu, g2_logger_setting_tx_encoded,
                                                   (uint16_t)length, 0u, 0x0cu);
        if (result == 0)
            return 0;
        log0(1u, 0x1acu, e_del_fwd_fail, c_del_fwd_fail);
        return result;
    }
    return reply_send_app(length);
}

static int32_t app_delete_all(uint8_t magic)
{
    uint32_t length;
    log0(3u, 0x1bau, e_del_all_req, c_del_all_req);
    int32_t deleted = delete_all_files_in_dir(dir_log);
    if (deleted < 0)
        log0(1u, 0x1bdu, e_del_all_fail, c_del_all_fail);
    else
        log1(4u, 0x1bfu, e_del_all_ok, c_del_all_ok, (uint32_t)deleted);
    logger_setting_msg_t *tx = reply_begin(0u, magic, 0u);
    tx->cmd = 6u;
    if (reply_encode(&length) == 0u)
        return 0;
    return reply_send_app(length);
}

/* R arm: append the peer's names to the stored own list and reply to the app. */
static void peer_file_list(void)
{
    const logger_setting_msg_t *rx = &g2_logger_setting_rx_msg;
    logger_setting_msg_t *tx = &g2_logger_setting_tx_msg;
    uint32_t length;
    if (g2_master_file_list_stored_flag != 1) {
        if (audio_uart_device_role_get() == 1u)
            log0(2u, 0x1fdu, e_not_stored, c_not_stored);
        return;
    }
    log0(4u, 0x1e4u, e_peer_list, c_peer_list);
    for (int32_t i = 0; i < (int32_t)rx->payload.file_list.count; i++) {
        log1(4u, 0x1e6u, e_peer_name, c_peer_name,
             (uintptr_t)rx->payload.file_list.names[i]);
        (void)audio_queue_copy_bytes(
            tx->payload.file_list.names[i + (int32_t)tx->payload.file_list.count],
            rx->payload.file_list.names[i], LOGGER_NAME_LEN);
    }
    tx->payload.file_list.count =
        (uint16_t)(rx->payload.file_list.count + tx->payload.file_list.count);
    if (reply_encode(&length) == 0u) {
        log0(1u, 0x1edu, e_encode, c_encode);
        return;
    }
    if (reply_send_app(length) != 0) {
        log0(1u, 0x1f4u, e_to_master_fail, c_to_master_fail);
        return;
    }
    log0(4u, 0x1f7u, e_to_master_ok, c_to_master_ok);
    g2_master_file_list_stored_flag = 0;
}

int32_t loggerSetting_common_data_handler(uint32_t source, const void *data, uint32_t length)
{
    log1(4u, 0xdeu, e_recv, c_recv, length);
    if (source == 0u) {
        if (decode_request(data, length, 0xe4u) == 0u)
            return 0;
        uint8_t cmd = g2_logger_setting_rx_msg.cmd;
        uint8_t magic = g2_logger_setting_rx_msg.magic_random;
        log2(4u, 0xeau, e_cmd, c_cmd, cmd, magic);
        switch (cmd) {
        case 0:
            log0(4u, 0xedu, e_heart, c_heart);
            return 0;
        case 1:
            return app_ble_switch(magic);
        case 2:
            return app_log_level(magic);
        case 4:
            return app_file_list(magic);
        case 5:
            return app_delete_file(magic);
        case 6:
            return app_delete_all(magic);
        default:
            log1(2u, 0x1d2u, e_unknown_sync, c_unknown_sync, cmd);
            return 0;
        }
    }
    if (source == 0x0bu) {
        if (decode_request(data, length, 0x1dbu) == 0u)
            return 0;
        uint8_t cmd = g2_logger_setting_rx_msg.cmd;
        uint8_t magic = g2_logger_setting_rx_msg.magic_random;
        log2(4u, 0x1e0u, e_cmd, c_cmd, cmd, magic);
        if (cmd == 4u)
            peer_file_list();
        else
            log1(2u, 0x204u, e_unknown, c_unknown, cmd);
        return 0;
    }
    if (source == 0x0cu) {
        /* The peer already encoded the delete reply; forward it unchanged. */
        log1(3u, 0x209u, e_peer_del, c_peer_del, length);
        int32_t result = Thread_MsgPbTxByBle(1u, 0x0fu, data, (uint16_t)length);
        if (result != 0) {
            log0(1u, 0x20cu, e_fwd_fail, c_fwd_fail);
            return result;
        }
        log0(3u, 0x20fu, e_fwd_ok, c_fwd_ok);
    }
    return 0;
}

/* "compress_log_<n>.bin" -> "<role>:<n>", "hardfault.txt" -> "<role>:h".
 * Returns the snprintf length, 0 on a null argument, or the nonzero strcmp
 * result for any other name (out is left untouched). */
int32_t simplify_log_filename(const char *filename, uint8_t role, char *out, uint32_t out_size)
{
    if (filename == 0 || out == 0 || out_size == 0u)
        return 0;
    if (extended_on())
        audio_log_extended(4u, module_tag, source_file, fn_simplify, 0x21au, e_simplify,
                           filename, role);
    if (compressed_on())
        (void)compress_log_output(0x10800000u, c_simplify, c_simplify, filename, role);
    int32_t index = -1;
    if (audio_ble_parse_version(filename, fmt_compress_log, &index) == 1)
        return g2_audio_dump_snprintf(out, out_size, fmt_role_index, role, index);
    int32_t result = audio_uart_font_path_compare(filename, name_hardfault);
    if (result == 0)
        result = g2_audio_dump_snprintf(out, out_size, fmt_role_hardfault, role);
    return result;
}
