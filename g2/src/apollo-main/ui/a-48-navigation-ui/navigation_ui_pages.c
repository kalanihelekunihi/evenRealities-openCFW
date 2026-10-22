/* Stock D:\01_workspace\s200_ap510b_iar_git\app\gui\navigation\navigation_ui.c (log tag
 * "navigation.ui"): startup, calibrate-compass, map and exit pages. Native
 * navigation_ui_startup_page_create 0x545d18..0x5464a3, map text refresh 0x5464b8..0x546607,
 * navigation_ui_create_calibrate_compass_page 0x546620..0x5467d5,
 * navigation_ui_create_map_page 0x54692c..0x5476d7 (inline "AM"/"PM" 0x546d98/0x546d9c),
 * navigation_ui_create_break_exit_page 0x5476e4..0x547785,
 * navigation_ui_create_none_location_list_page 0x5477ac..0x547867,
 * navigation_ui_startup_failed_exit_page 0x54787c..0x5479b3 and
 * navigation_ui_completed_exit_page 0x5479c8..0x547a71; literal pools 0x5467e0..0x54692b,
 * 0x5476d8..0x5476e3, 0x547788..0x5477ab, 0x547868..0x54787b, 0x5479b4..0x5479c7,
 * 0x547a74..0x547abb, 0x547dbc..0x547dcb, 0x547ebc..0x547ec7, 0x547fdc..0x548013,
 * 0x548298..0x5482c3 and 0x548474..0x548483. */
#include "navigation_ui_private.h"

static const char s_startup_fn[] = "navigation_ui_startup_page_create"; /* ROM 0x756d44 */
static const char s_fifo_fail[] = "navigation_ui_startup_page_create: Failed to create event FIFO"; /* ROM 0x70cee4 */
static const char s_fifo_fail_s[] =
    "[navigation.ui]navigation_ui_startup_page_create: Failed to create event FIFO"; /* ROM 0x6ee648 */
static const char s_anim_left[] = "navigation_calibrate_compass_loading_animation is not NULL!!!!!"; /* ROM 0x70cf24 */
static const char s_anim_left_s[] =
    "[navigation.ui]navigation_calibrate_compass_loading_animation is not NULL!!!!!"; /* ROM 0x6ee698 */
static const char s_state_startup[] =
    "NavigationInputEventHandler: navigation_ui_state = MENU_STARTUP_NAVIGATION_PAGE"; /* ROM 0x6ee6e8 */
static const char s_state_startup_s[] =
    "[navigation.ui]NavigationInputEventHandler: navigation_ui_state = MENU_STARTUP_NAVIGATION_PAGE"; /* ROM 0x6dde34 */
static const char s_state_wait[] =
    "NavigationInputEventHandler: navigation_ui_state = NAVIGATION_WAIT_MAP_DATA_PAGE"; /* ROM 0x6e8c80 */
static const char s_state_wait_s[] =
    "[navigation.ui]NavigationInputEventHandler: navigation_ui_state = NAVIGATION_WAIT_MAP_DATA_PAGE"; /* ROM 0x6dde94 */
static const char s_calib_sent[] =
    " compass calibration!!!! navigation_data_handler send force update compass calibration to UI: ret = %d\n"; /* ROM 0x6d935c */
static const char s_calib_sent_s[] =
    "[navigation.ui] compass calibration!!!! navigation_data_handler send force update compass calibration to UI: ret = %d\n"; /* ROM 0x6d66c8 */
static const char key_ble_disconnect[] = "ID_GENERAL_BLUETOOTH_DISCONNECT"; /* ROM 0x762590 */
static const char key_start[] = "ID_NAVIGATE_START"; /* ROM 0x7813b8 */

static const char s_calib_fn[] = "navigation_ui_create_calibrate_compass_page"; /* ROM 0x740398 */
static const char s_calib_msg[] = "navigation_ui_create_calibrate_compass_page"; /* ROM 0x7403c4 */
static const char s_calib_msg_s[] = "[navigation.ui]navigation_ui_create_calibrate_compass_page"; /* ROM 0x71663c */
static const char s_calib_anim_fail[] = "Failed to create loading animation"; /* ROM 0x756d68 */
static const char s_calib_anim_fail_s[] = "[navigation.ui]Failed to create loading animation"; /* ROM 0x72afc0 */
static const char key_calibrate[] = "ID_NAVIGATE_CALIBRATE_COMPASS"; /* ROM 0x7625b0 */

static const char s_map_fn[] = "navigation_ui_create_map_page"; /* ROM 0x7625d0 */
static const char s_map_msg[] = "navigation_ui_create_map_page"; /* ROM 0x7625f0 */
static const char s_map_msg_s[] = "[navigation.ui]navigation_ui_create_map_page"; /* ROM 0x735984 */
static const char s_map_done[] = "Navigation multi-layer containers created: A(visible), B(hidden)"; /* ROM 0x703ec8 */
static const char s_map_done_s[] =
    "[navigation.ui]Navigation multi-layer containers created: A(visible), B(hidden)"; /* ROM 0x6ee738 */
static const char key_recalculating[] = "ID_NAVIGATE_RECALCULATING"; /* ROM 0x76e734 */
static const char key_loading_mini[] = "ID_NAVIGATE_LOADING_MAP_MINI_MAP"; /* ROM 0x756d8c */
static const char key_loading_full[] = "ID_NAVIGATE_LOADING_MAP_FULL_MAP"; /* ROM 0x756db0 */
static const char fmt_clock_12h[] = "%02d:%02d %s"; /* ROM 0x787ac0 */
static const char fmt_clock_24h[] = "%02d:%02d"; /* ROM 0x78b5dc */
static const char s_am[] = "AM"; /* inline 0x546d98 */
static const char s_pm[] = "PM"; /* inline 0x546d9c */

