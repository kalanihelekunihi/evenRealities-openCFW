/* conversate_input_event_handler, stock
 * D:\01_workspace\s200_ap510b_iar_git\app\gui\conversate\conversate_ui.c.
 * Native 0x5b15e0..0x5b16cb; literal pool 0x5b1ad4..0x5b1af3.
 *
 * Master arm only: routes an input event to the handler of the current UI
 * state (1 idle page, 2 main page, 3 menu, 4 tag extend page, 5 prep-note
 * extend page). */
#include <stdint.h>

extern uint8_t audio_conversate_ui_state_20071368;            /* RAM 0x20071368 */
extern uint32_t display_driver_uled_mode_45a568(void);        /* device role, 1 = master */
extern void conversate_ui_idle_input_event_handler_5b2642(uint32_t event, const void *param); /* 0x48 closes */
extern void conversate_main_page_input_event_handler_5b2652(uint32_t event, const void *param);
extern void conversate_ui_menu_input_handler(uint32_t event, const void *param);               /* 0x5b5886 */
extern void conversate_tag_extend_page_input_event_handler(uint32_t event, const void *param); /* 0x5b5de4 */
extern void conversate_prep_note_extend_page_input_event_handler_5b7060(uint32_t event, const void *param);
extern uint32_t audio_log_flags(void); /* 0x43d0ce */
extern void audio_log_extended(uint8_t, const char *, const char *, const char *, uint32_t, const char *, ...); /* 0x43d574 */
extern uint32_t compress_log_output(uint32_t, const char *, const char *, ...); /* 0x43ce9e */

static const char module_tag[] = "conversate.ui"; /* ROM 0x7857f0 */
static const char source_file[] = "D:\\01_workspace\\s200_ap510b_iar_git\\app\\gui\\conversate\\conversate_ui.c"; /* ROM 0x6f956c */
static const char fn_name[] = "conversate_input_event_handler"; /* ROM 0x75eb70 */
static const char not_master[] = "conversate input event handler, but role is not master"; /* ROM 0x71d110 */
static const char not_master_c[] = "[conversate.ui]conversate input event handler, but role is not master"; /* ROM 0x6f95b4 */
static const char no_handler[] = "current state do not handle input event, state: %d"; /* ROM 0x727e30 */
static const char no_handler_c[] = "[conversate.ui]current state do not handle input event, state: %d"; /* ROM 0x70137c */

void conversate_input_event_handler_5b15e0(uint32_t event, const void *param)
{
    if (display_driver_uled_mode_45a568() != 1u) {
        if (audio_log_flags() & 2u)
            audio_log_extended(4u, module_tag, source_file, fn_name, 0x1bbu, not_master);
        if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
            (void)compress_log_output(0x10000000u, not_master_c, not_master_c);
        return;
    }
    switch (audio_conversate_ui_state_20071368) {
    case 1u:
        conversate_ui_idle_input_event_handler_5b2642(event, param);
        return;
    case 2u:
        conversate_main_page_input_event_handler_5b2652(event, param);
        return;
    case 3u:
        conversate_ui_menu_input_handler(event, param);
        return;
    case 4u:
        conversate_tag_extend_page_input_event_handler(event, param);
        return;
    case 5u:
        conversate_prep_note_extend_page_input_event_handler_5b7060(event, param);
        return;
    default:
        break;
    }
    if (audio_log_flags() & 2u)
        audio_log_extended(2u, module_tag, source_file, fn_name, 0x1d1u, no_handler,
                           (uint32_t)audio_conversate_ui_state_20071368);
    if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
        (void)compress_log_output(0x08400000u, no_handler_c, no_handler_c, (uint32_t)audio_conversate_ui_state_20071368);
}
