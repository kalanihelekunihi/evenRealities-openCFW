/* UI display-thread command handlers, stock
 * D:\01_workspace\s200_ap510b_iar_git\framework\sync\display_thread.c.
 * Native 0x44264e..0x442ba7 (ReStartCommandDataHandler),
 * 0x442ba8..0x442cc7 (getStartUpAppID) and 0x442d86..0x443479
 * (inputEventDataHandler); literal pools 0x442cd4..0x442d60 and
 * 0x443480..0x4437cc.
 *
 * ui_display_thread_handler (display-thread/display_thread.c, 0x4437e0) takes
 * 12-byte queue messages {u8 type; u32 app_id @+4; u32 length @+8} and copies
 * the payload from the display ring into a 0x2800-byte buffer. Message types:
 * 2 start / restart (ReStartCommandDataHandler once running), 3 app data,
 * 5 exit, 7 input event (inputEventDataHandler), 8 close all. Thread states:
 * 0 idle, 1 running, 2 closing.
 *
 * Input event payload: u16 key @+0, u32 event type @+2, u32 value @+6
 * (or s16 x @+6, s16 y @+8). Event types and the LVGL event code sent to the
 * active page: 0 key->0x0a, 1 key->0x48, 2 ->0x3f, 3 long press (->0x08 when
 * terminal/onboarding gated), 4 xy->0x44, 5 xy->0x45, 6 IMU look-up->0x4b
 * (onboarding only), 7 ->0x49, 8 ->0x40, 9 IMU_COMPASS_DIRECTION->0x41,
 * 10 JBD_CHANGE_BRIGHTNESS (unused), 11 APP_CHANGE_Y_COORDINATE (display
 * brightness table), 12 APP_CHANGE_X_COORDINATE (role profile), 13 ignored,
 * 14 xy->0x4a, 15 SYSTEM_EXIT_NOTIFY->0x4f, 16 IMU_COMPASS_CAL_STATE->0x50. */
#include <stdint.h>
#include <stddef.h>

/* Page-stack entry (layer 0 foreground app, 1 background/menu layer). */
typedef struct {
    uint32_t id;      /* +0x0 application / page id */
    void *screen;     /* +0x4 LVGL screen object */
    uint8_t pad[3];
    uint8_t layer;    /* +0xb */
} g2_ui_page_t;

extern uint32_t audio_uart_display_audio_handle; /* RAM 0x200744d0, page-stack state */
extern uint32_t audio_uart_display_mode;         /* RAM 0x200744dc */
extern uint32_t audio_uart_display_background;   /* RAM 0x200744e0, restarted / background app id */

