/* Teleprompt countdown / auto-scroll timer manager, stock
 * D:\01_workspace\s200_ap510b_iar_git\app\gui\teleprompt\teleprompt_timer_mgr.c
 * (path ROM 0x6f0218, module tag "teleprompt.timer" ROM 0x783eb0).
 * Native 0x588d74..0x58934d; literal pool 0x589350..0x5893ef.
 *
 * Two software timers polled from the UI tick (teleprompt.c event 4) on the
 * master side, both measured in osKernelGetTickCount() ms:
 *  - type 1 countdown: ctrl.countdown_sec before the elapsed-time clock
 *    starts (start timestamp refreshed from the RTC when it expires, then the
 *    auto-scroll timer is started);
 *  - type 2 auto scroll: every ctrl.auto_scroll_ms in auto mode ('A', mode 2)
 *    once the countdown is over, request a 28 px (one line) scroll down unless
 *    paused, busy or scroll-locked.
 * UI state transitions run the rule table ROM 0x783ec4 (5 x {from, to, timer
 * type, action}; 4 = any state; action 1 start, 2 stop, 3 restart):
 *   {0,2,1,start} {1,2,1,start} {2,2,2,start} {any,3,1,stop} {any,3,2,stop}.
 * Per-type start/stop functions come from ROM 0x77c52c ({NULL,NULL},
 * {countdown start, stop}, {auto scroll start, stop}). */
#include <stdint.h>
#include <stddef.h>

#define TP_TIMER_COUNTDOWN    1u
#define TP_TIMER_AUTO_SCROLL  2u
#define TP_TIMER_TYPES        3u
#define TP_TIMER_RULES        5u
#define TP_STATE_ANY          4u
#define TP_UI_STATE_MAIN      2u
#define TP_MODE_AUTO          2u
#define TP_SCROLL_LOCKED      2u
#define TP_LINE_H             0x1c
#define TP_REQ_SCROLL_DOWN    0x0du

enum {
    TP_TIMER_ACTION_NONE = 0u,
    TP_TIMER_ACTION_START = 1u,
    TP_TIMER_ACTION_STOP = 2u,
    TP_TIMER_ACTION_RESTART = 3u,
};

typedef struct {
    uint8_t from;        /* +0 */
    uint8_t to;          /* +1 */
    uint8_t timer_type;  /* +2 */
    uint8_t action;      /* +3 */
} g2_teleprompt_timer_rule_t;

typedef struct {
    void (*start)(void);
    void (*stop)(void);
} g2_teleprompt_timer_ops_t;

/* Teleprompt UI/page-window state (RAM 0x20073068). */
typedef struct {
    uint8_t reserved_00[0x18];
    void *content;              /* +0x18 page scroll container */
    uint8_t reserved_1c[4];
    uint8_t state;              /* +0x20 */
    uint8_t busy;               /* +0x21 */
    uint8_t reserved_22[2];
    uint32_t start_timestamp;   /* +0x24 RTC seconds when the clock starts */
    uint8_t reserved_28[0x18];
    uint32_t paused;            /* +0x40 */
} g2_teleprompt_ui_t;
_Static_assert(offsetof(g2_teleprompt_ui_t, state) == 0x20, "state at +0x20");
_Static_assert(offsetof(g2_teleprompt_ui_t, paused) == 0x40, "paused at +0x40");

/* Teleprompt FSM control block (RAM 0x20109390). */
typedef struct {
    uint8_t reserved_00[4];
    uint8_t mode;               /* +0x04 0 AI, 1 manual, 2 auto */
    uint8_t reserved_05[0x17];
    uint32_t auto_scroll_ms;    /* +0x1c */
    uint32_t countdown_sec;     /* +0x20 */
    uint8_t reserved_24[8];
    uint8_t scroll_mode;        /* +0x2c 2 = locked */
} g2_teleprompt_fsm_ctrl_t;
_Static_assert(offsetof(g2_teleprompt_fsm_ctrl_t, auto_scroll_ms) == 0x1c, "interval at +0x1c");
_Static_assert(offsetof(g2_teleprompt_fsm_ctrl_t, scroll_mode) == 0x2c, "scroll_mode at +0x2c");

