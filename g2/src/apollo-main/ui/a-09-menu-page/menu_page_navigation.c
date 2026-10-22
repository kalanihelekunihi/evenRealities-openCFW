/* Main menu navigation, stock D:\01_workspace\s200_ap510b_iar_git\app\gui\menu\menu_page.c.
 * Native 0x461620..0x462ea7 (menu_inject_event, menu_inject_event_absolute,
 * menu_find_item_by_name, menu_jump_to_item_instant and the focus-style refresh);
 * literal pools 0x461b10, 0x461e8c, 0x461fb8, 0x46236c..0x462590, 0x462878..0x4628c0,
 * 0x462a28..0x462a78, 0x462da8..0x462db0 and 0x462e94..0x462ea4.
 *
 * The menu shows five rows of 50 px; selected_index - scroll_offset is the focus
 * position inside the visible window (0..4). Moving past row 2 scrolls the content
 * container instead of the focus, except at the ends of the list. */
#include "menu_page_private.h"

#define MENU_EVENT_UP 0u
#define MENU_EVENT_DOWN 1u
#define MENU_EVENT_SELECT 2u
#define MENU_EVENT_CANCEL 3u

#define MENU_ACTION_NOTIFICATIONS 1u
#define MENU_ACTION_CONVERSATE 2u
#define MENU_ACTION_TELEPROMPT 3u
#define MENU_ACTION_TRANSLATE 4u
#define MENU_ACTION_NAVIGATE 5u
#define MENU_ACTION_EVEN_AI 6u
#define MENU_ACTION_DASHBOARD 7u
#define MENU_ACTION_SILENT_MODE 8u
#define MENU_ACTION_EXT_APP 0xffeu

#define APP_DASHBOARD 1u
#define APP_TRANSLATE 5u
#define APP_TELEPROMPT 6u
#define APP_NAVIGATION 8u
#define APP_CONVERSATE 0xbu
#define APP_EVENHUB_MAIN 0xe0u
#define APP_EVENHUB_LOADING 0xffeu
#define APP_MENU_CLOSE_REQ 7u
#define DEVICE_ROLE_MASTER 1u
#define LAUNCH_RECORD_KEY 0x40101u
#define SILENT_MODE_SERVICE 0x10au

extern void *audio_uart_lv_child_get_44dce2(void *obj, int32_t index);
extern uint32_t audio_uart_page_44104c(uint32_t rgb);                             /* lv_color_hex */
extern void audio_uart_page_44129e(void *obj, uint32_t opa, uint32_t selector);    /* bg_opa */
extern void audio_uart_page_4413ce(void *obj, uint32_t opa, uint32_t selector);    /* image_opa */
extern void audio_uart_page_44140e(void *obj, uint32_t color, uint32_t selector);  /* text_color */
extern void audio_uart_display_audio_reset_441488(void *obj, uint32_t opa, uint32_t selector); /* opa */
extern void audio_uart_lv_scroll_to_y_44ea04(void *obj, int32_t y, uint32_t animated);
extern void audio_uart_lv_anim_init_4503d6(void *anim);
extern void *audio_uart_lv_anim_start_450408(void *anim);
extern void audio_uart_lv_anim_values_4506ce(void *anim, int32_t start, int32_t end);
extern int32_t audio_uart_lv_anim_path_450688(void *anim);
extern uint32_t display_driver_uled_mode_45a568(void);                            /* device role */
extern uint32_t audio_system_alert_command_45a8ee(uint32_t app, const void *payload, uint32_t len,
                                                  uint32_t timeout_ms);           /* start app */
extern const int32_t *page_stack_current_45f6b4(uint32_t stack);                  /* NULL or app id record */
extern void audio_system_alert_close_464c36(uint32_t app, uint32_t payload, uint32_t len,
                                            uint32_t context);
extern uint32_t audio_sync_send_to_both_ext_464f76(uint32_t app, const void *bytes, uint32_t len,
                                                   uint32_t id, uint32_t event);
extern int32_t audio_uart_master_input_event(uint32_t device, uint32_t event, uint32_t value,
                                             uint32_t context);                   /* 0x465748 */
extern uint8_t audio_silent_mode_status_get(void);                               /* 0x46919e */
extern void audio_uart_ring_wear_persist_48eb32(uint32_t key, uint32_t length, const void *payload);
extern uint32_t evenhub_loading_widget_id_492ce6(void);
extern uint32_t evenhub_main_widget_id_4935fe(void);
extern void audio_even_ai_ancc_state_sync_497cf0(uint32_t state, uint32_t delay);
extern void service_even_ai_fn_0049832e(uint32_t event, uint32_t arg);