extern uint32_t audio_uart_display_audio_terminal_mode_45bbf4(void);
extern g2_ui_page_t *display_page_active_get_45f8d0(void *state);
extern g2_ui_page_t *audio_uart_display_audio_current_45f8e6(void *state);
extern void *audio_uart_display_audio_handler_a_45f6a8(void *state);
extern uint32_t display_page_send_event_45f8fc(void *state, uint32_t code, void *param);
extern void *audio_uart_display_audio_find_45f840(void *state, uint32_t id);
extern uint32_t audio_uart_display_audio_priority_45f706(const void *state, const void *entry);
extern uint32_t audio_uart_display_audio_stop(void *state, uint32_t mode, uint32_t id, uint32_t ambient); /* 0x45faa8 */
extern uint8_t display_registry_layer_get_442618(uint32_t id);
extern void audio_uart_display_audio_schedule_44228a(uint32_t id, uint32_t operation, uint32_t arg0, uint32_t arg1);
extern uint32_t audio_uart_page_460084(const char *key);
extern uint32_t audio_uart_page_45fffe(uint32_t fallback, uint32_t index);
extern int32_t menu_find_item_by_name_4628c4(uint32_t name);
extern void resume_menu_anim_time_460374(void);
extern void dispThread_Fadeout_Anim_Start_464242(void *screen, uint32_t ms);
extern uint32_t audio_uart_display_process(void); /* 0x464344 lv_timer_handler */
extern void audio_uart_task_delay(uint32_t ticks); /* 0x454b4c */
extern uint8_t audio_uart_device_role_get(void);  /* 0x45a568 */
extern void audio_system_alert_close_464c36(uint32_t application_id, uint32_t payload, uint32_t length, uint32_t context);
extern void audio_uart_master_display_start(uint32_t id, const void *payload, uint16_t length, uint32_t extra); /* 0x464b2e */
extern uint32_t audio_system_alert_command_45a8ee(uint32_t target, uint32_t payload, uint32_t length, uint32_t value);
extern uint8_t universal_setting_startup_apptype_46651e(uint8_t system_on, uint8_t op_type);
extern uint32_t display_input_gated_442d64(void);
extern void system_close_page_factory_0046ae9c(uint32_t, uint32_t);
extern uint32_t audio_settings_brightness_level(uint8_t level);   /* 0x46c622 system_get_brightness_level */
extern uint32_t audio_settings_profile_for_role(uint8_t index);   /* 0x46c600 settings_role_head_up_profile */
extern uint32_t display_driver_set_brightness_46c984(uint32_t value);
extern uint32_t display_driver_set_profile_46c9aa(uint32_t value);
extern void audio_uart_buffer_zero(void *dst, uint32_t len, uint32_t fill); /* 0x43c0e4 memset */
extern uint32_t audio_log_flags(void); /* 0x43d0ce */
extern void audio_log_extended(uint8_t, const char *, const char *, const char *, uint32_t, const char *, ...); /* 0x43d574 */
extern uint32_t compress_log_output(uint32_t, const char *, const char *, ...);

#define SID_UI_FOREGROUND_MENU_ID 3u
#define APP_ID_TERMINAL_GLOBAL    0x30u
#define APP_ID_CLOSE_PAGE         0xe0u
#define LAYER_FOREGROUND          0u
#define LAYER_BACKGROUND          1u
#define LAYER_NOT_REGISTERED      2u
#define DEVICE_ROLE_MASTER        1u

static const char module_tag[] = "display_thread"; /* ROM 0x785aa0 */
static const char source_file[] = "D:\\01_workspace\\s200_ap510b_iar_git\\framework\\sync\\display_thread.c"; /* ROM 0x701fb4 */

static const char restart_fn[] = "ReStartCommandDataHandler"; /* ROM 0x76ad20 */
static const char rs_terminal[] = "terminal mode,drop it,restart app id = %d"; /* ROM 0x73dcc0 */
static const char rs_terminal_s[] = "[display_thread]terminal mode,drop it,restart app id = %d"; /* ROM 0x714170 */
static const char rs_drop[] = "ReStartAppID = %d drop it.."; /* ROM 0x76ad3c */
static const char rs_drop_s[] = "[display_thread]ReStartAppID = %d drop it.."; /* ROM 0x73dcec */
static const char rs_page_id[] = "pActivePageins->config.page_id = %d"; /* ROM 0x7535b8 */
static const char rs_page_id_s[] = "[display_thread]pActivePageins->config.page_id = %d"; /* ROM 0x728928 */
static const char rs_page_null[] = "pActivePageins is null"; /* ROM 0x77694c */
static const char rs_page_null_s[] = "[display_thread]pActivePageins is null"; /* ROM 0x74918c */
static const char rs_unreg[] = "ReStartAppID = %d not register"; /* ROM 0x75f350 */
static const char rs_unreg_s[] = "[display_thread]ReStartAppID = %d not register"; /* ROM 0x733014 */
static const char rs_layer[] = "ReStartAppID = %d ReStartAppLayer = %d"; /* ROM 0x7491b4 */
static const char rs_layer_s[] = "[display_thread]ReStartAppID = %d ReStartAppLayer = %d"; /* ROM 0x71dce0 */
static const char rs_menu[] = "ReStartApplicationID == SID_UI_FOREGROUND_MEUN_ID, jump to the corresponding page"; /* ROM 0x6e74e0 */
static const char rs_menu_s[] = "[display_thread]ReStartApplicationID == SID_UI_FOREGROUND_MEUN_ID, jump to the corresponding page"; /* ROM 0x6da674 */
static const char menu_conversate[] = "ID_MENU_CONVERSATE"; /* ROM 0x77ed0c */
static const char menu_translate[] = "ID_MENU_TRANSLATE";   /* ROM 0x77ed20 */
static const char menu_teleprompt[] = "ID_MENU_TELEPROMPT"; /* ROM 0x77ed34 */
static const char menu_navigate[] = "ID_MENU_NAVIGATE";     /* ROM 0x77ed48 */
static const char rs_jump[] = "jump to the corresponding page, index = %d"; /* ROM 0x73dd18 */
static const char rs_jump_s[] = "[display_thread]jump to the corresponding page, index = %d"; /* ROM 0x7141ac */
static const char rs_default[] = "jump to the default page"; /* ROM 0x76ad58 */
static const char rs_default_s[] = "[display_thread]jump to the default page"; /* ROM 0x73dd44 */
static const char rs_ok[] = "page restart success"; /* ROM 0x776964 */
static const char rs_ok_s[] = "[display_thread]page restart success"; /* ROM 0x7491dc */
static const char rs_received[] = "received ReStartAppID = %d ReStartAppLayer = %d"; /* ROM 0x733044 */
static const char rs_received_s[] = "[display_thread]received ReStartAppID = %d ReStartAppLayer = %d"; /* ROM 0x70ab64 */

