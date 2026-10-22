/* General/module configure service, stock D:\01_workspace\s200_ap510b_iar_git\app\gui\module_configure\general_configure.c.
 * Native 0x4711b2..0x471527 and 0x471554..0x471ac1 (literal pool 0x471ac4..0x471b9b).
 * 0x471528 (initial sync request) is owned by app/service-prepare4/service_prepare4.c.
 *
 * The protobuf channel 0x20 handler (ui-registry row 08, native table 0x6a4530)
 * decodes an 8-byte ModuleConfigure message (descriptor ROM 0x77979c) into RAM
 * 0x2037ce2c and answers through Thread_MsgPbTxByBle(1, 0x20, ...). Language and
 * dashboard auto-close changes only mark a dirty flag and raise event bit 4 on the
 * shared log/persist event group; the save routines below run from that thread. */
#include <stdint.h>
#include <stddef.h>
#include "g2_kvdb.h"

#define GC_LANGUAGE_COUNT 8u
#define GC_RESPONSE_BYTES 13u
#define GC_CHANNEL 0x20u
#define GC_PERSIST_EVENT 4u
#define GC_SOURCE_PROTOBUF 0
#define GC_SOURCE_PEER 5

enum { GC_CMD_SYNC_INFO = 0u, GC_CMD_AUTO_CLOSE_INQUIRY = 1u, GC_CMD_AUTO_CLOSE_SET = 2u };
enum { GC_PAYLOAD_LANGUAGE = 3u, GC_PAYLOAD_AUTO_CLOSE = 4u };
enum { GC_PEER_GENERAL_SETTING = 1u, GC_PEER_GENERAL_INQUIRY = 2u };

/* nanopb-generated ModuleConfigure message (8 bytes). */
typedef struct {
    uint8_t cmd;          /* +0x0 */
    uint8_t magic_random; /* +0x1 */
    uint16_t which;       /* +0x2 payload tag: 3 language, 4 auto-close value */
    uint32_t value;       /* +0x4 */
} gc_message_t;
_Static_assert(sizeof(gc_message_t) == 8u, "ModuleConfigure message is 8 bytes");

typedef struct {
    void *callback;
    void *state;
    uint32_t max_size;
    uint32_t bytes_written; /* +0xc */
    const char *errmsg;
} gc_pb_ostream_t;
_Static_assert(sizeof(gc_pb_ostream_t) == 20u, "nanopb pb_ostream_t");

typedef struct {
    void *callback;
    void *state;
    uint32_t bytes_left;
    const char *errmsg; /* +0xc */
} gc_pb_istream_t;
_Static_assert(sizeof(gc_pb_istream_t) == 16u, "nanopb pb_istream_t");

extern volatile uint32_t audio_uart_display_locale_index;      /* RAM 0x20000030 system language */
extern uint32_t g2_kvdb_dashboard_auto_close_value;             /* RAM 0x20000038 */
extern volatile uint32_t g2_general_configure_language_dirty;   /* RAM 0x20074604 */
extern volatile uint32_t g2_general_configure_auto_close_dirty; /* RAM 0x20074608 */
extern uint32_t g2_audio_log_event_handle;                      /* RAM 0x20074570 osEventFlagsId_t */
extern gc_message_t g2_general_configure_rx_message;            /* RAM 0x2037ce2c */
extern gc_message_t g2_general_configure_tx_message;            /* RAM 0x2037ce34 */
extern uint8_t g2_general_configure_tx_buffer[GC_RESPONSE_BYTES]; /* RAM 0x20073e54 */
extern const uint8_t g2_module_configure_pb_fields[];           /* ROM 0x77979c */

extern void audio_uart_buffer_zero(void *dst, uint32_t len, uint32_t fill);              /* 0x43c0e4 */
extern void *audio_uart_display_area_copy_439c04(void *dst, const void *src, uint32_t len);
extern void audio_pb_ostream_from_buffer(gc_pb_ostream_t *out, void *buffer, uint32_t size); /* 0x4905f4 */
extern uint32_t audio_pb_encode(void *stream, const void *fields, const void *src);       /* 0x490c32 */
extern void audio_uart_pb_stream_init(gc_pb_istream_t *out, const void *buffer, uint32_t size); /* 0x48f49c */
extern uint32_t audio_uart_pb_decode(void *stream, const void *fields, void *dst);        /* 0x490120 */
/* Thread_MsgPbTxByBle 0x475b14; the stock call site also passes a fifth zero argument. */
extern uint32_t audio_ring_pb_tx_ble_475b14(uint32_t type, uint32_t command, const void *payload,
                                            uint32_t length, uint32_t unused);
