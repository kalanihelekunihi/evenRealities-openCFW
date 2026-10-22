/* Teleprompt UI storage (S5-ui-b storage-definition pass, 2.2.6.10).
 *
 * Stock owner: app\gui\teleprompt\teleprompt_ui.c (ui/a-53-teleprompt-ui,
 * ui/a-54-teleprompt-ui, ui/x-03-teleprompt-ui). The state/event name tables
 * are .data in the stock image (decoded init stream, scatter record
 * 0x75d3f4); their strings and the FSM table are copied from ROM. The FSM
 * actions are the a-54 functions (teleprompt_ui_actions.c); stock pointers
 * are the Thumb addresses (address | 1) of those functions. The file icon
 * (ROM 0x772a24) is in teleprompt_image_assets_data.c. */
#include <stdint.h>
#include "../a-54-teleprompt-ui/teleprompt_ui_internal.h"

/* Same layout as ui/a-53-teleprompt-ui/teleprompt_ui.c. */
typedef struct {
    uint8_t next_state;
    uint8_t reserved_01[3];
    int32_t (*action)(uint8_t state, uint32_t arg);
} g2_teleprompt_ui_transition_data_t;
_Static_assert(sizeof(g2_teleprompt_ui_transition_data_t) == 8, "stock entry is 8 bytes");

int32_t g2_teleprompt_elapsed_20074a80; /* RAM 0x20074a80 */

/* RAM 0x20003dec (.data): TP_UI_STATES = 4. */
const char *const g2_teleprompt_ui_state_names_20003dec[4] = {
    "TELEPROMPT_UI_STATE_CLOSED", /* ROM 0x772d88 */
    "TELEPROMPT_UI_STATE_MENU", /* ROM 0x772da4 */
    "TELEPROMPT_UI_STATE_MAIN", /* ROM 0x772dc0 */
    "TELEPROMPT_UI_STATE_CLOSING", /* ROM 0x772ddc */
};

/* RAM 0x20003e00 (.data): TP_UI_EVENTS = 19. */
const char *const g2_teleprompt_ui_event_names_20003e00[19] = {
    "TELEPROMPT_UI_EVENT_NONE", /* ROM 0x772df8 */
    "TELEPROMPT_UI_EVENT_MENU_START", /* ROM 0x765f70 */
    "TELEPROMPT_UI_EVENT_APP_START", /* ROM 0x765f90 */
    "TELEPROMPT_UI_EVENT_FILE_LIST_UPDATE", /* ROM 0x74f12c */
    "TELEPROMPT_UI_EVENT_MENU_SELECT", /* ROM 0x765fb0 */
    "TELEPROMPT_UI_EVENT_LOADING_DONE", /* ROM 0x75aef0 */
    "TELEPROMPT_UI_EVENT_PAGE_DATA_READY", /* ROM 0x75af14 */
    "TELEPROMPT_UI_EVENT_PAUSE", /* ROM 0x772e14 */
    "TELEPROMPT_UI_EVENT_RESUME", /* ROM 0x772e30 */
    "TELEPROMPT_UI_EVENT_MENU_EXIT", /* ROM 0x765fd0 */
    "TELEPROMPT_UI_EVENT_APP_EXIT", /* ROM 0x765ff0 */
    "TELEPROMPT_UI_EVENT_GIF_COMPLETE", /* ROM 0x75af38 */
    "TELEPROMPT_UI_EVENT_SCROLL_UP", /* ROM 0x766010 */
    "TELEPROMPT_UI_EVENT_SCROLL_DOWN", /* ROM 0x766030 */
    "TELEPROMPT_UI_EVENT_PAGE_SWITCH_PREV", /* ROM 0x74f154 */
    "TELEPROMPT_UI_EVENT_PAGE_SWITCH_NEXT", /* ROM 0x74f17c */
    "TELEPROMPT_UI_EVENT_AI_SYNC", /* ROM 0x772e4c */
    "TELEPROMPT_UI_EVENT_SCROLL_SYNC", /* ROM 0x766050 */
    "TELEPROMPT_UI_EVENT_UPDATE_ELAPSED_TIME", /* ROM 0x74f1a4 */
};

/* ROM 0x6a9cf4: [TP_UI_STATES][TP_UI_EVENTS] transitions (0x260 bytes);
 * empty cells are {0, NULL}. */