extern g2_teleprompt_ui_t g2_teleprompt_ui_window;               /* RAM 0x20073068 */
extern g2_teleprompt_fsm_ctrl_t g2_teleprompt_fsm_ctrl;          /* RAM 0x20109390 */
extern uint8_t g2_teleprompt_auto_scroll_running_20075029;       /* RAM 0x20075029 */
extern uint8_t g2_teleprompt_countdown_done_2007502a;            /* RAM 0x2007502a */
extern uint8_t g2_teleprompt_countdown_running_2007502b;         /* RAM 0x2007502b */
extern uint32_t g2_teleprompt_countdown_deadline_20074a74;       /* RAM 0x20074a74 */
extern uint32_t g2_teleprompt_auto_scroll_deadline_20074a78;     /* RAM 0x20074a78 */
extern const g2_teleprompt_timer_ops_t g2_teleprompt_timer_ops_77c52c[TP_TIMER_TYPES];      /* ROM 0x77c52c */
extern const g2_teleprompt_timer_rule_t g2_teleprompt_timer_rules_783ec4[TP_TIMER_RULES];   /* ROM 0x783ec4 */

extern uint32_t audio_log_flags(void);                                          /* 0x43d0ce */
extern void audio_log_extended(uint8_t, const char *, const char *, const char *, uint32_t,
                               const char *, ...);                              /* 0x43d574 */
extern uint32_t compress_log_output(uint32_t, const char *, const char *, ...); /* 0x43ce9e */
extern uint32_t osKernelGetTickCount(void);                                     /* 0x4490cc */
extern uint8_t audio_uart_device_role_get(void);                                /* 0x45a568, 1 = master */
extern uint32_t service_time_rtc_refresh(void);                                 /* 0x44a1ea, epoch seconds */
extern int32_t teleprompt_ui_get_scroll_target_y_5548c4(void *obj, int32_t offset, int32_t speed);
extern uint32_t teleprompt_controller_post_589b68(uint8_t event, uint32_t arg);

static const char module_tag[] = "teleprompt.timer"; /* ROM 0x783eb0 */
static const char source_file[] = "D:\\01_workspace\\s200_ap510b_iar_git\\app\\gui\\teleprompt\\teleprompt_timer_mgr.c"; /* ROM 0x6f0218 */

static const char fn_countdown_start[] = "teleprompt_timer_countdown_start"; /* ROM 0x75ae60 */
static const char fn_countdown_stop[] = "teleprompt_timer_countdown_stop"; /* ROM 0x765f30 */
static const char fn_auto_scroll_start[] = "teleprompt_timer_auto_scroll_start"; /* ROM 0x75ae84 */
static const char fn_auto_scroll_stop[] = "teleprompt_timer_auto_scroll_stop"; /* ROM 0x75aea8 */
static const char fn_start_by_config[] = "teleprompt_timer_start_by_config"; /* ROM 0x75aecc */
static const char fn_stop_by_config[] = "teleprompt_timer_stop_by_config"; /* ROM 0x765f50 */
static const char fn_init[] = "teleprompt_timer_mgr_init"; /* ROM 0x772d50 */
static const char fn_deinit[] = "teleprompt_timer_mgr_deinit"; /* ROM 0x772d6c */
static const char fn_process[] = "teleprompt_timer_mgr_process_auto_reflash"; /* ROM 0x744800 */

