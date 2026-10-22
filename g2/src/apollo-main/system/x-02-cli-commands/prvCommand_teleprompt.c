/* Product FreeRTOS-Plus-CLI "teleprompt" and "legalregulatory" handlers,
 * stock directory D:\01_workspace\s200_ap510b_iar_git\kernel\
 * FreeRTOS-Plus-CLI\prvCommand\ (file name not retained). Native:
 * teleprompt 0x582448..0x5827b5, legalregulatory 0x5827b6..0x5827cf, pool
 * 0x5827ec..0x5828f7 (shared). The rest of this stock module (conversate,
 * translate, the teleprompt pb helpers 0x58237a / 0x5823f6 and the
 * registrar 0x5827d0) is in a-59-cli-commands/prvCommand_app.c.
 *
 *   teleprompt start <page> <total> [lines=5] [scroll_mode=0] [mode=1]
 *   teleprompt stop|pause|resume          control actions 4 / 2 / 3
 *   teleprompt aisync <page> <line> <char>
 *   teleprompt page <id>                  dump a cached page
 *   teleprompt fill [total] [lines<=10]   inject synthetic pages
 * Packages go to both arms on sync app 6 (see prvCommand_app.c). */
#include <stddef.h>
#include <stdint.h>
#include "g2_teleprompt_page_data.h"
#include "../a-59-cli-commands/cli_commands.h"

#define TP_ACTION_START 1u
#define TP_ACTION_PAUSE 2u
#define TP_ACTION_RESUME 3u
#define TP_ACTION_STOP 4u
#define TP_CMD_PAGE 3u
#define TP_CMD_AISYNC 4u
#define TP_WHICH_PAGE 5u
#define TP_WHICH_AISYNC 6u
#define TP_PKG_BYTES 0xf58u
#define TP_DEFAULT_LINES 5
#define TP_DEFAULT_MODE 1
#define TP_FILL_LINES_MAX 10u
#define TP_FILL_PAGES_CACHED 20u
#define TP_FILL_TEXT_BYTES 1024u
#define TP_FILL_SEND_DELAY 20u
#define TP_START_WIDTH 567u   /* constant fields of the start payload */
#define TP_START_HEIGHT 2320u
#define LEGAL_REGULATORY_APP 0x109u

/* Start parameters: bytes 0..1 are presence flags, bytes 4..47 are the
 * 44-byte control payload passed to teleprompt_cli_send_control_5823f6. */
typedef struct {
    uint8_t has_start;      /* +0x00 */
    uint8_t has_data;       /* +0x01 */
    uint8_t pad0[2];
    uint8_t mode;           /* +0x04 */
    uint8_t pad1[3];
    uint32_t start_page;    /* +0x08 */
    uint32_t reserved0;     /* +0x0c */
    uint32_t total_pages;   /* +0x10 */
    uint32_t total_lines;   /* +0x14 total_pages * 10 */
    uint32_t width;         /* +0x18 567 */
    uint32_t height;        /* +0x1c 2320 */
    uint32_t reserved1;     /* +0x20 */
    uint32_t reserved2;     /* +0x24 */
    uint32_t lines;         /* +0x28 */
    uint8_t scroll_mode;    /* +0x2c */
    uint8_t pad2[3];
} g2_teleprompt_cli_start_t;
_Static_assert(sizeof(g2_teleprompt_cli_start_t) == 48u, "start parameters");

typedef struct {
    uint32_t page;          /* +0x0 */
    uint32_t line;          /* +0x4 */
    uint32_t character;     /* +0x8 */
} g2_teleprompt_cli_aisync_t;
_Static_assert(sizeof(g2_teleprompt_cli_aisync_t) == 12u, "aisync payload");

/* Package (RAM 0x200fea50): cmd, rolling magic, oneof selector, payload. */
typedef struct {
    uint8_t cmd;            /* +0x0 */
    uint8_t magic;          /* +0x1 */
    uint16_t which;         /* +0x2 */
    uint8_t payload[TP_PKG_BYTES - 4u]; /* +0x4 */
} g2_teleprompt_cli_pkg_view_t;
_Static_assert(sizeof(g2_teleprompt_cli_pkg_view_t) == TP_PKG_BYTES, "teleprompt package");

