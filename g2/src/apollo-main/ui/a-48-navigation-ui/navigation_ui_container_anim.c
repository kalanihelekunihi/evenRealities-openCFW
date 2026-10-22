/* Stock D:\01_workspace\s200_ap510b_iar_git\app\gui\navigation\navigation_ui.c (log tag
 * "navigation.ui"): map page layer cross-fade. Native opa exec callback 0x547abc..0x547ad1,
 * navigation_show_container_B_with_animation 0x547ad2..0x547dbb,
 * navigation_hide_container_B_with_animation 0x547dcc..0x547ebb,
 * navigation_container_A_fade_out_complete_cb 0x547ec8..0x547fd9,
 * navigation_container_B_fade_in_complete_cb 0x548014..0x548295 and
 * navigation_container_A_fade_in_complete_cb 0x5482c4..0x548473; literal pools
 * 0x54854c..0x5485c3 and 0x548b3c..0x548b97 (shared with segment a-49).
 *
 * Show B: fade A 255 -> 0, then hide A, show B and fade B 0 -> 255 (100 ms each, ease in
 * out). Hide B: fade B 255 -> 0; 0x548484 (a-49) then restores A. When a fade finishes, one
 * queued 5-byte page event is popped; LV_EVENT_CLICKED toggles B again. */
#include "navigation_ui_private.h"

static const char s_show_fn[] = "navigation_show_container_B_with_animation"; /* ROM 0x74041c */
static const char s_busy[] = "Animation already running or containers not initialized"; /* ROM 0x7204e8 */
static const char s_busy_s[] = "[navigation.ui]Animation already running or containers not initialized"; /* ROM 0x6fb774 */
static const char s_busy_state[] = "animation_running=%d, mini_map=%p, max_map=%p"; /* ROM 0x735a14 */
static const char s_busy_state_s[] = "[navigation.ui]animation_running=%d, mini_map=%p, max_map=%p"; /* ROM 0x70cf64 */
static const char s_show_start[] = "Starting animation: show container B"; /* ROM 0x74b6bc */
static const char s_show_start_s[] = "[navigation.ui]Starting animation: show container B"; /* ROM 0x72b05c */
static const char s_a_visible[] = "Container A visible: %d"; /* ROM 0x779934 */
static const char s_a_visible_s[] = "[navigation.ui]Container A visible: %d"; /* ROM 0x74b6e4 */
static const char s_b_visible[] = "Container B visible: %d"; /* ROM 0x77994c */
static const char s_b_visible_s[] = "[navigation.ui]Container B visible: %d"; /* ROM 0x74b70c */
static const char s_a_opa[] = "Container A opacity: %d"; /* ROM 0x779964 */
static const char s_a_opa_s[] = "[navigation.ui]Container A opacity: %d"; /* ROM 0x74b734 */
static const char s_b_opa[] = "Container B opacity: %d"; /* ROM 0x77997c */
static const char s_b_opa_s[] = "[navigation.ui]Container B opacity: %d"; /* ROM 0x74b75c */
static const char s_hide_fn[] = "navigation_hide_container_B_with_animation"; /* ROM 0x740448 */
static const char s_hide_start[] = "Starting animation: hide container B"; /* ROM 0x74b784 */
static const char s_hide_start_s[] = "[navigation.ui]Starting animation: hide container B"; /* ROM 0x72b090 */
static const char s_a_out_fn[] = "navigation_container_A_fade_out_complete_cb"; /* ROM 0x740474 */
static const char s_a_out[] = "Container A fade out complete, showing container B"; /* ROM 0x72b0c4 */
static const char s_a_out_s[] = "[navigation.ui]Container A fade out complete, showing container B"; /* ROM 0x703f0c */
static const char s_b_before[] = "Before fade in: Container B opacity: %d"; /* ROM 0x74b7ac */
static const char s_b_before_s[] = "[navigation.ui]Before fade in: Container B opacity: %d"; /* ROM 0x720520 */
static const char s_b_in_fn[] = "navigation_container_B_fade_in_complete_cb"; /* ROM 0x7404a0 */
static const char s_b_in[] = "Container B fade in complete"; /* ROM 0x762630 */
static const char s_b_in_s[] = "[navigation.ui]Container B fade in complete"; /* ROM 0x7404cc */
static const char s_b_final_visible[] = "Container B final visible: %d"; /* ROM 0x762650 */
static const char s_b_final_visible_s[] = "[navigation.ui]Container B final visible: %d"; /* ROM 0x735a44 */
static const char s_b_final_opa[] = "Container B final opacity: %d"; /* ROM 0x762670 */
static const char s_b_final_opa_s[] = "[navigation.ui]Container B final opacity: %d"; /* ROM 0x735a74 */
static const char s_fifo_pop[] = "fifo is not empty,pop event from fifo"; /* ROM 0x74b7d4 */
static const char s_fifo_pop_s[] = "[navigation.ui]fifo is not empty,pop event from fifo"; /* ROM 0x720558 */
static const char s_clicked[] = "event_type == LV_EVENT_CLICKED"; /* ROM 0x762690 */
static const char s_clicked_s[] = "[navigation.ui]event_type == LV_EVENT_CLICKED"; /* ROM 0x735aa4 */
static const char s_reflash_show[] = "navigation_ui_reflash_page_handler: show container B"; /* ROM 0x720590 */
static const char s_reflash_show_s[] =
    "[navigation.ui]navigation_ui_reflash_page_handler: show container B"; /* ROM 0x703f50 */
