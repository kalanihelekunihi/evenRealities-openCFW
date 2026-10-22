/* Teleprompt FSM dispatcher and app-control actions, stock
 * D:\01_workspace\s200_ap510b_iar_git\app\gui\teleprompt\teleprompt_fsm.c.
 * Native 0x58c874..0x58cfff (the page_data, ai_sync, scroll_sync and
 * heartbeat actions at 0x58d000..0x58d40f are app/p-09-teleprompt);
 * literal pools 0x58d2d0..0x58d2f3 and 0x58d410..0x58d4af; action table
 * ROM 0x74ef4c; event-name table RAM 0x20003dc0 (.data).
 *
 * teleprompt_machine_handler_58c89e(event, data, len) logs the event and
 * runs action[event](ctrl, data, len); the actions post follow-up work to
 * the teleprompt controller (0x589b68) as (event, arg). */
#include <stddef.h>
#include <stdint.h>
#include "g2_teleprompt_page_data.h"

#define TELEPROMPT_EVENT_COUNT 10u
#define DEVICE_ROLE_MASTER 1u
#define AUDIO_USER_TELEPROMPT 2u

enum {
    TELEPROMPT_UI_IDLE = 0u,
    TELEPROMPT_UI_MENU = 1u,
    TELEPROMPT_UI_MAIN = 2u,
};

/* Controller events (teleprompt_controller_post_589b68). */
enum {
    TELEPROMPT_CTRL_SHOW_MAIN = 2u,
    TELEPROMPT_CTRL_FILE_LIST = 3u,
    TELEPROMPT_CTRL_PAUSE = 7u,
    TELEPROMPT_CTRL_RESUME = 8u,
    TELEPROMPT_CTRL_EXIT = 10u,
};

/* Document parameters sent with APP_START (0x2c bytes). */
typedef struct {
    uint8_t mode;               /* +0x00 0 AI, 1 manual, 2 auto */
    uint8_t reserved_01[3];
    uint32_t start_page;        /* +0x04 */
    uint32_t start_line;        /* +0x08 */
    uint32_t total_pages;       /* +0x0c */
    uint32_t total_lines;       /* +0x10 */
    uint32_t display_width;     /* +0x14 px, default 567 */
    uint32_t scroll_interval_ms;/* +0x18 >= 800 */
    uint32_t countdown_seconds; /* +0x1c */
    uint32_t use_audio;         /* +0x20 acquire the audio path */
    uint32_t display_lines;     /* +0x24 5..9 */
    uint8_t scroll_mode;        /* +0x28 0..2 */
    uint8_t reserved_29[3];
} g2_teleprompt_config_t;
_Static_assert(sizeof(g2_teleprompt_config_t) == 0x2c, "stock config copy is 0x2c bytes");

/* Decoded APP_START control payload. */
typedef struct {
    uint8_t reserved_00;
    uint8_t has_config;         /* +0x01 */
    uint8_t reserved_02[2];
    g2_teleprompt_config_t config; /* +0x04 */
} g2_teleprompt_app_start_t;

/* FSM control block (RAM 0x20109390, 0x44 bytes; cleared on APP_EXIT). */
typedef struct {
    uint8_t running;            /* +0x00 */
    uint8_t reserved_01[3];
    g2_teleprompt_config_t config; /* +0x04 */
    uint32_t ai_sync[3];        /* +0x30 page, line, char of the last AI sync */
    uint8_t reserved_3c;
    uint8_t jump_pending;       /* +0x3d */
    uint8_t reserved_3e[2];
    uint32_t jump_page;         /* +0x40 */
} g2_teleprompt_fsm_ctrl_t;
_Static_assert(offsetof(g2_teleprompt_fsm_ctrl_t, config.scroll_mode) == 0x2c, "scroll_mode at +0x2c");
_Static_assert(offsetof(g2_teleprompt_fsm_ctrl_t, jump_page) == 0x40, "jump_page at +0x40");
_Static_assert(sizeof(g2_teleprompt_fsm_ctrl_t) == 0x44, "stock memset size");

typedef int32_t (*teleprompt_action_t)(g2_teleprompt_fsm_ctrl_t *ctrl, const void *data, uint32_t len);