static const char s_break_fn[] = "navigation_ui_create_break_exit_page"; /* ROM 0x74b5f4 */
static const char s_break_msg[] = "navigation_ui_create_break_exit_page"; /* ROM 0x74b61c */
static const char s_break_msg_s[] = "[navigation.ui]navigation_ui_create_break_exit_page"; /* ROM 0x72aff4 */
static const char key_timeout[] = "ID_NAVIGATE_CONNECTION_TIME_OUT"; /* ROM 0x762610 */
static const char s_none_fn[] = "navigation_ui_create_none_location_list_page"; /* ROM 0x7359b4 */
static const char s_none_msg[] = "navigation_ui_create_none_location_list_page"; /* ROM 0x7359e4 */
static const char s_none_msg_s[] = "[navigation.ui]navigation_ui_create_none_location_list_page"; /* ROM 0x716678 */
static const char key_no_favorites[] = "ID_NAVIGATE_NO_FAVORITE_LOCATIONS"; /* ROM 0x756dd4 */
static const char s_failed_fn[] = "navigation_ui_startup_failed_exit_page"; /* ROM 0x74b644 */
static const char s_failed_msg[] = "navigation_ui_startup_failed_exit_page"; /* ROM 0x74b66c */
static const char s_failed_msg_s[] = "[navigation.ui]navigation_ui_startup_failed_exit_page"; /* ROM 0x7204b0 */
static const char key_too_far[] = "ID_NAVIGATE_FAIL_LOCATION_TOO_FAR"; /* ROM 0x756df8 */
static const char key_went_wrong[] = "ID_NAVIGATE_FAIL_SOMETHING_WENT_WRONG"; /* ROM 0x74b694 */
static const char key_no_access[] = "ID_NAVIGATE_FAIL_NO_LOCATION_ACCESS"; /* ROM 0x756e1c */
static const char key_unlock[] = "ID_NAVIGATE_UNLOCK_YOUR_PHONE_TO_CONTINUE"; /* ROM 0x7403f0 */
static const char s_completed_fn[] = "navigation_ui_completed_exit_page"; /* ROM 0x756e40 */
static const char s_completed_msg[] = "navigation_ui_completed_exit_page"; /* ROM 0x756e64 */
static const char s_completed_msg_s[] = "[navigation.ui]navigation_ui_completed_exit_page"; /* ROM 0x72b028 */
static const char key_complete[] = "ID_NAVIGATE_COMPLETE"; /* ROM 0x77991c */

/* Sync record sent to the master side after compass start (app 8, 6 bytes). */
#define NAV_SYNC_APP 8u
#define NAV_SYNC_COMPASS_CALIBRATION 0xf5u

static const char *localized(const char *key)
{
    return audio_uart_page_45fffe(key, audio_uart_page_460084(key));
}

static void label_font_white(void *label)
{
    audio_uart_page_44143e(label, audio_uart_ring_primary_head_cell, LV_PART_MAIN);
    audio_uart_page_44140e(label, audio_uart_page_44104c(0xffffffu), LV_PART_MAIN);
}

/* Fixed widget flags used on every map page child. */
static void map_child_flags(void *obj)
{
    audio_uart_page_43ded4(obj, LV_OBJ_FLAG_ADV_HITTEST);
    audio_uart_page_43dfa4(obj, LV_OBJ_FLAG_SCROLLABLE);
}

/* Border / outline / shadow / padding / radius cleared, scrolling off. */
static void layer_plain(void *obj)
{
    audio_uart_page_44131c(obj, 0, LV_PART_MAIN);
    audio_uart_page_44133a(obj, 0, LV_PART_MAIN);
    audio_uart_page_441386(obj, 0, LV_PART_MAIN);
    lv_obj_set_style_pad_all_545594(obj, 0, LV_PART_MAIN);
    audio_uart_page_44146a(obj, 0, LV_PART_MAIN);
    audio_uart_page_43dfa4(obj, LV_OBJ_FLAG_SCROLLABLE);
}

/* Centred full-content label on the page root (exit / status pages). */
static void *status_label(void)
{
    void *label = audio_uart_page_499416(g2_navigation_page_root_20074718);

    audio_uart_page_43f506(label, LV_SIZE_CONTENT);
    audio_uart_page_43f568(label, LV_SIZE_CONTENT);
    audio_uart_page_43f6ac(label, LV_ALIGN_CENTER);
    return label;
}

/* Centred full-content label on the startup layer. */
static void *startup_label(void)
{
    void *label = audio_uart_page_499416(g2_navigation_startup_obj_20074740);

    audio_uart_page_43f506(label, LV_SIZE_CONTENT);
    audio_uart_page_43f568(label, LV_SIZE_CONTENT);
    audio_uart_page_43f6ac(label, LV_ALIGN_CENTER);
    return label;
}

