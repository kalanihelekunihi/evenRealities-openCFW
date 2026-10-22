/* Product FreeRTOS-Plus-CLI app test commands (conversate, translate,
 * teleprompt, legalregulatory), stock directory
 * D:\01_workspace\s200_ap510b_iar_git\kernel\FreeRTOS-Plus-CLI\prvCommand\
 * (file name not retained). Native 0x581de0..0x5827eb; pool
 * 0x5827ec..0x582897, inline "tag" 0x582220 and "add" 0x582444.
 * The teleprompt handler 0x582448 and legalregulatory handler 0x5827b6
 * have no inventory rows.
 *
 * The conversate and teleprompt commands build the same nanopb packages
 * the phone would send (cmd byte, rolling magic byte, oneof selector,
 * payload), encode them into a static buffer and push them to both arms
 * with the sync interface (app 11 conversate, app 6 teleprompt). */
#include <stddef.h>
#include <stdint.h>
#include "cli_commands.h"

#define CONVERSATE_SYNC_APP 11u
#define TELEPROMPT_SYNC_APP 6u
#define CONVERSATE_PB_BYTES 0xfb2u  /* 4018 */
#define TELEPROMPT_PB_BYTES 0xfa9u  /* 4009 */
#define CONVERSATE_PATTERN_BYTES 4000u
#define CONVERSATE_PREP_MAX 20u
#define CONVERSATE_PREP_DEFAULT 3u
#define TRANSLATE_FSM_EVENT_ADD 5u
#define TRANSLATE_SENTENCE_BYTES 26u

/* nanopb pb_ostream_t */
typedef struct {
    void *callback;
    void *state;
    uint32_t max_size;
    uint32_t bytes_written; /* +0x0c */
    const char *errmsg;
} g2_pb_ostream_t;
_Static_assert(sizeof(g2_pb_ostream_t) == 20u, "pb_ostream_t");

/* Package header shared by the conversate and teleprompt CLI messages. */
typedef struct {
    uint8_t cmd;      /* +0x0 */
    uint8_t magic;    /* +0x1 rolling counter */
    uint16_t which;   /* +0x2 payload oneof tag */
} g2_cli_pkg_header_t;

typedef struct {               /* "tag": RAM 0x200fa738 */
    uint8_t type;              /* +0x000 atoi(arg2); 1 selects the long extend text */
    uint8_t pad0;
    uint16_t text_length;      /* +0x002 */
    char text[128];            /* +0x004 */
    uint16_t extend_length;    /* +0x084 */
    char extend[1024];         /* +0x086 */
    uint8_t reserved[6];       /* +0x486 */
} g2_conversate_cli_tag_t;
_Static_assert(sizeof(g2_conversate_cli_tag_t) == 0x48cu, "tag payload");

typedef struct {               /* "start": RAM 0x200fabc4 */
    uint8_t flags[8];          /* +0x00 */
    uint16_t name_length;      /* +0x08 */
    char name[128];            /* +0x0a */
    uint8_t pad0[2];
    uint32_t total_packets;    /* +0x8c */
    uint8_t reserved[4];       /* +0x90 */
} g2_conversate_cli_start_t;
_Static_assert(sizeof(g2_conversate_cli_start_t) == 0x94u, "start payload");

typedef struct {               /* "packet": RAM 0x200fb700 */
    uint32_t index;            /* +0x000 */
    uint16_t size;             /* +0x004 */
    char data[CONVERSATE_PATTERN_BYTES]; /* +0x006 */
    uint8_t pad0[2];
} g2_conversate_cli_packet_t;
_Static_assert(sizeof(g2_conversate_cli_packet_t) == 0xfa8u, "packet payload");

typedef struct {
    uint32_t id;               /* +0x00 */
    uint16_t name_length;      /* +0x04 */
    char name[128];            /* +0x06 */
    uint8_t pad0[2];
} g2_conversate_cli_prep_t;
_Static_assert(sizeof(g2_conversate_cli_prep_t) == 0x88u, "prep note row");

