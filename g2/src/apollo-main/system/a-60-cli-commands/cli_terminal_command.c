/* FreeRTOS-Plus-CLI "terminal" command: simulates the phone-side terminal
 * (AI agent) protobuf traffic from the debug shell.
 * Stock source path not proven by a string; by analogy with
 * D:\01_workspace\s200_ap510b_iar_git\kernel\FreeRTOS-Plus-CLI\prvCommand\prvCommand_filesystem.c
 * it is one of the prvCommand_*.c files under kernel\FreeRTOS-Plus-CLI\prvCommand\.
 * Native 0x582b0c..0x5836af (interpreter), literal pool 0x5836b0..0x5836b7 (shared with
 * 0x582960/0x582a48), registration 0x5836b8..0x5836c1, pool 0x5836c4..0x5837bb.
 * Short sub-command words "hi" 0x582ea4, "add" 0x582f70, "dim" 0x582fec, "rep" 0x583040,
 * "asr" 0x583044, "ble" 0x583294 and "err" 0x583530 sit inline in the code.
 *
 * Every sub-command fills the nanopb terminal message at RAM 0x20100954 (0x850 bytes,
 * descriptor ROM 0x77c634), bumps the one-byte magic counter at RAM 0x20075002 and hands
 * it to terminal_cli_send_582960, which encodes it and sends it on service 0x30 as if it
 * had come from the host. "cache" only prints the terminal data module state.
 * The interpreter never writes its output buffer and always returns 0 (pdFALSE). */
#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

/* FreeRTOS-Plus-CLI CLI_Command_Definition_t. */
typedef int32_t (*g2_cli_interpreter_t)(char *write_buffer, size_t write_buffer_len, const char *command);
typedef struct {
    const char *command;          /* +0x0 */
    const char *help;             /* +0x4 */
    g2_cli_interpreter_t handler; /* +0x8 */
    int8_t expected_params;       /* +0xc, -1 = variable */
} g2_cli_command_definition_t;
_Static_assert(sizeof(g2_cli_command_definition_t) == 16, "CLI definition is 16 bytes");

/* Terminal protobuf message (nanopb: cmd, magic, oneof payload). */
enum {
    TERMINAL_CMD_MODE = 1,
    TERMINAL_CMD_HOST = 2,
    TERMINAL_CMD_ASR = 3,
    TERMINAL_CMD_STATUS = 4,
    TERMINAL_CMD_CONTENT = 5,
    TERMINAL_CMD_QUERY = 6,
    TERMINAL_CMD_ERR = 7,
    TERMINAL_CMD_SESSION_LIST = 8,
    TERMINAL_CMD_SWITCH_RESULT = 9,
    TERMINAL_CMD_SESSION_CHANGED = 10,
    TERMINAL_CMD_NEW_RESULT = 11,
    TERMINAL_CMD_QUERY_REPLY = 0xa3,
};

enum { STYLE_HIGHLIGHT = 0, STYLE_DIM = 1, STYLE_USER = 2 };
enum { CONTENT_OP_APPEND = 0, CONTENT_OP_REPLACE = 1 };
enum { SESSION_STATUS_THINKING = 1, SESSION_STATUS_DONE = 3, SESSION_STATUS_RESET = 4 };

#define TERMINAL_QUERY_OPTIONS_MAX 8
#define TERMINAL_OPTION_TEXT 0x80

typedef struct {
    uint32_t id;                      /* +0x00 */
    uint16_t text_len;                /* +0x04 */
    char text[TERMINAL_OPTION_TEXT];  /* +0x06 */
    uint8_t reserved[2];              /* +0x86 */
} g2_terminal_option_t;
_Static_assert(sizeof(g2_terminal_option_t) == 0x88, "query option is 0x88 bytes");