int32_t navigation_ui_startup_page_create_545d18(void *parent, const uint8_t *msg, uint16_t wait_map)
{
    void *label;
    int32_t x;
    int32_t y;
    uint8_t sync[10];
    uint32_t ret;

    navigation_mutex_init_585ca4();
    if (g2_nav_event_fifo_20074734 != NULL) {
        ui_common_api_fn_00509c96(g2_nav_event_fifo_20074734);
        g2_nav_event_fifo_20074734 = NULL;
    }
    if (g2_nav_event_fifo_20074734 == NULL) {
        g2_nav_event_fifo_20074734 = ui_common_api_fn_00509c1c();
        if (g2_nav_event_fifo_20074734 == NULL) {
            NAV_LOG(1, s_startup_fn, 0x217, 0x4000000u, s_fifo_fail, s_fifo_fail_s);
            return -1;
        }
    }

    /* State reset (stock order; the list/mode reset block appears twice). */
    g2_navigation_var_20074720 = 0u;
    g2_navigation_flag_20074fe6 = 0u;
    g2_navigation_location_container_2007479c = NULL;
    g2_navigation_location_content_200747a0 = NULL;
    audio_uart_buffer_zero(g2_navigation_location_items_20072c68, 0x50u, 0u);
    g2_navigation_location_selected_200747a4 = 0;
    g2_navigation_location_scroll_offset_200747a8 = 0;
    g2_navigation_location_animating_20074fe8 = 0u;
    g2_navigation_mode_container_200747ac = NULL;
    g2_navigation_mode_content_200747b0 = NULL;
    audio_uart_buffer_zero(g2_navigation_mode_items_20074160, 8u, 0u);
    g2_navigation_mode_selected_200747b4 = 0;
    g2_navigation_mode_scroll_offset_200747b8 = 0;
    g2_navigation_mode_animating_20074fe9 = 0u;
    g2_nav_b_clock_label_20074764 = NULL;
    g2_nav_a_clock_label_200747e0 = NULL;
    g2_nav_animation_running_20074fec = 0u;
    g2_navigation_mode_animating_20074fe9 = 0u;
    g2_navigation_mode_container_200747ac = NULL;
    g2_navigation_mode_content_200747b0 = NULL;
    audio_uart_buffer_zero(g2_navigation_mode_items_20074160, 8u, 0u);
    g2_navigation_mode_selected_200747b4 = 0;
    g2_navigation_mode_scroll_offset_200747b8 = 0;
    g2_nav_flag_20074fe7 = 0u;
    g2_nav_var_20074754 = 0u;
    audio_uart_buffer_zero(g2_nav_buf_200f4784, 0x40u, 0u);
    g2_nav_container_b_shown_2007473c = 0u;
    g2_navigation_var_200747f0 = 0u;
    g2_navigation_var_200747f4 = 0u;
    g2_navigation_var_200747f8 = 0u;
    g2_navigation_var_200747fc = 0u;
    g2_navigation_flag_20074fea = 0u;
    g2_navigation_flag_20074feb = 0u;

    (void)osMutexAcquire(g2_navigation_mutex, WAIT_FOREVER);
    g2_nav_var_20074758 = 0u;
    audio_uart_buffer_zero(&g2_navigation_location_list_20376c38, 0x55cu, 0u);
    audio_uart_buffer_zero(&g2_navigation_info_staging_2037bdd0, 0x18cu, 0u);
    audio_uart_buffer_zero(g2_nav_buf_20329600, 0x4674u, 0u);
    audio_uart_buffer_zero(g2_nav_buf_202e4fc8, 0xea7cu, 0u);
    audio_uart_buffer_zero(&g2_navigation_ui_data_202c0d70, 0x13258u, 0u);
    (void)osMutexRelease(g2_navigation_mutex);

    g2_navigation_map_page_200747bc = NULL;
    g2_navigation_container_a_200747c0 = NULL;
    g2_navigation_container_b_200747c4 = NULL;
    g2_navigation_a_turn_icon_200747cc = NULL;
    g2_navigation_a_turn_label_200747d0 = NULL;
    g2_navigation_a_road_label_200747d4 = NULL;
    g2_nav_a_compass_img_200747e8 = NULL;
    g2_nav_a_loading_label_200747ec = NULL;
    g2_nav_b_clock_label_20074764 = NULL;
    g2_navigation_b_text_c8_label_20074768 = NULL;
    g2_navigation_b_text_88_label_2007476c = NULL;
    g2_navigation_b_text_108_label_20074778 = NULL;
    if (g2_nav_calibrate_anim_20074750 != NULL) {
        NAV_LOG(2, s_startup_fn, 0x262, 0x8000000u, s_anim_left, s_anim_left_s);
        generic_animation_destroy_463e1c(g2_nav_calibrate_anim_20074750, 0u);
    }
    g2_nav_calibrate_anim_20074750 = NULL;
    g2_nav_var_2007474c = 0u;
    g2_nav_var_20074748 = 0u;
    g2_navigation_var_20074744 = 0u;
    g2_nav_var_20002cfc = 20u;

    /* Page root: opaque black 576x288, white text, no decoration. */
    g2_navigation_page_root_20074718 = audio_uart_page_43de82(parent);
    audio_uart_page_43dfa4(g2_navigation_page_root_20074718, LV_OBJ_FLAG_SCROLLABLE);
    audio_uart_page_43f506(g2_navigation_page_root_20074718, NAV_SCREEN_W);
    audio_uart_page_43f568(g2_navigation_page_root_20074718, NAV_SCREEN_H);
    audio_uart_page_43f09a(g2_navigation_page_root_20074718, 0, 0);
    audio_uart_page_43dfa4(g2_navigation_page_root_20074718, LV_OBJ_FLAG_SCROLLABLE);
    audio_uart_page_44127e(g2_navigation_page_root_20074718, audio_uart_page_44104c(0u), LV_PART_MAIN);
    audio_uart_page_44129e(g2_navigation_page_root_20074718, LV_OPA_COVER, LV_PART_MAIN);
    audio_uart_page_44140e(g2_navigation_page_root_20074718, audio_uart_page_44104c(0xffffffu), LV_PART_MAIN);
    audio_uart_page_44142e(g2_navigation_page_root_20074718, LV_OPA_COVER, LV_PART_MAIN);
    audio_uart_page_4412ec(g2_navigation_page_root_20074718, audio_uart_page_44104c(0u), LV_PART_MAIN);
    audio_uart_page_44131c(g2_navigation_page_root_20074718, 0, LV_PART_MAIN);
    audio_uart_page_44133a(g2_navigation_page_root_20074718, 0, LV_PART_MAIN);
    audio_uart_page_441378(g2_navigation_page_root_20074718, 0, LV_PART_MAIN);
    audio_uart_page_441386(g2_navigation_page_root_20074718, 0, LV_PART_MAIN);
    audio_uart_page_4413b0(g2_navigation_page_root_20074718, 0, LV_PART_MAIN);
    audio_uart_page_441394(g2_navigation_page_root_20074718, 0, LV_PART_MAIN);
    audio_uart_page_4413a2(g2_navigation_page_root_20074718, 0, LV_PART_MAIN);
    audio_uart_page_44146a(g2_navigation_page_root_20074718, 0, LV_PART_MAIN);
    lv_obj_set_style_pad_all_545594(g2_navigation_page_root_20074718, 0, LV_PART_MAIN);
    audio_uart_page_44120e(g2_navigation_page_root_20074718, 0, LV_PART_MAIN);
    audio_uart_page_44121c(g2_navigation_page_root_20074718, 0, LV_PART_MAIN);
    audio_uart_page_44122a(g2_navigation_page_root_20074718, 0, LV_PART_MAIN);
    audio_uart_page_441238(g2_navigation_page_root_20074718, 0, LV_PART_MAIN);

    /* Startup layer: transparent, at the page offset. */
    g2_navigation_startup_obj_20074740 = audio_uart_page_43de82(g2_navigation_page_root_20074718);
    audio_uart_page_43f506(g2_navigation_startup_obj_20074740, NAV_SCREEN_W);
    audio_uart_page_43f568(g2_navigation_startup_obj_20074740, NAV_SCREEN_H);
    (void)ui_common_api_fn_00509f7a(&x, &y);
    audio_uart_page_43f09a(g2_navigation_startup_obj_20074740, x, y);
    audio_uart_page_44127e(g2_navigation_startup_obj_20074740, audio_uart_page_44104c(0u), LV_PART_MAIN);
    audio_uart_page_44129e(g2_navigation_startup_obj_20074740, LV_OPA_TRANSP, LV_PART_MAIN);
    audio_uart_page_44131c(g2_navigation_startup_obj_20074740, 0, LV_PART_MAIN);
    audio_uart_page_44133a(g2_navigation_startup_obj_20074740, 0, LV_PART_MAIN);
    audio_uart_page_441378(g2_navigation_startup_obj_20074740, 0, LV_PART_MAIN);
    audio_uart_page_441386(g2_navigation_startup_obj_20074740, 0, LV_PART_MAIN);
    audio_uart_page_4413b0(g2_navigation_startup_obj_20074740, 0, LV_PART_MAIN);
    audio_uart_page_441394(g2_navigation_startup_obj_20074740, 0, LV_PART_MAIN);
    audio_uart_page_4413a2(g2_navigation_startup_obj_20074740, 0, LV_PART_MAIN);
    lv_obj_set_style_pad_all_545594(g2_navigation_startup_obj_20074740, 0, LV_PART_MAIN);
    audio_uart_page_44120e(g2_navigation_startup_obj_20074740, 0, LV_PART_MAIN);
    audio_uart_page_44121c(g2_navigation_startup_obj_20074740, 0, LV_PART_MAIN);
    audio_uart_page_44122a(g2_navigation_startup_obj_20074740, 0, LV_PART_MAIN);
    audio_uart_page_441238(g2_navigation_startup_obj_20074740, 0, LV_PART_MAIN);
    audio_uart_page_44146a(g2_navigation_startup_obj_20074740, 0, LV_PART_MAIN);
    audio_uart_page_4412ec(g2_navigation_startup_obj_20074740, audio_uart_page_44104c(0u), LV_PART_MAIN);
    audio_uart_page_44140e(g2_navigation_startup_obj_20074740, audio_uart_page_44104c(0xffffffu), LV_PART_MAIN);
    audio_uart_page_44142e(g2_navigation_startup_obj_20074740, LV_OPA_COVER, LV_PART_MAIN);

    if (wait_map == 0u) {
        NAV_LOG(4, s_startup_fn, 0x2a3, 0x10000000u, s_state_startup, s_state_startup_s);
        if (UX_GetSystemBLEStatus() == 0u) {
            label = startup_label();
            audio_uart_page_49942e(label, localized(key_ble_disconnect));
            audio_uart_page_44143e(label, audio_uart_ring_primary_head_cell, LV_PART_MAIN);
            audio_uart_page_44145a(label, LV_TEXT_ALIGN_CENTER, LV_PART_MAIN);
            g2_nav_var_2007474c = 1u;
            g2_nav_var_20074748 = 0xf0u;
            g2_navigation_ui_state_20074fed = 4u;
        } else {
            label = startup_label();
            audio_uart_page_49942e(label, localized(key_start));
            audio_uart_page_44143e(label, audio_uart_ring_primary_head_cell, LV_PART_MAIN);
            g2_navigation_ui_state_20074fed = 0u;
            (void)navigation_send_type_1_allocating();
        }
        return 0; /* stock leaves the last callee's r0 */
    }

    NAV_LOG(4, s_startup_fn, 699, 0x10000000u, s_state_wait, s_state_wait_s);
    label = startup_label();
    audio_uart_page_49942e(label, localized(key_start));
    audio_uart_page_44143e(label, audio_uart_ring_primary_head_cell, LV_PART_MAIN);
    g2_navigation_ui_state_20074fed = 1u;
    (void)navigation_send_type_5_shared(msg[1], 0u);
    (void)StartIMUCompassFunc_5455e4();
    if (audio_uart_service_mode() != 1u)
        return 0;
    if (semantic_get_flag_20074fdc() != 0u)
        return 0;
    (void)navigation_send_type_16_allocating();
    audio_uart_buffer_zero(sync, sizeof(sync), 0u);
    sync[0] = NAV_SYNC_COMPASS_CALIBRATION;
    sync[1] = 0u;
    sync[2] = 0u;
    sync[3] = 0u;
    sync[4] = 0u;
    sync[5] = 0u;
    ret = audio_uart_master_display_refresh(NAV_SYNC_APP, sync, 6u, 0u);
    NAV_LOG(4, s_startup_fn, 0x2d4, 0x10400000u, s_calib_sent, s_calib_sent_s, ret);
    return 0;
}