g2_teleprompt_fsm_ctrl_t g2_teleprompt_fsm_ctrl; /* RAM 0x20109390 */

extern uint8_t teleprompt_ui_state_get_5540b2(void);
extern const char *teleprompt_ui_state_name_5540bc(uint8_t state);
extern uint32_t teleprompt_controller_post_589b68(uint8_t event, uint32_t arg);
extern uint32_t display_driver_uled_mode_45a568(void);        /* device role, 1 = master */
extern uint32_t audio_system_alert_command_45a8ee(uint32_t target, uint32_t payload, uint32_t length, uint32_t value);
extern void audio_uart_ring_wear_persist_48eb32(uint32_t key, uint32_t length, const void *payload); /* event report */
extern int32_t AUDM_appAcquire(uint32_t user);                /* 0x54f380 */
extern void *aeabi_memset_43c0e4(void *dst, uint32_t len, int32_t value);
extern void *audio_queue_copy_bytes(void *dst, const void *src, uint32_t len); /* 0x439be4 memcpy */
extern uint32_t audio_log_flags(void); /* 0x43d0ce */
extern void audio_log_extended(uint8_t, const char *, const char *, const char *, uint32_t, const char *, ...); /* 0x43d574 */
extern uint32_t compress_log_output(uint32_t, const char *, const char *, ...); /* 0x43ce9e */

/* Actions in app/p-09-teleprompt (two-argument definitions; the third
 * register is ignored). */
extern int32_t teleprompt_action_page_data_58d000(g2_teleprompt_fsm_ctrl_t *ctrl, const void *page_data);
extern int32_t teleprompt_action_ai_sync_58d0d0(g2_teleprompt_fsm_ctrl_t *ctrl, const void *sync);
extern int32_t teleprompt_action_scroll_sync_58d228(g2_teleprompt_fsm_ctrl_t *ctrl, const void *sync);
extern int32_t teleprompt_action_heartbeat_58d2f4(g2_teleprompt_fsm_ctrl_t *ctrl, const void *hb);

int32_t teleprompt_action_app_start_58ca2a(g2_teleprompt_fsm_ctrl_t *ctrl, const void *data, uint32_t len);
int32_t teleprompt_action_app_pause_58ceb4(g2_teleprompt_fsm_ctrl_t *ctrl, const void *data, uint32_t len);
int32_t teleprompt_action_app_resume_58cec2(g2_teleprompt_fsm_ctrl_t *ctrl, const void *data, uint32_t len);
int32_t teleprompt_action_app_exit_58cf12(g2_teleprompt_fsm_ctrl_t *ctrl, const void *data, uint32_t len);
int32_t teleprompt_action_file_list_58cf50(g2_teleprompt_fsm_ctrl_t *ctrl, const void *data, uint32_t len);

#define P09_ACTION(fn) ((teleprompt_action_t)(void (*)(void))(fn))

static const teleprompt_action_t teleprompt_actions[TELEPROMPT_EVENT_COUNT] = { /* ROM 0x74ef4c */
    NULL,
    teleprompt_action_app_start_58ca2a,
    teleprompt_action_app_pause_58ceb4,
    teleprompt_action_app_resume_58cec2,
    teleprompt_action_app_exit_58cf12,
    teleprompt_action_file_list_58cf50,
    P09_ACTION(teleprompt_action_page_data_58d000),
    P09_ACTION(teleprompt_action_ai_sync_58d0d0),
    P09_ACTION(teleprompt_action_scroll_sync_58d228),
    P09_ACTION(teleprompt_action_heartbeat_58d2f4),
};

