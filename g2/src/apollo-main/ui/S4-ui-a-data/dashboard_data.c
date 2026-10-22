/* Dashboard storage (S4-ui-a storage-definition pass, G2 2.2.6.10).
 *
 * Stock owners app\gui\dashboard (dashboard.c data copies, dashboard main screen tileview/indicator state).
 * .data values come from the decoded scatter init streams (records 0x75d3f4
 * for 0x20000000.. and 0x75d404 for 0x20080000..); every other RAM cell is
 * zero-initialised (.bss 0x20004558.. / 0x2013be70..). ROM bytes are copied
 * from ota_s200_firmware_ota.bin (VA = file offset + 0x437fe0). Absolute
 * placement is a linker obligation; compiling this file does not establish
 * byte identity. */
#include <stdint.h>

const int32_t g2_dashboard_indicator_size = 4; /* ROM 0x78f4fc */

const int32_t g2_dashboard_indicator_pitch = 16; /* ROM 0x78f500 */

uint32_t g2_dashboard_package_id = 0x7d0u; /* RAM 0x200005b8 (.data, init record 0x75d3f4) */

/* RAM 0x2000420c (.data, init record 0x75d3f4); extern view: g2_dashboard_ext_cfg_t g2_dashboard_ext_cfg_2000420c; */
__attribute__((aligned(4))) uint8_t g2_dashboard_ext_cfg_2000420c[0x18] = {
    0x00, 0x00, 0x00, 0x00, 0xe0, 0x00, 0x00, 0x00, 0x03, 0x00, 0x00, 0x00, 0xce, 0x00, 0x00, 0x00,
    0xff, 0xff, 0xff, 0xff, 0x01,
};

/* RAM 0x20004224 (.data, init record 0x75d3f4); extern view: uint8_t g2_dashboard_widget_types_20004224[DASH_WIDGET_COUNT]; */
__attribute__((aligned(4))) uint8_t g2_dashboard_widget_types_20004224[0x5] = {
    0x00, 0x01, 0x02, 0x04, 0x03,
};

int32_t g2_dashboard_scroll_ms_2000422c = 390; /* RAM 0x2000422c (.data, init record 0x75d3f4) */

int32_t g2_dashboard_bounce_px_20004230 = 80; /* RAM 0x20004230 (.data, init record 0x75d3f4) */

int32_t g2_dashboard_bounce_ms_20004234 = 260; /* RAM 0x20004234 (.data, init record 0x75d3f4) */

int32_t g2_dashboard_word_20004238 = 200; /* RAM 0x20004238 (.data, init record 0x75d3f4) */

int32_t g2_dashboard_tile_indicator_count = 5; /* RAM 0x2000423c (.data, init record 0x75d3f4) */

void *g2_dashboard_tile_pairs_200734bc[12]; /* RAM 0x200734bc */

void *g2_dashboard_tile_indicators[6]; /* RAM 0x20073c50 */

uint32_t g2_dashboard_layout_saved_20074b94; /* RAM 0x20074b94 */

void *g2_dashboard_input_fifo_20074b98; /* RAM 0x20074b98 */

void *g2_dashboard_ext_container_20074b9c; /* RAM 0x20074b9c */

void *g2_dashboard_obj_20074ba4; /* RAM 0x20074ba4 */

void *g2_dashboard_tileview_20074ba8; /* RAM 0x20074ba8 */

int32_t g2_dashboard_tile_index_20074bac; /* RAM 0x20074bac */

uint32_t g2_dashboard_ext_index_20074bb0; /* RAM 0x20074bb0 */

int32_t g2_dashboard_saved_tile_index_20074bb4; /* RAM 0x20074bb4 */

uint32_t g2_dashboard_word_20074bb8; /* RAM 0x20074bb8 */

int32_t g2_dashboard_bounce_origin_y_20074bbc; /* RAM 0x20074bbc */

uint32_t g2_dashboard_animating_20074bc0; /* RAM 0x20074bc0 */

uint32_t g2_dashboard_word_20074bc4; /* RAM 0x20074bc4 */

uint32_t g2_dashboard_word_20074bc8; /* RAM 0x20074bc8 */

int32_t g2_dashboard_scroll_accum_20074bcc; /* RAM 0x20074bcc */

void *g2_dashboard_tile_col0_20074bd0[6]; /* RAM 0x20074bd0 */

void *g2_dashboard_tile_col1_20074be8[6]; /* RAM 0x20074be8 */

__attribute__((aligned(4))) uint8_t g2_dashboard_stock_data_a[0x428]; /* RAM 0x200e4f20; extern view: uint8_t g2_dashboard_stock_data_a[0x428]; */

__attribute__((aligned(4))) uint8_t g2_dashboard_stock_data_b[0x430]; /* RAM 0x200e5348; extern view: uint8_t g2_dashboard_stock_data_b[0x430]; */

__attribute__((aligned(4))) uint8_t g2_dashboard_calendar_data_a[0x1080]; /* RAM 0x200e5778; extern view: uint8_t g2_dashboard_calendar_data_a[0x1080]; */

/* RAM 0x20120134 (.data, init record 0x75d404); extern view: uint8_t g2_dashboard_saved_layout_20120134[0x80]; */
__attribute__((aligned(4))) uint8_t g2_dashboard_saved_layout_20120134[0x80] = {
    0x00, 0x05, 0x00, 0x01, 0x02, 0x04, 0x03,
};

__attribute__((aligned(4))) uint8_t g2_dashboard_status_rx_201201b4[0xa0]; /* RAM 0x201201b4; extern view: uint8_t g2_dashboard_status_rx_201201b4[DASH_STATE_LEN]; */
