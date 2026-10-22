/* Message-notification list storage (S5-ui-b storage-definition pass,
 * 2.2.6.10).
 *
 * Stock owners: app\gui\MessageNotify\ui_msg_notif_list.c
 * (ui/a-52-msg-notif-list, ui/a-53-msg-notif-list) and msg_notif_timer.c
 * (ui/a-53-msg-notif-list). .data values from the decoded 0x20000000 init
 * stream (scatter record 0x75d3f4); key strings copied from ROM. The card and
 * separator icons (ROM 0x769804, 0x76e248) are in notify_image_assets_data.c. */
#include <stdint.h>

/* RAM 0x2006f734: g2_msg_notif_ui_t (0x1d0 bytes; tileview +0x3c, ten 0x28-byte
 * items from +0x40). */
__attribute__((aligned(4))) uint8_t g2_msg_notif_ui_2006f734[0x1d0];
/* RAM 0x20071db8: g2_msg_tile_binding_t[MSG_NOTIF_MAX_BINDINGS] (10 x 12 bytes). */
__attribute__((aligned(4))) uint8_t g2_msg_tile_bindings_20071db8[10][12];
/* RAM 0x2007405c: msg_notif_timer.c timer manager g2_msg_notif_timer_t (12 bytes). */
__attribute__((aligned(4))) uint8_t g2_msg_notif_timer_2007405c[0x0c];
int32_t g2_msg_notif_current_index_20074cd0; /* RAM 0x20074cd0 */
int32_t g2_msg_notif_original_y_20074cd4;    /* RAM 0x20074cd4 */

/* RAM 0x20004278..0x20004283 (.data): animation tuning {250 ms, 80 px, 250 ms}. */
int32_t g2_msg_notif_scroll_duration_20004278 = 250;
int32_t g2_msg_notif_bounce_distance_2000427c = 80;
int32_t g2_msg_notif_bounce_duration_20004280 = 250;

/* RAM 0x20004554..0x20004556 (.data): all -1 (no delete prompt). */
int8_t g2_msg_notif_delete_tile_20004554 = -1;
int8_t g2_msg_notif_delete_count_20004555 = -1;
int8_t g2_msg_notif_delete_visible_20004556 = -1;

/* RAM 0x2000425c (.data): i18n weekday keys, Sunday first. */
const char *g2_msg_notif_weekday_keys_2000425c[7] = {
    "ID_GENERAL_SUN", /* ROM 0x789d40 */
    "ID_GENERAL_MON", /* ROM 0x789d50 */
    "ID_GENERAL_TUE", /* ROM 0x789d60 */
    "ID_GENERAL_WED", /* ROM 0x789d70 */
    "ID_GENERAL_THU", /* ROM 0x789d80 */
    "ID_GENERAL_FRI", /* ROM 0x789d90 */
    "ID_GENERAL_SAT", /* ROM 0x789da0 */
};
