/* Calendar widget storage (S4-ui-a storage-definition pass, G2 2.2.6.10).
 *
 * Stock owner app\gui\dashboard\widget_calendar (tile + expanded page).
 * .data values come from the decoded scatter init streams (records 0x75d3f4
 * for 0x20000000.. and 0x75d404 for 0x20080000..); every other RAM cell is
 * zero-initialised (.bss 0x20004558.. / 0x2013be70..). ROM bytes are copied
 * from ota_s200_firmware_ota.bin (VA = file offset + 0x437fe0). Absolute
 * placement is a linker obligation; compiling this file does not establish
 * byte identity. */
#include <stdint.h>

uint32_t g2_calendar_widget_init_flag_20074b1c; /* RAM 0x20074b1c */

uint32_t g2_calendar_scroll_anim_running_20074b20; /* RAM 0x20074b20 */

__attribute__((aligned(4))) uint8_t g2_calendar_event_widgets_20074b24[0x48]; /* RAM 0x20074b24; extern view: g2_calendar_event_widgets_t g2_calendar_event_widgets_20074b24[CALENDAR_WIDGET_EVENTS]; */

void *g2_calendar_ext_root_20074b6c; /* RAM 0x20074b6c */

void *g2_calendar_ext_content_20074b70; /* RAM 0x20074b70 */

void *g2_calendar_ext_scrollbar_20074b74; /* RAM 0x20074b74 */

int32_t g2_calendar_ext_content_height_20074b78; /* RAM 0x20074b78 */

int32_t g2_calendar_ext_scroll_y_20074b7c; /* RAM 0x20074b7c */

int32_t g2_calendar_ext_target_y_20074b80; /* RAM 0x20074b80 */

uint32_t g2_calendar_state_20074b84; /* RAM 0x20074b84 */

void *g2_calendar_ext_fifo_20074b88; /* RAM 0x20074b88 */

uint32_t g2_calendar_tilelist_index_20074b8c; /* RAM 0x20074b8c */

uint32_t g2_calendar_ext_active_20074b90; /* RAM 0x20074b90 */

__attribute__((aligned(4))) uint8_t g2_calendar_ext_items_2011efbc[0xc0]; /* RAM 0x2011efbc; extern view: g2_calendar_item_objs_t g2_calendar_ext_items_2011efbc[CAL_EVENT_MAX]; */

__attribute__((aligned(4))) uint8_t g2_calendar_expire_scratch_2011f0ac[0x1088]; /* RAM 0x2011f0ac; extern view: uint8_t g2_calendar_expire_scratch_2011f0ac[CAL_UI_SIZE]; */