typedef struct {               /* "preplist": RAM 0x200fac58 */
    uint16_t count;            /* +0x000 */
    uint8_t pad0[2];
    g2_conversate_cli_prep_t notes[CONVERSATE_PREP_MAX]; /* +0x004 */
    uint32_t done;             /* +0xaa4 */
} g2_conversate_cli_preplist_t;
_Static_assert(sizeof(g2_conversate_cli_preplist_t) == 0xaa8u, "preplist payload");

typedef struct {               /* RAM 0x200fc6a8 */
    g2_cli_pkg_header_t header; /* +0x0 */
    uint8_t payload[0xfa8];    /* +0x4 */
} g2_conversate_cli_pkg_t;
_Static_assert(sizeof(g2_conversate_cli_pkg_t) == 0xfacu, "conversate package");

typedef struct {               /* translate FSM message, RAM 0x200651c0 */
    uint16_t source_length;    /* +0x000 */
    char source[1024];         /* +0x002 */
    uint16_t target_length;    /* +0x402 */
    char target[1028];         /* +0x404 */
    uint32_t valid;            /* +0x808 */
    uint8_t reserved[0x44];    /* +0x80c */
} g2_translate_cli_message_t;
_Static_assert(sizeof(g2_translate_cli_message_t) == 0x850u, "translate message");

typedef struct {               /* RAM 0x200fea50 */
    g2_cli_pkg_header_t header; /* +0x0 */
    uint8_t action;            /* +0x4 */
    uint8_t has_data;          /* +0x5 */
    uint8_t pad0[2];
    uint8_t data[44];          /* +0x8 */
    uint8_t reserved[0xf58 - 0x34];
} g2_teleprompt_cli_pkg_t;
_Static_assert(sizeof(g2_teleprompt_cli_pkg_t) == 0xf58u, "teleprompt package");

/* Conversate tag cache row (0x5964e2): +4 key, +8 value. */
typedef struct {
    uint32_t reserved;
    const char *key;
    const char *value;
} g2_conversate_tag_view_t;

extern g2_cli_command_t g2_cli_cmd_teleprompt_200035a8;       /* "teleprompt", variable */
extern g2_cli_command_t g2_cli_cmd_translate_200035b8;        /* "translate", variable */
extern g2_cli_command_t g2_cli_cmd_conversate_200035c8;       /* "conversate", variable */
extern g2_cli_command_t g2_cli_cmd_legalregulatory_200035d8;  /* "legalregulatory", variable */

extern uint8_t g2_conversate_cli_pb_buffer_200fd654[CONVERSATE_PB_BYTES];
extern g2_conversate_cli_tag_t g2_conversate_cli_tag_200fa738;
extern g2_conversate_cli_pkg_t g2_conversate_cli_pkg_200fc6a8;
extern uint8_t g2_conversate_cli_magic_2013be6c;
extern g2_conversate_cli_start_t g2_conversate_cli_start_200fabc4;
extern uint8_t g2_conversate_cli_note_sent_2013be6d;  /* set by "start <arg>" */
extern g2_conversate_cli_packet_t g2_conversate_cli_packet_200fb700;
extern g2_conversate_cli_preplist_t g2_conversate_cli_preplist_200fac58;
extern char g2_translate_cli_source_200035e8[TRANSLATE_SENTENCE_BYTES]; /* initialized "this is a src sentence 00" */
extern char g2_translate_cli_target_20003604[TRANSLATE_SENTENCE_BYTES]; /* initialized "this is a dst sentence 00" */
extern uint32_t g2_translate_cli_counter_200748c0;
extern g2_translate_cli_message_t g2_translate_cli_message_200651c0;
extern uint8_t g2_teleprompt_cli_pb_buffer_200ff9a8[TELEPROMPT_PB_BYTES];
extern g2_teleprompt_cli_pkg_t g2_teleprompt_cli_pkg_200fea50;
extern uint8_t g2_teleprompt_cli_magic_20075001;