static const char menu_module_tag[] = "menu.page"; /* ROM 0x78b5b8 */
static const char menu_source_file[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\app\\gui\\menu\\menu_page.c"; /* ROM 0x70ca64 */
static const char inject_fn[] = "menu_inject_event"; /* ROM 0x781264 */
static const char absolute_fn[] = "menu_inject_event_absolute"; /* ROM 0x76e0f8 */
static const char find_fn[] = "menu_find_item_by_name"; /* ROM 0x7796f4 */
static const char jump_fn[] = "menu_jump_to_item_instant"; /* ROM 0x76e114 */

static const char not_init[] = "Menu page not initialized"; /* ROM 0x76e0a4 */
static const char not_init_s[] = "[menu.page]Menu page not initialized"; /* ROM 0x74b324 */
static const char busy[] = "Animation in progress, ignoring input"; /* ROM 0x74b34c */
static const char busy_s[] = "[menu.page]Animation in progress, ignoring input"; /* ROM 0x72abe4 */
static const char up_msg[] = "MENU_EVENT_UP: current index=%d, focus_pos=%d, scroll_offset=%d"; /* ROM 0x70cb24 */
static const char up_msg_s[] =
    "[menu.page]MENU_EVENT_UP: current index=%d, focus_pos=%d, scroll_offset=%d"; /* ROM 0x6f4488 */
static const char focus_msg[] = "  -> Move focus only: new index=%d"; /* ROM 0x756a2c */
static const char focus_msg_s[] = "[menu.page]  -> Move focus only: new index=%d"; /* ROM 0x735624 */
static const char scroll_msg[] =
    "  -> Scroll content: new index=%d, scroll_offset=%d, target_scroll=%d"; /* ROM 0x6fb5c4 */
static const char scroll_msg_s[] =
    "[menu.page]  -> Scroll content: new index=%d, scroll_offset=%d, target_scroll=%d"; /* ROM 0x6e8b30 */
static const char top_msg[] = "  -> At top, move focus: new index=%d"; /* ROM 0x74b374 */
static const char top_msg_s[] = "[menu.page]  -> At top, move focus: new index=%d"; /* ROM 0x72ac18 */
static const char first_msg[] = "MENU_EVENT_UP: At first item, trigger rubber band"; /* ROM 0x72ac4c */
static const char first_msg_s[] =
    "[menu.page]MENU_EVENT_UP: At first item, trigger rubber band"; /* ROM 0x70cb64 */
static const char down_msg[] =
    "MENU_EVENT_DOWN: current index=%d, focus_pos=%d, scroll_offset=%d"; /* ROM 0x703b10 */
static const char down_msg_s[] =
    "[menu.page]MENU_EVENT_DOWN: current index=%d, focus_pos=%d, scroll_offset=%d"; /* ROM 0x6ee4b8 */
static const char bottom_msg[] = "  -> At bottom, move focus: new index=%d"; /* ROM 0x740080 */
static const char bottom_msg_s[] = "[menu.page]  -> At bottom, move focus: new index=%d"; /* ROM 0x72ac80 */
static const char last_msg[] = "MENU_EVENT_DOWN: At last item, trigger rubber band"; /* ROM 0x72acb4 */
static const char last_msg_s[] =
    "[menu.page]MENU_EVENT_DOWN: At last item, trigger rubber band"; /* ROM 0x70cba4 */
static const char selected_msg[] = "Menu item selected: %s (ID: %d)"; /* ROM 0x762310 */
static const char selected_msg_s[] = "[menu.page]Menu item selected: %s (ID: %d)"; /* ROM 0x7400ac */
static const char ext_msg[] = "EXT_APP_ID_ACTION_ID: %d"; /* ROM 0x76e0c0 */
static const char ext_msg_s[] = "[menu.page]EXT_APP_ID_ACTION_ID: %d"; /* ROM 0x756a50 */
static const char hub_loading_msg[] = "Evenhub loading page is already running"; /* ROM 0x74b39c */
static const char hub_loading_msg_s[] =
    "[menu.page]Evenhub loading page is already running"; /* ROM 0x72ace8 */
static const char hub_loading_same[] =
    "Evenhub loading page is already running, startup widget id is %d"; /* ROM 0x703b54 */
static const char hub_loading_same_s[] =
    "[menu.page]Evenhub loading page is already running, startup widget id is %d"; /* ROM 0x6f44d4 */
static const char hub_loading_restart[] =
    "Evenhub loading page is not running, startup widget id is %d, ext_app_id is %d.restart evenhub loading page"; /* ROM 0x6d7ab0 */
static const char hub_loading_restart_s[] =
    "[menu.page]Evenhub loading page is not running, startup widget id is %d, ext_app_id is %d.restart evenhub loading page"; /* ROM 0x6d6560 */
static const char hub_main_msg[] = "Evenhub main page is already running"; /* ROM 0x74b3c4 */
static const char hub_main_msg_s[] = "[menu.page]Evenhub main page is already running"; /* ROM 0x735654 */
static const char hub_main_same[] =
    "Evenhub main page is already running, startup widget id is %d"; /* ROM 0x70cbe4 */
static const char hub_main_same_s[] =
    "[menu.page]Evenhub main page is already running, startup widget id is %d"; /* ROM 0x6f4520 */
static const char hub_main_restart[] =
    "Evenhub main page is not running, startup widget id is %d, ext_app_id is %d"; /* ROM 0x6f456c */
static const char hub_main_restart_s[] =
    "[menu.page]Evenhub main page is not running, startup widget id is %d, ext_app_id is %d"; /* ROM 0x6e4278 */
static const char conversate_running[] = "Conversate is already running"; /* ROM 0x762330 */
static const char conversate_running_s[] = "[menu.page]Conversate is already running"; /* ROM 0x7400d8 */
static const char teleprompt_running[] = "Teleprompt is already running"; /* ROM 0x762350 */
static const char teleprompt_running_s[] = "[menu.page]Teleprompt is already running"; /* ROM 0x740104 */
static const char translate_running[] = "Translate is already running"; /* ROM 0x762370 */
static const char translate_running_s[] = "[menu.page]Translate is already running"; /* ROM 0x74b3ec */
static const char navigation_running[] = "NAVIGATION is already running"; /* ROM 0x762390 */
static const char navigation_running_s[] = "[menu.page]NAVIGATION is already running"; /* ROM 0x740130 */
static const char dashboard_running[] = "Dashboard is already running"; /* ROM 0x7623b0 */
static const char dashboard_running_s[] = "[menu.page]Dashboard is already running"; /* ROM 0x74b414 */
static const char cancel_msg[] = "Menu cancel event"; /* ROM 0x781278 */
static const char cancel_msg_s[] = "[menu.page]Menu cancel event"; /* ROM 0x7623d0 */
static const char unknown_msg[] = "unknown menu event code: %d"; /* ROM 0x76e0dc */
static const char unknown_msg_s[] = "[menu.page]unknown menu event code: %d"; /* ROM 0x74b43c */
static const char abs_busy[] = "Animation in progress, ignoring absolute positioning input"; /* ROM 0x71645c */
static const char abs_busy_s[] =
    "[menu.page]Animation in progress, ignoring absolute positioning input"; /* ROM 0x6fb60c */
static const char abs_invalid[] = "Invalid target index: %d (valid range: 0-%d)"; /* ROM 0x735684 */
static const char abs_invalid_s[] =
    "[menu.page]Invalid target index: %d (valid range: 0-%d)"; /* ROM 0x720398 */
static const char abs_same[] = "Already at target index %d (%s)"; /* ROM 0x7623f0 */
static const char abs_same_s[] = "[menu.page]Already at target index %d (%s)"; /* ROM 0x74015c */
static const char abs_jump[] =
    "menu_inject_event_absolute: jump from %d (%s) to %d (%s), scroll_offset=%d, scroll=%d"; /* ROM 0x6e42d0 */
static const char abs_jump_s[] =
    "[menu.page]menu_inject_event_absolute: jump from %d (%s) to %d (%s), scroll_offset=%d, scroll=%d"; /* ROM 0x6db164 */
static const char find_null[] = "menu_find_item_by_name: item_name is NULL"; /* ROM 0x740188 */
static const char find_null_s[] = "[menu.page]menu_find_item_by_name: item_name is NULL"; /* ROM 0x7203d0 */
static const char find_hit[] = "Found item '%s' with action_id=%d at index=%d"; /* ROM 0x7356b4 */
static const char find_hit_s[] = "[menu.page]Found item '%s' with action_id=%d at index=%d"; /* ROM 0x716498 */
static const char find_miss[] = "Item not found: '%s'"; /* ROM 0x77970c */
static const char find_miss_s[] = "[menu.page]Item not found: '%s'"; /* ROM 0x762410 */
static const char jump_invalid[] = "Invalid index: %d"; /* ROM 0x78128c */
static const char jump_invalid_s[] = "[menu.page]Invalid index: %d"; /* ROM 0x762430 */
static const char jump_same[] = "Already at target item: %s (index=%d)"; /* ROM 0x74b464 */
static const char jump_same_s[] = "[menu.page]Already at target item: %s (index=%d)"; /* ROM 0x72ad1c */
static const char jump_msg[] =
    "menu_jump_to_item_instant: jump from %d (%s) to %d (%s,), scroll_offset=%d, scroll=%d"; /* ROM 0x6e4328 */
static const char jump_msg_s[] =
    "[menu.page]menu_jump_to_item_instant: jump from %d (%s) to %d (%s,), scroll_offset=%d, scroll=%d"; /* ROM 0x6db1c8 */
static const char jump_done[] = "Jump complete: now at %s (index=%d)"; /* ROM 0x756a74 */
static const char jump_done_s[] = "[menu.page]Jump complete: now at %s (index=%d)"; /* ROM 0x7356e4 */

/* Launch records copied from ROM 0x78dcc4..0x78dd18 (two words each). */
#define LAUNCH_SOURCE_MENU 1u
#define LAUNCH_CONVERSATE 1u
#define LAUNCH_TELEPROMPT 3u
#define LAUNCH_TRANSLATE 2u
#define LAUNCH_NAVIGATION 4u

static void menu_scroll_window_for(int32_t index)
{
    if (index < 2) {
        g2_menu_scroll_offset = 0;
    } else if (index < g2_menu_item_count - 2) {
        g2_menu_scroll_offset = index - 2;
    } else {
        g2_menu_scroll_offset = g2_menu_item_count - G2_MENU_VISIBLE_ROWS;
        if (g2_menu_scroll_offset < 0)
            g2_menu_scroll_offset = 0;
    }
}

/* Focus-only move: restyle rows and animate the focus frame. */
static void menu_move_focus(void)
{
    menu_item_styles_hook_462db4();
    menu_update_item_styles_462db6();
    menu_focus_change_anim_start_4612f8();
}

static void menu_scroll_content(int32_t target)
{
    menu_item_styles_hook_462db4();
    menu_update_item_styles_462db6();
    menu_scroll_anim_start_460fc6(g2_menu_list_obj, target, 200);
}

/* Starts a built-in app unless it is already the top page. */
static void menu_launch_app(uint32_t app, uint32_t record_app, uint32_t line,
                            const char *running, const char *running_s)
{
    const int32_t *top = page_stack_current_45f6b4(audio_uart_display_audio_handle);
    if (top == NULL) {
        (void)audio_system_alert_command_45a8ee(app, NULL, 0u, 500u);
        g2_menu_launch_record_t record = { record_app, LAUNCH_SOURCE_MENU };
        audio_uart_ring_wear_persist_48eb32(LAUNCH_RECORD_KEY, 2u, &record);
    } else if ((uint32_t)*top == app) {
        MENU_LOG(3u, inject_fn, line, 0xc000000u, running, running_s);
    } else {
        (void)audio_system_alert_command_45a8ee(app, NULL, 0u, 500u);
        g2_menu_launch_record_t record = { record_app, LAUNCH_SOURCE_MENU };
        audio_uart_ring_wear_persist_48eb32(LAUNCH_RECORD_KEY, 2u, &record);
    }
}

static void menu_launch_ext_app(const g2_menu_page_item_t *item)
{
    const uint32_t app_id = (uint32_t)item->app_id;
    uint8_t payload[64];

    MENU_LOG(3u, inject_fn, 0x36fu, 0xc400000u, ext_msg, ext_msg_s, item->app_id);
    /* Stock clears the payload twice (initialiser plus memset). */
    audio_uart_buffer_zero(payload, sizeof payload, 0u);
    audio_uart_buffer_zero(payload, sizeof payload, 0u);
    payload[0] = 0u;
    payload[1] = (uint8_t)app_id;
    payload[2] = (uint8_t)(app_id >> 8);
    payload[3] = (uint8_t)(app_id >> 16);
    payload[4] = (uint8_t)(app_id >> 24);
    (void)audio_queue_copy_bytes(&payload[5], item->text, g2_log_module_length(item->text));

    if (display_driver_uled_mode_45a568() != DEVICE_ROLE_MASTER)
        return;
    (void)audio_uart_master_input_event(APP_MENU_CLOSE_REQ, 3u, 0u, 0u);
    const int32_t *top = page_stack_current_45f6b4(audio_uart_display_audio_handle);
    if (top == NULL) {
        (void)audio_system_alert_command_45a8ee(APP_EVENHUB_LOADING, payload, sizeof payload, 500u);
    } else if ((uint32_t)*top == APP_EVENHUB_LOADING) {
        MENU_LOG(4u, inject_fn, 0x381u, 0x10000000u, hub_loading_msg, hub_loading_msg_s);
        const uint32_t widget = evenhub_loading_widget_id_492ce6();
        if (widget == app_id) {
            MENU_LOG(3u, inject_fn, 0x384u, 0xc400000u, hub_loading_same, hub_loading_same_s, widget);
        } else {
            MENU_LOG(3u, inject_fn, 0x386u, 0xc800000u, hub_loading_restart, hub_loading_restart_s,
                     widget, app_id);
            audio_system_alert_close_464c36(APP_EVENHUB_LOADING, 0u, 0u, 0u);
            (void)audio_system_alert_command_45a8ee(APP_EVENHUB_LOADING, payload, sizeof payload, 500u);
            g2_menu_launch_record_t record = { app_id, LAUNCH_SOURCE_MENU };
            audio_uart_ring_wear_persist_48eb32(LAUNCH_RECORD_KEY, 2u, &record);
        }
    } else if ((uint32_t)*top == APP_EVENHUB_MAIN) {
        MENU_LOG(4u, inject_fn, 0x38cu, 0x10000000u, hub_main_msg, hub_main_msg_s);
        const uint32_t widget = evenhub_main_widget_id_4935fe();
        if (widget == app_id) {
            MENU_LOG(3u, inject_fn, 0x38fu, 0xc400000u, hub_main_same, hub_main_same_s, widget);
        } else {
            MENU_LOG(3u, inject_fn, 0x391u, 0xc800000u, hub_main_restart, hub_main_restart_s,
                     widget, app_id);
            audio_system_alert_close_464c36(APP_EVENHUB_MAIN, 0u, 0u, 0u);
            (void)audio_system_alert_command_45a8ee(APP_EVENHUB_LOADING, payload, sizeof payload, 500u);
            g2_menu_launch_record_t record = { app_id, LAUNCH_SOURCE_MENU };
            audio_uart_ring_wear_persist_48eb32(LAUNCH_RECORD_KEY, 2u, &record);
        }
    } else {
        (void)audio_system_alert_command_45a8ee(APP_EVENHUB_LOADING, payload, sizeof payload, 500u);
        g2_menu_launch_record_t record = { app_id, LAUNCH_SOURCE_MENU };
        audio_uart_ring_wear_persist_48eb32(LAUNCH_RECORD_KEY, 2u, &record);
    }
}

static void menu_select_current(void)
{
    MENU_LOG(4u, inject_fn, 0x35du, 0x10800000u, selected_msg, selected_msg_s,
             MENU_ITEM_TR(g2_menu_current_index), g2_menu_display_items[g2_menu_current_index].text_res);

    /* Press feedback: scale the row 320 -> 360 (256 = 100 %) and back, 150 ms each way. */
    void *row = g2_menu_item_objs[g2_menu_current_index];
    g2_lv_anim_t anim;
    audio_uart_lv_anim_init_4503d6(&anim);
    anim.var = row;
    anim.exec_cb = (void *)menu_obj_set_style_transform_scale_46015a;
    audio_uart_lv_anim_values_4506ce(&anim, 0x140, 0x168);
    anim.duration = 150;
    anim.path_cb = (void *)audio_uart_lv_anim_path_450688;
    anim.playback_duration = 150u;
    (void)audio_uart_lv_anim_start_450408(&anim);

    const g2_menu_page_item_t *item = &g2_menu_display_items[g2_menu_current_index];
    switch (item->text_res) {
    case MENU_ACTION_NOTIFICATIONS:
        if (display_driver_uled_mode_45a568() == DEVICE_ROLE_MASTER) {
            (void)audio_uart_master_input_event(APP_MENU_CLOSE_REQ, 3u, 0u, 0u);
            audio_even_ai_ancc_state_sync_497cf0(2u, 500u);
        }
        break;
    case MENU_ACTION_CONVERSATE:
        if (display_driver_uled_mode_45a568() == DEVICE_ROLE_MASTER) {
            (void)audio_uart_master_input_event(APP_MENU_CLOSE_REQ, 3u, 0u, 0u);
            menu_launch_app(APP_CONVERSATE, LAUNCH_CONVERSATE, 0x3aau, conversate_running,
                            conversate_running_s);
        }
        break;
    case MENU_ACTION_TELEPROMPT:
        if (display_driver_uled_mode_45a568() == DEVICE_ROLE_MASTER) {
            (void)audio_uart_master_input_event(APP_MENU_CLOSE_REQ, 3u, 0u, 0u);
            menu_launch_app(APP_TELEPROMPT, LAUNCH_TELEPROMPT, 0x3bfu, teleprompt_running,
                            teleprompt_running_s);
        }
        break;
    case MENU_ACTION_TRANSLATE:
        if (display_driver_uled_mode_45a568() == DEVICE_ROLE_MASTER) {
            (void)audio_uart_master_input_event(APP_MENU_CLOSE_REQ, 3u, 0u, 0u);
            menu_launch_app(APP_TRANSLATE, LAUNCH_TRANSLATE, 0x3d3u, translate_running,
                            translate_running_s);
        }
        break;
    case MENU_ACTION_NAVIGATE:
        if (display_driver_uled_mode_45a568() == DEVICE_ROLE_MASTER) {
            (void)audio_uart_master_input_event(APP_MENU_CLOSE_REQ, 3u, 0u, 0u);
            menu_launch_app(APP_NAVIGATION, LAUNCH_NAVIGATION, 0x3e8u, navigation_running,
                            navigation_running_s);
        }
        break;
    case MENU_ACTION_EVEN_AI:
        if (display_driver_uled_mode_45a568() == DEVICE_ROLE_MASTER) {
            (void)audio_uart_master_input_event(APP_MENU_CLOSE_REQ, 3u, 0u, 0u);
            service_even_ai_fn_0049832e(1u, 500u);
        }
        break;
    case MENU_ACTION_DASHBOARD:
        if (display_driver_uled_mode_45a568() == DEVICE_ROLE_MASTER) {
            (void)audio_uart_master_input_event(APP_MENU_CLOSE_REQ, 3u, 0u, 0u);
            const int32_t *top = page_stack_current_45f6b4(audio_uart_display_audio_handle);
            if (top == NULL) {
                (void)audio_system_alert_command_45a8ee(APP_DASHBOARD, NULL, 0u, 500u);
            } else if ((uint32_t)*top == APP_DASHBOARD) {
                MENU_LOG(3u, inject_fn, 0x410u, 0xc000000u, dashboard_running, dashboard_running_s);
            } else {
                (void)audio_system_alert_command_45a8ee(APP_DASHBOARD, NULL, 0u, 500u);
            }
        }
        break;
    case MENU_ACTION_SILENT_MODE:
        if (display_driver_uled_mode_45a568() == DEVICE_ROLE_MASTER) {
            (void)audio_uart_master_input_event(APP_MENU_CLOSE_REQ, 3u, 0u, 0u);
            uint8_t enable = audio_silent_mode_status_get() == 0u ? 1u : 0u; /* toggle */
            (void)audio_sync_send_to_both_ext_464f76(SILENT_MODE_SERVICE, &enable, 1u, 0u, 4u);
        }
        break;
    case MENU_ACTION_EXT_APP:
        menu_launch_ext_app(item);
        break;
    default:
        break;
    }
}

void menu_inject_event_461620(uint8_t event)
{
    if (g2_menu_focus_anim_obj == NULL) {
        MENU_LOG(2u, inject_fn, 0x2e8u, 0x8000000u, not_init, not_init_s);
        return;
    }
    if (g2_menu_anim_in_progress != 0u) {
        MENU_LOG(4u, inject_fn, 0x2eeu, 0x10000000u, busy, busy_s);
        return;
    }

    switch (event) {
    case MENU_EVENT_UP:
        if (g2_menu_current_index < 1) {
            MENU_LOG(2u, inject_fn, 0x320u, 0x8000000u, first_msg, first_msg_s);
            menu_trigger_rubber_band_effect_46137c(true);
            break;
        }
        {
            const int32_t focus = g2_menu_current_index - g2_menu_scroll_offset;
            MENU_LOG(4u, inject_fn, 0x2f9u, 0x10c00000u, up_msg, up_msg_s, g2_menu_current_index,
                     focus, g2_menu_scroll_offset);
            if (focus >= 3) {
                g2_menu_current_index--;
                MENU_LOG(4u, inject_fn, 0x2feu, 0x10400000u, focus_msg, focus_msg_s,
                         g2_menu_current_index);
                menu_move_focus();
            } else if (focus == 2) {
                if (g2_menu_scroll_offset < 1) {
                    g2_menu_current_index--;
                    MENU_LOG(4u, inject_fn, 0x311u, 0x10400000u, top_msg, top_msg_s,
                             g2_menu_current_index);
                    menu_move_focus();
                } else {
                    g2_menu_scroll_offset--;
                    g2_menu_current_index--;
                    const int32_t target = menu_calculate_scroll_position_for_item_460d6c(g2_menu_current_index);
                    MENU_LOG(4u, inject_fn, 0x30au, 0x10c00000u, scroll_msg, scroll_msg_s,
                             g2_menu_current_index, g2_menu_scroll_offset, target);
                    menu_scroll_content(target);
                }
            } else {
                g2_menu_current_index--;
                MENU_LOG(4u, inject_fn, 0x319u, 0x10400000u, focus_msg, focus_msg_s,
                         g2_menu_current_index);
                menu_move_focus();
            }
        }
        break;

    case MENU_EVENT_DOWN:
        if (g2_menu_current_index >= g2_menu_item_count - 1) {
            MENU_LOG(2u, inject_fn, 0x355u, 0x8000000u, last_msg, last_msg_s);
            menu_trigger_rubber_band_effect_46137c(false);
            break;
        }
        {
            const int32_t focus = g2_menu_current_index - g2_menu_scroll_offset;
            MENU_LOG(4u, inject_fn, 0x32bu, 0x10c00000u, down_msg, down_msg_s, g2_menu_current_index,
                     focus, g2_menu_scroll_offset);
            if (focus < 2) {
                g2_menu_current_index++;
                MENU_LOG(4u, inject_fn, 0x330u, 0x10400000u, focus_msg, focus_msg_s,
                         g2_menu_current_index);
                menu_move_focus();
            } else if (focus == 2) {
                int32_t max_offset = g2_menu_item_count - G2_MENU_VISIBLE_ROWS;
                if (max_offset < 0)
                    max_offset = 0;
                if (g2_menu_scroll_offset < max_offset) {
                    g2_menu_scroll_offset++;
                    g2_menu_current_index++;
                    const int32_t target = menu_calculate_scroll_position_for_item_460d6c(g2_menu_current_index);
                    MENU_LOG(4u, inject_fn, 0x33fu, 0x10c00000u, scroll_msg, scroll_msg_s,
                             g2_menu_current_index, g2_menu_scroll_offset, target);
                    menu_scroll_content(target);
                } else {
                    g2_menu_current_index++;
                    MENU_LOG(4u, inject_fn, 0x346u, 0x10400000u, bottom_msg, bottom_msg_s,
                             g2_menu_current_index);
                    menu_move_focus();
                }
            } else {
                g2_menu_current_index++;
                MENU_LOG(4u, inject_fn, 0x34eu, 0x10400000u, focus_msg, focus_msg_s,
                         g2_menu_current_index);
                menu_move_focus();
            }
        }
        break;

    case MENU_EVENT_SELECT:
        menu_select_current();
        break;

    case MENU_EVENT_CANCEL:
        MENU_LOG(4u, inject_fn, 0x43cu, 0x10000000u, cancel_msg, cancel_msg_s);
        break;

    default:
        MENU_LOG(2u, inject_fn, 0x43fu, 0x8400000u, unknown_msg, unknown_msg_s, event);
        break;
    }
}

/* Animated jump to an absolute row (phone/ring "jump to index"). */
void menu_inject_event_absolute_462594(int32_t index)
{
    if (g2_menu_focus_anim_obj == NULL) {
        MENU_LOG(2u, absolute_fn, 0x447u, 0x8000000u, not_init, not_init_s);
        return;
    }
    if (g2_menu_anim_in_progress != 0u) {
        MENU_LOG(4u, absolute_fn, 0x44du, 0x10000000u, abs_busy, abs_busy_s);
        return;
    }
    if (index < 0 || index >= g2_menu_item_count) {
        MENU_LOG(2u, absolute_fn, 0x453u, 0x8800000u, abs_invalid, abs_invalid_s, index,
                 g2_menu_item_count - 1);
        return;
    }
    if (index == g2_menu_current_index) {
        MENU_LOG(4u, absolute_fn, 0x459u, 0x10800000u, abs_same, abs_same_s, index,
                 MENU_ITEM_TR(index));
        return;
    }

    const int32_t old = g2_menu_current_index;
    g2_menu_current_index = index;
    menu_scroll_window_for(index);
    g2_menu_anim_in_progress = 1u;
    const int32_t target = menu_calculate_scroll_position_for_item_460d6c(index);
    MENU_LOG(4u, absolute_fn, 0x471u, 0x11800000u, abs_jump, abs_jump_s, old, MENU_ITEM_TR(old),
             index, MENU_ITEM_TR(index), g2_menu_scroll_offset, target);
    menu_scroll_anim_start_460fc6(g2_menu_list_obj, target, 200);
}

/* Returns the row whose localized text equals the localized item_name, or -1. */
int32_t menu_find_item_by_name_4628c4(const char *item_name)
{
    if (item_name == NULL) {
        MENU_LOG(2u, find_fn, 0x49eu, 0x8000000u, find_null, find_null_s);
        return -1;
    }
    menu_page_mutex_lock_46018e();
    for (int32_t i = 0; i < g2_menu_item_count; i++) {
        const char *wanted = MENU_TR(item_name);
        const char *text = MENU_ITEM_TR(i);
        if (audio_uart_font_path_compare(text, wanted) == 0) {
            MENU_LOG(4u, find_fn, 0x4a5u, 0x10c00000u, find_hit, find_hit_s, item_name,
                     g2_menu_display_items[i].text_res, i);
            menu_page_mutex_unlock_4601ea();
            return i;
        }
    }
    menu_page_mutex_unlock_4601ea();
    MENU_LOG(2u, find_fn, 0x4acu, 0x8400000u, find_miss, find_miss_s, item_name);
    return -1;
}

/* Unanimated jump; note the stock bound only rejects index > count. */
void menu_jump_to_item_instant_462a7c(int32_t index)
{
    if (g2_menu_focus_anim_obj == NULL) {
        MENU_LOG(2u, jump_fn, 0x4ccu, 0x8000000u, not_init, not_init_s);
        return;
    }
    if (g2_menu_item_count < index) {
        MENU_LOG(1u, jump_fn, 0x4d1u, 0x4400000u, jump_invalid, jump_invalid_s, index);
        return;
    }
    if (index == g2_menu_current_index) {
        MENU_LOG(4u, jump_fn, 0x4d9u, 0x10800000u, jump_same, jump_same_s, MENU_ITEM_TR(index), index);
        menu_update_item_styles_462db6();
        menu_item_styles_hook_462db4();
        return;
    }

    const int32_t old = g2_menu_current_index;
    g2_menu_current_index = index;
    menu_scroll_window_for(index);
    const int32_t target = menu_calculate_scroll_position_for_item_460d6c(index);
    MENU_LOG(4u, jump_fn, 0x4f3u, 0x11800000u, jump_msg, jump_msg_s, old, MENU_ITEM_TR(old), index,
             MENU_ITEM_TR(index), g2_menu_scroll_offset, target);
    audio_uart_lv_scroll_to_y_44ea04(g2_menu_list_obj, target, 0u);
    menu_update_item_styles_462db6();
    menu_item_styles_hook_462db4();
    MENU_LOG(4u, jump_fn, 0x4feu, 0x10800000u, jump_done, jump_done_s,
             MENU_ITEM_TR(g2_menu_current_index), g2_menu_current_index);
}

/* Empty in stock (0x462db4 is a bare BX LR); always paired with 0x462db6. */
void menu_item_styles_hook_462db4(void)
{
}

/* Focused row: 50/255 background opacity, white label, opaque icon; others:
 * transparent background, grey 0x444444 label, 32/255 icon. Scale reset to 100 %. */
void menu_update_item_styles_462db6(void)
{
    if (g2_menu_frame_obj == NULL)
        return;
    for (int32_t i = 0; i < g2_menu_item_count; i++) {
        if (g2_menu_item_objs[i] == NULL)
            continue;
        void *icon = audio_uart_lv_child_get_44dce2(g2_menu_item_objs[i], 0);
        void *label = audio_uart_lv_child_get_44dce2(g2_menu_item_objs[i], 1);
        if (i == g2_menu_current_index) {
            audio_uart_page_44129e(g2_menu_item_objs[i], 0x32u, 0u);
            if (label != NULL)
                audio_uart_page_44140e(label, audio_uart_page_44104c(0xffffffu), 0u);
            if (icon != NULL)
                audio_uart_page_4413ce(icon, 0xffu, 0u);
        } else {
            audio_uart_page_44129e(g2_menu_item_objs[i], 0u, 0u);
            if (label != NULL) {
                audio_uart_page_44140e(label, audio_uart_page_44104c(0x444444u), 0u);
                menu_obj_set_style_transform_scale_46015a(label, 0x100, 0u);
            }
            if (icon != NULL) {
                audio_uart_page_4413ce(icon, 0x20u, 0u);
                menu_obj_set_style_transform_scale_46015a(icon, 0x100, 0u);
            }
        }
        audio_uart_display_audio_reset_441488(g2_menu_item_objs[i], 0xffu, 0u);
        menu_obj_set_style_transform_scale_46015a(g2_menu_item_objs[i], 0x100, 0u);
    }
}