static const char startup_fn[] = "getStartUpAppID"; /* ROM 0x785ac0 */
static const char su_unknown[] = "Unknown apptype: %d"; /* ROM 0x77ed5c */
static const char su_unknown_s[] = "[display_thread]Unknown apptype: %d"; /* ROM 0x7535dc */
static const char su_result[] = "getStartUpAppID: sys_status=%d, input_type=%d, op_type=%d, apptype=%d, app_id=%d"; /* ROM 0x6e7534 */
static const char su_result_s[] = "[display_thread]getStartUpAppID: sys_status=%d, input_type=%d, op_type=%d, apptype=%d, app_id=%d"; /* ROM 0x6da6d8 */

static const char input_fn[] = "inputEventDataHandler"; /* ROM 0x77697c */
static const char in_no_page[] = "current active page is null,exit..."; /* ROM 0x753600 */
static const char in_no_page_s[] = "[display_thread]current active page is null,exit..."; /* ROM 0x72895c */
static const char in_terminal[] = "terminal mode,check if the current page is terminal global id"; /* ROM 0x70aba4 */
static const char in_terminal_s[] = "[display_thread]terminal mode,check if the current page is terminal global id"; /* ROM 0x6ecb18 */
static const char in_terminal_lp[] = "terminal mode,send long press event to terminal global id"; /* ROM 0x7141e8 */
static const char in_terminal_lp_s[] = "[display_thread]terminal mode,send long press event to terminal global id"; /* ROM 0x6f2e90 */
static const char in_lp_disabled[] = "long press function is disabled!"; /* ROM 0x753624 */
static const char in_lp_disabled_s[] = "[display_thread]long press function is disabled!"; /* ROM 0x728990 */
static const char in_offset[] = "x_offset = %d,y_offset = %d"; /* ROM 0x76ad74 */
static const char in_offset_s[] = "[display_thread]x_offset = %d,y_offset = %d"; /* ROM 0x73dd70 */
static const char in_onboarding[] = "onboarding is running,send imu lookup event to onboarding"; /* ROM 0x714224 */
static const char in_onboarding_s[] = "[display_thread]onboarding is running,send imu lookup event to onboarding"; /* ROM 0x6f2edc */
static const char in_compass[] = "IMU_COMPASS_DIRECTION, eventValue = %d"; /* ROM 0x749204 */
static const char in_compass_s[] = "[display_thread]IMU_COMPASS_DIRECTION, eventValue = %d"; /* ROM 0x71dd18 */
static const char in_cal[] = "IMU_COMPASS_CAL_STATE, eventValue = %d"; /* ROM 0x74922c */
static const char in_cal_s[] = "[display_thread]IMU_COMPASS_CAL_STATE, eventValue = %d"; /* ROM 0x71dd50 */
static const char in_jbd[] = "JBD_CHANGE_BRIGHTNESS no use now"; /* ROM 0x753648 */
static const char in_jbd_s[] = "[display_thread]JBD_CHANGE_BRIGHTNESS no use now"; /* ROM 0x7289c4 */
static const char in_exit[] = "SYSTEM_EXIT_NOTIFY, eventValue = %d"; /* ROM 0x75366c */
static const char in_exit_s[] = "[display_thread]SYSTEM_EXIT_NOTIFY, eventValue = %d"; /* ROM 0x7289f8 */
static const char in_y[] = "APP_CHANGE_Y_COORDINATE, eventValue = %d"; /* ROM 0x73dd9c */
static const char in_y_s[] = "[display_thread]APP_CHANGE_Y_COORDINATE, eventValue = %d"; /* ROM 0x714260 */
static const char in_x[] = "APP_CHANGE_X_COORDINATE, eventValue = %d"; /* ROM 0x73ddc8 */
static const char in_x_s[] = "[display_thread]APP_CHANGE_X_COORDINATE, eventValue = %d"; /* ROM 0x71429c */
static const char in_unknown[] = "unknow input eventID = %d"; /* ROM 0x76ad90 */
static const char in_unknown_s[] = "[display_thread]unknow input eventID = %d"; /* ROM 0x73ddf4 */