extern const uint8_t audio_conversate_response_descriptor_775b24[]; /* pb_msgdesc_t */
extern const uint8_t g2_teleprompt_pb_msgdesc_77c304[];          /* pb_msgdesc_t */

extern void audio_pb_ostream_from_buffer(g2_pb_ostream_t *out, void *buf, uint32_t size); /* 0x4905f4 */
extern uint32_t audio_pb_encode(void *stream, const void *fields, const void *src);       /* 0x490c32 */
extern uint32_t audio_sync_send_to_both_ext_464f76(uint32_t app, const void *bytes, uint32_t length,
                                                   uint32_t id, uint32_t event);
extern void *audio_uart_display_area_copy_439c04(void *dst, const void *src, uint32_t len); /* memcpy */
extern void *audio_queue_copy_bytes(void *dst, const void *src, uint32_t len);            /* 0x439be4 memcpy */
extern void *aeabi_memset_43c0e4(void *dst, uint32_t len, int32_t value);
extern int32_t audio_ble_hci_vendor_compare_44b610(const void *a, const void *b, uint32_t len); /* strncmp */
extern void *audio_settings_copy_text(void *dst, const void *src, uint32_t len); /* 0x44b5a0 strncpy */
extern int32_t g2_audio_dump_snprintf(char *dst, uint32_t size, const char *format, ...); /* 0x44b728 */
extern uint32_t g2_log_module_length(const char *text);                       /* 0x44a43c strlen */
extern int32_t atoi_48d868(const char *text);
extern uint32_t audio_conversate_tag_storage_count_59674e(void);
extern const g2_conversate_tag_view_t *audio_conversate_tag_get_by_index_5964e2(uint32_t index);
extern int32_t translate_machine_handler_596b0c(uint8_t event, const void *data, uint32_t length);

static const char s_conv_pkg_null[] = "conversate cli pb send failed: pkg is NULL\r\n";  /* ROM 0x737034 */
static const char s_conv_encode[] = "conversate cli pb encode failed\r\n";               /* ROM 0x7588f8 */
static const char s_conv_send[] = "conversate cli pb send failed, ret=%d\r\n";           /* ROM 0x74cfbc */
static const char s_conv_sent[] = "conversate cli pb sent, cmd=%d, magic=%d, len=%d\r\n"; /* ROM 0x72c23c */
static const char s_conv_missing[] = "conversate: missing sub command\r\n";             /* ROM 0x75891c */
static const char s_sub_tag[] = "tag";                                                  /* ROM 0x582220 */
static const char s_default_text[] = "text";                                            /* ROM 0x78e2f4 */
static const char s_knowledge_extend[] =
    "Knowledge extend text\nline 1\nline 2\nline 3\nline 4\nline 5\nline 6\nline 7\nline 8\nline 9"; /* ROM 0x6e4900 */
static const char s_extend_text[] = "extend text";                                      /* ROM 0x78bac8 */
static const char s_sub_start[] = "start";                                              /* ROM 0x78e2fc */
static const char s_prep_note_name[] = "CLI PrepNote 2Pkt";                             /* ROM 0x7828f8 */
static const char s_sub_packet[] = "packet";                                            /* ROM 0x78e304 */
static const char s_packet_no_note[] =
    "run 'conversate start note' first to send note_info(total_packets=2)\r\n";         /* ROM 0x6fc224 */
static const char s_packet_missing[] = "conversate packet: missing packet index(0/1)\r\n"; /* ROM 0x737064 */
static const char s_packet_invalid[] =
    "conversate packet: invalid packet index=%d, only support 0 or 1\r\n";              /* ROM 0x704b44 */
