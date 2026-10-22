/* Health widget storage (S4-ui-a storage-definition pass, G2 2.2.6.10).
 *
 * Stock owners app\gui\health (tile, expanded page, health storage/data manager).
 * .data values come from the decoded scatter init streams (records 0x75d3f4
 * for 0x20000000.. and 0x75d404 for 0x20080000..); every other RAM cell is
 * zero-initialised (.bss 0x20004558.. / 0x2013be70..). ROM bytes are copied
 * from ota_s200_firmware_ota.bin (VA = file offset + 0x437fe0). Absolute
 * placement is a linker obligation; compiling this file does not establish
 * byte identity. */
#include <stdint.h>

__attribute__((aligned(4))) uint8_t g2_health_insight_objs[0x28]; /* RAM 0x20073800; extern view: g2_health_insight_objs_t g2_health_insight_objs[HEALTH_INSIGHT_MAX]; */

void *g2_health_ext_pages[2]; /* RAM 0x20074190 */

void *g2_health_page_dots[2]; /* RAM 0x20074198 */

void *g2_health_storage_mutex; /* RAM 0x20074658 */

int32_t g2_health_widget_init_flag; /* RAM 0x20074c0c */

void *g2_health_ext_fifo; /* RAM 0x20074c10 */

int32_t g2_health_is_animating; /* RAM 0x20074c14 */

uint32_t g2_health_tile_index; /* RAM 0x20074c18 */

int32_t g2_health_ext_widget_init_flag; /* RAM 0x20074c1c */

uint32_t g2_health_page_index; /* RAM 0x20074c20 */

void *g2_health_tile_root; /* RAM 0x20074c24 */

void *g2_health_ring_icon; /* RAM 0x20074c28 */

void *g2_health_score_title; /* RAM 0x20074c2c */

void *g2_health_score_value; /* RAM 0x20074c30 */

void *g2_health_steps_icon; /* RAM 0x20074c34 */

void *g2_health_steps_label; /* RAM 0x20074c38 */

void *g2_health_steps_bar; /* RAM 0x20074c3c */

void *g2_health_steps_mask; /* RAM 0x20074c40 */

void *g2_health_calories_icon; /* RAM 0x20074c44 */

void *g2_health_calories_label; /* RAM 0x20074c48 */

void *g2_health_calories_bar; /* RAM 0x20074c4c */

void *g2_health_calories_mask; /* RAM 0x20074c50 */

void *g2_health_duration_icon; /* RAM 0x20074c54 */

void *g2_health_duration_label; /* RAM 0x20074c58 */

void *g2_health_heart_icon; /* RAM 0x20074c5c */

void *g2_health_heart_label; /* RAM 0x20074c60 */

void *g2_health_percent_icon; /* RAM 0x20074c64 */

void *g2_health_percent_label; /* RAM 0x20074c68 */

void *g2_health_scroll_container; /* RAM 0x20074c6c */

void *g2_health_ext_ring_icon; /* RAM 0x20074c70 */

void *g2_health_ext_score_title; /* RAM 0x20074c74 */

void *g2_health_ext_score_value; /* RAM 0x20074c78 */

void *g2_health_ext_steps_icon; /* RAM 0x20074c7c */

void *g2_health_ext_steps_label; /* RAM 0x20074c80 */

void *g2_health_ext_steps_goal; /* RAM 0x20074c84 */

void *g2_health_ext_steps_bar; /* RAM 0x20074c88 */

void *g2_health_ext_steps_mask; /* RAM 0x20074c8c */

void *g2_health_ext_calories_icon; /* RAM 0x20074c90 */

void *g2_health_ext_calories_label; /* RAM 0x20074c94 */

void *g2_health_ext_calories_goal; /* RAM 0x20074c98 */

void *g2_health_ext_calories_bar; /* RAM 0x20074c9c */

void *g2_health_ext_calories_mask; /* RAM 0x20074ca0 */

void *g2_health_ext_sleep_icon; /* RAM 0x20074ca4 */

void *g2_health_ext_sleep_value; /* RAM 0x20074ca8 */

void *g2_health_ext_sleep_duration; /* RAM 0x20074cac */

void *g2_health_ext_heart_icon; /* RAM 0x20074cb0 */

void *g2_health_ext_heart_value; /* RAM 0x20074cb4 */

void *g2_health_ext_heart_average; /* RAM 0x20074cb8 */

void *g2_health_ext_oxygen_icon; /* RAM 0x20074cbc */

void *g2_health_ext_oxygen_value; /* RAM 0x20074cc0 */

void *g2_health_ext_oxygen_average; /* RAM 0x20074cc4 */

void *g2_health_ext_insight_placeholder; /* RAM 0x20074cc8 */

void *g2_health_ext_indicator; /* RAM 0x20074ccc */

__attribute__((aligned(4))) uint8_t g2_health_data[0x5d0]; /* RAM 0x200f41b4; extern view: g2_health_data_t g2_health_data; */