static void *page_state(void)
{
    return (void *)(uintptr_t)audio_uart_display_audio_handle;
}

static void log0(uint8_t level, const char *fn, uint32_t line, const char *text, const char *text_short)
{
    if (audio_log_flags() & 2u)
        audio_log_extended(level, module_tag, source_file, fn, line, text);
    if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
        (void)compress_log_output((uint32_t)level << 26, text_short, text_short);
}

static void log1(uint8_t level, const char *fn, uint32_t line, const char *text, const char *text_short,
                 uint32_t arg)
{
    if (audio_log_flags() & 2u)
        audio_log_extended(level, module_tag, source_file, fn, line, text, arg);
    if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
        (void)compress_log_output(((uint32_t)level << 26) | 0x400000u, text_short, text_short, arg);
}

static void log2(uint8_t level, const char *fn, uint32_t line, const char *text, const char *text_short,
                 uint32_t arg0, uint32_t arg1)
{
    if (audio_log_flags() & 2u)
        audio_log_extended(level, module_tag, source_file, fn, line, text, arg0, arg1);
    if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
        (void)compress_log_output(((uint32_t)level << 26) | 0x800000u, text_short, text_short, arg0, arg1);
}

static int32_t menu_index(const char *name)
{
    return menu_find_item_by_name_4628c4(audio_uart_page_45fffe((uint32_t)(uintptr_t)name,
                                                                audio_uart_page_460084(name)));
}

/* Restart (re-open) request for app_id while the display is running.
 * Returns 1 when a background page was resumed (its id is stored in
 * audio_uart_display_background), 0 when handled otherwise, -1 when dropped. */
