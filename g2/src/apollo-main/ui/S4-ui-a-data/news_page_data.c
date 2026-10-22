/* News widget storage (S4-ui-a storage-definition pass, G2 2.2.6.10).
 *
 * Stock owner app\gui\dashboard\widget_news (tile, list page, detail page).
 * .data values come from the decoded scatter init streams (records 0x75d3f4
 * for 0x20000000.. and 0x75d404 for 0x20080000..); every other RAM cell is
 * zero-initialised (.bss 0x20004558.. / 0x2013be70..). ROM bytes are copied
 * from ota_s200_firmware_ota.bin (VA = file offset + 0x437fe0). Absolute
 * placement is a linker obligation; compiling this file does not establish
 * byte identity. */
#include <stdint.h>

int32_t g2_news_tile_index_2000432c = -1; /* RAM 0x2000432c (.data, init record 0x75d3f4) */

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
/* RAM 0x20004330 (.data 0x20000000 init stream): 25 spinner frames (24x24 L8). */
const void *g2_news_loading_frames_20004330[25] = {
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

void *g2_news_items_20073d9c[5]; /* RAM 0x20073d9c */

int32_t g2_news_widget_init_flag_20074e60; /* RAM 0x20074e60 */

int32_t g2_news_widget_state_20074e64; /* RAM 0x20074e64 */

int32_t g2_news_expanded_20074e68; /* RAM 0x20074e68 */

void *g2_news_ext_fifo_20074e6c; /* RAM 0x20074e6c */

void *g2_news_list_page_20074e70; /* RAM 0x20074e70 */

void *g2_news_scroll_container_20074e74; /* RAM 0x20074e74 */

int32_t g2_news_selected_index_20074e78; /* RAM 0x20074e78 */

int32_t g2_news_item_count_20074e7c; /* RAM 0x20074e7c */

void *g2_news_end_item_20074e80; /* RAM 0x20074e80 */

void *g2_news_loading_anim_20074e84; /* RAM 0x20074e84 */

int32_t g2_news_anim_running_20074e88; /* RAM 0x20074e88 */

int32_t g2_news_update_animating_20074e8c; /* RAM 0x20074e8c */

int32_t g2_news_update_timeout_20074e90; /* RAM 0x20074e90 */

int32_t g2_news_expanding_20074e94; /* RAM 0x20074e94 */

int32_t g2_news_status_shown_20074e98; /* RAM 0x20074e98 */

int32_t g2_news_status_resume_20074e9c; /* RAM 0x20074e9c */

void *g2_news_expand_container_20074ea0; /* RAM 0x20074ea0 */

uint32_t g2_news_detail_20074ea4; /* RAM 0x20074ea4 */

uint32_t g2_news_detail_20074ea8; /* RAM 0x20074ea8 */

uint32_t g2_news_detail_20074eac; /* RAM 0x20074eac */

uint32_t g2_news_detail_20074eb0; /* RAM 0x20074eb0 */

uint32_t g2_news_detail_20074eb4; /* RAM 0x20074eb4 */

uint32_t g2_news_detail_20074eb8; /* RAM 0x20074eb8 */

uint32_t g2_news_detail_20074ebc; /* RAM 0x20074ebc */

uint32_t g2_news_detail_20074ec0; /* RAM 0x20074ec0 */

int32_t g2_news_detail_scrolling_20074ec4; /* RAM 0x20074ec4 */

int32_t g2_news_expand_x_20074ec8; /* RAM 0x20074ec8 */

int32_t g2_news_expand_y_20074ecc; /* RAM 0x20074ecc */

int32_t g2_news_expand_w_20074ed0; /* RAM 0x20074ed0 */

int32_t g2_news_expand_h_20074ed4; /* RAM 0x20074ed4 */

int32_t g2_news_expand_index_20074ed8; /* RAM 0x20074ed8 */