static const char msg_countdown_start[] = "Countdown timer start %dms"; /* ROM 0x772d34 */
static const char msg_countdown_start_s[] = "[teleprompt.timer]Countdown timer start %dms"; /* ROM 0x7393a4 */
static const char msg_countdown_stop[] = "Countdown timer stop"; /* ROM 0x77c4cc */
static const char msg_countdown_stop_s[] = "[teleprompt.timer]Countdown timer stop"; /* ROM 0x74f08c */
static const char msg_auto_start[] = "Auto scroll timer start"; /* ROM 0x77c4e4 */
static const char msg_auto_start_s[] = "[teleprompt.timer]Auto scroll timer start"; /* ROM 0x74477c */
static const char msg_auto_stop[] = "Auto scroll timer stop"; /* ROM 0x77c4fc */
static const char msg_auto_stop_s[] = "[teleprompt.timer]Auto scroll timer stop"; /* ROM 0x7447a8 */
static const char msg_invalid_type[] = "Invalid timer type: %d"; /* ROM 0x77c514 */
static const char msg_invalid_type_s[] = "[teleprompt.timer]Invalid timer type: %d"; /* ROM 0x7447d4 */
static const char msg_no_start[] = "No start function configured for timer type: %d"; /* ROM 0x7393d4 */
static const char msg_no_start_s[] = "[teleprompt.timer]No start function configured for timer type: %d"; /* ROM 0x706838 */
static const char msg_no_stop[] = "No stop function configured for timer type: %d"; /* ROM 0x739404 */
static const char msg_no_stop_s[] = "[teleprompt.timer]No stop function configured for timer type: %d"; /* ROM 0x70687c */
static const char msg_init[] = "Teleprompt timer manager initialized"; /* ROM 0x74f0b4 */
static const char msg_init_s[] = "[teleprompt.timer]Teleprompt timer manager initialized"; /* ROM 0x723e00 */
static const char msg_deinit[] = "Teleprompt timer manager deinitialized"; /* ROM 0x74f0dc */
static const char msg_deinit_s[] = "[teleprompt.timer]Teleprompt timer manager deinitialized"; /* ROM 0x7196fc */
static const char msg_countdown_end[] = "Countdown end, start elapsed time = %u"; /* ROM 0x74f104 */
static const char msg_countdown_end_s[] = "[teleprompt.timer]Countdown end, start elapsed time = %u"; /* ROM 0x719738 */