uint32_t ReStartCommandDataHandler_44264e(uint32_t app_id, const void *data, uint32_t length)
{
    g2_ui_page_t *page;
    uint8_t layer;

    if (audio_uart_display_audio_terminal_mode_45bbf4() == 1u) {
        log1(3u, restart_fn, 0xbcu, rs_terminal, rs_terminal_s, app_id);
        return UINT32_MAX;
    }
    page = display_page_active_get_45f8d0(page_state());
    if (page == NULL || page->id == app_id) {
        log1(3u, restart_fn, 0xc1u, rs_drop, rs_drop_s, app_id);
        if (page != NULL)
            log1(4u, restart_fn, 0xc3u, rs_page_id, rs_page_id_s, page->id);
        else
            log0(4u, restart_fn, 0xc5u, rs_page_null, rs_page_null_s);
        return UINT32_MAX;
    }
    layer = display_registry_layer_get_442618(app_id);
    if (layer == LAYER_NOT_REGISTERED) {
        log1(2u, restart_fn, 0xcbu, rs_unreg, rs_unreg_s, app_id);
        return UINT32_MAX;
    }

    if (page->layer == LAYER_FOREGROUND) {
        if (layer == LAYER_BACKGROUND) {
            log2(4u, restart_fn, 0xd0u, rs_layer, rs_layer_s, app_id, layer);
            if (app_id == SID_UI_FOREGROUND_MENU_ID) {
                /* Tell the menu which entry to focus: {1, 0xf0, s32 index}. */
                uint8_t jump[10];
                int32_t index;

                log0(4u, restart_fn, 0xd2u, rs_menu, rs_menu_s);
                audio_uart_buffer_zero(jump, sizeof jump, 0u);
                audio_uart_buffer_zero(jump, sizeof jump, 0u);
                jump[0] = 1u;
                jump[1] = 0xf0u;
                switch (page->id) {
                case 1u:  index = 0; break;
                case 5u:  index = menu_index(menu_translate); break;
                case 6u:  index = menu_index(menu_teleprompt); break;
                case 8u:  index = menu_index(menu_navigate); break;
                case 11u: index = menu_index(menu_conversate); break;
                default:  index = -1; break;
                }
                if (index >= 0) {
                    log1(4u, restart_fn, 0xeeu, rs_jump, rs_jump_s, (uint32_t)index);
                    jump[2] = (uint8_t)index;
                    jump[3] = (uint8_t)((uint32_t)index >> 8);
                    jump[4] = (uint8_t)((uint32_t)index >> 16);
                    jump[5] = (uint8_t)((uint32_t)index >> 24);
                } else {
                    jump[2] = 0u;
                    jump[3] = 0u;
                    jump[4] = 0u;
                    jump[5] = 0u;
                    log0(4u, restart_fn, 0xfau, rs_default, rs_default_s);
                }
                audio_uart_display_audio_schedule_44228a(SID_UI_FOREGROUND_MENU_ID, 3u,
                                                          (uint32_t)(uintptr_t)jump, 6u);
            }
            if ((uint8_t)audio_uart_display_audio_stop(page_state(), 1u, app_id, 0u) == 1u) {
                log0(4u, restart_fn, 0x100u, rs_ok, rs_ok_s);
                audio_uart_display_background = app_id;
                return 1u;
            }
        } else if (layer == LAYER_FOREGROUND) {
            const g2_ui_page_t *top = (const g2_ui_page_t *)audio_uart_display_audio_handler_a_45f6a8(page_state());

            if (top->id != app_id) {
                dispThread_Fadeout_Anim_Start_464242(top->screen, 300u);
                for (int32_t i = 0; i < 22; i++) {
                    (void)audio_uart_display_process();
                    audio_uart_task_delay(16u);
                }
            }
            if (audio_uart_device_role_get() == DEVICE_ROLE_MASTER && top->id != app_id) {
                audio_system_alert_close_464c36(page->id & 0xffffu, 0u, 0u, 0u);
                audio_uart_master_display_start(app_id & 0xffffu, data, (uint16_t)length, 0u);
            }
        }
    } else if (page->layer == LAYER_BACKGROUND) {
        if (layer == LAYER_FOREGROUND) {
            log2(4u, restart_fn, 0x115u, rs_received, rs_received_s, app_id, 0u);
            if (audio_uart_device_role_get() == DEVICE_ROLE_MASTER) {
                audio_system_alert_close_464c36(page->id & 0xffffu, 0u, 0u, 0u);
                (void)audio_system_alert_command_45a8ee(app_id, (uint32_t)(uintptr_t)data, length, 500u);
            }
        } else if (layer == LAYER_BACKGROUND) {
            if (audio_uart_display_audio_priority_45f706(page_state(),
                    audio_uart_display_audio_find_45f840(page_state(), app_id)) == 1u)
                audio_uart_display_audio_schedule_44228a(page->id, 5u, 0u, 0u);
            if ((uint8_t)audio_uart_display_audio_stop(page_state(), 2u, app_id, 0u) == 1u &&
                audio_uart_display_audio_priority_45f706(page_state(),
                    audio_uart_display_audio_find_45f840(page_state(), app_id)) == 1u) {
                audio_uart_display_background = app_id;
                return 1u;
            }
        }
    }
    return 0u;
}