/* Teleprompt FSM control block (RAM 0x20109390); only total_pages read. */
typedef struct {
    uint8_t reserved[0x10];
    uint32_t total_pages;   /* +0x10 (doc +0x0c) */
} g2_teleprompt_fsm_ctrl_view_t;

extern g2_teleprompt_cli_start_t g2_teleprompt_cli_start_200fea14;   /* RAM 0x200fea14 */
extern g2_teleprompt_cli_aisync_t g2_teleprompt_cli_aisync_200fea44; /* RAM 0x200fea44 */
extern g2_teleprompt_page_t g2_teleprompt_cli_page_200fe608;         /* RAM 0x200fe608 */
extern g2_teleprompt_cli_pkg_view_t g2_teleprompt_cli_pkg_200fea50;  /* RAM 0x200fea50 */
extern uint8_t g2_teleprompt_cli_magic_20075001;                     /* RAM 0x20075001 */
extern g2_teleprompt_fsm_ctrl_view_t g2_teleprompt_fsm_ctrl;         /* RAM 0x20109390 */

extern int32_t audio_ble_hci_vendor_compare_44b610(const void *a, const void *b, uint32_t len); /* strncmp */
extern int32_t atoi_48d868(const char *text);
extern void *aeabi_memset_43c0e4(void *dst, uint32_t len, int32_t value);
extern void *aeabi_memcpy4_439c04(void *dst, const void *src, uint32_t len);
extern int32_t g2_audio_dump_snprintf(char *dst, uint32_t size, const char *format, ...); /* 0x44b728 */
extern void audio_uart_task_delay(uint32_t ticks); /* 0x454b4c */
extern void audio_uart_master_display_start(uint32_t app, const void *payload,
                                            uint16_t length, uint32_t extra); /* 0x464b2e */
extern int32_t teleprompt_cli_pb_send_58237a(const void *pkg);
extern void teleprompt_cli_send_control_5823f6(uint8_t action, const void *data);

static const char s_missing[] =
    "teleprompt: missing sub command (start/fill/stop/pause/resume/aisync/page)\r\n"; /* ROM 0x6ef3b8 */
static const char s_start[] = "start";   /* ROM 0x78e2fc */
static const char s_start_log[] =
    "teleprompt start: page=%d total=%d lines=%d scroll_mode=%d mode=%d\r\n"; /* ROM 0x6fc26c */
static const char s_stop[] = "stop";     /* ROM 0x78e314 */
static const char s_pause[] = "pause";   /* ROM 0x78e31c */
static const char s_resume[] = "resume"; /* ROM 0x78e324 */
static const char s_aisync[] = "aisync"; /* ROM 0x78e32c */
static const char s_page[] = "page";     /* ROM 0x78e334 */
static const char s_page_missing[] = "Page id:%d not ready\r\n"; /* ROM 0x77abf4 */
static const char s_page_dump[] = "Page id:%d, line count:%d, text size:%d:\r\n%s"; /* ROM 0x7370c4 */
static const char s_fill[] = "fill";     /* ROM 0x78e33c */
static const char s_fill_no_total[] =
    "teleprompt fill: run 'teleprompt start' first, or pass total_pages\r\n"; /* ROM 0x6fc2b4 */
static const char s_fill_evict[] =
    "teleprompt fill: note page cache holds 20 pages, extra pages will be evicted\r\n"; /* ROM 0x6ef408 */
static const char s_fill_line[] = "P%u-L%u teleprompt test line\n"; /* ROM 0x764130 */
static const char s_fill_done[] = "teleprompt fill: injected %u pages x %u lines\r\n"; /* ROM 0x7370f4 */
static const char s_unknown[] =
    "Unknown teleprompt command. Use 'teleprompt help' for available commands.\r\n"; /* ROM 0x6f5788 */
static const char s_legal[] = "legalregulatory command not implemented\r\n"; /* ROM 0x741ec0 */

int32_t cli_cmd_teleprompt_582448(char *write_buffer, size_t write_buffer_len, const char *command_string);
int32_t cli_cmd_legalregulatory_5827b6(char *write_buffer, size_t write_buffer_len,
                                       const char *command_string);

/* atoi of an optional parameter, or fallback when absent/empty. */
static int32_t tp_optional_int(const char *text, int32_t length, int32_t fallback)
{
    if (text != NULL && length >= 1)
        return atoi_48d868(text);
    return fallback;
}