#define TIMER_LOG(level, fn, line, cflags, name, ...)                                              \
    do {                                                                                          \
        if ((audio_log_flags() & 2u) != 0u)                                                       \
            audio_log_extended((level), module_tag, source_file, (fn), (line), name,              \
                               ##__VA_ARGS__);                                                    \
        if ((audio_log_flags() & 1u) != 0u || (audio_log_flags() & 4u) != 0u)                     \
            (void)compress_log_output((cflags), name##_s, name##_s, ##__VA_ARGS__);              \
    } while (0)

/* Only in the main page state. */
void teleprompt_timer_countdown_start_588d74(void)
{
    uint32_t ms;

    if (g2_teleprompt_ui_window.state != TP_UI_STATE_MAIN)
        return;
    ms = g2_teleprompt_fsm_ctrl.countdown_sec * 1000u;
    TIMER_LOG(3u, fn_countdown_start, 0x3bu, 0x0c400000u, msg_countdown_start, ms);
    g2_teleprompt_countdown_done_2007502a = 0u;
    g2_teleprompt_countdown_running_2007502b = 1u;
    g2_teleprompt_countdown_deadline_20074a74 = ms + osKernelGetTickCount();
}

void teleprompt_timer_countdown_stop_588df4(void)
{
    TIMER_LOG(3u, fn_countdown_stop, 0x46u, 0x0c000000u, msg_countdown_stop);
    g2_teleprompt_countdown_running_2007502b = 0u;
}

/* Auto mode in the main page, not yet running, interval set, countdown over. */
void teleprompt_timer_auto_scroll_start_588e42(void)
{
    if (g2_teleprompt_ui_window.state != TP_UI_STATE_MAIN ||
        g2_teleprompt_fsm_ctrl.mode != TP_MODE_AUTO ||
        g2_teleprompt_auto_scroll_running_20075029 == 1u ||
        g2_teleprompt_fsm_ctrl.auto_scroll_ms == 0u ||
        g2_teleprompt_countdown_done_2007502a != 1u)
        return;
    TIMER_LOG(3u, fn_auto_scroll_start, 0x5au, 0x0c000000u, msg_auto_start);
    g2_teleprompt_auto_scroll_running_20075029 = 1u;
    g2_teleprompt_auto_scroll_deadline_20074a78 =
        g2_teleprompt_fsm_ctrl.auto_scroll_ms + osKernelGetTickCount();
}

void teleprompt_timer_auto_scroll_stop_588ecc(void)
{
    TIMER_LOG(3u, fn_auto_scroll_stop, 0x64u, 0x0c000000u, msg_auto_stop);
    g2_teleprompt_auto_scroll_running_20075029 = 0u;
}

void teleprompt_timer_start_by_config_588f1a(uint8_t type)
{
    if (type >= TP_TIMER_TYPES || type == 0u) {
        TIMER_LOG(1u, fn_start_by_config, 0x9bu, 0x04400000u, msg_invalid_type, type);
        return;
    }
    if (g2_teleprompt_timer_ops_77c52c[type].start == NULL) {
        TIMER_LOG(1u, fn_start_by_config, 0xa2u, 0x04400000u, msg_no_start, type);
        return;
    }
    g2_teleprompt_timer_ops_77c52c[type].start();
}

void teleprompt_timer_stop_by_config_588fe4(uint8_t type)
{
    if (type >= TP_TIMER_TYPES || type == 0u) {
        TIMER_LOG(1u, fn_stop_by_config, 0xadu, 0x04400000u, msg_invalid_type, type);
        return;
    }
    if (g2_teleprompt_timer_ops_77c52c[type].stop == NULL) {
        TIMER_LOG(1u, fn_stop_by_config, 0xb4u, 0x04400000u, msg_no_stop, type);
        return;
    }
    g2_teleprompt_timer_ops_77c52c[type].stop();
}

void teleprompt_timer_apply_action_5890ae(uint8_t type, uint8_t action)
{
    if (action == TP_TIMER_ACTION_START) {
        teleprompt_timer_start_by_config_588f1a(type);
    } else if (action == TP_TIMER_ACTION_NONE) {
        /* nothing */
    } else if (action == TP_TIMER_ACTION_RESTART) {
        teleprompt_timer_stop_by_config_588fe4(type);
        teleprompt_timer_start_by_config_588f1a(type);
    } else if (action < TP_TIMER_ACTION_RESTART) {
        teleprompt_timer_stop_by_config_588fe4(type);
    }
}

void teleprompt_timer_rule_apply_5890ea(const g2_teleprompt_timer_rule_t *rule)
{
    teleprompt_timer_apply_action_5890ae(rule->timer_type, rule->action);
}

/* A rule with both ends "any" never matches; otherwise each end must equal
 * the transition state or be "any". */
uint8_t teleprompt_timer_rule_match_5890f6(const g2_teleprompt_timer_rule_t *rule, uint8_t from,
                                           uint8_t to)
{
    uint8_t from_ok;
    uint8_t to_ok;

    if (rule->from == TP_STATE_ANY && rule->to == TP_STATE_ANY)
        return 0u;
    if (rule->from == from && rule->to == to)
        return 1u;
    from_ok = (rule->from == from || rule->from == TP_STATE_ANY) ? 1u : 0u;
    to_ok = (rule->to == to || rule->to == TP_STATE_ANY) ? 1u : 0u;
    return from_ok & to_ok;
}

void teleprompt_timer_mgr_init_589152(void)
{
    if (audio_uart_device_role_get() != 1u)
        return;
    g2_teleprompt_auto_scroll_running_20075029 = 0u;
    g2_teleprompt_countdown_done_2007502a = 0u;
    g2_teleprompt_countdown_running_2007502b = 0u;
    g2_teleprompt_countdown_deadline_20074a74 = 0u;
    g2_teleprompt_auto_scroll_deadline_20074a78 = 0u;
    TIMER_LOG(4u, fn_init, 0x110u, 0x10000000u, msg_init);
}

void teleprompt_timer_mgr_deinit_5891b6(void)
{
    if (audio_uart_device_role_get() != 1u)
        return;
    g2_teleprompt_auto_scroll_running_20075029 = 0u;
    g2_teleprompt_countdown_done_2007502a = 0u;
    g2_teleprompt_countdown_running_2007502b = 0u;
    g2_teleprompt_countdown_deadline_20074a74 = 0u;
    g2_teleprompt_auto_scroll_deadline_20074a78 = 0u;
    TIMER_LOG(4u, fn_deinit, 0x120u, 0x10000000u, msg_deinit);
    for (int32_t type = TP_TIMER_COUNTDOWN; type < (int32_t)TP_TIMER_TYPES; type++)
        teleprompt_timer_stop_by_config_588fe4((uint8_t)type);
}

/* Polled from the UI tick. Deadlines compare as signed tick differences. */
void teleprompt_timer_mgr_process_auto_reflash_58922c(void)
{
    g2_teleprompt_ui_t *ui = &g2_teleprompt_ui_window;
    g2_teleprompt_fsm_ctrl_t *ctrl = &g2_teleprompt_fsm_ctrl;
    uint32_t now;

    if (audio_uart_device_role_get() != 1u)
        return;
    now = osKernelGetTickCount();
    if (g2_teleprompt_countdown_running_2007502b != 0u &&
        (int32_t)(now - g2_teleprompt_countdown_deadline_20074a74) >= 0) {
        g2_teleprompt_countdown_running_2007502b = 0u;
        g2_teleprompt_countdown_done_2007502a = 1u;
        ui->start_timestamp = service_time_rtc_refresh();
        TIMER_LOG(3u, fn_process, 0x138u, 0x0c400000u, msg_countdown_end, ui->start_timestamp);
        teleprompt_timer_start_by_config_588f1a(TP_TIMER_AUTO_SCROLL);
    }
    if (g2_teleprompt_auto_scroll_running_20075029 != 0u && ui->state == TP_UI_STATE_MAIN &&
        ctrl->mode == TP_MODE_AUTO && ctrl->auto_scroll_ms != 0u &&
        g2_teleprompt_countdown_done_2007502a == 1u &&
        (int32_t)(now - g2_teleprompt_auto_scroll_deadline_20074a78) >= 0) {
        if (ui->paused == 0u && ui->busy == 0u && ctrl->scroll_mode != TP_SCROLL_LOCKED) {
            int32_t y = teleprompt_ui_get_scroll_target_y_5548c4(ui->content, TP_LINE_H, 0);
            (void)teleprompt_controller_post_589b68(TP_REQ_SCROLL_DOWN, (uint32_t)y);
        }
        g2_teleprompt_auto_scroll_deadline_20074a78 = ctrl->auto_scroll_ms + now;
    }
}

/* Called by the UI FSM on every state change (from -> to). */
void teleprompt_timer_mgr_on_state_change_58930a(uint8_t from, uint8_t to)
{
    uint8_t matched = 0u;

    if (audio_uart_device_role_get() != 1u)
        return;
    for (uint32_t i = 0u; i < TP_TIMER_RULES; i++) {
        const g2_teleprompt_timer_rule_t *rule = &g2_teleprompt_timer_rules_783ec4[i];
        if (teleprompt_timer_rule_match_5890f6(rule, from, to) != 0u) {
            teleprompt_timer_rule_apply_5890ea(rule);
            matched = 1u;
        }
    }
    (void)matched; /* computed and tested but unused in stock */
}