/* Maps the boot input to the first application: input_type 0/1/4 select
 * op_type 0/1/2, the universal setting picks an app type, and app type 1
 * means the menu (3); anything else starts nothing (0). */
uint32_t getStartUpAppID_442ba8(uint8_t sys_status, uint32_t input_type)
{
    uint8_t op_type;
    uint8_t app_type;
    uint32_t app_id;

    switch (input_type) {
    case 0u: op_type = 0u; break;
    case 1u: op_type = 1u; break;
    case 4u: op_type = 2u; break;
    default: return 0u;
    }
    app_type = universal_setting_startup_apptype_46651e(sys_status == 1u, op_type);
    if (app_type == 0u) {
        app_id = 0u;
    } else if (app_type == 1u) {
        app_id = SID_UI_FOREGROUND_MENU_ID;
    } else {
        log1(2u, startup_fn, 0x156u, su_unknown, su_unknown_s, app_type);
        app_id = 0u;
    }
    if (audio_log_flags() & 2u)
        audio_log_extended(4u, module_tag, source_file, startup_fn, 0x15cu, su_result,
                           (uint32_t)sys_status, input_type, (uint32_t)op_type, (uint32_t)app_type, app_id);
    if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
        (void)compress_log_output(0x11400000u, su_result_s, su_result_s,
                                  (uint32_t)sys_status, input_type, (uint32_t)op_type, (uint32_t)app_type, app_id);
    return app_id;
}

static uint16_t get16(const uint8_t *p)
{
    return (uint16_t)(p[0] | ((uint32_t)p[1] << 8));
}

static uint32_t get32(const uint8_t *p)
{
    return (uint32_t)p[0] | ((uint32_t)p[1] << 8) | ((uint32_t)p[2] << 16) | ((uint32_t)p[3] << 24);
}

static void send_offset(uint32_t line, uint32_t code, const uint8_t *event)
{
    int32_t xy[2];
    int16_t x = (int16_t)get16(event + 6);
    int16_t y = (int16_t)get16(event + 8);

    log2(4u, input_fn, line, in_offset, in_offset_s, (uint32_t)(int32_t)x, (uint32_t)(int32_t)y);
    xy[0] = x;
    xy[1] = y;
    (void)display_page_send_event_45f8fc(page_state(), code, xy);
}

/* Long press: forwarded as event 8 when gated; otherwise it closes or
 * restarts pages depending on the active page and its layer. */
static uint32_t handle_long_press(const g2_ui_page_t *page, uint32_t *value)
{
    if (display_input_gated_442d64() != 0u) {
        log0(4u, input_fn, 0x1a4u, in_lp_disabled, in_lp_disabled_s);
        (void)display_page_send_event_45f8fc(page_state(), 8u, value);
        return 0u;
    }
    if (audio_uart_display_audio_terminal_mode_45bbf4() != 0u) {
        log0(4u, input_fn, 0x19du, in_terminal, in_terminal_s);
        if (page->id == APP_ID_TERMINAL_GLOBAL) {
            log0(3u, input_fn, 0x19fu, in_terminal_lp, in_terminal_lp_s);
            (void)display_page_send_event_45f8fc(page_state(), 8u, value);
        }
        return 0u;
    }
    if (page->layer == LAYER_FOREGROUND) {
        if (page->id == APP_ID_CLOSE_PAGE)
            system_close_page_factory_0046ae9c(1u, APP_ID_CLOSE_PAGE);
        else if (audio_uart_device_role_get() == DEVICE_ROLE_MASTER)
            audio_uart_master_display_start(SID_UI_FOREGROUND_MENU_ID, NULL, 0u, 0u);
    } else if (page->layer == LAYER_BACKGROUND) {
        if (page->id != SID_UI_FOREGROUND_MENU_ID) {
            if (audio_uart_display_audio_priority_45f706(page_state(),
                    audio_uart_display_audio_find_45f840(page_state(), SID_UI_FOREGROUND_MENU_ID)) == 1u)
                audio_uart_display_audio_schedule_44228a(page->id, 5u, 0u, 0u);
            if ((uint8_t)audio_uart_display_audio_stop(page_state(), 2u, SID_UI_FOREGROUND_MENU_ID, 0u) == 1u &&
                audio_uart_display_audio_priority_45f706(page_state(),
                    audio_uart_display_audio_find_45f840(page_state(), SID_UI_FOREGROUND_MENU_ID)) == 1u)
                audio_uart_display_background = SID_UI_FOREGROUND_MENU_ID;
        } else {
            resume_menu_anim_time_460374();
            (void)audio_uart_display_audio_stop(page_state(), 0u, SID_UI_FOREGROUND_MENU_ID, 0u);
            if (audio_uart_display_mode == 2u)
                return 1u;
            audio_uart_display_background = 0u;
        }
    }
    return 0u;
}