static const char ev_none[] = "TELEPROMPT_EVENT_NONE"; /* ROM 0x77c454 */
static const char ev_app_start[] = "TELEPROMPT_EVENT_APP_START"; /* ROM 0x772a5c */
static const char ev_app_pause[] = "TELEPROMPT_EVENT_APP_PAUSE"; /* ROM 0x772a78 */
static const char ev_app_resume[] = "TELEPROMPT_EVENT_APP_RESUME"; /* ROM 0x772a94 */
static const char ev_app_exit[] = "TELEPROMPT_EVENT_APP_EXIT"; /* ROM 0x772ab0 */
static const char ev_file_list[] = "TELEPROMPT_EVENT_FILE_LIST"; /* ROM 0x772acc */
static const char ev_page_data[] = "TELEPROMPT_EVENT_PAGE_DATA"; /* ROM 0x772ae8 */
static const char ev_ai_sync[] = "TELEPROMPT_EVENT_AI_SYNC"; /* ROM 0x772b04 */
static const char ev_scroll_sync[] = "TELEPROMPT_EVENT_SCROLL_SYNC"; /* ROM 0x765d30 */
static const char ev_heartbeat[] = "TELEPROMPT_EVENT_HEARTBEAT"; /* ROM 0x772b20 */

static const char *g2_teleprompt_event_names[TELEPROMPT_EVENT_COUNT] = { /* RAM 0x20003dc0 */
    ev_none, ev_app_start, ev_app_pause, ev_app_resume, ev_app_exit,
    ev_file_list, ev_page_data, ev_ai_sync, ev_scroll_sync, ev_heartbeat,
};

/* Two-word event reports sent to the phone (ROM 0x78eae4 / 0x78eaec). */
#define TELEPROMPT_REPORT_START_KEY 0x40101u
#define TELEPROMPT_REPORT_EXIT_KEY 0x40102u
static const uint32_t teleprompt_report_start[2] = { 3u, 2u }; /* ROM 0x78eae4 */
static const uint32_t teleprompt_report_exit[2] = { 3u, 2u };  /* ROM 0x78eaec */

static const char module_tag[] = "teleprompt.fsm"; /* ROM 0x789730 */
static const char source_file[] = "D:\\01_workspace\\s200_ap510b_iar_git\\app\\gui\\teleprompt\\teleprompt_fsm.c"; /* ROM 0x6fd8ec */

static const char fn_handler[] = "teleprompt_machine_handler"; /* ROM 0x772b3c */
static const char ev_invalid[] = "event is invalid"; /* ROM 0x783e10 */
static const char ev_invalid_c[] = "[teleprompt.fsm]event is invalid"; /* ROM 0x75abfc */
static const char ev_recv[] = "recv event [%d|%s]"; /* ROM 0x783e24 */
static const char ev_recv_c[] = "[teleprompt.fsm]recv event [%d|%s]"; /* ROM 0x75ac20 */
static const char ev_no_action[] = "event[%d|%s] no match action"; /* ROM 0x765d50 */
static const char ev_no_action_c[] = "[teleprompt.fsm]event[%d|%s] no match action"; /* ROM 0x739104 */
static const char ev_failed[] = "action execution failed"; /* ROM 0x77c484 */
static const char ev_failed_c[] = "[teleprompt.fsm]action execution failed"; /* ROM 0x74ef24 */