typedef struct {
    uint8_t cmd;            /* +0x0 */
    uint8_t magic;          /* +0x1 */
    uint16_t which_payload; /* +0x2 nanopb oneof tag */
    union {                 /* +0x4 */
        struct { uint8_t mode; } mode;                     /* tag 3 */
        struct {                                           /* tag 4 */
            uint8_t host;
            uint8_t reserved;
        } host;
        struct {                                           /* tag 5 */
            uint16_t text_len;      /* msg +0x004 */
            char text[0x200];       /* msg +0x006 */
            uint8_t sentence_final; /* msg +0x206 */
            uint8_t all_final;      /* msg +0x207 */
        } asr;
        struct {                                           /* tag 6 */
            uint8_t status;         /* msg +0x4 */
            uint8_t reserved[3];
            uint32_t tick;          /* msg +0x8 */
        } status;
        struct {                                           /* tag 7 */
            uint8_t style;          /* msg +0x004 */
            uint8_t reserved0;
            uint16_t text_len;      /* msg +0x006 */
            char text[0x200];       /* msg +0x008 */
            uint8_t op;             /* msg +0x208 */
            uint8_t reserved1[0xb];
            uint32_t tick;          /* msg +0x214 */
        } content;
        struct {                                           /* tag 8 */
            uint32_t query_id;      /* msg +0x004 */
            uint16_t question_len;  /* msg +0x008 */
            char question[0x400];   /* msg +0x00a */
            uint16_t option_count;  /* msg +0x40a */
            g2_terminal_option_t options[TERMINAL_QUERY_OPTIONS_MAX]; /* msg +0x40c */
            uint32_t tick;          /* msg +0x84c */
        } query;
        struct {                                           /* tag 0xb */
            uint32_t query_id;      /* msg +0x4 */
            uint32_t option_id;     /* msg +0x8 */
        } query_reply;
        uint8_t err;                /* tag 0xf */
        uint8_t session_list[1];    /* tag 0x10, filled by terminal_session_list_fill_582a48 */
        uint8_t switch_result;      /* tag 0x11 */
        uint32_t session_changed;   /* tag 0x15 */
        uint8_t new_result;         /* tag 0x17 */
    } payload;
} g2_terminal_pb_msg_t;
_Static_assert(sizeof(g2_terminal_pb_msg_t) == 0x850, "terminal message is 0x850 bytes");
_Static_assert(offsetof(g2_terminal_pb_msg_t, payload.content.op) == 0x208, "content op");
_Static_assert(offsetof(g2_terminal_pb_msg_t, payload.content.tick) == 0x214, "content tick");
_Static_assert(offsetof(g2_terminal_pb_msg_t, payload.asr.sentence_final) == 0x206, "asr flags");
_Static_assert(offsetof(g2_terminal_pb_msg_t, payload.query.option_count) == 0x40a, "query count");
_Static_assert(offsetof(g2_terminal_pb_msg_t, payload.query.options) == 0x40c, "query options");
_Static_assert(offsetof(g2_terminal_pb_msg_t, payload.query.tick) == 0x84c, "query tick");

/* Terminal data module views used by "cache". */
typedef struct {                /* td_state_ptr(): ASR cache */
    char text[0x800];           /* +0x000 */
    uint16_t final_len;         /* +0x800 */
    uint16_t len;               /* +0x802 */
    uint8_t sentence_final;     /* +0x804 */
    uint8_t all_final;          /* +0x805 */
} g2_td_asr_view_t;

typedef struct {                /* td_session_record_at(i): agent content record */
    uint8_t style;              /* +0x000 */
    uint8_t reserved;
    char text[0x202];           /* +0x002 */
    uint16_t text_len;          /* +0x204 */
    uint8_t reserved1[0xa];
    uint32_t seq;               /* +0x210 */
} g2_td_content_record_t;
_Static_assert(offsetof(g2_td_content_record_t, seq) == 0x210, "record seq");

typedef struct {                /* td_session_struct_ptr(): cached query */
    uint32_t query_id;          /* +0x000 */
    uint16_t question_len;      /* +0x004 */
    uint8_t reserved[0x400];
    uint16_t option_count;      /* +0x406 */
} g2_td_query_view_t;
_Static_assert(offsetof(g2_td_query_view_t, option_count) == 0x406, "query option count");

typedef struct {                /* td_active_session() + 0x9c + i * 0x90 */
    uint32_t id;                /* +0x00 */
    uint16_t title_len;         /* +0x04 */
    char title[0x80];           /* +0x06 */
    uint8_t status;             /* +0x86 */
    uint8_t reserved;
    uint32_t timer;             /* +0x88 */
    uint8_t notify_dismiss;     /* +0x8c */
    uint8_t reserved1[3];
} g2_td_session_entry_t;
_Static_assert(sizeof(g2_td_session_entry_t) == 0x90, "session entry is 0x90 bytes");

#define TD_HOST_STATUS_OFFSET 0xa1d8u    /* td_state_ptr_alias1() + 0xa1d8 */
#define TD_RING_COUNT_OFFSET 0x8500u     /* u16 record count */
#define TD_RING_ID_OFFSET 0x8504u        /* u32 content id */
#define TD_SESSION_COUNT_OFFSET 8u       /* u32 */
#define TD_SESSION_ENTRIES_OFFSET 0x9cu

extern g2_terminal_pb_msg_t g2_terminal_cli_msg_20100954;    /* RAM 0x20100954 */
extern uint8_t g2_terminal_cli_magic_20075002;                /* RAM 0x20075002 */
extern const char *g2_terminal_cli_long_query_20003630;       /* RAM 0x20003630, init -> ROM 0x6a9a88 */
extern g2_cli_command_definition_t g2_cli_cmd_terminal_20003620; /* RAM 0x20003620 "terminal" */

