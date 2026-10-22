/* Conversate page input listener, stock
 * D:\01_workspace\s200_ap510b_iar_git\app\gui\conversate\conversate.c
 * (between conversate_action_* and Conversate_ui_event_handler; no own
 * strings). Native 0x5b05d0..0x5b06a9; literal pool words 0x5b0a4c,
 * 0x5b0a74, 0x5b0a78.
 *
 * Same shape as translate_page_event_handler_59efe0: swipe codes 0x44/0x45
 * are mirrored, navigation codes go to conversate_input_event_handler,
 * 0x42/0x43 dim/restore the page root while the UI is in state 2, and
 * 0x4f (page closed) reports the exit to the phone and posts controller
 * event 0x13. Always returns 1 (consumed). */
#include <stddef.h>
#include <stdint.h>

#define CONVERSATE_UI_STATE_MAIN 2u
#define CONVERSATE_STATE_6 6u
#define CONVERSATE_ROOT_OFFSET 0x20u        /* root object at RAM 0x20071388 */
#define CONVERSATE_REPORT_EXIT_KEY 0x40102u
#define CONVERSATE_CTRL_PAGE_CLOSED 0x13u
#define FOREGROUND_NONE 0u
#define FOREGROUND_SELF 0x21u
#define DEVICE_ROLE_MASTER 1u

/* UI state block, base RAM 0x20071368 (+0x00 state byte, +0x20 root obj). */
extern uint8_t audio_conversate_ui_state_20071368;
extern uint32_t audio_conversate_ui_state_get_5b16d0(void);
extern void conversate_input_event_handler_5b15e0(uint32_t event, const void *param);
extern void audio_uart_display_audio_reset_441488(void *obj, uint32_t opa, uint32_t sel); /* lv_obj_set_style_opa */
extern void audio_conversate_report_5b02e4(uint32_t, uint32_t);
extern uint32_t display_driver_uled_mode_45a568(void);        /* device role, 1 = master */
extern void audio_uart_ring_wear_persist_48eb32(uint32_t key, uint32_t length, const void *payload); /* event report */

static const uint32_t conversate_report_exit[2] = { 1u, 1u }; /* ROM 0x78d1fc */

static void *conversate_root(void)
{
    return *(void *const *)(const void *)((const uint8_t *)&audio_conversate_ui_state_20071368 + CONVERSATE_ROOT_OFFSET);
}

uint32_t conversate_page_event_handler_5b05d0(uint32_t unused0, uint32_t unused1, uint32_t event,
                                              const uint32_t *param)
{
    (void)unused0;
    (void)unused1;
    uint32_t mapped = event;
    if (event == 0x44u)
        mapped = 0x45u;
    else if (event == 0x45u)
        mapped = 0x44u;

    switch (event) {
    case 0x0au:
    case 0x44u:
    case 0x45u:
    case 0x48u:
        conversate_input_event_handler_5b15e0(mapped, param);
        break;
    case 0x42u:
        if (audio_conversate_ui_state_get_5b16d0() != CONVERSATE_STATE_6) {
            uint32_t foreground = param != NULL ? *param : FOREGROUND_NONE;
            if (foreground != FOREGROUND_NONE && foreground != FOREGROUND_SELF && conversate_root() != NULL &&
                audio_conversate_ui_state_20071368 == CONVERSATE_UI_STATE_MAIN)
                audio_uart_display_audio_reset_441488(conversate_root(), 0x7fu, 0u);
        }
        break;
    case 0x43u:
        if (audio_conversate_ui_state_get_5b16d0() != CONVERSATE_STATE_6 && conversate_root() != NULL &&
            audio_conversate_ui_state_20071368 == CONVERSATE_UI_STATE_MAIN)
            audio_uart_display_audio_reset_441488(conversate_root(), 0xffu, 0u);
        break;
    case 0x4fu:
        if (display_driver_uled_mode_45a568() == DEVICE_ROLE_MASTER) {
            uint32_t report[2] = { conversate_report_exit[0], conversate_report_exit[1] };
            audio_uart_ring_wear_persist_48eb32(CONVERSATE_REPORT_EXIT_KEY, 2u, report);
        }
        audio_conversate_report_5b02e4(CONVERSATE_CTRL_PAGE_CLOSED, 0u);
        break;
    default:
        break;
    }
    return 1u;
}