static const char fn_app_start[] = "teleprompt_action_app_start"; /* ROM 0x772b58 */
static const char st_null[] = "ctrl is NULL"; /* ROM 0x789740 */
static const char st_null_c[] = "[teleprompt.fsm]ctrl is NULL"; /* ROM 0x765d70 */
static const char st_running[] = "teleprompt already running (MAIN), treat duplicate START as success"; /* ROM 0x70676c */
static const char st_running_c[] = "[teleprompt.fsm]teleprompt already running (MAIN), treat duplicate START as success"; /* ROM 0x6ea27c */
static const char st_bad_state[] = "teleprompt ui state is invalid, no need to start: [%d|%s]"; /* ROM 0x7193f0 */
static const char st_bad_state_c[] = "[teleprompt.fsm]teleprompt ui state is invalid, no need to start: [%d|%s]"; /* ROM 0x6f67dc */
static const char st_config[] = "mode = %d, start_page = %d, start_line = %d,total_pages = %d, total_lines = %d, display_width = %d,scroll_interval_ms = %d, countdown_seconds = %d, use_audio = %d,display_lines = %d, scroll_mode = %d"; /* ROM 0x6d1540 */
static const char st_config_c[] = "[teleprompt.fsm]mode = %d, start_page = %d, start_line = %d,total_pages = %d, total_lines = %d, display_width = %d,scroll_interval_ms = %d, countdown_seconds = %d, use_audio = %d,display_lines = %d, scroll_mode = %d"; /* ROM 0x6d0d1c */
static const char st_mode[] = "mode is invalid, set to %d"; /* ROM 0x772b74 */
static const char st_mode_c[] = "[teleprompt.fsm]mode is invalid, set to %d"; /* ROM 0x744514 */
static const char st_page[] = "start_page_id is invalid, set to %d"; /* ROM 0x75ac44 */
static const char st_page_c[] = "[teleprompt.fsm]start_page_id is invalid, set to %d"; /* ROM 0x72e594 */
static const char st_line[] = "start_line_id is invalid, set to %d"; /* ROM 0x75ac68 */
static const char st_line_c[] = "[teleprompt.fsm]start_line_id is invalid, set to %d"; /* ROM 0x72e5c8 */
static const char st_width[] = "display_width is invalid, set to %d"; /* ROM 0x75ac8c */
static const char st_width_c[] = "[teleprompt.fsm]display_width is invalid, set to %d"; /* ROM 0x72e5fc */
static const char st_lines[] = "display_lines is invalid, set to %d"; /* ROM 0x75acb0 */
static const char st_lines_c[] = "[teleprompt.fsm]display_lines is invalid, set to %d"; /* ROM 0x72e630 */
static const char st_scroll[] = "scroll_mode is invalid, set to %d"; /* ROM 0x75acd4 */
static const char st_scroll_c[] = "[teleprompt.fsm]scroll_mode is invalid, set to %d"; /* ROM 0x72e664 */
static const char st_interval[] = "scroll_interval_ms is invalid, set to %d"; /* ROM 0x744540 */
static const char st_interval_c[] = "[teleprompt.fsm]scroll_interval_ms is invalid, set to %d"; /* ROM 0x71942c */

static const char fn_app_resume[] = "teleprompt_action_app_resume"; /* ROM 0x765d90 */
static const char resume_msg[] = "teleprompt_action_resume"; /* ROM 0x772b90 */
static const char resume_msg_c[] = "[teleprompt.fsm]teleprompt_action_resume"; /* ROM 0x74456c */

static const char fn_file_list[] = "teleprompt_action_file_list"; /* ROM 0x772bac */
static const char fl_null[] = "file_list is NULL"; /* ROM 0x783e38 */
static const char fl_null_c[] = "[teleprompt.fsm]file_list is NULL"; /* ROM 0x75acf8 */
static const char fl_count[] = "file_count=%d"; /* ROM 0x789750 */
static const char fl_count_c[] = "[teleprompt.fsm]file_count=%d"; /* ROM 0x765db0 */

#define TP_LOG(level, fn, line, msg, cflags, cmsg, ...)                                      \
    do {                                                                                     \
        if (audio_log_flags() & 2u)                                                          \
            audio_log_extended((level), module_tag, source_file, (fn), (line), (msg), ##__VA_ARGS__); \
        if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))                            \
            (void)compress_log_output((cflags), (cmsg), (cmsg), ##__VA_ARGS__);              \
    } while (0)

void teleprompt_fsm_jump_set_58c874(uint32_t page)
{
    g2_teleprompt_fsm_ctrl.jump_pending = 1u;
    g2_teleprompt_fsm_ctrl.jump_page = page;
}

void teleprompt_fsm_jump_clear_58c882(void)
{
    g2_teleprompt_fsm_ctrl.jump_pending = 0u;
    g2_teleprompt_fsm_ctrl.jump_page = 0u;
}

const char *teleprompt_event_name_58c892(uint8_t event)
{
    return g2_teleprompt_event_names[event];
}