const g2_teleprompt_ui_transition_data_t g2_teleprompt_ui_fsm_table_6a9cf4[4][19] = {
    { /* TELEPROMPT_UI_STATE_CLOSED */
        [1] = {1u, {0u, 0u, 0u}, teleprompt_ui_action_display_menu_page_555758}, /* TELEPROMPT_UI_EVENT_MENU_START */
        [2] = {2u, {0u, 0u, 0u}, teleprompt_ui_action_main_page_create_5558d4}, /* TELEPROMPT_UI_EVENT_APP_START */
    },
    { /* TELEPROMPT_UI_STATE_MENU */
        [2] = {2u, {0u, 0u, 0u}, teleprompt_ui_action_main_page_create_5558d4}, /* TELEPROMPT_UI_EVENT_APP_START */
        [3] = {1u, {0u, 0u, 0u}, teleprompt_ui_action_file_list_update_555d18}, /* TELEPROMPT_UI_EVENT_FILE_LIST_UPDATE */
        [4] = {1u, {0u, 0u, 0u}, teleprompt_ui_action_file_select_556010}, /* TELEPROMPT_UI_EVENT_MENU_SELECT */
        [9] = {3u, {0u, 0u, 0u}, teleprompt_ui_action_exit_556b78}, /* TELEPROMPT_UI_EVENT_MENU_EXIT */
        [12] = {1u, {0u, 0u, 0u}, teleprompt_ui_action_menu_scroll_up_556134}, /* TELEPROMPT_UI_EVENT_SCROLL_UP */
        [13] = {1u, {0u, 0u, 0u}, teleprompt_ui_action_menu_scroll_down_556284}, /* TELEPROMPT_UI_EVENT_SCROLL_DOWN */
    },
    { /* TELEPROMPT_UI_STATE_MAIN */
        [5] = {2u, {0u, 0u, 0u}, teleprompt_ui_action_display_main_page_555c04}, /* TELEPROMPT_UI_EVENT_LOADING_DONE */
        [6] = {2u, {0u, 0u, 0u}, teleprompt_ui_action_page_data_5560d0}, /* TELEPROMPT_UI_EVENT_PAGE_DATA_READY */
        [7] = {2u, {0u, 0u, 0u}, teleprompt_ui_action_pause_556b2c}, /* TELEPROMPT_UI_EVENT_PAUSE */
        [8] = {2u, {0u, 0u, 0u}, teleprompt_ui_action_resume_556b52}, /* TELEPROMPT_UI_EVENT_RESUME */
        [9] = {3u, {0u, 0u, 0u}, teleprompt_ui_action_exit_556b78}, /* TELEPROMPT_UI_EVENT_MENU_EXIT */
        [10] = {3u, {0u, 0u, 0u}, teleprompt_ui_action_exit_animated_556bfe}, /* TELEPROMPT_UI_EVENT_APP_EXIT */
        [11] = {2u, {0u, 0u, 0u}, teleprompt_ui_action_gif_complete_556c44}, /* TELEPROMPT_UI_EVENT_GIF_COMPLETE */
        [12] = {2u, {0u, 0u, 0u}, teleprompt_ui_action_main_scroll_up_5563c0}, /* TELEPROMPT_UI_EVENT_SCROLL_UP */
        [13] = {2u, {0u, 0u, 0u}, teleprompt_ui_action_main_scroll_down_556428}, /* TELEPROMPT_UI_EVENT_SCROLL_DOWN */
        [14] = {2u, {0u, 0u, 0u}, teleprompt_ui_action_main_page_switch_prev_556cd8}, /* TELEPROMPT_UI_EVENT_PAGE_SWITCH_PREV */
        [15] = {2u, {0u, 0u, 0u}, teleprompt_ui_action_main_page_switch_next_556ed4}, /* TELEPROMPT_UI_EVENT_PAGE_SWITCH_NEXT */
        [16] = {2u, {0u, 0u, 0u}, teleprompt_ui_action_ai_sync_5564a8}, /* TELEPROMPT_UI_EVENT_AI_SYNC */
        [17] = {2u, {0u, 0u, 0u}, teleprompt_ui_action_scroll_sync_556688}, /* TELEPROMPT_UI_EVENT_SCROLL_SYNC */
        [18] = {2u, {0u, 0u, 0u}, teleprompt_ui_action_update_elapsed_time_557280}, /* TELEPROMPT_UI_EVENT_UPDATE_ELAPSED_TIME */
    },
    { /* TELEPROMPT_UI_STATE_CLOSING */
    },
};

/* ROM 0x78f6c0: 2-byte status notify template {0, 0}. */
const uint16_t g2_teleprompt_status_notify_init_78f6c0 = 0u;