static const char s_packet_sent[] = "conversate packet sent, packet_index=%d, payload_size=%d\r\n"; /* ROM 0x717d70 */
static const char s_sub_preplist[] = "preplist";                                        /* ROM 0x78bad4 */
static const char s_prep_name[] = "Fake prep note %d";                                  /* ROM 0x78290c */
static const char s_prep_sent[] = "conversate fake prep note list sent by pb, count=%d\r\n"; /* ROM 0x721a90 */
static const char s_sub_cache[] = "cache";                                              /* ROM 0x78e30c */
static const char s_cache_header[] = "===============tag=================\r\n";          /* ROM 0x74cfe4 */
static const char s_cache_row[] = "[%s|%s]\r\n";                                         /* ROM 0x78bae0 */
static const char s_sub_add[] = "add";                                                  /* ROM 0x582444 */
static const char s_source_format[] = "this is a src sentence %02d";                     /* ROM 0x7702e0 */
static const char s_target_format[] = "this is a dst sentence %02d";                     /* ROM 0x7702fc */
static const char s_tele_pkg_null[] = "teleprompt cli pb send failed: pkg is NULL\r\n";  /* ROM 0x737094 */
static const char s_tele_encode[] = "teleprompt cli pb encode failed\r\n";               /* ROM 0x758940 */
static const char s_tele_send[] = "teleprompt cli pb send failed, ret=%d\r\n";           /* ROM 0x74d00c */

int32_t conversate_cli_pb_send_581de0(const g2_conversate_cli_pkg_t *pkg);
uint32_t conversate_cli_fill_pattern_581e6a(uint32_t mode, char *buffer, uint32_t capacity);
int32_t cli_cmd_conversate_581ed0(char *write_buffer, size_t write_buffer_len, const char *command_string);
int32_t cli_cmd_translate_5822e6(char *write_buffer, size_t write_buffer_len, const char *command_string);
int32_t teleprompt_cli_pb_send_58237a(const g2_teleprompt_cli_pkg_t *pkg);
void teleprompt_cli_send_control_5823f6(uint8_t action, const void *data);
void cli_register_app_commands_5827d0(void);

int32_t conversate_cli_pb_send_581de0(const g2_conversate_cli_pkg_t *pkg)
{
    g2_pb_ostream_t created;
    g2_pb_ostream_t stream;
    uint32_t status;

    if (pkg == NULL) {
        audio_ble_hci_boot_log_4733ee(s_conv_pkg_null);
        return -1;
    }
    audio_pb_ostream_from_buffer(&created, g2_conversate_cli_pb_buffer_200fd654, CONVERSATE_PB_BYTES);
    (void)audio_uart_display_area_copy_439c04(&stream, &created, sizeof(stream));
    if (audio_pb_encode(&stream, audio_conversate_response_descriptor_775b24, pkg) == 0u) {
        audio_ble_hci_boot_log_4733ee(s_conv_encode);
        return -1;
    }
    status = audio_sync_send_to_both_ext_464f76(CONVERSATE_SYNC_APP, g2_conversate_cli_pb_buffer_200fd654,
                                                (uint16_t)stream.bytes_written, 0u, 0u);
    if (status != 0u) {
        audio_ble_hci_boot_log_4733ee(s_conv_send, status);
        return -1;
    }
    audio_ble_hci_boot_log_4733ee(s_conv_sent, pkg->header.cmd, pkg->header.magic, stream.bytes_written);
    return 0;
}

/* Test payload: mode 0 "ABC..Z" (at most 4000 bytes), mode 1 "abc..z" (at
 * most 200), a newline every 80th byte. Returns bytes written. */
uint32_t conversate_cli_fill_pattern_581e6a(uint32_t mode, char *buffer, uint32_t capacity)
{
    uint32_t limit;
    uint8_t base;
    uint32_t i;

    if (buffer == NULL || capacity == 0u)
        return 0u;
    if (mode == 0u) {
        limit = 4000u;
        base = 'A';
    } else if (mode == 1u) {
        limit = 200u;
        base = 'a';
    } else {
        return 0u;
    }
    if (capacity < limit)
        limit = capacity;
    for (i = 0u; i < limit; i++) {
        if ((i + 1u) % 80u == 0u)
            buffer[i] = '\n';
        else
            buffer[i] = (char)((uint8_t)(i + base) - (i / 26u) * 26u);
    }
    return limit;
}