static const char s_reflash_hide[] = "navigation_ui_reflash_page_handler: hide container B"; /* ROM 0x7205c8 */
static const char s_reflash_hide_s[] =
    "[navigation.ui]navigation_ui_reflash_page_handler: hide container B"; /* ROM 0x703f94 */
static const char s_a_in_fn[] = "navigation_container_A_fade_in_complete_cb"; /* ROM 0x7404f8 */
static const char s_a_in[] = "Container A fade in complete"; /* ROM 0x7626b0 */
static const char s_a_in_s[] = "[navigation.ui]Container A fade in complete"; /* ROM 0x740524 */

#define NAV_FADE_MS 100

void navigation_container_opa_anim_exec_cb_547abc(void *obj, int32_t opa)
{
    audio_uart_display_audio_reset_441488(obj, (uint8_t)opa, LV_PART_MAIN);
    audio_uart_page_invalidate_440656(obj);
}

static uint32_t visible(void *obj)
{
    return (audio_uart_lv_obj_has_flag_43e0e0(obj, LV_OBJ_FLAG_HIDDEN) ^ 1u) & 0xffu;
}

static void start_fade(void *obj, int32_t from, int32_t to, void (*done)(void *))
{
    g2_lv_anim_t anim;

    audio_uart_lv_anim_init_4503d6(&anim);
    anim.var = obj;
    anim.exec_cb = navigation_container_opa_anim_exec_cb_547abc;
    audio_uart_lv_anim_values_4506ce(&anim, from, to);
    anim.duration = NAV_FADE_MS;
    anim.path_cb = audio_uart_lv_anim_path_450688;
    anim.completed_cb = done;
    (void)audio_uart_lv_anim_start_450408(&anim);
}

