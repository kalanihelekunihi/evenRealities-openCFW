/* Quicklist widget storage (S4-ui-a storage-definition pass, G2 2.2.6.10).
 *
 * Stock owner app\gui\quicklist (tile + expanded page, UI data copies).
 * .data values come from the decoded scatter init streams (records 0x75d3f4
 * for 0x20000000.. and 0x75d404 for 0x20080000..); every other RAM cell is
 * zero-initialised (.bss 0x20004558.. / 0x2013be70..). ROM bytes are copied
 * from ota_s200_firmware_ota.bin (VA = file offset + 0x437fe0). Absolute
 * placement is a linker obligation; compiling this file does not establish
 * byte identity. */
#include <stdint.h>

extern const void *g2_quicklist_loading_frames_200042c4[25]; /* RAM 0x200042c4, below */
/* ROM 0x767bf0: generic_animation config {frames, count, period ms, mode,
 * width, height, colour/opa, bg colour/opa}; extern view g2_generic_animation_config_t. */
const struct {
    const void *const *frames;
    uint32_t frame_count, period_ms, mode;
    int32_t width, height;
    uint32_t color_a, bg_color;
} g2_quicklist_loading_anim_config = {
    g2_quicklist_loading_frames_200042c4, 25u, 50u, 0x0u, 24, 24, 0xff000000u, 0x00000000u,
};

const uint8_t g2_quicklist_request_msg[8] = {0x05, 0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00}; /* ROM 0x78ed9c; extern view: const g2_quicklist_request_msg_t g2_quicklist_request_msg; */

int32_t g2_quicklist_focus_index_200042c0 = -1; /* RAM 0x200042c0 (.data, init record 0x75d3f4) */

extern const struct g2_icon_descriptor g2_img_dsc_76c1e8;
extern const struct g2_icon_descriptor g2_img_dsc_76c204;
extern const struct g2_icon_descriptor g2_img_dsc_76c220;
extern const struct g2_icon_descriptor g2_img_dsc_76c23c;
extern const struct g2_icon_descriptor g2_img_dsc_76c258;
extern const struct g2_icon_descriptor g2_img_dsc_76c274;
extern const struct g2_icon_descriptor g2_img_dsc_76c290;
extern const struct g2_icon_descriptor g2_img_dsc_76c2ac;
extern const struct g2_icon_descriptor g2_img_dsc_76c2c8;
extern const struct g2_icon_descriptor g2_img_dsc_76c2e4;
extern const struct g2_icon_descriptor g2_img_dsc_76c300;
extern const struct g2_icon_descriptor g2_img_dsc_76c31c;
extern const struct g2_icon_descriptor g2_img_dsc_76c338;
extern const struct g2_icon_descriptor g2_img_dsc_76c354;
extern const struct g2_icon_descriptor g2_img_dsc_76c370;
extern const struct g2_icon_descriptor g2_img_dsc_76c38c;
extern const struct g2_icon_descriptor g2_img_dsc_76c3a8;
extern const struct g2_icon_descriptor g2_img_dsc_76c3c4;
extern const struct g2_icon_descriptor g2_img_dsc_76c3e0;
extern const struct g2_icon_descriptor g2_img_dsc_76c3fc;
extern const struct g2_icon_descriptor g2_img_dsc_76c418;
extern const struct g2_icon_descriptor g2_img_dsc_76c434;
extern const struct g2_icon_descriptor g2_img_dsc_76c450;
extern const struct g2_icon_descriptor g2_img_dsc_76c46c;
extern const struct g2_icon_descriptor g2_img_dsc_76c488;
/* RAM 0x200042c4 (.data 0x20000000 init stream): the same 25 spinner frames,
 * referenced only by g2_quicklist_loading_anim_config (ROM 0x767bf0). */
const void *g2_quicklist_loading_frames_200042c4[25] = {
    &g2_img_dsc_76c1e8, &g2_img_dsc_76c31c, &g2_img_dsc_76c3e0,
    &g2_img_dsc_76c3fc, &g2_img_dsc_76c418, &g2_img_dsc_76c434,
    &g2_img_dsc_76c450, &g2_img_dsc_76c46c, &g2_img_dsc_76c488,
    &g2_img_dsc_76c204, &g2_img_dsc_76c220, &g2_img_dsc_76c23c,
    &g2_img_dsc_76c258, &g2_img_dsc_76c274, &g2_img_dsc_76c290,
    &g2_img_dsc_76c2ac, &g2_img_dsc_76c2c8, &g2_img_dsc_76c2e4,
    &g2_img_dsc_76c300, &g2_img_dsc_76c338, &g2_img_dsc_76c354,
    &g2_img_dsc_76c370, &g2_img_dsc_76c38c, &g2_img_dsc_76c3a8,
    &g2_img_dsc_76c3c4,
};

__attribute__((aligned(4))) uint8_t g2_quicklist_rows_2006e370[0x280]; /* RAM 0x2006e370; extern view: g2_quicklist_row_t g2_quicklist_rows_2006e370[QL_MAX_ITEMS]; */

uint64_t g2_quicklist_loading_tick_200741a0; /* RAM 0x200741a0 */

uint64_t g2_quicklist_request_tick_200741a8; /* RAM 0x200741a8 */

uint32_t g2_quicklist_word_20074df8; /* RAM 0x20074df8 */

void *g2_quicklist_root; /* RAM 0x20074dfc */

void *g2_quicklist_container_20074e00; /* RAM 0x20074e00 */

void *g2_quicklist_border; /* RAM 0x20074e04 */

void *g2_quicklist_loading_20074e08; /* RAM 0x20074e08 */

void *g2_quicklist_loading_label; /* RAM 0x20074e0c */

void *g2_quicklist_loading_anim; /* RAM 0x20074e10 */

void *g2_quicklist_event_fifo_20074e14; /* RAM 0x20074e14 */

int32_t g2_quicklist_tile_index; /* RAM 0x20074e18 */

int32_t g2_quicklist_page_active_20074e1c; /* RAM 0x20074e1c */

int32_t g2_quicklist_anim_state_20074e20; /* RAM 0x20074e20 */

int32_t g2_quicklist_org_scroll_y_20074e24; /* RAM 0x20074e24 */

int32_t g2_quicklist_word_20074e28; /* RAM 0x20074e28 */

uint8_t g2_quicklist_border_state_2007503f; /* RAM 0x2007503f */

uint8_t g2_quicklist_loading_shown_20075040; /* RAM 0x20075040 */

uint8_t g2_quicklist_flag_20075041; /* RAM 0x20075041 */

__attribute__((aligned(8))) uint8_t g2_quicklist_ui_data_2012a72c[0x2e50]; /* RAM 0x2012a72c; extern view: g2_quicklist_storage_t g2_quicklist_ui_data_2012a72c; */

__attribute__((aligned(8))) uint8_t g2_quicklist_completed_201303cc[0x288]; /* RAM 0x201303cc; extern view: g2_quicklist_completed_t g2_quicklist_completed_201303cc; */

__attribute__((aligned(8))) uint8_t g2_quicklist_temp_cache_20130654[0x288]; /* RAM 0x20130654; extern view: g2_quicklist_uid_cache_t g2_quicklist_temp_cache_20130654; */