/* Stamp header (cmd, ++magic, which), copy the payload and send. */
static void conversate_cli_send_payload(uint8_t cmd, uint16_t which, const void *payload, uint32_t size)
{
    g2_conversate_cli_pkg_t *pkg = &g2_conversate_cli_pkg_200fc6a8;

    (void)aeabi_memset_43c0e4(pkg, sizeof(*pkg), 0);
    pkg->header.cmd = cmd;
    g2_conversate_cli_magic_2013be6c++;
    pkg->header.magic = g2_conversate_cli_magic_2013be6c;
    pkg->header.which = which;
    (void)audio_uart_display_area_copy_439c04(pkg->payload, payload, size);
    (void)conversate_cli_pb_send_581de0(pkg);
}

/* conversate tag [type] [text] [extend] | start [x] | packet <0|1> |
 * preplist [count] | cache */
int32_t cli_cmd_conversate_581ed0(char *write_buffer, size_t write_buffer_len, const char *command_string)
{
    int32_t sub_length = 0;
    int32_t arg2_length = 0;
    int32_t arg3_length = 0;
    int32_t arg4_length = 0;
    const char *sub;
    const char *arg2;
    const char *arg3;
    const char *arg4;

    (void)write_buffer;
    (void)write_buffer_len;
    sub = freertos_cli_get_parameter_5848fc(command_string, 1u, &sub_length);
    arg2 = freertos_cli_get_parameter_5848fc(command_string, 2u, &arg2_length);
    arg3 = freertos_cli_get_parameter_5848fc(command_string, 3u, &arg3_length);
    arg4 = freertos_cli_get_parameter_5848fc(command_string, 4u, &arg4_length);
    if (sub == NULL || sub_length < 1) {
        audio_ble_hci_boot_log_4733ee(s_conv_missing);
        return 0;
    }

    if (audio_ble_hci_vendor_compare_44b610(sub, s_sub_tag, 3u) == 0) {
        g2_conversate_cli_tag_t *tag = &g2_conversate_cli_tag_200fa738;
        uint32_t n;

        (void)aeabi_memset_43c0e4(tag, sizeof(*tag), 0);
        if (arg2 != NULL && arg2_length >= 1)
            tag->type = (uint8_t)atoi_48d868(arg2);
        if (arg3 != NULL && arg3_length >= 1) {
            n = (uint32_t)arg3_length < 0x80u ? (uint32_t)arg3_length : 0x7fu;
            (void)audio_settings_copy_text(tag->text, arg3, n);
            tag->text[n] = '\0';
            tag->text_length = (uint16_t)n;
        } else {
            (void)g2_audio_dump_snprintf(tag->text, sizeof(tag->text), s_default_text);
            tag->text_length = (uint16_t)g2_log_module_length(tag->text);
        }
        if (arg4 != NULL && arg4_length >= 1) {
            n = (uint32_t)arg4_length < 0x400u ? (uint32_t)arg4_length : 0x3ffu;
            (void)audio_settings_copy_text(tag->extend, arg4, n);
            tag->extend[n] = '\0';
            tag->extend_length = (uint16_t)n;
        } else if (tag->type == 1u) {
            (void)g2_audio_dump_snprintf(tag->extend, sizeof(tag->extend), s_knowledge_extend);
            tag->extend_length = (uint16_t)g2_log_module_length(tag->extend);
        } else {
            (void)g2_audio_dump_snprintf(tag->extend, sizeof(tag->extend), s_extend_text);
            tag->extend_length = (uint16_t)g2_log_module_length(tag->extend);
        }
        conversate_cli_send_payload(5u, 7u, tag, sizeof(*tag));
    } else if (audio_ble_hci_vendor_compare_44b610(sub, s_sub_start, 5u) == 0) {
        g2_conversate_cli_start_t *start = &g2_conversate_cli_start_200fabc4;

        (void)aeabi_memset_43c0e4(start, sizeof(*start), 0);
        start->flags[0] = 1u;
        start->flags[1] = 1u;
        start->flags[3] = 1u;
        start->flags[4] = 1u;
        start->flags[5] = 0u;
        start->flags[2] = 1u;
        start->flags[6] = 0u;
        start->flags[7] = 0u;
        g2_conversate_cli_note_sent_2013be6d = 0u;
        if (arg2 != NULL && arg2_length >= 1) {
            uint32_t n;

            start->flags[7] = 1u;
            start->total_packets = 2u;
            n = (uint32_t)g2_audio_dump_snprintf(start->name, sizeof(start->name), s_prep_note_name);
            if (n >= 0x80u)
                n = 0x7fu;
            start->name_length = (uint16_t)n;
            g2_conversate_cli_note_sent_2013be6d = 1u;
        }
        conversate_cli_send_payload(1u, 3u, start, sizeof(*start));
    } else if (audio_ble_hci_vendor_compare_44b610(sub, s_sub_packet, 6u) == 0) {
        g2_conversate_cli_packet_t *packet = &g2_conversate_cli_packet_200fb700;
        uint32_t index;
        uint32_t size;

        if (g2_conversate_cli_note_sent_2013be6d == 0u) {
            audio_ble_hci_boot_log_4733ee(s_packet_no_note);
            return 0;
        }
        if (arg2 == NULL || arg2_length < 1) {
            audio_ble_hci_boot_log_4733ee(s_packet_missing);
            return 0;
        }
        index = (uint32_t)atoi_48d868(arg2);
        if (index >= 2u) {
            audio_ble_hci_boot_log_4733ee(s_packet_invalid, index);
            return 0;
        }
        (void)aeabi_memset_43c0e4(packet, sizeof(*packet), 0);
        packet->index = index;
        size = conversate_cli_fill_pattern_581e6a(index, packet->data, CONVERSATE_PATTERN_BYTES);
        packet->size = (uint16_t)size;
        conversate_cli_send_payload(7u, 13u, packet, sizeof(*packet));
        audio_ble_hci_boot_log_4733ee(s_packet_sent, index, size);
    } else if (audio_ble_hci_vendor_compare_44b610(sub, s_sub_preplist, 8u) == 0) {
        g2_conversate_cli_preplist_t *list = &g2_conversate_cli_preplist_200fac58;
        uint32_t count = CONVERSATE_PREP_DEFAULT;
        uint32_t i;

        if (arg2 != NULL && arg2_length >= 1) {
            int32_t requested = atoi_48d868(arg2);

            if (requested >= 1)
                count = (uint32_t)requested;
        }
        if (count >= CONVERSATE_PREP_MAX + 1u)
            count = CONVERSATE_PREP_MAX;
        (void)aeabi_memset_43c0e4(list, sizeof(*list), 0);
        list->count = (uint16_t)count;
        list->done = 1u;
        for (i = 0u; i < count; i++) {
            uint32_t n;

            list->notes[i].id = i + 1u;
            n = (uint32_t)g2_audio_dump_snprintf(list->notes[i].name, sizeof(list->notes[i].name),
                                                 s_prep_name, i + 1u);
            if (n >= 0x80u)
                n = 0x7fu;
            list->notes[i].name_length = (uint16_t)n;
        }
        conversate_cli_send_payload(3u, 5u, list, sizeof(*list));
        audio_ble_hci_boot_log_4733ee(s_prep_sent, count);
    } else if (audio_ble_hci_vendor_compare_44b610(sub, s_sub_cache, 5u) == 0) {
        uint16_t i;

        audio_ble_hci_boot_log_4733ee(s_cache_header);
        for (i = 0u; i < audio_conversate_tag_storage_count_59674e(); i++) {
            const g2_conversate_tag_view_t *row = audio_conversate_tag_get_by_index_5964e2(i);

            audio_ble_hci_boot_log_4733ee(s_cache_row, row->key, row->value);
        }
    }
    return 0;
}