void navigation_show_container_B_with_animation_547ad2(void)
{
    void *a = g2_navigation_container_a_200747c0;
    void *b = g2_navigation_container_b_200747c4;

    if (g2_nav_animation_running_20074fec != 0u || g2_navigation_container_a_200747c0 == NULL ||
        g2_navigation_container_b_200747c4 == NULL) {
        NAV_LOG(2, s_show_fn, 0x54b, 0x8000000u, s_busy, s_busy_s);
        NAV_LOG(2, s_show_fn, 0x54d, 0x8c00000u, s_busy_state, s_busy_state_s,
                (uint32_t)g2_nav_animation_running_20074fec, g2_navigation_container_a_200747c0,
                g2_navigation_container_b_200747c4);
        return;
    }
    NAV_LOG(4, s_show_fn, 0x552, 0x10000000u, s_show_start, s_show_start_s);
    if ((audio_log_flags() & 2u) != 0u)
        audio_log_extended(4, nav_tag, nav_file, s_show_fn, 0x553, s_a_visible, visible(a));
    if ((audio_log_flags() & 1u) != 0u || (audio_log_flags() & 4u) != 0u)
        (void)compress_log_output(0x10400000u, s_a_visible_s, s_a_visible_s, visible(a));
    if ((audio_log_flags() & 2u) != 0u)
        audio_log_extended(4, nav_tag, nav_file, s_show_fn, 0x554, s_b_visible, visible(b));
    if ((audio_log_flags() & 1u) != 0u || (audio_log_flags() & 4u) != 0u)
        (void)compress_log_output(0x10400000u, s_b_visible_s, s_b_visible_s, visible(b));
    if ((audio_log_flags() & 2u) != 0u)
        audio_log_extended(4, nav_tag, nav_file, s_show_fn, 0x555, s_a_opa,
                           (uint32_t)lv_obj_get_style_opa_545588(a, LV_PART_MAIN));
    if ((audio_log_flags() & 1u) != 0u || (audio_log_flags() & 4u) != 0u)
        (void)compress_log_output(0x10400000u, s_a_opa_s, s_a_opa_s,
                                  (uint32_t)lv_obj_get_style_opa_545588(a, LV_PART_MAIN));
    if ((audio_log_flags() & 2u) != 0u)
        audio_log_extended(4, nav_tag, nav_file, s_show_fn, 0x556, s_b_opa,
                           (uint32_t)lv_obj_get_style_opa_545588(b, LV_PART_MAIN));
    if ((audio_log_flags() & 1u) != 0u || (audio_log_flags() & 4u) != 0u)
        (void)compress_log_output(0x10400000u, s_b_opa_s, s_b_opa_s,
                                  (uint32_t)lv_obj_get_style_opa_545588(b, LV_PART_MAIN));

    audio_uart_display_audio_reset_441488(a, LV_OPA_COVER, LV_PART_MAIN);
    audio_uart_page_invalidate_440656(a);
    g2_nav_animation_running_20074fec = 1u;
    start_fade(a, LV_OPA_COVER, LV_OPA_TRANSP, navigation_container_A_fade_out_complete_cb_547ec8);
}

void navigation_hide_container_B_with_animation_547dcc(void)
{
    if (g2_nav_animation_running_20074fec != 0u || g2_navigation_container_a_200747c0 == NULL ||
        g2_navigation_container_b_200747c4 == NULL) {
        NAV_LOG(2, s_hide_fn, 0x56d, 0x8000000u, s_busy, s_busy_s);
        return;
    }
    g2_nav_animation_running_20074fec = 1u;
    NAV_LOG(4, s_hide_fn, 0x572, 0x10000000u, s_hide_start, s_hide_start_s);
    start_fade(g2_navigation_container_b_200747c4, LV_OPA_COVER, LV_OPA_TRANSP,
               navigation_container_B_fade_out_complete_cb_548484);
}

void navigation_container_A_fade_out_complete_cb_547ec8(void *anim)
{
    void *b = g2_navigation_container_b_200747c4;

    (void)anim;
    NAV_LOG(4, s_a_out_fn, 0x582, 0x10000000u, s_a_out, s_a_out_s);
    audio_uart_page_43dfa4(b, LV_OBJ_FLAG_HIDDEN);
    audio_uart_display_audio_reset_441488(b, LV_OPA_TRANSP, LV_PART_MAIN);
    audio_uart_page_43ded4(g2_navigation_container_a_200747c0, LV_OBJ_FLAG_HIDDEN);
    audio_uart_page_invalidate_440656(g2_navigation_container_a_200747c0);
    audio_uart_page_invalidate_440656(b);
    if ((audio_log_flags() & 2u) != 0u)
        audio_log_extended(4, nav_tag, nav_file, s_a_out_fn, 0x58e, s_b_before,
                           (uint32_t)lv_obj_get_style_opa_545588(b, LV_PART_MAIN));
    if ((audio_log_flags() & 1u) != 0u || (audio_log_flags() & 4u) != 0u)
        (void)compress_log_output(0x10400000u, s_b_before_s, s_b_before_s,
                                  (uint32_t)lv_obj_get_style_opa_545588(b, LV_PART_MAIN));
    start_fade(b, LV_OPA_TRANSP, LV_OPA_COVER, navigation_container_B_fade_in_complete_cb_548014);
}