/* Re-applies the turn texts and re-aligns the top-right rows of layers A and B. */
void navigation_ui_update_map_texts_5464b8(void)
{
    g2_navigation_info_t *info = &g2_navigation_ui_data_202c0d70.info;

    if (info->valid != 1u)
        return;
    audio_uart_page_498680(g2_navigation_a_turn_icon_200747cc, navigation_icon_name_for_code(info->field_04));
    audio_uart_page_49942e(g2_navigation_a_turn_label_200747d0, info->distance);
    audio_uart_page_49942e(g2_navigation_a_road_label_200747d4, info->road_name);
    audio_uart_page_49942e(g2_navigation_b_text_88_label_2007476c, info->spend_time);
    audio_uart_page_49942e(g2_navigation_b_text_c8_label_20074768, info->remain_distance);
    audio_uart_page_49942e(g2_navigation_b_text_148_label_20074770, info->speed);
    audio_uart_page_49942e(g2_navigation_b_text_108_label_20074778, info->eta_time);
    audio_uart_page_43f6b8(g2_navigation_b_text_88_label_2007476c, LV_ALIGN_TOP_RIGHT, 0, 0);
    audio_uart_page_43f6d6(g2_navigation_b_text_c8_label_20074768, g2_navigation_b_text_88_label_2007476c,
                           LV_ALIGN_OUT_LEFT_MID, -16, 0);
    if (info->navigate_work_method == 1u) {
        audio_uart_page_43ded4(g2_navigation_b_text_148_label_20074770, LV_OBJ_FLAG_HIDDEN);
    } else {
        audio_uart_page_43dfa4(g2_navigation_b_text_148_label_20074770, LV_OBJ_FLAG_HIDDEN);
        audio_uart_page_43f6d6(g2_navigation_b_text_148_label_20074770, g2_navigation_b_text_c8_label_20074768,
                               LV_ALIGN_OUT_LEFT_MID, -16, 0);
    }
    if (info->navigate_work_method == 1u)
        audio_uart_page_43f6d6(g2_navigation_b_text_108_label_20074778, g2_navigation_b_text_c8_label_20074768,
                               LV_ALIGN_OUT_LEFT_MID, -16, 0);
    else
        audio_uart_page_43f6d6(g2_navigation_b_text_108_label_20074778, g2_navigation_b_text_148_label_20074770,
                               LV_ALIGN_OUT_LEFT_MID, -16, 0);
    audio_uart_page_49942e(g2_navigation_a_text_88_label_200747dc, info->spend_time);
    audio_uart_page_49942e(g2_navigation_a_text_c8_label_200747d8, info->remain_distance);
    audio_uart_page_43f6b8(g2_navigation_a_text_88_label_200747dc, LV_ALIGN_TOP_RIGHT, 0, 0);
    audio_uart_page_43f6d6(g2_navigation_a_text_c8_label_200747d8, g2_navigation_a_text_88_label_200747dc,
                           LV_ALIGN_OUT_LEFT_MID, -16, 0);
    audio_uart_page_43f66c(g2_navigation_container_a_200747c0);
    audio_uart_page_43f66c(g2_navigation_container_b_200747c4);
}