extern int32_t freertos_cli_register_command_5847ac(const g2_cli_command_definition_t *definition); /* FreeRTOS_CLIRegisterCommand */
extern const char *freertos_cli_get_parameter_5848fc(const char *command, uint32_t index,
                                                     int32_t *length); /* 0x5848fc FreeRTOS_CLIGetParameter */
extern void audio_ble_hci_boot_log_4733ee(const char *format, ...); /* console printf */
extern void *aeabi_memset_43c0e4(void *dst, uint32_t len, int32_t value); /* memset (dst, n, c) */
extern int32_t audio_ble_hci_vendor_compare_44b610(const void *a, const void *b, uint32_t n); /* strncmp */
extern uint32_t g2_log_module_length(const char *s);                  /* 0x44a43c strlen */
extern int32_t atoi_48d868(const char *s);                            /* 0x48d868 */
extern int32_t g2_audio_dump_snprintf(char *dst, uint32_t size, const char *format, ...); /* 0x44b728 */

/* Same-file helpers before the interpreter (not in this unit). */
extern const char *terminal_session_status_name_5828f8(uint8_t status); /* SESSION_STATUS_* */
extern const char *terminal_style_name_582924(uint8_t style);           /* STYLE_* */
extern const char *terminal_host_status_name_582942(uint8_t status);    /* HOST_STATUS_* */
extern int32_t terminal_cli_send_582960(const g2_terminal_pb_msg_t *msg); /* pb encode + send, service 0x30 */
extern void terminal_text_copy_5829e0(void *dst_len_prefixed, uint32_t cap, const char *src, int32_t len);
extern void terminal_session_list_fill_582a48(void *dst, int32_t host, int32_t current, uint32_t count);

/* Terminal data module (app\gui\terminal\terminal_data.c). */
extern const uint8_t *audio_td_state_ptr(void);              /* 0x597318 td_state_ptr */
extern uint8_t *audio_td_session_struct_ptr(void);           /* 0x59731e td_session_struct_ptr */
extern uint32_t audio_terminal_resource_597324(void);        /* td_ring_ptr */
extern uint8_t *audio_td_active_session(void);               /* 0x59732a td_active_session */
extern uint8_t *audio_td_state_ptr_alias1(void);             /* 0x597344 td_state_ptr_alias1 */
extern uint32_t audio_terminal_item_59737c(uint32_t index);  /* td_session_record_at */
extern uint8_t td_flag_get(void);                            /* 0x5973aa */
extern uint32_t audio_td_host_counter_get_5973d4(void);      /* td_counter_a_get */
extern uint32_t audio_terminal_counter_b_get_5973dc(void);   /* td_counter_b_get */
extern uint8_t audio_td_record_status_read(void);            /* 0x597446 td_record_status_read */
extern uint8_t audio_td_flag_b_get(void);                    /* 0x59758e td_flag_b_get */
extern uint8_t audio_ux_get_system_ble_status(void);         /* 0x47d8ce UX_GetSystemBLEStatus */
extern void CB_BLE_STATUS_Notify(uint32_t event, uint32_t value); /* 0x4abd60 */

int32_t cli_terminal_command_582b0c(char *write_buffer, size_t write_buffer_len, const char *command);
void cli_register_terminal_command_5836b8(void);

static const char missing_sub[] = "terminal: missing sub command\r\n"; /* ROM 0x764150 */
static const char w_mode[] = "mode";                                  /* ROM 0x78e344 */
static const char mode_missing[] = "terminal mode: missing <0|1>\r\n"; /* ROM 0x764170 */
static const char w_content[] = "content";                            /* ROM 0x78e34c */
static const char content_usage[] =
    "terminal content: usage: content <hi|dim|user> <add|rep> <text>\r\n"; /* ROM 0x704b88 */
static const char w_hi[] = "hi";                                      /* code 0x582ea4 */
static const char w_highlight[] = "highlight";                        /* ROM 0x78bb1c */
static const char w_dim[] = "dim";                                    /* code 0x582fec */
static const char w_user[] = "user";                                  /* ROM 0x78e354 */
static const char content_bad_style[] =
    "terminal content: invalid style '%.*s', expect hi|dim|user\r\n"; /* ROM 0x70e124 */
static const char w_add[] = "add";                                    /* code 0x582f70 */
static const char w_append[] = "append";                              /* ROM 0x78e35c */
static const char w_rep[] = "rep";                                    /* code 0x583040 */
static const char w_replace[] = "replace";                            /* ROM 0x78e364 */
static const char content_bad_op[] =
    "terminal content: invalid op '%.*s', expect add|rep\r\n";        /* ROM 0x721ac8 */