static void tp_start(const char *command_string, const char *page_text, const char *total_text,
                     const char *lines_text, int32_t lines_length)
{
    g2_teleprompt_cli_start_t *start = &g2_teleprompt_cli_start_200fea14;
    int32_t scroll_length = 0;
    int32_t mode_length = 0;
    const char *scroll_text;
    const char *mode_text;
    int32_t lines;
    int32_t scroll_mode;
    int32_t mode;

    scroll_text = freertos_cli_get_parameter_5848fc(command_string, 5u, &scroll_length);
    mode_text = freertos_cli_get_parameter_5848fc(command_string, 6u, &mode_length);
    lines = tp_optional_int(lines_text, lines_length, TP_DEFAULT_LINES);
    scroll_mode = tp_optional_int(scroll_text, scroll_length, 0);
    mode = tp_optional_int(mode_text, mode_length, TP_DEFAULT_MODE);

    (void)aeabi_memset_43c0e4(start, sizeof(*start), 0);
    start->has_start = 1u;
    start->has_data = 1u;
    start->mode = (uint8_t)mode;
    start->start_page = (uint32_t)atoi_48d868(page_text);
    start->reserved0 = 0u;
    start->total_pages = (uint32_t)atoi_48d868(total_text);
    start->total_lines = start->total_pages * 10u;
    start->width = TP_START_WIDTH;
    start->height = TP_START_HEIGHT;
    start->reserved1 = 0u;
    start->reserved2 = 0u;
    start->lines = (uint32_t)lines;
    start->scroll_mode = (uint8_t)scroll_mode;
    teleprompt_cli_send_control_5823f6(TP_ACTION_START, &start->mode);
    audio_ble_hci_boot_log_4733ee(s_start_log, start->start_page, start->total_pages, lines,
                                  scroll_mode, mode);
}

static void tp_aisync(const char *page_text, const char *line_text, const char *char_text)
{
    g2_teleprompt_cli_aisync_t *sync = &g2_teleprompt_cli_aisync_200fea44;
    g2_teleprompt_cli_pkg_view_t *pkg = &g2_teleprompt_cli_pkg_200fea50;

    (void)aeabi_memset_43c0e4(sync, sizeof(*sync), 0);
    sync->page = (uint32_t)atoi_48d868(page_text);
    sync->line = (uint32_t)atoi_48d868(line_text);
    sync->character = (uint32_t)atoi_48d868(char_text);
    (void)aeabi_memset_43c0e4(pkg, sizeof(*pkg), 0);
    pkg->cmd = TP_CMD_AISYNC;
    g2_teleprompt_cli_magic_20075001++;
    pkg->magic = g2_teleprompt_cli_magic_20075001;
    pkg->which = TP_WHICH_AISYNC;
    *(g2_teleprompt_cli_aisync_t *)(void *)pkg->payload = *sync;
    (void)teleprompt_cli_pb_send_58237a(pkg);
}

static void tp_fill(const char *total_text, int32_t total_length, const char *lines_text,
                    int32_t lines_length)
{
    g2_teleprompt_page_t *page = &g2_teleprompt_cli_page_200fe608;
    g2_teleprompt_cli_pkg_view_t *pkg = &g2_teleprompt_cli_pkg_200fea50;
    uint32_t total = g2_teleprompt_fsm_ctrl.total_pages;
    uint32_t lines = TP_FILL_LINES_MAX;
    uint32_t page_index;
    uint32_t line;
    uint32_t used;
    int32_t n;

    if (total_text != NULL && total_length >= 1)
        total = (uint32_t)atoi_48d868(total_text);
    if (lines_text != NULL && lines_length >= 1)
        lines = (uint32_t)atoi_48d868(lines_text);
    if (lines == 0u || lines > TP_FILL_LINES_MAX)
        lines = TP_FILL_LINES_MAX;
    if (total == 0u) {
        audio_ble_hci_boot_log_4733ee(s_fill_no_total);
        return;
    }
    if (total > TP_FILL_PAGES_CACHED)
        audio_ble_hci_boot_log_4733ee(s_fill_evict);
    for (page_index = 0u; page_index < total; page_index++) {
        (void)aeabi_memset_43c0e4(page, sizeof(*page), 0);
        page->page_id = page_index;
        page->field_04 = lines;
        used = 0u;
        for (line = 0u; line < lines; line++) {
            n = g2_audio_dump_snprintf(&page->text[used], TP_FILL_TEXT_BYTES - used, s_fill_line,
                                       page_index, line);
            if (n < 1 || (uint32_t)n >= TP_FILL_TEXT_BYTES - used)
                break;
            used += (uint32_t)n;
        }
        page->text_size = (uint16_t)used;
        (void)aeabi_memset_43c0e4(pkg, sizeof(*pkg), 0);
        pkg->cmd = TP_CMD_PAGE;
        g2_teleprompt_cli_magic_20075001++;
        pkg->magic = g2_teleprompt_cli_magic_20075001;
        pkg->which = TP_WHICH_PAGE;
        (void)aeabi_memcpy4_439c04(pkg->payload, page, G2_TELEPROMPT_PAGE_SIZE);
        (void)teleprompt_cli_pb_send_58237a(pkg);
        audio_uart_task_delay(TP_FILL_SEND_DELAY);
    }
    audio_ble_hci_boot_log_4733ee(s_fill_done, total, lines);
}