/* Dispatches one input event (message type 7). Returns 1 when the display
 * must close (long press on the menu while closing), -1 without an active
 * page, else 0. */
uint32_t inputEventDataHandler_442d86(const uint8_t *event)
{
    uint32_t key = get16(event);
    uint32_t type = get32(event + 2);
    uint32_t value = get32(event + 6);
    const g2_ui_page_t *page = audio_uart_display_audio_current_45f8e6(page_state());

    if (page == NULL) {
        log0(2u, input_fn, 0x177u, in_no_page, in_no_page_s);
        return UINT32_MAX;
    }
    switch (type) {
    case 0u:
        (void)display_page_send_event_45f8fc(page_state(), 0x0au, &key);
        break;
    case 1u:
        (void)display_page_send_event_45f8fc(page_state(), 0x48u, &key);
        break;
    case 2u:
        (void)display_page_send_event_45f8fc(page_state(), 0x3fu, &value);
        break;
    case 3u:
        return handle_long_press(page, &value);
    case 4u:
        send_offset(0x1bau, 0x44u, event);
        break;
    case 5u:
        send_offset(0x1c5u, 0x45u, event);
        break;
    case 6u:
        if (display_input_gated_442d64() == 1u) {
            log0(4u, input_fn, 0x1dbu, in_onboarding, in_onboarding_s);
            (void)display_page_send_event_45f8fc(page_state(), 0x4bu, &value);
        }
        break;
    case 7u:
        (void)display_page_send_event_45f8fc(page_state(), 0x49u, &value);
        break;
    case 8u:
        (void)display_page_send_event_45f8fc(page_state(), 0x40u, &value);
        break;
    case 9u:
        log1(3u, input_fn, 0x1e9u, in_compass, in_compass_s, value);
        (void)display_page_send_event_45f8fc(page_state(), 0x41u, &value);
        break;
    case 10u:
        log0(2u, input_fn, 0x1f3u, in_jbd, in_jbd_s);
        break;
    case 11u:
        log1(4u, input_fn, 0x1fcu, in_y, in_y_s, value);
        (void)display_driver_set_brightness_46c984(audio_settings_brightness_level((uint8_t)value));
        break;
    case 12u:
        log1(4u, input_fn, 0x202u, in_x, in_x_s, value);
        (void)display_driver_set_profile_46c9aa(audio_settings_profile_for_role((uint8_t)value));
        break;
    case 13u:
        break;
    case 14u:
        send_offset(0x1d3u, 0x4au, event);
        break;
    case 15u:
        log1(3u, input_fn, 0x1f7u, in_exit, in_exit_s, value);
        (void)display_page_send_event_45f8fc(page_state(), 0x4fu, &value);
        break;
    case 16u:
        log1(3u, input_fn, 0x1eeu, in_cal, in_cal_s, value);
        (void)display_page_send_event_45f8fc(page_state(), 0x50u, &value);
        break;
    default:
        log1(2u, input_fn, 0x20bu, in_unknown, in_unknown_s, type);
        break;
    }
    return 0u;
}