static const char w_asr_final[] = "asr_final";                        /* ROM 0x78bb28 */
static const char w_asr_sfinal[] = "asr_sfinal";                      /* ROM 0x78bb34 */
static const char w_asr[] = "asr";                                    /* code 0x583044 */
static const char w_status[] = "status";                              /* ROM 0x78e36c */
static const char status_missing[] = "terminal status: missing <0-4>\r\n"; /* ROM 0x7589ac */
static const char status_invalid[] = "terminal status: invalid <0-4>\r\n"; /* ROM 0x7589d0 */
static const char w_reset[] = "reset";                                /* ROM 0x78e374 */
static const char w_host[] = "host";                                  /* ROM 0x78e37c */
static const char host_missing[] = "terminal host: missing <0-2>\r\n"; /* ROM 0x764190 */
static const char host_invalid[] = "terminal host: invalid <0-2>\r\n"; /* ROM 0x7641b0 */
static const char w_ble[] = "ble";                                    /* code 0x583294 */
static const char ble_missing[] = "terminal ble: missing <0|1>\r\n";   /* ROM 0x7641d0 */
static const char ble_invalid[] = "terminal ble: invalid <0|1>\r\n";   /* ROM 0x7641f0 */
static const char ble_set[] =
    "terminal ble: set system status=%d and trigger callback\r\n";    /* ROM 0x717dac */
static const char w_query[] = "query";                                /* ROM 0x78e384 */
static const char query_missing_text[] = "terminal query: missing <question text>\r\n"; /* ROM 0x741eec */
static const char query_missing_cnt[] = "terminal query: missing <option cnt>\r\n";     /* ROM 0x74d034 */
static const char query_invalid_cnt[] = "terminal query: invalid <option cnt>\r\n";     /* ROM 0x74d05c */
static const char option_fmt[] = "option %d";                         /* ROM 0x78bb40 */
static const char w_query_long[] = "query_long";                      /* ROM 0x78bb4c */
static const char w_query_reply[] = "query_reply";                    /* ROM 0x78bb58 */
static const char query_reply_usage[] =
    "terminal query_reply: usage: query_reply <option_id> [query_id]\r\n"; /* ROM 0x704bcc */
static const char query_reply_no_cache[] =
    "terminal query_reply: no cached query, please pass <query_id> explicitly\r\n"; /* ROM 0x6f57d4 */
static const char query_reply_sent[] =
    "terminal query_reply: query_id=%lu option_id=%lu\r\n";           /* ROM 0x72c270 */
static const char w_err[] = "err";                                    /* code 0x583530 */
static const char err_missing[] = "terminal err: missing <0-2>\r\n";   /* ROM 0x764210 */
static const char err_invalid[] = "terminal err: invalid <0-2>\r\n";   /* ROM 0x764230 */
static const char w_session_list[] = "session_list";                  /* ROM 0x788280 */
static const char session_list_usage[] =
    "terminal session_list: usage: session_list <host> <current_session_id> <count>\r\n"; /* ROM 0x6e95b0 */
static const char w_switch_result[] = "switch_result";                /* ROM 0x788290 */
static const char switch_missing[] = "terminal switch_result: missing <0|1>\r\n"; /* ROM 0x74d084 */
static const char switch_invalid[] = "terminal switch_result: invalid <0|1>\r\n"; /* ROM 0x74d0ac */
static const char w_new_result[] = "new_result";                      /* ROM 0x78bb64 */
static const char new_missing[] = "terminal new_result: missing <0|1>\r\n"; /* ROM 0x74d0d4 */
static const char new_invalid[] = "terminal new_result: invalid <0|1>\r\n"; /* ROM 0x74d0fc */
static const char w_session_changed[] = "session_changed";            /* ROM 0x7882a0 */
static const char session_changed_missing[] =
    "terminal session_changed: missing <session_id>\r\n";             /* ROM 0x72c2a4 */
static const char w_cache[] = "cache";                                /* ROM 0x78e38c */
static const char cache_banner[] = "=== terminal cache ===\r\n";      /* ROM 0x770350 */
static const char cache_asr[] =
    "[ASR] final_len=%u len=%u sentence_final=%u all_final=%u text=\"%s\"\r\n"; /* ROM 0x6fc2fc */
static const char s_connected[] = "CONNECTED";                        /* ROM 0x78bb70 */
static const char s_disconnected[] = "DISCONNECTED";                  /* ROM 0x7882b0 */
static const char cache_runtime[] =
    "[Runtime] ble_connected=%s(%u) host_status=%s(%d)\r\n";          /* ROM 0x72c2d8 */