int32_t teleprompt_machine_handler_58c89e(uint8_t event, const void *data, uint32_t len)
{
    if (event >= TELEPROMPT_EVENT_COUNT) {
        TP_LOG(1u, fn_handler, 0x60u, ev_invalid, 0x04000000u, ev_invalid_c);
        return -1;
    }
    if (audio_log_flags() & 2u)
        audio_log_extended(3u, module_tag, source_file, fn_handler, 100u, ev_recv, event,
                           teleprompt_event_name_58c892(event));
    if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
        (void)compress_log_output(0x0c800000u, ev_recv_c, ev_recv_c, event, teleprompt_event_name_58c892(event));

    teleprompt_action_t action = teleprompt_actions[event];
    if (action == NULL) {
        if (audio_log_flags() & 2u)
            audio_log_extended(2u, module_tag, source_file, fn_handler, 0x6bu, ev_no_action, event,
                               teleprompt_event_name_58c892(event));
        if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
            (void)compress_log_output(0x08800000u, ev_no_action_c, ev_no_action_c, event,
                                      teleprompt_event_name_58c892(event));
        return -1;
    }
    int32_t ret = action(&g2_teleprompt_fsm_ctrl, data, len);
    if (ret != 0)
        TP_LOG(2u, fn_handler, 0x72u, ev_failed, 0x08000000u, ev_failed_c);
    return ret;
}

/* Starts the session from idle (report + system alert on the master arm) or
 * from the file menu (show the main page), copies and sanitises the
 * document parameters. A START while already on the main page succeeds. */
int32_t teleprompt_action_app_start_58ca2a(g2_teleprompt_fsm_ctrl_t *ctrl, const void *data, uint32_t len)
{
    const g2_teleprompt_app_start_t *start = data;
    (void)len;

    if (start == NULL) {
        TP_LOG(1u, fn_app_start, 0x85u, st_null, 0x04000000u, st_null_c);
        return -1;
    }

    uint8_t state = teleprompt_ui_state_get_5540b2();
    if (state == TELEPROMPT_UI_IDLE) {
        if (display_driver_uled_mode_45a568() == DEVICE_ROLE_MASTER) {
            uint32_t report[2] = { teleprompt_report_start[0], teleprompt_report_start[1] };
            audio_uart_ring_wear_persist_48eb32(TELEPROMPT_REPORT_START_KEY, 2u, report);
        }
        if (display_driver_uled_mode_45a568() == DEVICE_ROLE_MASTER)
            (void)audio_system_alert_command_45a8ee(6u, 0u, 0u, 500u);
    } else if (state == TELEPROMPT_UI_MENU) {
        (void)teleprompt_controller_post_589b68(TELEPROMPT_CTRL_SHOW_MAIN, 0u);
    } else if (state == TELEPROMPT_UI_MAIN) {
        TP_LOG(2u, fn_app_start, 0x96u, st_running, 0x08000000u, st_running_c);
        return 0;
    } else {
        if (audio_log_flags() & 2u)
            audio_log_extended(1u, module_tag, source_file, fn_app_start, 0x99u, st_bad_state, state,
                               teleprompt_ui_state_name_5540bc(state));
        if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
            (void)compress_log_output(0x04800000u, st_bad_state_c, st_bad_state_c, state,
                                      teleprompt_ui_state_name_5540bc(state));
        return -1;
    }

    ctrl->running = 1u;
    teleprompt_fsm_jump_clear_58c882();

    g2_teleprompt_config_t *cfg = &ctrl->config;
    if (start != NULL && start->has_config != 0u) {
        (void)audio_queue_copy_bytes(cfg, &start->config, sizeof *cfg);
        if (audio_log_flags() & 2u)
            audio_log_extended(3u, module_tag, source_file, fn_app_start, 0xaau, st_config, cfg->mode,
                               cfg->start_page, cfg->start_line, cfg->total_pages, cfg->total_lines,
                               cfg->display_width, cfg->scroll_interval_ms, cfg->countdown_seconds,
                               cfg->use_audio, cfg->display_lines, cfg->scroll_mode);
        /* Eleven arguments overflow the log macro's 4-bit count field; stock
         * encodes the last argument (scroll_mode & 0xf) as the count. */
        if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
            (void)compress_log_output(((uint32_t)(cfg->scroll_mode & 0xfu) << 22) | 0x0c000000u, st_config_c,
                                      st_config_c, cfg->mode, cfg->start_page, cfg->start_line,
                                      cfg->total_pages, cfg->total_lines, cfg->display_width,
                                      cfg->scroll_interval_ms, cfg->countdown_seconds, cfg->use_audio,
                                      cfg->display_lines, cfg->scroll_mode);
    }

    if (cfg->mode > 2u) {
        cfg->mode = 1u;
        TP_LOG(2u, fn_app_start, 0xb0u, st_mode, 0x08400000u, st_mode_c, cfg->mode);
    }
    if (cfg->start_page > cfg->total_pages - 1u) {
        cfg->start_page = 0u;
        TP_LOG(2u, fn_app_start, 0xb5u, st_page, 0x08400000u, st_page_c, cfg->start_page);
    }
    if (cfg->start_line > 30u) {
        cfg->start_line = 0u;
        TP_LOG(2u, fn_app_start, 0xbau, st_line, 0x08400000u, st_line_c, cfg->start_line);
    }
    if (cfg->display_width == 0u) {
        cfg->display_width = 567u;
        TP_LOG(2u, fn_app_start, 0xbfu, st_width, 0x08400000u, st_width_c, cfg->display_width);
    }
    if (cfg->display_lines - 5u > 4u) {
        cfg->display_lines = 5u;
        TP_LOG(2u, fn_app_start, 0xc5u, st_lines, 0x08400000u, st_lines_c, cfg->display_lines);
    }
    if (cfg->scroll_mode > 2u) {
        cfg->scroll_mode = 0u;
        TP_LOG(2u, fn_app_start, 0xcbu, st_scroll, 0x08400000u, st_scroll_c, cfg->scroll_mode);
    }
    if (cfg->scroll_interval_ms < 800u) {
        cfg->scroll_interval_ms = 800u;
        TP_LOG(2u, fn_app_start, 0xd0u, st_interval, 0x08400000u, st_interval_c, cfg->scroll_interval_ms);
    }
    if (cfg->use_audio != 0u)
        (void)AUDM_appAcquire(AUDIO_USER_TELEPROMPT);
    return 0;
}

