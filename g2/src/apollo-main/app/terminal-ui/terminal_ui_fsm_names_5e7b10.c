/* Stock Terminal UI FSM state/event name lookups and RAM pointer slots. */
#include <stdint.h>

/* Stock .data initialises both tables with ROM name strings (init image
 * 0x20003ea4..0x20003f7b); nothing writes them at runtime. */
const char *audio_terminal_ui_state_names[13]
    __attribute__((section(".data.opencfw.terminal.ui_state_names"), aligned(4), used)) = {
    "TERMINAL_UI_STATE_CLOSED", /* ROM 0x7732e4 */
    "TERMINAL_UI_STATE_BOOTSTRAP", /* ROM 0x773300 */
    "TERMINAL_UI_STATE_IDLE", /* ROM 0x77ca54 */
    "TERMINAL_UI_STATE_BLOCKED", /* ROM 0x77331c */
    "TERMINAL_UI_STATE_VOICE_CAPTURING", /* ROM 0x75b6ac */
    "TERMINAL_UI_STATE_ASR_STREAMING", /* ROM 0x7664f0 */
    "TERMINAL_UI_STATE_ASR_FINAL", /* ROM 0x773338 */
    "TERMINAL_UI_STATE_AGENT_PROCESSING", /* ROM 0x75b6d0 */
    "TERMINAL_UI_STATE_AGENT_INTERRUPT_CONFIRM", /* ROM 0x745014 */
    "TERMINAL_UI_STATE_QUERY_PENDING", /* ROM 0x766510 */
    "TERMINAL_UI_STATE_QUERY_NOTIFICATION", /* ROM 0x74f924 */
    "TERMINAL_UI_STATE_SESSION_LIST", /* ROM 0x766530 */
    "TERMINAL_UI_STATE_NEW_SESSION_PENDING", /* ROM 0x74f94c */
};
const char *audio_terminal_ui_event_names[40]
    __attribute__((section(".data.opencfw.terminal.ui_event_names"), aligned(4), used)) = {
    "TERMINAL_UI_EVENT_NONE", /* ROM 0x77ca84 */
    "TERMINAL_UI_EVENT_DISPLAY_ENTER", /* ROM 0x766550 */
    "TERMINAL_UI_EVENT_BLE_DISCONNECTED", /* ROM 0x75b6f4 */
    "TERMINAL_UI_EVENT_HOST_SETUP_PENDING", /* ROM 0x74f974 */
    "TERMINAL_UI_EVENT_HOST_OFFLINE", /* ROM 0x766570 */
    "TERMINAL_UI_EVENT_RESTORE_TO_IDLE", /* ROM 0x75b718 */
    "TERMINAL_UI_EVENT_RESTORE_TO_AGENT_PROCESSING", /* ROM 0x739ac4 */
    "TERMINAL_UI_EVENT_RESTORE_TO_QUERY_PENDING", /* ROM 0x745040 */
    "TERMINAL_UI_EVENT_VOICE_START", /* ROM 0x766590 */
    "TERMINAL_UI_EVENT_VOICE_STOP", /* ROM 0x7665b0 */
    "TERMINAL_UI_EVENT_ASR_UPDATE", /* ROM 0x7665d0 */
    "TERMINAL_UI_EVENT_ASR_FINAL_RECEIVED", /* ROM 0x74f99c */
    "TERMINAL_UI_EVENT_ASR_FAIL", /* ROM 0x773354 */
    "TERMINAL_UI_EVENT_INPUT_CONFIRM", /* ROM 0x7665f0 */
    "TERMINAL_UI_EVENT_INPUT_CANCEL", /* ROM 0x766610 */
    "TERMINAL_UI_EVENT_SESSION_STATUS_UPDATE", /* ROM 0x74f9c4 */
    "TERMINAL_UI_EVENT_AGENT_DONE", /* ROM 0x766630 */
    "TERMINAL_UI_EVENT_AGENT_RESET", /* ROM 0x766650 */
    "TERMINAL_UI_EVENT_CONTENT_UPDATE", /* ROM 0x75b73c */
    "TERMINAL_UI_EVENT_CONTENT_TRIGGER", /* ROM 0x75b760 */
    "TERMINAL_UI_EVENT_UPDATE_RESPONSE_ELAPSED", /* ROM 0x74506c */
    "TERMINAL_UI_EVENT_QUERY_SHOW", /* ROM 0x766670 */
    "TERMINAL_UI_EVENT_QUERY_NOTIFICATION_SHOW", /* ROM 0x745098 */
    "TERMINAL_UI_EVENT_QUERY_NOTIFICATION_ACTIVATE", /* ROM 0x739af4 */
    "TERMINAL_UI_EVENT_QUERY_NOTIFICATION_DISMISS", /* ROM 0x739b24 */
    "TERMINAL_UI_EVENT_QUERY_REPLY", /* ROM 0x766690 */
    "TERMINAL_UI_EVENT_INTERRUPT_CONFIRM_SHOW", /* ROM 0x7450c4 */
    "TERMINAL_UI_EVENT_SESSION_LIST_SHOW", /* ROM 0x75b784 */
    "TERMINAL_UI_EVENT_SESSION_LIST_UPDATE", /* ROM 0x74f9ec */
    "TERMINAL_UI_EVENT_SESSION_LIST_SELECT", /* ROM 0x74fa14 */
    "TERMINAL_UI_EVENT_SESSION_LIST_CLOSE", /* ROM 0x74fa3c */
    "TERMINAL_UI_EVENT_SESSION_SWITCH_RESULT", /* ROM 0x74fa64 */
    "TERMINAL_UI_EVENT_NEW_SESSION_RESULT_SUCCESS", /* ROM 0x739b54 */
    "TERMINAL_UI_EVENT_NEW_SESSION_RESULT_FAILED", /* ROM 0x7450f0 */
    "TERMINAL_UI_EVENT_SESSION_LIST_RETURN", /* ROM 0x74fa8c */
    "TERMINAL_UI_EVENT_SESSION_ID_CHANGED", /* ROM 0x74fab4 */
    "TERMINAL_UI_EVENT_SCROLL_UP", /* ROM 0x773370 */
    "TERMINAL_UI_EVENT_SCROLL_DOWN", /* ROM 0x7666b0 */
    "TERMINAL_UI_EVENT_AGENT_INTERRUPT", /* ROM 0x75b7a8 */
    "TERMINAL_UI_EVENT_USER_EXIT", /* ROM 0x77338c */
};
_Static_assert(sizeof audio_terminal_ui_state_names == 52u,
               "stock Terminal state-name pointer extent");
_Static_assert(sizeof audio_terminal_ui_event_names == 160u,
               "stock Terminal event-name pointer extent");

static const char unknown_state[] = "UNKNOWN_STATE";
static const char unknown_event[] = "UNKNOWN_EVENT";

const char *audio_terminal_ui_state_name_5e7b10(uint32_t state) {
    uint8_t index = (uint8_t)state;
    return index < 13u ? audio_terminal_ui_state_names[index] : unknown_state;
}

const char *audio_terminal_ui_event_name_5e7b2a(uint32_t event) {
    uint8_t index = (uint8_t)event;
    return index < 40u ? audio_terminal_ui_event_names[index] : unknown_event;
}