static const char cache_content[] =
    "[Agent Content Cache] id=%u count=%u active=%u completed=%u session_status=%s(%d)\r\n"; /* ROM 0x6e9604 */
static const char cache_record[] =
    "  [%u] seq=%u style=%s(%d) text_len=%u text=\"%s\"\r\n";         /* ROM 0x72c30c */
static const char cache_query[] = "[Query] query_id=%u question_len=%u options=%u\r\n"; /* ROM 0x72c340 */
static const char cache_session[] =
    "[Session] valid=%u new_pending=%u host=%u current=%u count=%u\r\n"; /* ROM 0x70e164 */
static const char cache_session_entry[] =
    "  session[%u] id=%u title_len=%u title=\"%.*s\" status=%s(%d) notify_dismiss=%u timer=%u\r\n"; /* ROM 0x6e1430 */
static const char unknown_sub[] = "terminal: unknown sub command '%.*s'\r\n"; /* ROM 0x74d124 */
static const char usage[] =
    "Use: mode|content|asr|asr_sfinal|asr_final|status|reset|host|ble|query|query_long|"
    "query_reply|err|session_list|switch_result|new_result|session_changed|cache\r\n"; /* ROM 0x6d32b8 */

/* Stock compares the measured parameter length first, then strncmp over that length. */
static bool word_is(const char *arg, int32_t len, int32_t want, const char *word)
{
    return len == want && audio_ble_hci_vendor_compare_44b610(arg, word, (uint32_t)len) == 0;
}

/* Clears the message and fills the header; the magic byte is pre-incremented. */
static g2_terminal_pb_msg_t *msg_begin(uint8_t cmd, uint16_t which)
{
    g2_terminal_pb_msg_t *msg = &g2_terminal_cli_msg_20100954;
    (void)aeabi_memset_43c0e4(msg, sizeof *msg, 0);
    msg->cmd = cmd;
    g2_terminal_cli_magic_20075002++;
    msg->magic = g2_terminal_cli_magic_20075002;
    msg->which_payload = which;
    return msg;
}

/* "option N" labels for the first count options (count already clamped to 8). */
static void query_fill_options(g2_terminal_pb_msg_t *msg, int32_t count)
{
    for (int32_t i = 0; i < count; i++) {
        g2_terminal_option_t *option = &msg->payload.query.options[i];
        option->id = (uint32_t)(i + 1);
        int32_t n = g2_audio_dump_snprintf(option->text, TERMINAL_OPTION_TEXT, option_fmt, i + 1);
        if (n < 0)
            n = 0;
        if ((uint32_t)n > TERMINAL_OPTION_TEXT - 1u)
            n = TERMINAL_OPTION_TEXT - 1;
        option->text_len = (uint16_t)n;
    }
}

static void print_cache(void)
{
    uint8_t *alias = audio_td_state_ptr_alias1();
    const g2_td_asr_view_t *asr = (const g2_td_asr_view_t *)(const void *)audio_td_state_ptr();
    const uint8_t *ring = (const uint8_t *)(uintptr_t)audio_terminal_resource_597324();
    const g2_td_query_view_t *query = (const g2_td_query_view_t *)(void *)audio_td_session_struct_ptr();
    const uint8_t *active = audio_td_active_session();
    uint8_t host_status = alias[TD_HOST_STATUS_OFFSET];
    uint8_t record_status = audio_td_record_status_read();
    uint32_t content_active = record_status == SESSION_STATUS_THINKING;
    uint32_t content_done = record_status == SESSION_STATUS_DONE;
    uint32_t ble = audio_ux_get_system_ble_status() != 0u;

    audio_ble_hci_boot_log_4733ee(cache_banner);
    audio_ble_hci_boot_log_4733ee(cache_asr, asr->final_len, asr->len, asr->sentence_final,
                                         asr->all_final, asr->text);
    audio_ble_hci_boot_log_4733ee(cache_runtime, ble ? s_connected : s_disconnected, ble,
                                         terminal_host_status_name_582942(host_status), host_status);

    const uint16_t *record_count = (const uint16_t *)(const void *)(ring + TD_RING_COUNT_OFFSET);
    audio_ble_hci_boot_log_4733ee(cache_content, *(const uint32_t *)(const void *)(ring + TD_RING_ID_OFFSET),
                                         *record_count, content_active, content_done,
                                         terminal_session_status_name_5828f8(record_status), record_status);
    for (uint16_t i = 0; i < *record_count; i++) {
        const g2_td_content_record_t *record =
            (const g2_td_content_record_t *)(uintptr_t)audio_terminal_item_59737c(i);
        if (record != NULL)
            audio_ble_hci_boot_log_4733ee(cache_record, i, record->seq, terminal_style_name_582924(record->style),
                                                 record->style, record->text_len, record->text);
    }

    audio_ble_hci_boot_log_4733ee(cache_query, query->query_id, query->question_len, query->option_count);

    uint32_t count = active != NULL ? *(const uint32_t *)(const void *)(active + TD_SESSION_COUNT_OFFSET) : 0u;
    uint32_t current = audio_terminal_counter_b_get_5973dc();
    uint32_t host = audio_td_host_counter_get_5973d4();
    uint32_t new_pending = audio_td_flag_b_get() != 0u;
    uint32_t valid = td_flag_get() != 0u;
    audio_ble_hci_boot_log_4733ee(cache_session, valid, new_pending, host, current, count);
    if (active == NULL)
        return;
    const g2_td_session_entry_t *entries =
        (const g2_td_session_entry_t *)(const void *)(active + TD_SESSION_ENTRIES_OFFSET);
    for (uint32_t i = 0; i < *(const uint32_t *)(const void *)(active + TD_SESSION_COUNT_OFFSET); i++) {
        const g2_td_session_entry_t *entry = &entries[i];
        uint32_t shown = entry->title_len;
        if (shown > 0x80u)
            shown = 0x80u;
        uint32_t notify = entry->notify_dismiss != 0u;
        audio_ble_hci_boot_log_4733ee(cache_session_entry, i, entry->id, entry->title_len, shown, entry->title,
                                             terminal_session_status_name_5828f8(entry->status), entry->status,
                                             notify, entry->timer);
    }
}