int32_t teleprompt_action_app_pause_58ceb4(g2_teleprompt_fsm_ctrl_t *ctrl, const void *data, uint32_t len)
{
    (void)ctrl;
    (void)data;
    (void)len;
    (void)teleprompt_controller_post_589b68(TELEPROMPT_CTRL_PAUSE, 0u);
    return 0;
}

int32_t teleprompt_action_app_resume_58cec2(g2_teleprompt_fsm_ctrl_t *ctrl, const void *data, uint32_t len)
{
    (void)ctrl;
    (void)data;
    (void)len;
    TP_LOG(4u, fn_app_resume, 0xefu, resume_msg, 0x10000000u, resume_msg_c);
    (void)teleprompt_controller_post_589b68(TELEPROMPT_CTRL_RESUME, 0u);
    return 0;
}

int32_t teleprompt_action_app_exit_58cf12(g2_teleprompt_fsm_ctrl_t *ctrl, const void *data, uint32_t len)
{
    (void)ctrl;
    (void)data;
    (void)len;
    (void)aeabi_memset_43c0e4(&g2_teleprompt_fsm_ctrl, sizeof g2_teleprompt_fsm_ctrl, 0);
    if (display_driver_uled_mode_45a568() == DEVICE_ROLE_MASTER) {
        uint32_t report[2] = { teleprompt_report_exit[0], teleprompt_report_exit[1] };
        audio_uart_ring_wear_persist_48eb32(TELEPROMPT_REPORT_EXIT_KEY, 2u, report);
    }
    (void)teleprompt_controller_post_589b68(TELEPROMPT_CTRL_EXIT, 0u);
    return 0;
}

int32_t teleprompt_action_file_list_58cf50(g2_teleprompt_fsm_ctrl_t *ctrl, const void *data, uint32_t len)
{
    (void)ctrl;
    (void)len;
    if (data == NULL) {
        TP_LOG(1u, fn_file_list, 0x10fu, fl_null, 0x04000000u, fl_null_c);
        return -1;
    }
    uint32_t count = *(const uint16_t *)data;
    TP_LOG(3u, fn_file_list, 0x113u, fl_count, 0x0c400000u, fl_count_c, count);
    teleprompt_file_list_update(data);
    (void)teleprompt_controller_post_589b68(TELEPROMPT_CTRL_FILE_LIST, 0u);
    return 0;
}