int32_t navigation_ui_create_calibrate_compass_page_546620(void)
{
    g2_generic_animation_config_t config;
    uint32_t color;
    int32_t x;
    int32_t y;

    NAV_LOG(4, s_calib_fn, 0x31c, 0x10000000u, s_calib_msg, s_calib_msg_s);
    if (g2_navigation_page_root_20074718 != NULL)
        audio_uart_page_44d878(g2_navigation_page_root_20074718);

    g2_navigation_calibrate_page_20074800 = audio_uart_page_43de82(g2_navigation_page_root_20074718);
    audio_uart_page_43f4c0(g2_navigation_calibrate_page_20074800, NAV_SCREEN_W, NAV_SCREEN_H);
    (void)ui_common_api_fn_00509f7a(&x, &y);
    audio_uart_page_43f09a(g2_navigation_calibrate_page_20074800, x, y);
    audio_uart_page_44129e(g2_navigation_calibrate_page_20074800, LV_OPA_TRANSP, LV_PART_MAIN);
    layer_plain(g2_navigation_calibrate_page_20074800);

    g2_navigation_calibrate_label_20074804 = audio_uart_page_499416(g2_navigation_calibrate_page_20074800);
    audio_uart_page_43f506(g2_navigation_calibrate_label_20074804, LV_SIZE_CONTENT);
    audio_uart_page_43f568(g2_navigation_calibrate_label_20074804, LV_SIZE_CONTENT);
    audio_uart_page_49942e(g2_navigation_calibrate_label_20074804, localized(key_calibrate));
    audio_uart_page_44143e(g2_navigation_calibrate_label_20074804, audio_uart_ring_primary_head_cell, LV_PART_MAIN);
    audio_uart_page_44145a(g2_navigation_calibrate_label_20074804, LV_TEXT_ALIGN_CENTER, LV_PART_MAIN);
    audio_uart_page_44140e(g2_navigation_calibrate_label_20074804, audio_uart_page_44104c(0xffffffu), LV_PART_MAIN);
    audio_uart_page_43f6b8(g2_navigation_calibrate_label_20074804, LV_ALIGN_TOP_MID, 0, 0x95);

    /* 64-frame 32x32 loading animation from the ROM template, white on black. */
    (void)audio_uart_display_area_copy_439c04(&config, &g2_navigation_calibrate_anim_config_762870, sizeof(config));
    color = lv_color_white_441094();
    (void)audio_queue_copy_bytes(config.color_a, &color, 3u);
    color = lv_color_black_4410a6();
    (void)audio_queue_copy_bytes(config.bg_color, &color, 3u);
    g2_nav_calibrate_anim_20074750 = generic_animation_create_463c68(g2_navigation_calibrate_page_20074800, &config);
    if (g2_nav_calibrate_anim_20074750 == NULL) {
        NAV_LOG(1, s_calib_fn, 0x362, 0x4000000u, s_calib_anim_fail, s_calib_anim_fail_s);
    } else {
        audio_uart_page_43f09a(g2_nav_calibrate_anim_20074750->image, 0x110, 0x6d);
        generic_animation_start_463ea6(g2_nav_calibrate_anim_20074750);
    }
    return 0;
}

static void *map_layer(void *page)
{
    void *layer = audio_uart_page_43de82(page);

    audio_uart_page_43f4c0(layer, NAV_SCREEN_W, NAV_SCREEN_H);
    audio_uart_page_43f09a(layer, 0, 0);
    audio_uart_page_44127e(layer, audio_uart_page_44104c(0u), LV_PART_MAIN);
    audio_uart_page_44129e(layer, LV_OPA_COVER, LV_PART_MAIN);
    layer_plain(layer);
    return layer;
}

static void *map_image(void *parent, const void *src, int32_t w, int32_t h, int32_t x, int32_t y)
{
    void *img = audio_uart_page_498668(parent);

    audio_uart_page_498680(img, src);
    audio_uart_page_43f506(img, w);
    audio_uart_page_43f568(img, h);
    audio_uart_page_43f0e0(img, x);
    audio_uart_page_43f142(img, y);
    map_child_flags(img);
    return img;
}