int32_t cli_terminal_command_582b0c(char *write_buffer, size_t write_buffer_len, const char *command)
{
    int32_t len1 = 0, len2 = 0, len3 = 0, len4 = 0;
    g2_terminal_pb_msg_t *msg;
    (void)write_buffer;
    (void)write_buffer_len;

    const char *sub = freertos_cli_get_parameter_5848fc(command, 1u, &len1);
    const char *arg2 = freertos_cli_get_parameter_5848fc(command, 2u, &len2);
    const char *arg3 = freertos_cli_get_parameter_5848fc(command, 3u, &len3);
    const char *arg4 = freertos_cli_get_parameter_5848fc(command, 4u, &len4);

    if (sub == NULL || len1 < 1) {
        audio_ble_hci_boot_log_4733ee(missing_sub);
        return 0;
    }

    if (word_is(sub, len1, 4, w_mode)) {
        if (arg2 == NULL) {
            audio_ble_hci_boot_log_4733ee(mode_missing);
            return 0;
        }
        msg = msg_begin(TERMINAL_CMD_MODE, 3u);
        msg->payload.mode.mode = atoi_48d868(arg2) != 0 ? 2u : 1u;
        (void)terminal_cli_send_582960(msg);
    } else if (word_is(sub, len1, 7, w_content)) {
        uint8_t style, op;
        if (arg2 == NULL || arg3 == NULL || arg4 == NULL) {
            audio_ble_hci_boot_log_4733ee(content_usage);
            return 0;
        }
        if (word_is(arg2, len2, 2, w_hi) || word_is(arg2, len2, 9, w_highlight)) {
            style = STYLE_HIGHLIGHT;
        } else if (word_is(arg2, len2, 3, w_dim)) {
            style = STYLE_DIM;
        } else if (word_is(arg2, len2, 4, w_user)) {
            style = STYLE_USER;
        } else {
            audio_ble_hci_boot_log_4733ee(content_bad_style, len2, arg2);
            return 0;
        }
        if (word_is(arg3, len3, 3, w_add) || word_is(arg3, len3, 6, w_append)) {
            op = CONTENT_OP_APPEND;
        } else if (word_is(arg3, len3, 3, w_rep) || word_is(arg3, len3, 7, w_replace)) {
            op = CONTENT_OP_REPLACE;
        } else {
            audio_ble_hci_boot_log_4733ee(content_bad_op, len3, arg3);
            return 0;
        }
        msg = msg_begin(TERMINAL_CMD_CONTENT, 7u);
        msg->payload.content.style = style;
        msg->payload.content.op = op;
        msg->payload.content.tick = audio_terminal_counter_b_get_5973dc();
        terminal_text_copy_5829e0(&msg->payload.content.text_len, 0x200u, arg4, len4);
        (void)terminal_cli_send_582960(msg);
    } else if (word_is(sub, len1, 9, w_asr_final)) {
        msg = msg_begin(TERMINAL_CMD_ASR, 5u);
        msg->payload.asr.sentence_final = 1u;
        msg->payload.asr.all_final = 1u;
        terminal_text_copy_5829e0(&msg->payload.asr.text_len, 0x200u, arg2, len2);
        (void)terminal_cli_send_582960(msg);
    } else if (word_is(sub, len1, 10, w_asr_sfinal)) {
        msg = msg_begin(TERMINAL_CMD_ASR, 5u);
        msg->payload.asr.sentence_final = 1u;
        msg->payload.asr.all_final = 0u;
        terminal_text_copy_5829e0(&msg->payload.asr.text_len, 0x200u, arg2, len2);
        (void)terminal_cli_send_582960(msg);
    } else if (word_is(sub, len1, 3, w_asr)) {
        msg = msg_begin(TERMINAL_CMD_ASR, 5u);
        msg->payload.asr.sentence_final = 0u;
        msg->payload.asr.all_final = 0u;
        terminal_text_copy_5829e0(&msg->payload.asr.text_len, 0x200u, arg2, len2);
        (void)terminal_cli_send_582960(msg);
    } else if (word_is(sub, len1, 6, w_status)) {
        if (arg2 == NULL) {
            audio_ble_hci_boot_log_4733ee(status_missing);
            return 0;
        }
        uint32_t status = (uint32_t)atoi_48d868(arg2);
        if (status >= 5u) {
            audio_ble_hci_boot_log_4733ee(status_invalid);
            return 0;
        }
        msg = msg_begin(TERMINAL_CMD_STATUS, 6u);
        msg->payload.status.status = (uint8_t)status;
        msg->payload.status.tick = audio_terminal_counter_b_get_5973dc();
        (void)terminal_cli_send_582960(msg);
    } else if (word_is(sub, len1, 5, w_reset)) {
        msg = msg_begin(TERMINAL_CMD_STATUS, 6u);
        msg->payload.status.status = SESSION_STATUS_RESET;
        msg->payload.status.tick = audio_terminal_counter_b_get_5973dc();
        (void)terminal_cli_send_582960(msg);
    } else if (word_is(sub, len1, 4, w_host)) {
        if (arg2 == NULL) {
            audio_ble_hci_boot_log_4733ee(host_missing);
            return 0;
        }
        uint32_t host = (uint32_t)atoi_48d868(arg2);
        if (host >= 3u) {
            audio_ble_hci_boot_log_4733ee(host_invalid);
            return 0;
        }
        msg = msg_begin(TERMINAL_CMD_HOST, 4u);
        msg->payload.host.host = (uint8_t)host;
        msg->payload.host.reserved = 0u;
        (void)terminal_cli_send_582960(msg);
    } else if (word_is(sub, len1, 3, w_ble)) {
        if (arg2 == NULL) {
            audio_ble_hci_boot_log_4733ee(ble_missing);
            return 0;
        }
        uint32_t ble = (uint32_t)atoi_48d868(arg2);
        if (ble == 0u || ble == 1u) {
            CB_BLE_STATUS_Notify(0u, (uint8_t)ble);
            audio_ble_hci_boot_log_4733ee(ble_set, ble);
        } else {
            audio_ble_hci_boot_log_4733ee(ble_invalid);
        }
    } else if (word_is(sub, len1, 5, w_query)) {
        if (arg2 == NULL) {
            audio_ble_hci_boot_log_4733ee(query_missing_text);
            return 0;
        }
        if (arg3 == NULL) {
            audio_ble_hci_boot_log_4733ee(query_missing_cnt);
            return 0;
        }
        /* The message, both magic increments and the tick are committed before the count check. */
        msg = msg_begin(TERMINAL_CMD_QUERY, 8u);
        g2_terminal_cli_magic_20075002++;
        msg->payload.query.query_id = g2_terminal_cli_magic_20075002;
        msg->payload.query.tick = audio_terminal_counter_b_get_5973dc();
        int32_t count = atoi_48d868(arg3);
        if (count < 1) {
            audio_ble_hci_boot_log_4733ee(query_invalid_cnt);
            return 0;
        }
        if (count > TERMINAL_QUERY_OPTIONS_MAX)
            count = TERMINAL_QUERY_OPTIONS_MAX;
        terminal_text_copy_5829e0(&msg->payload.query.question_len, 0x400u, arg2, len2);
        msg->payload.query.option_count = (uint16_t)count;
        query_fill_options(msg, count);
        (void)terminal_cli_send_582960(msg);
    } else if (word_is(sub, len1, 10, w_query_long)) {
        msg = msg_begin(TERMINAL_CMD_QUERY, 8u);
        g2_terminal_cli_magic_20075002++;
        msg->payload.query.query_id = g2_terminal_cli_magic_20075002;
        msg->payload.query.tick = audio_terminal_counter_b_get_5973dc();
        terminal_text_copy_5829e0(&msg->payload.query.question_len, 0x400u, g2_terminal_cli_long_query_20003630,
                                  (int32_t)g2_log_module_length(g2_terminal_cli_long_query_20003630));
        msg->payload.query.option_count = TERMINAL_QUERY_OPTIONS_MAX;
        query_fill_options(msg, TERMINAL_QUERY_OPTIONS_MAX);
        (void)terminal_cli_send_582960(msg);
    } else if (word_is(sub, len1, 11, w_query_reply)) {
        uint32_t query_id;
        if (arg2 == NULL) {
            audio_ble_hci_boot_log_4733ee(query_reply_usage);
            return 0;
        }
        uint32_t option_id = (uint32_t)atoi_48d868(arg2);
        if (arg3 == NULL) {
            const uint32_t *cached = (const uint32_t *)(void *)audio_td_session_struct_ptr();
            if (cached == NULL || *cached == 0u) {
                audio_ble_hci_boot_log_4733ee(query_reply_no_cache);
                return 0;
            }
            query_id = *cached;
        } else {
            query_id = (uint32_t)atoi_48d868(arg3);
        }
        msg = msg_begin(TERMINAL_CMD_QUERY_REPLY, 0xbu);
        msg->payload.query_reply.query_id = query_id;
        msg->payload.query_reply.option_id = option_id;
        audio_ble_hci_boot_log_4733ee(query_reply_sent, query_id, option_id);
        (void)terminal_cli_send_582960(msg);
    } else if (word_is(sub, len1, 3, w_err)) {
        if (arg2 == NULL) {
            audio_ble_hci_boot_log_4733ee(err_missing);
            return 0;
        }
        uint32_t err = (uint32_t)atoi_48d868(arg2);
        if (err >= 3u) {
            audio_ble_hci_boot_log_4733ee(err_invalid);
            return 0;
        }
        msg = msg_begin(TERMINAL_CMD_ERR, 0xfu);
        msg->payload.err = (uint8_t)err;
        (void)terminal_cli_send_582960(msg);
    } else if (word_is(sub, len1, 12, w_session_list)) {
        if (arg2 == NULL || arg3 == NULL || arg4 == NULL) {
            audio_ble_hci_boot_log_4733ee(session_list_usage);
            return 0;
        }
        int32_t host = atoi_48d868(arg2);
        int32_t current = atoi_48d868(arg3);
        int32_t count = atoi_48d868(arg4);
        msg = msg_begin(TERMINAL_CMD_SESSION_LIST, 0x10u);
        terminal_session_list_fill_582a48(msg->payload.session_list, host, current, (uint32_t)count);
        (void)terminal_cli_send_582960(msg);
    } else if (word_is(sub, len1, 13, w_switch_result)) {
        if (arg2 == NULL) {
            audio_ble_hci_boot_log_4733ee(switch_missing);
            return 0;
        }
        uint32_t result = (uint32_t)atoi_48d868(arg2);
        if (result >= 2u) {
            audio_ble_hci_boot_log_4733ee(switch_invalid);
            return 0;
        }
        msg = msg_begin(TERMINAL_CMD_SWITCH_RESULT, 0x11u);
        msg->payload.switch_result = (uint8_t)result;
        (void)terminal_cli_send_582960(msg);
    } else if (word_is(sub, len1, 10, w_new_result)) {
        if (arg2 == NULL) {
            audio_ble_hci_boot_log_4733ee(new_missing);
            return 0;
        }
        uint32_t result = (uint32_t)atoi_48d868(arg2);
        if (result >= 2u) {
            audio_ble_hci_boot_log_4733ee(new_invalid);
            return 0;
        }
        msg = msg_begin(TERMINAL_CMD_NEW_RESULT, 0x17u);
        msg->payload.new_result = (uint8_t)result;
        (void)terminal_cli_send_582960(msg);
    } else if (word_is(sub, len1, 15, w_session_changed)) {
        if (arg2 == NULL) {
            audio_ble_hci_boot_log_4733ee(session_changed_missing);
            return 0;
        }
        int32_t session_id = atoi_48d868(arg2);
        msg = msg_begin(TERMINAL_CMD_SESSION_CHANGED, 0x15u);
        msg->payload.session_changed = (uint32_t)session_id;
        (void)terminal_cli_send_582960(msg);
    } else if (word_is(sub, len1, 5, w_cache)) {
        print_cache();
    } else {
        audio_ble_hci_boot_log_4733ee(unknown_sub, len1, sub);
        audio_ble_hci_boot_log_4733ee(usage);
    }
    return 0;
}

void cli_register_terminal_command_5836b8(void)
{
    (void)freertos_cli_register_command_5847ac(&g2_cli_cmd_terminal_20003620);
}