int32_t cli_cmd_teleprompt_582448(char *write_buffer, size_t write_buffer_len, const char *command_string)
{
    int32_t length1 = 0;
    int32_t length2 = 0;
    int32_t length3 = 0;
    int32_t length4 = 0;
    const g2_teleprompt_page_t *cached;
    const char *sub;
    const char *arg2;
    const char *arg3;
    const char *arg4;
    int32_t page_id;

    (void)write_buffer;
    (void)write_buffer_len;
    sub = freertos_cli_get_parameter_5848fc(command_string, 1u, &length1);
    arg2 = freertos_cli_get_parameter_5848fc(command_string, 2u, &length2);
    arg3 = freertos_cli_get_parameter_5848fc(command_string, 3u, &length3);
    arg4 = freertos_cli_get_parameter_5848fc(command_string, 4u, &length4);
    if (sub == NULL || length1 < 1) {
        audio_ble_hci_boot_log_4733ee(s_missing);
        return 0;
    }
    if (audio_ble_hci_vendor_compare_44b610(sub, s_start, 5u) == 0) {
        tp_start(command_string, arg2, arg3, arg4, length4);
    } else if (audio_ble_hci_vendor_compare_44b610(sub, s_stop, 4u) == 0) {
        teleprompt_cli_send_control_5823f6(TP_ACTION_STOP, NULL);
    } else if (audio_ble_hci_vendor_compare_44b610(sub, s_pause, 5u) == 0) {
        teleprompt_cli_send_control_5823f6(TP_ACTION_PAUSE, NULL);
    } else if (audio_ble_hci_vendor_compare_44b610(sub, s_resume, 6u) == 0) {
        teleprompt_cli_send_control_5823f6(TP_ACTION_RESUME, NULL);
    } else if (audio_ble_hci_vendor_compare_44b610(sub, s_aisync, 6u) == 0) {
        tp_aisync(arg2, arg3, arg4);
    } else if (audio_ble_hci_vendor_compare_44b610(sub, s_page, 4u) == 0) {
        page_id = atoi_48d868(arg2);
        cached = teleprompt_page_data_get((uint32_t)page_id);
        if (cached == NULL) {
            audio_ble_hci_boot_log_4733ee(s_page_missing, page_id);
            return 0;
        }
        audio_ble_hci_boot_log_4733ee(s_page_dump, cached->page_id, cached->field_04, cached->text_size,
                                      cached->text);
    } else if (audio_ble_hci_vendor_compare_44b610(sub, s_fill, 4u) == 0) {
        tp_fill(arg2, length2, arg3, length3);
    } else {
        audio_ble_hci_boot_log_4733ee(s_unknown);
    }
    return 0;
}

/* Placeholder in stock: logs and opens display app 0x109. */
int32_t cli_cmd_legalregulatory_5827b6(char *write_buffer, size_t write_buffer_len,
                                       const char *command_string)
{
    (void)write_buffer;
    (void)write_buffer_len;
    (void)command_string;
    audio_ble_hci_boot_log_4733ee(s_legal);
    audio_uart_master_display_start(LEGAL_REGULATORY_APP, NULL, 0u, 0u);
    return 0;
}