int32_t navigation_ui_create_map_page_54692c(void)
{
    g2_navigation_ui_data_t *data = &g2_navigation_ui_data_202c0d70;
    g2_calendar_t now;
    char clock[16];
    int32_t x;
    int32_t y;
    int32_t width;
    void *a;
    void *b;
    void *c;

    NAV_LOG(4, s_map_fn, 0x36e, 0x10000000u, s_map_msg, s_map_msg_s);
    if (g2_navigation_page_root_20074718 != NULL)
        audio_uart_page_44d878(g2_navigation_page_root_20074718);

    g2_navigation_map_page_200747bc = audio_uart_page_43de82(g2_navigation_page_root_20074718);
    audio_uart_page_43f4c0(g2_navigation_map_page_200747bc, NAV_SCREEN_W, NAV_SCREEN_H);
    (void)ui_common_api_fn_00509f7a(&x, &y);
    audio_uart_page_43f09a(g2_navigation_map_page_200747bc, x, y);
    audio_uart_page_44129e(g2_navigation_map_page_200747bc, LV_OPA_TRANSP, LV_PART_MAIN);
    layer_plain(g2_navigation_map_page_200747bc);

    g2_navigation_container_a_200747c0 = a = map_layer(g2_navigation_map_page_200747bc);
    g2_navigation_container_b_200747c4 = b = map_layer(g2_navigation_map_page_200747bc);
    audio_uart_page_43ded4(b, LV_OBJ_FLAG_HIDDEN);
    g2_nav_container_c_200747c8 = c = map_layer(g2_navigation_map_page_200747bc);
    audio_uart_page_43ded4(c, LV_OBJ_FLAG_HIDDEN);

    /* Layer C: "recalculating" notice. */
    g2_navigation_c_recalculating_label_20074798 = audio_uart_page_499416(c);
    audio_uart_page_49942e(g2_navigation_c_recalculating_label_20074798, localized(key_recalculating));
    label_font_white(g2_navigation_c_recalculating_label_20074798);
    lv_obj_center_4409fa(g2_navigation_c_recalculating_label_20074798);
    map_child_flags(g2_navigation_c_recalculating_label_20074798);

    /* Layer A: turn icon and texts. */
    g2_navigation_a_turn_icon_200747cc = audio_uart_page_498668(a);
    if (data->info.valid == 1u)
        audio_uart_page_498680(g2_navigation_a_turn_icon_200747cc, navigation_icon_name_for_code(data->info.field_04));
    audio_uart_page_43f506(g2_navigation_a_turn_icon_200747cc, 0x3c);
    audio_uart_page_43f568(g2_navigation_a_turn_icon_200747cc, 0x3c);
    audio_uart_page_43f0e0(g2_navigation_a_turn_icon_200747cc, 0);
    audio_uart_page_43f142(g2_navigation_a_turn_icon_200747cc, 0xe4);
    map_child_flags(g2_navigation_a_turn_icon_200747cc);

    g2_navigation_a_turn_label_200747d0 = audio_uart_page_499416(a);
    if (data->info.valid == 1u)
        audio_uart_page_49942e(g2_navigation_a_turn_label_200747d0, data->info.distance);
    label_font_white(g2_navigation_a_turn_label_200747d0);
    audio_uart_page_43f0e0(g2_navigation_a_turn_label_200747d0, 0x48);
    audio_uart_page_43f142(g2_navigation_a_turn_label_200747d0, 0xe8);
    map_child_flags(g2_navigation_a_turn_label_200747d0);

    g2_navigation_a_road_label_200747d4 = audio_uart_page_499416(a);
    if (data->info.valid == 1u)
        audio_uart_page_49942e(g2_navigation_a_road_label_200747d4, data->info.road_name);
    label_font_white(g2_navigation_a_road_label_200747d4);
    audio_uart_page_43f506(g2_navigation_a_road_label_200747d4, 0x170);
    audio_uart_page_43f568(g2_navigation_a_road_label_200747d4, 0x1e);
    audio_uart_page_43f0e0(g2_navigation_a_road_label_200747d4, 0x48);
    audio_uart_page_43f142(g2_navigation_a_road_label_200747d4, 0x104);
    map_child_flags(g2_navigation_a_road_label_200747d4);

    /* Clock text, 12 h ("%02d:%02d AM") or 24 h. */
    service_time_epoch_to_calendar(service_time_current_epoch_get(), &now);
    audio_uart_buffer_zero(clock, sizeof(clock), 0u);
    g2_navigation_clock_hour_2007475c = now.hour;
    g2_navigation_clock_minute_20074760 = now.minute;
    if (audio_time_format_mode_46650c() == 1u) {
        uint32_t hour = now.hour % 12u;

        if (hour == 0u)
            hour = 12u;
        (void)audio_ble_format_to_buffer(clock, fmt_clock_12h, hour, now.minute, (now.hour < 12u) ? s_am : s_pm);
    } else {
        (void)audio_ble_format_to_buffer(clock, fmt_clock_24h, now.hour, now.minute);
    }

    g2_nav_a_clock_label_200747e0 = audio_uart_page_499416(a);
    if (data->info.valid == 1u)
        audio_uart_page_49942e(g2_nav_a_clock_label_200747e0, clock);
    label_font_white(g2_nav_a_clock_label_200747e0);
    audio_uart_page_43f506(g2_nav_a_clock_label_200747e0, LV_SIZE_CONTENT);
    audio_uart_page_43f568(g2_nav_a_clock_label_200747e0, LV_SIZE_CONTENT);
    audio_uart_page_43f0e0(g2_nav_a_clock_label_200747e0, 0);
    audio_uart_page_43f142(g2_nav_a_clock_label_200747e0, 0);
    map_child_flags(g2_nav_a_clock_label_200747e0);
    audio_uart_page_43f66c(g2_nav_a_clock_label_200747e0);
    width = audio_uart_lv_obj_width_43fd9e(g2_nav_a_clock_label_200747e0);

    g2_navigation_a_clock_icon_200747e4 = audio_uart_page_498668(a);
    if (data->info.navigate_work_method == 1u)
        audio_uart_page_498680(g2_navigation_a_clock_icon_200747e4, g2_navigation_img_clock_mode1_7747c8);
    else
        audio_uart_page_498680(g2_navigation_a_clock_icon_200747e4, g2_navigation_img_clock_76a86c);
    audio_uart_page_43f506(g2_navigation_a_clock_icon_200747e4, 0x18);
    audio_uart_page_43f568(g2_navigation_a_clock_icon_200747e4, 0x18);
    audio_uart_page_43f0e0(g2_navigation_a_clock_icon_200747e4, width + 0x10);
    audio_uart_page_43f142(g2_navigation_a_clock_icon_200747e4, 2);
    map_child_flags(g2_navigation_a_clock_icon_200747e4);

    g2_navigation_a_text_88_label_200747dc = audio_uart_page_499416(a);
    if (data->info.valid == 1u)
        audio_uart_page_49942e(g2_navigation_a_text_88_label_200747dc, data->info.spend_time);
    audio_uart_page_43f506(g2_navigation_a_text_88_label_200747dc, LV_SIZE_CONTENT);
    audio_uart_page_43f568(g2_navigation_a_text_88_label_200747dc, 0x1c);
    label_font_white(g2_navigation_a_text_88_label_200747dc);
    audio_uart_page_43f6b8(g2_navigation_a_text_88_label_200747dc, LV_ALIGN_TOP_RIGHT, 0, 0);
    map_child_flags(g2_navigation_a_text_88_label_200747dc);

    g2_navigation_a_text_c8_label_200747d8 = audio_uart_page_499416(a);
    if (data->info.valid == 1u)
        audio_uart_page_49942e(g2_navigation_a_text_c8_label_200747d8, data->info.remain_distance);
    label_font_white(g2_navigation_a_text_c8_label_200747d8);
    audio_uart_page_43f506(g2_navigation_a_text_c8_label_200747d8, LV_SIZE_CONTENT);
    audio_uart_page_43f568(g2_navigation_a_text_c8_label_200747d8, 0x1c);
    audio_uart_page_43f6d6(g2_navigation_a_text_c8_label_200747d8, g2_navigation_a_text_88_label_200747dc,
                           LV_ALIGN_OUT_LEFT_MID, -16, 0);
    map_child_flags(g2_navigation_a_text_c8_label_200747d8);

    /* Mini map: 120x120 rotated image at (456, 168), a 20x20 position marker and four
     * 6x6 corner masks; a "loading" label covers it until the first mini map arrives. */
    g2_nav_a_compass_img_200747e8 = navigation_create_rotated_img_54e44c(a, 0x78, 0x78, 0x1c8, 0xa8);
    g2_navigation_a_marker_img_20074784 = map_image(a, g2_navigation_img_marker_76acb0, 0x14, 0x14, 0x1fa, 0xda);
    g2_navigation_a_corner_tl_img_20074788 = map_image(a, g2_navigation_img_corner_tl_76c4f8, 6, 6, 0x1c8, 0xa8);
    g2_navigation_a_corner_tr_img_2007478c = map_image(a, g2_navigation_img_corner_tr_770ac0, 6, 6, 0x23a, 0xa8);
    g2_navigation_a_corner_bl_img_20074790 = map_image(a, g2_navigation_img_corner_bl_76be84, 6, 6, 0x1c8, 0x11a);
    g2_navigation_a_corner_br_img_20074794 = map_image(a, g2_navigation_img_corner_br_7709a8, 6, 6, 0x23a, 0x11a);

    g2_nav_a_loading_label_200747ec = audio_uart_page_499416(a);
    audio_uart_page_43f506(g2_nav_a_loading_label_200747ec, 0x78);
    audio_uart_page_43f568(g2_nav_a_loading_label_200747ec, 0x78);
    audio_uart_page_49942e(g2_nav_a_loading_label_200747ec, localized(key_loading_mini));
    label_font_white(g2_nav_a_loading_label_200747ec);
    audio_uart_page_44129e(g2_nav_a_loading_label_200747ec, LV_OPA_COVER, LV_PART_MAIN);
    audio_uart_page_44127e(g2_nav_a_loading_label_200747ec, audio_uart_page_44104c(0u), LV_PART_MAIN);
    audio_uart_page_43f0e0(g2_nav_a_loading_label_200747ec, 0x1c8);
    audio_uart_page_43f142(g2_nav_a_loading_label_200747ec, 0xa8);
    audio_uart_page_43ded4(g2_nav_a_loading_label_200747ec, LV_OBJ_FLAG_ADV_HITTEST);
    if (data->mini_map_ready == 1u) {
        /* Rotate opposite to the heading, in 0.1 degree units. */
        (void)navigation_update_rotated_img_54e660(g2_nav_a_compass_img_200747e8,
                                                   g2_navigation_mini_map_decode_2032dc74, 0xaa, 0xaa,
                                                   3600 - g2_nav_compass_heading_2007480c * 10, 4u);
        audio_uart_page_43ded4(g2_nav_a_loading_label_200747ec, LV_OBJ_FLAG_HIDDEN);
    } else {
        audio_uart_page_43dfa4(g2_nav_a_loading_label_200747ec, LV_OBJ_FLAG_HIDDEN);
    }

    /* Layer B: clock row and the max map. */
    g2_nav_b_clock_label_20074764 = audio_uart_page_499416(b);
    audio_uart_page_49942e(g2_nav_b_clock_label_20074764, clock);
    label_font_white(g2_nav_b_clock_label_20074764);
    audio_uart_page_43f506(g2_nav_b_clock_label_20074764, LV_SIZE_CONTENT);
    audio_uart_page_43f568(g2_nav_b_clock_label_20074764, 0x20);
    audio_uart_page_43f0e0(g2_nav_b_clock_label_20074764, 0);
    audio_uart_page_43f142(g2_nav_b_clock_label_20074764, 0);
    map_child_flags(g2_nav_b_clock_label_20074764);
    audio_uart_page_43f66c(g2_nav_b_clock_label_20074764);
    width = audio_uart_lv_obj_width_43fd9e(g2_nav_b_clock_label_20074764);

    g2_navigation_b_clock_icon_20074774 = audio_uart_page_498668(b);
    if (data->info.navigate_work_method == 1u)
        audio_uart_page_498680(g2_navigation_b_clock_icon_20074774, g2_navigation_img_clock_mode1_7747c8);
    else
        audio_uart_page_498680(g2_navigation_b_clock_icon_20074774, g2_navigation_img_clock_76a86c);
    audio_uart_page_43f506(g2_navigation_b_clock_icon_20074774, 0x18);
    audio_uart_page_43f568(g2_navigation_b_clock_icon_20074774, 0x18);
    audio_uart_page_43f0e0(g2_navigation_b_clock_icon_20074774, width + 0x10);
    audio_uart_page_43f142(g2_navigation_b_clock_icon_20074774, 2);
    map_child_flags(g2_navigation_b_clock_icon_20074774);

    g2_navigation_b_text_88_label_2007476c = audio_uart_page_499416(b);
    if (data->info.valid == 1u)
        audio_uart_page_49942e(g2_navigation_b_text_88_label_2007476c, data->info.spend_time);
    label_font_white(g2_navigation_b_text_88_label_2007476c);
    audio_uart_page_43f506(g2_navigation_b_text_88_label_2007476c, LV_SIZE_CONTENT);
    audio_uart_page_43f568(g2_navigation_b_text_88_label_2007476c, 0x20);
    audio_uart_page_43f6b8(g2_navigation_b_text_88_label_2007476c, LV_ALIGN_TOP_RIGHT, 0, 0);
    map_child_flags(g2_navigation_b_text_88_label_2007476c);

    g2_navigation_b_text_c8_label_20074768 = audio_uart_page_499416(b);
    if (data->info.valid == 1u)
        audio_uart_page_49942e(g2_navigation_b_text_c8_label_20074768, data->info.remain_distance);
    label_font_white(g2_navigation_b_text_c8_label_20074768);
    audio_uart_page_43f506(g2_navigation_b_text_c8_label_20074768, LV_SIZE_CONTENT);
    audio_uart_page_43f568(g2_navigation_b_text_c8_label_20074768, 0x20);
    audio_uart_page_43f6d6(g2_navigation_b_text_c8_label_20074768, g2_navigation_b_text_88_label_2007476c,
                           LV_ALIGN_OUT_LEFT_MID, -16, 0);
    map_child_flags(g2_navigation_b_text_c8_label_20074768);

    g2_navigation_b_text_148_label_20074770 = audio_uart_page_499416(b);
    if (data->info.valid == 1u)
        audio_uart_page_49942e(g2_navigation_b_text_148_label_20074770, data->info.speed);
    label_font_white(g2_navigation_b_text_148_label_20074770);
    audio_uart_page_43f506(g2_navigation_b_text_148_label_20074770, LV_SIZE_CONTENT);
    audio_uart_page_43f568(g2_navigation_b_text_148_label_20074770, 0x20);
    if (data->info.navigate_work_method == 1u) {
        audio_uart_page_43f09a(g2_navigation_b_text_148_label_20074770, -100, -100);
        audio_uart_page_43ded4(g2_navigation_b_text_148_label_20074770, LV_OBJ_FLAG_HIDDEN);
    } else {
        audio_uart_page_43f6d6(g2_navigation_b_text_148_label_20074770, g2_navigation_b_text_c8_label_20074768,
                               LV_ALIGN_OUT_LEFT_MID, -16, 0);
        audio_uart_page_43dfa4(g2_navigation_b_text_148_label_20074770, LV_OBJ_FLAG_HIDDEN);
    }
    map_child_flags(g2_navigation_b_text_148_label_20074770);

    g2_navigation_b_text_108_label_20074778 = audio_uart_page_499416(b);
    if (data->info.valid == 1u)
        audio_uart_page_49942e(g2_navigation_b_text_108_label_20074778, data->info.eta_time);
    label_font_white(g2_navigation_b_text_108_label_20074778);
    audio_uart_page_43f506(g2_navigation_b_text_108_label_20074778, LV_SIZE_CONTENT);
    audio_uart_page_43f568(g2_navigation_b_text_108_label_20074778, 0x20);
    if (data->info.navigate_work_method == 1u)
        audio_uart_page_43f6d6(g2_navigation_b_text_108_label_20074778, g2_navigation_b_text_c8_label_20074768,
                               LV_ALIGN_OUT_LEFT_MID, -16, 0);
    else
        audio_uart_page_43f6d6(g2_navigation_b_text_108_label_20074778, g2_navigation_b_text_148_label_20074770,
                               LV_ALIGN_OUT_LEFT_MID, -16, 0);
    map_child_flags(g2_navigation_b_text_108_label_20074778);

    g2_nav_max_map_img_2007477c = navigation_create_max_map_5456f6(b, 0, 0x20);

    g2_nav_b_loading_label_20074780 = audio_uart_page_499416(b);
    audio_uart_page_44129e(g2_nav_b_loading_label_20074780, LV_OPA_COVER, LV_PART_MAIN);
    audio_uart_page_44127e(g2_nav_b_loading_label_20074780, audio_uart_page_44104c(0u), LV_PART_MAIN);
    audio_uart_page_49942e(g2_nav_b_loading_label_20074780, localized(key_loading_full));
    label_font_white(g2_nav_b_loading_label_20074780);
    audio_uart_page_44145a(g2_nav_b_loading_label_20074780, LV_TEXT_ALIGN_CENTER, LV_PART_MAIN);
    audio_uart_page_43f506(g2_nav_b_loading_label_20074780, NAV_SCREEN_W);
    audio_uart_page_43f568(g2_nav_b_loading_label_20074780, (int32_t)NAV_MAX_MAP_H);
    audio_uart_page_43f0e0(g2_nav_b_loading_label_20074780, 0);
    audio_uart_page_43f142(g2_nav_b_loading_label_20074780, 0x20);
    audio_uart_page_43ded4(g2_nav_b_loading_label_20074780, LV_OBJ_FLAG_ADV_HITTEST);
    if (data->max_map_ready == 1u) {
        audio_uart_page_43ded4(g2_nav_b_loading_label_20074780, LV_OBJ_FLAG_HIDDEN);
        (void)navigation_set_max_map_data_5458a2(g2_nav_max_map_img_2007477c,
                                                 g2_navigation_max_map_decode_202f3a44);
    } else {
        audio_uart_page_43dfa4(g2_nav_b_loading_label_20074780, LV_OBJ_FLAG_HIDDEN);
    }
    NAV_LOG(4, s_map_fn, 0x4f5, 0x10000000u, s_map_done, s_map_done_s);
    return 0;
}

