/* Stock Main low-RAM initialization record supplies these indexed strings. */
#include <stdint.h>

__attribute__((used, section(".g2_conversate_event_names_200004f4"), aligned(4)))
const char *audio_conversate_event_names_200004f4[13] = {
    "CONVERSATE_EVENT_NONE",
    "CONVERSATE_EVENT_START",
    "CONVERSATE_EVENT_PAUSE",
    "CONVERSATE_EVENT_RESUME",
    "CONVERSATE_EVENT_CLOSE",
    "CONVERSATE_EVENT_CONFIG",
    "CONVERSATE_EVENT_MENU_START",
    "CONVERSATE_EVENT_MENU_EXIT",
    "CONVERSATE_EVENT_PREP_NOTE_LIST",
    "CONVERSATE_EVENT_PREP_NOTE_PACKET",
    "CONVERSATE_EVENT_TAG_UPDATE",
    "CONVERSATE_EVENT_TRANSCRIBE_RESULT",
    "CONVERSATE_EVENT_HEARTBEAT",
};

__attribute__((used, section(".g2_conversate_ui_state_names_20000540"), aligned(4)))
const char *audio_conversate_ui_state_names_20000540[7] = {
    "CONVERSATE_UI_STATE_CLOSED",
    "CONVERSATE_UI_STATE_LOADING",
    "CONVERSATE_UI_STATE_MAIN",
    "CONVERSATE_UI_STATE_MENU",
    "CONVERSATE_UI_STATE_TAG_EXTEND",
    "CONVERSATE_UI_STATE_PREP_NOTE_EXTEND",
    "CONVERSATE_UI_STATE_CLOSING",
};

_Static_assert(sizeof(audio_conversate_event_names_200004f4) == 52u,
               "13 event-name pointers");
_Static_assert(sizeof(audio_conversate_ui_state_names_20000540) == 28u,
               "seven UI-state pointers");