/* "translate add": feed one numbered source/target sentence pair to the
 * translate state machine. The parameter is not NULL-checked. */
int32_t cli_cmd_translate_5822e6(char *write_buffer, size_t write_buffer_len, const char *command_string)
{
    int32_t length = 0;
    const char *sub;
    g2_translate_cli_message_t *message = &g2_translate_cli_message_200651c0;

    (void)write_buffer;
    (void)write_buffer_len;
    sub = freertos_cli_get_parameter_5848fc(command_string, 1u, &length);
    if (audio_ble_hci_vendor_compare_44b610(sub, s_sub_add, 3u) == 0) {
        (void)g2_audio_dump_snprintf(g2_translate_cli_source_200035e8, TRANSLATE_SENTENCE_BYTES,
                                     s_source_format, g2_translate_cli_counter_200748c0);
        (void)g2_audio_dump_snprintf(g2_translate_cli_target_20003604, TRANSLATE_SENTENCE_BYTES,
                                     s_target_format, g2_translate_cli_counter_200748c0);
        g2_translate_cli_counter_200748c0++;
        message->source_length = (uint16_t)g2_log_module_length(g2_translate_cli_source_200035e8);
        message->target_length = (uint16_t)g2_log_module_length(g2_translate_cli_target_20003604);
        (void)audio_queue_copy_bytes(message->source, g2_translate_cli_source_200035e8,
                                     message->source_length);
        (void)audio_queue_copy_bytes(message->target, g2_translate_cli_target_20003604,
                                     message->target_length);
        message->valid = 1u;
        (void)translate_machine_handler_596b0c(TRANSLATE_FSM_EVENT_ADD, message, sizeof(*message));
    }
    return 0;
}