void navigation_ui_create_break_exit_page_5476e4(void)
{
    void *label;

    NAV_LOG(4, s_break_fn, 0x4fb, 0x10000000u, s_break_msg, s_break_msg_s);
    label = status_label();
    audio_uart_page_49942e(label, localized(key_timeout));
    label_font_white(label);
}

void navigation_ui_create_none_location_list_page_5477ac(void)
{
    void *label;

    NAV_LOG(4, s_none_fn, 0x507, 0x10000000u, s_none_msg, s_none_msg_s);
    if (g2_navigation_page_root_20074718 != NULL)
        audio_uart_page_44d878(g2_navigation_page_root_20074718);
    label = audio_uart_page_499416(g2_navigation_page_root_20074718);
    audio_uart_page_43f506(label, LV_SIZE_CONTENT);
    audio_uart_page_43f568(label, LV_SIZE_CONTENT);
    lv_obj_center_4409fa(label);
    audio_uart_page_49942e(label, localized(key_no_favorites));
    label_font_white(label);
    audio_uart_page_44145a(label, LV_TEXT_ALIGN_CENTER, LV_PART_MAIN);
}

/* reason: 1 location too far, 2 something went wrong, 3 no location access,
 * 4 unlock the phone; anything else shows "too far". */
void navigation_ui_startup_failed_exit_page_54787c(uint32_t reason)
{
    void *label;
    const char *key;

    NAV_LOG(4, s_failed_fn, 0x518, 0x10000000u, s_failed_msg, s_failed_msg_s);
    label = status_label();
    switch (reason) {
    case 2u:
        key = key_went_wrong;
        break;
    case 3u:
        key = key_no_access;
        break;
    case 4u:
        key = key_unlock;
        break;
    case 1u:
    default:
        key = key_too_far;
        break;
    }
    audio_uart_page_49942e(label, localized(key));
    label_font_white(label);
    audio_uart_page_44145a(label, LV_TEXT_ALIGN_CENTER, LV_PART_MAIN);
}

void navigation_ui_completed_exit_page_5479c8(void)
{
    void *label;

    NAV_LOG(4, s_completed_fn, 0x536, 0x10000000u, s_completed_msg, s_completed_msg_s);
    label = status_label();
    audio_uart_page_49942e(label, localized(key_complete));
    label_font_white(label);
}