extern uint32_t audio_uart_handshake_send(uint32_t channel, const void *data, uint32_t size,
                                          uint32_t flags, uint32_t timeout);              /* 0x465480 */
extern uint32_t osEventFlagsSet(void *ef_id, uint32_t flags);                             /* 0x4495e4 */
extern uint32_t audio_log_flags(void);                                                    /* 0x43d0ce */
extern void audio_log_extended(uint8_t, const char *, const char *, const char *, uint32_t, const char *, ...); /* 0x43d574 */
extern uint32_t compress_log_output(uint32_t, const char *, const char *, ...);            /* 0x43ce9e */

static const char module_tag[] = "general_configure"; /* ROM 0x77f6bc */
static const char source_file[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\app\\gui\\module_configure\\general_configure.c"; /* ROM 0x6e8158 */
static const char set_language_fn[] = "set_general_configure_language"; /* ROM 0x760270 */
static const char bad_language[] = "set_general_configure_language: language %d not supported, set to %d"; /* ROM 0x6facc4 */
static const char bad_language_short[] =
    "[general_configure]set_general_configure_language: language %d not supported, set to %d"; /* ROM 0x6e3670 */
static const char inquiry_fn[] = "ModuleConfigureService_response_inquiry_cmd"; /* ROM 0x73efa8 */
static const char auto_close_inquiry_fn[] = "ModuleDashboardAutoCloseValueService_response_inquiry_cmd"; /* ROM 0x715778 */
static const char auto_close_set_fn[] = "ModuleDashboardAutoCloseValueService_response_set_cmd"; /* ROM 0x71f560 */
static const char inquiry_msg[] = "syncInfoService_response_inquiry_cmd"; /* ROM 0x74a35c */
static const char inquiry_short[] = "[general_configure]syncInfoService_response_inquiry_cmd"; /* ROM 0x71f4f0 */
static const char encode_failed[] = "syncInfoService: pb_encode failed"; /* ROM 0x754a40 */
static const char encode_failed_short[] = "[general_configure]syncInfoService: pb_encode failed"; /* ROM 0x71f528 */
static const char language_save_fn[] = "SystemLanguageSaveToFlash"; /* ROM 0x76bb90 */
static const char language_save[] = "SystemLanguageSaveToFlash,language = %d"; /* ROM 0x74a384 */
static const char language_save_short[] = "[general_configure]SystemLanguageSaveToFlash,language = %d"; /* ROM 0x7157b4 */
static const char language_save_failed[] = "SystemLanguageSaveToFlash failed"; /* ROM 0x754a64 */
static const char language_save_failed_short[] = "[general_configure]SystemLanguageSaveToFlash failed"; /* ROM 0x729dac */
static const char auto_close_save_fn[] = "DashboardAutoCloseValueSaveToFlash"; /* ROM 0x754a88 */
static const char auto_close_save[] = "DashboardAutoCloseValueSaveToFlash,auto_close_value = %d"; /* ROM 0x7157f0 */
static const char auto_close_save_short[] =
    "[general_configure]DashboardAutoCloseValueSaveToFlash,auto_close_value = %d"; /* ROM 0x6f3d1c */
static const char auto_close_save_failed[] = "DashboardAutoCloseValueSaveToFlash failed"; /* ROM 0x73efd4 */
static const char auto_close_save_failed_short[] =
    "[general_configure]DashboardAutoCloseValueSaveToFlash failed"; /* ROM 0x70c0a4 */
static const char handler_fn[] = "ModuleConfigureService_common_data_handler"; /* ROM 0x73f000 */
static const char rx_len[] = "module_configure_data_handler recv data len = %d"; /* ROM 0x729de0 */
static const char rx_len_short[] = "[general_configure]module_configure_data_handler recv data len = %d"; /* ROM 0x703208 */
static const char none_text[] = "(none)"; /* ROM 0x78d6bc */
static const char decode_failed[] = "module_configure_data_handler protobuf decode failed: %s\n"; /* ROM 0x71582c */
static const char decode_failed_short[] =
    "[general_configure]module_configure_data_handler protobuf decode failed: %s\n"; /* ROM 0x6ed5b8 */
static const char rx_cmd[] = "module_configure_data_handler cmd = %d, magicRandom = %d"; /* ROM 0x715868 */
static const char rx_cmd_short[] =
    "[general_configure]module_configure_data_handler cmd = %d, magicRandom = %d"; /* ROM 0x6f3d68 */
static const char rx_sync[] = "module_configure_data_handler receive sync info request from APP"; /* ROM 0x70324c */
static const char rx_sync_short[] =
    "[general_configure]module_configure_data_handler receive sync info request from APP"; /* ROM 0x6e81ac */
static const char rx_ac_inquiry[] =
    "module_configure_data_handler receive dashboard auto close value inquiry from APP"; /* ROM 0x6e8200 */
static const char rx_ac_inquiry_short[] =
    "[general_configure]module_configure_data_handler receive dashboard auto close value inquiry from APP"; /* ROM 0x6d8b3c */
static const char rx_ac_set[] = "module_configure_data_handler receive dashboard auto close value set from APP"; /* ROM 0x6ed608 */
static const char rx_ac_set_short[] =
    "[general_configure]module_configure_data_handler receive dashboard auto close value set from APP"; /* ROM 0x6daac0 */
static const char rx_unknown[] = "module_configure_data_handler: unknown cmd = %d"; /* ROM 0x734514 */
static const char rx_unknown_short[] = "[general_configure]module_configure_data_handler: unknown cmd = %d"; /* ROM 0x703290 */
static const char rx_general[] = "module_configure_data_handler receive system general setting packet from APP"; /* ROM 0x6ed658 */
static const char rx_general_short[] =
    "[general_configure]module_configure_data_handler receive system general setting packet from APP"; /* ROM 0x6dd474 */
static const char rx_set_language[] = "module_configure_data_handler set general configure language to %d"; /* ROM 0x7032d4 */
static const char rx_set_language_short[] =
    "[general_configure]module_configure_data_handler set general configure language to %d"; /* ROM 0x6e36c8 */

static inline uint32_t compact_enabled(void)
{
    return (audio_log_flags() & 1u) || (audio_log_flags() & 4u);
}

int32_t set_general_configure_language_4711b2(uint32_t language)
{
    if (language < GC_LANGUAGE_COUNT) {
        audio_uart_display_locale_index = language;
        return 0;
    }
    if (audio_log_flags() & 2u)
        audio_log_extended(2u, module_tag, source_file, set_language_fn, 0x55u, bad_language, language, 0u);
    if (compact_enabled())
        (void)compress_log_output(0x08800000u, bad_language_short, bad_language_short, language, 0u);
    return -1;
}

uint32_t get_dashboard_auto_close_value_47121c(void)
{
    return g2_kvdb_dashboard_auto_close_value;
}

/* Shared body of the three inquiry/set responses: fill the response, encode, transmit. */
static uint32_t send_response(const char *function, uint32_t log_line, uint32_t fail_line,
                              uint8_t cmd, uint8_t magic, int with_value)
{
    gc_pb_ostream_t stream;
    gc_pb_ostream_t encoder;
    gc_message_t *response = &g2_general_configure_tx_message;

    if (audio_log_flags() & 2u)
        audio_log_extended(4u, module_tag, source_file, function, log_line, inquiry_msg);
    if (compact_enabled())
        (void)compress_log_output(0x10000000u, inquiry_short, inquiry_short);

    audio_uart_buffer_zero(response, sizeof(*response), 0u);
    audio_uart_buffer_zero(g2_general_configure_tx_buffer, GC_RESPONSE_BYTES, 0u);
    response->cmd = cmd;
    response->magic_random = magic;
    if (with_value) {
        response->which = GC_PAYLOAD_AUTO_CLOSE;
        response->value = g2_kvdb_dashboard_auto_close_value;
    }
    audio_pb_ostream_from_buffer(&stream, g2_general_configure_tx_buffer, GC_RESPONSE_BYTES);
    (void)audio_uart_display_area_copy_439c04(&encoder, &stream, sizeof(encoder));
    if (audio_pb_encode(&encoder, g2_module_configure_pb_fields, response) == 0u) {
        if (audio_log_flags() & 2u)
            audio_log_extended(1u, module_tag, source_file, function, fail_line, encode_failed);
        if (compact_enabled())
            (void)compress_log_output(0x04000000u, encode_failed_short, encode_failed_short);
        return 0u;
    }
    return audio_ring_pb_tx_ble_475b14(1u, GC_CHANNEL, g2_general_configure_tx_buffer,
                                       (uint16_t)encoder.bytes_written, 0u);
}

uint32_t module_configure_response_inquiry_cmd_471224(uint8_t magic)
{
    return send_response(inquiry_fn, 0x6cu, 0x75u, GC_CMD_SYNC_INFO, magic, 0);
}

uint32_t module_dashboard_auto_close_response_inquiry_cmd_47132c(uint8_t magic)
{
    return send_response(auto_close_inquiry_fn, 0x86u, 0x91u, GC_CMD_AUTO_CLOSE_INQUIRY, magic, 1);
}

uint32_t module_dashboard_auto_close_response_set_cmd_47142a(uint8_t magic)
{
    return send_response(auto_close_set_fn, 0xa0u, 0xabu, GC_CMD_AUTO_CLOSE_SET, magic, 1);
}

void system_language_save_to_flash_471554(void)
{
    if (g2_general_configure_language_dirty != 1u)
        return;
    if (audio_log_flags() & 2u)
        audio_log_extended(3u, module_tag, source_file, language_save_fn, 0xc5u, language_save,
                           audio_uart_display_locale_index);
    if (compact_enabled())
        (void)compress_log_output(0x0c400000u, language_save_short, language_save_short,
                                  audio_uart_display_locale_index);
    if (SVC_KvdbWriteLanguage((uint8_t)audio_uart_display_locale_index) != 0) {
        if (audio_log_flags() & 2u)
            audio_log_extended(1u, module_tag, source_file, language_save_fn, 0xc8u, language_save_failed);
        if (compact_enabled())
            (void)compress_log_output(0x04000000u, language_save_failed_short, language_save_failed_short);
    }
    g2_general_configure_language_dirty = 0u;
}

void dashboard_auto_close_value_save_to_flash_471608(void)
{
    if (g2_general_configure_auto_close_dirty != 1u)
        return;
    if (audio_log_flags() & 2u)
        audio_log_extended(3u, module_tag, source_file, auto_close_save_fn, 0xd1u, auto_close_save,
                           g2_kvdb_dashboard_auto_close_value);
    if (compact_enabled())
        (void)compress_log_output(0x0c400000u, auto_close_save_short, auto_close_save_short,
                                  g2_kvdb_dashboard_auto_close_value);
    if (SVC_KvdbWriteDashboardAutoCloseValue(g2_kvdb_dashboard_auto_close_value) != 0) {
        if (audio_log_flags() & 2u)
            audio_log_extended(1u, module_tag, source_file, auto_close_save_fn, 0xd4u, auto_close_save_failed);
        if (compact_enabled())
            (void)compress_log_output(0x04000000u, auto_close_save_failed_short, auto_close_save_failed_short);
    }
    g2_general_configure_auto_close_dirty = 0u;
}

static void request_persist(void)
{
    (void)osEventFlagsSet((void *)(uintptr_t)g2_audio_log_event_handle, GC_PERSIST_EVENT);
}

/* source 0: protobuf from the phone app; source 5: two-byte packet from the peer side. */
uint32_t module_configure_common_data_handler_4716ba(int32_t source, const uint8_t *data, uint32_t length)
{
    if (audio_log_flags() & 2u)
        audio_log_extended(4u, module_tag, source_file, handler_fn, 0xdcu, rx_len, length);
    if (compact_enabled())
        (void)compress_log_output(0x10400000u, rx_len_short, rx_len_short, length);

    if (source == GC_SOURCE_PROTOBUF) {
        gc_message_t *message = &g2_general_configure_rx_message;
        gc_pb_istream_t stream;
        gc_pb_istream_t decoder;

        audio_uart_buffer_zero(message, sizeof(*message), 0u);
        audio_uart_pb_stream_init(&stream, data, length);
        (void)audio_uart_display_area_copy_439c04(&decoder, &stream, sizeof(decoder));
        if ((uint8_t)audio_uart_pb_decode(&decoder, g2_module_configure_pb_fields, message) == 0u) {
            if (audio_log_flags() & 2u)
                audio_log_extended(1u, module_tag, source_file, handler_fn, 0xe3u, decode_failed,
                                   decoder.errmsg != NULL ? decoder.errmsg : none_text);
            if (compact_enabled())
                (void)compress_log_output(0x04400000u, decode_failed_short, decode_failed_short,
                                          decoder.errmsg != NULL ? decoder.errmsg : none_text);
            return 0u;
        }

        uint8_t cmd = message->cmd;
        uint8_t magic = message->magic_random;
        if (audio_log_flags() & 2u)
            audio_log_extended(4u, module_tag, source_file, handler_fn, 0xe9u, rx_cmd, (uint32_t)cmd, (uint32_t)magic);
        if (compact_enabled())
            (void)compress_log_output(0x10800000u, rx_cmd_short, rx_cmd_short, (uint32_t)cmd, (uint32_t)magic);

        if (cmd == GC_CMD_SYNC_INFO) {
            if (audio_log_flags() & 2u)
                audio_log_extended(4u, module_tag, source_file, handler_fn, 0xecu, rx_sync);
            if (compact_enabled())
                (void)compress_log_output(0x10000000u, rx_sync_short, rx_sync_short);
            if (message->which == GC_PAYLOAD_LANGUAGE) {
                (void)set_general_configure_language_4711b2(message->value);
                g2_general_configure_language_dirty = 1u;
                request_persist();
                (void)module_configure_response_inquiry_cmd_471224(magic);
            }
        } else if (cmd == GC_CMD_AUTO_CLOSE_SET) {
            if (audio_log_flags() & 2u)
                audio_log_extended(4u, module_tag, source_file, handler_fn, 0xfbu, rx_ac_set);
            if (compact_enabled())
                (void)compress_log_output(0x10000000u, rx_ac_set_short, rx_ac_set_short);
            if (message->which == GC_PAYLOAD_AUTO_CLOSE) {
                g2_kvdb_dashboard_auto_close_value = message->value;
                g2_general_configure_auto_close_dirty = 1u;
                request_persist();
                (void)module_dashboard_auto_close_response_set_cmd_47142a(magic);
            }
        } else if (cmd < GC_CMD_AUTO_CLOSE_SET) {
            if (audio_log_flags() & 2u)
                audio_log_extended(4u, module_tag, source_file, handler_fn, 0xf6u, rx_ac_inquiry);
            if (compact_enabled())
                (void)compress_log_output(0x10000000u, rx_ac_inquiry_short, rx_ac_inquiry_short);
            (void)module_dashboard_auto_close_response_inquiry_cmd_47132c(magic);
        } else {
            if (audio_log_flags() & 2u)
                audio_log_extended(2u, module_tag, source_file, handler_fn, 0x105u, rx_unknown, (uint32_t)cmd);
            if (compact_enabled())
                (void)compress_log_output(0x08400000u, rx_unknown_short, rx_unknown_short, (uint32_t)cmd);
        }
    } else if (source == GC_SOURCE_PEER) {
        uint8_t cmd = data[0];
        if (cmd == GC_PEER_GENERAL_SETTING) {
            if (audio_log_flags() & 2u)
                audio_log_extended(3u, module_tag, source_file, handler_fn, 0x10du, rx_general);
            if (compact_enabled())
                (void)compress_log_output(0x0c000000u, rx_general_short, rx_general_short);
            if ((uint32_t)data[1] != audio_uart_display_locale_index) {
                (void)set_general_configure_language_4711b2(data[1]);
                g2_general_configure_language_dirty = 1u;
                request_persist();
                if (audio_log_flags() & 2u)
                    audio_log_extended(3u, module_tag, source_file, handler_fn, 0x112u, rx_set_language,
                                       (uint32_t)data[1]);
                if (compact_enabled())
                    (void)compress_log_output(0x0c400000u, rx_set_language_short, rx_set_language_short,
                                              (uint32_t)data[1]);
            }
        } else if (cmd == GC_PEER_GENERAL_INQUIRY) {
            uint8_t reply[10];
            if (audio_log_flags() & 2u)
                audio_log_extended(4u, module_tag, source_file, handler_fn, 0x117u, rx_general);
            if (compact_enabled())
                (void)compress_log_output(0x10000000u, rx_general_short, rx_general_short);
            audio_uart_buffer_zero(reply, sizeof(reply), 0u);
            reply[0] = GC_PEER_GENERAL_SETTING;
            reply[1] = (uint8_t)audio_uart_display_locale_index;
            (void)audio_uart_handshake_send(GC_CHANNEL, reply, 2u, 0u, 5u);
        } else {
            if (audio_log_flags() & 2u)
                audio_log_extended(2u, module_tag, source_file, handler_fn, 0x120u, rx_unknown, (uint32_t)cmd);
            if (compact_enabled())
                (void)compress_log_output(0x08400000u, rx_unknown_short, rx_unknown_short, (uint32_t)cmd);
        }
    }
    return 0u;
}