/* Shared tail of both fade-in callbacks: pop one queued event; a click toggles B. */
static void replay_queued_event(const char *fn, uint32_t line_pop, uint32_t line_click,
                                uint32_t line_show, uint32_t line_hide)
{
    uint8_t event[5];

    g2_nav_animation_running_20074fec = 0u;
    if (ui_common_api_fn_00509dfa(g2_nav_event_fifo_20074734) != 0)
        return;
    NAV_LOG(4, fn, line_pop, 0x10000000u, s_fifo_pop, s_fifo_pop_s);
    audio_uart_buffer_zero(event, sizeof(event), 0u);
    (void)ui_common_api_fn_00509e14(g2_nav_event_fifo_20074734, event, sizeof(event));
    if (event[0] != LV_EVENT_CLICKED)
        return;
    NAV_LOG(4, fn, line_click, 0x10000000u, s_clicked, s_clicked_s);
    if (g2_nav_container_b_shown_2007473c == 0u) {
        g2_nav_container_b_shown_2007473c = 1u;
        NAV_LOG(4, fn, line_show, 0x10000000u, s_reflash_show, s_reflash_show_s);
        navigation_show_container_B_thunk_54853a();
        return;
    }
    g2_nav_container_b_shown_2007473c = 0u;
    NAV_LOG(4, fn, line_hide, 0x10000000u, s_reflash_hide, s_reflash_hide_s);
    navigation_hide_container_B_thunk_548542();
}

void navigation_container_B_fade_in_complete_cb_548014(void *anim)
{
    void *b = g2_navigation_container_b_200747c4;

    (void)anim;
    NAV_LOG(4, s_b_in_fn, 0x59e, 0x10000000u, s_b_in, s_b_in_s);
    if ((audio_log_flags() & 2u) != 0u)
        audio_log_extended(4, nav_tag, nav_file, s_b_in_fn, 0x59f, s_b_final_visible, visible(b));
    if ((audio_log_flags() & 1u) != 0u || (audio_log_flags() & 4u) != 0u)
        (void)compress_log_output(0x10400000u, s_b_final_visible_s, s_b_final_visible_s,
                                  visible(g2_navigation_container_b_200747c4));
    if ((audio_log_flags() & 2u) != 0u)
        audio_log_extended(4, nav_tag, nav_file, s_b_in_fn, 0x5a0, s_b_final_opa,
                           (uint32_t)lv_obj_get_style_opa_545588(g2_navigation_container_b_200747c4,
                                                                 LV_PART_MAIN));
    if ((audio_log_flags() & 1u) != 0u || (audio_log_flags() & 4u) != 0u)
        (void)compress_log_output(0x10400000u, s_b_final_opa_s, s_b_final_opa_s,
                                  (uint32_t)lv_obj_get_style_opa_545588(g2_navigation_container_b_200747c4,
                                                                        LV_PART_MAIN));
    replay_queued_event(s_b_in_fn, 0x5a4, 0x5aa, 0x5ad, 0x5b1);
}

void navigation_container_A_fade_in_complete_cb_5482c4(void *anim)
{
    (void)anim;
    NAV_LOG(4, s_a_in_fn, 0x5ba, 0x10000000u, s_a_in, s_a_in_s);
    replay_queued_event(s_a_in_fn, 0x5be, 0x5c4, 0x5c7, 0x5cb);
}