int32_t teleprompt_cli_pb_send_58237a(const g2_teleprompt_cli_pkg_t *pkg)
{
    g2_pb_ostream_t created;
    g2_pb_ostream_t stream;
    uint32_t status;

    if (pkg == NULL) {
        audio_ble_hci_boot_log_4733ee(s_tele_pkg_null);
        return -1;
    }
    audio_pb_ostream_from_buffer(&created, g2_teleprompt_cli_pb_buffer_200ff9a8, TELEPROMPT_PB_BYTES);
    (void)audio_uart_display_area_copy_439c04(&stream, &created, sizeof(stream));
    if (audio_pb_encode(&stream, g2_teleprompt_pb_msgdesc_77c304, pkg) == 0u) {
        audio_ble_hci_boot_log_4733ee(s_tele_encode);
        return -1;
    }
    status = audio_sync_send_to_both_ext_464f76(TELEPROMPT_SYNC_APP, g2_teleprompt_cli_pb_buffer_200ff9a8,
                                                (uint16_t)stream.bytes_written, 0u, 0u);
    if (status != 0u) {
        audio_ble_hci_boot_log_4733ee(s_tele_send, status);
        return -1;
    }
    return 0;
}

/* Package cmd 1 / oneof 3: one action byte plus an optional 44-byte
 * argument block. */
void teleprompt_cli_send_control_5823f6(uint8_t action, const void *data)
{
    g2_teleprompt_cli_pkg_t *pkg = &g2_teleprompt_cli_pkg_200fea50;

    (void)aeabi_memset_43c0e4(pkg, sizeof(*pkg), 0);
    pkg->header.cmd = 1u;
    g2_teleprompt_cli_magic_20075001++;
    pkg->header.magic = g2_teleprompt_cli_magic_20075001;
    pkg->header.which = 3u;
    pkg->action = action;
    if (data != NULL) {
        pkg->has_data = 1u;
        (void)audio_uart_display_area_copy_439c04(pkg->data, data, sizeof(pkg->data));
    }
    (void)teleprompt_cli_pb_send_58237a(pkg);
}

void cli_register_app_commands_5827d0(void)
{
    (void)freertos_cli_register_command_5847ac(&g2_cli_cmd_teleprompt_200035a8);
    (void)freertos_cli_register_command_5847ac(&g2_cli_cmd_translate_200035b8);
    (void)freertos_cli_register_command_5847ac(&g2_cli_cmd_conversate_200035c8);
    (void)freertos_cli_register_command_5847ac(&g2_cli_cmd_legalregulatory_200035d8);
}
