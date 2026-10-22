/* Onboarding UI storage (S5-ui-b storage-definition pass, 2.2.6.10).
 *
 * Stock owners: app\gui\onboarding\ui_onboarding_news_scroll.c,
 * ui_onboarding_stock_page.c and onboarding_animation.c (log tags
 * "onboarding.news", "onboarding.stock", "onboarding.animation"). Types and
 * sizes are those of the referencing declarations in
 * ui/a-42-onboarding-news-scroll, ui/a-42-onboarding-stock-page and
 * ui/a-43-onboarding-animation; struct-typed cells whose layout lives in those
 * .c files are defined as aligned storage of the asserted size.
 *
 * .data values come from the decoded 0x20000000 init stream (scatter record
 * 0x75d3f4) and the LZ-compressed SSRAM init stream for 0x20080000 (record
 * 0x75d404); everything else is zero-initialised.
 *
 * The prerendered chart images (ROM 0x76ebe8 / 0x76ec04 / 0x76ec20) and the
 * frame images referenced by the tables below are ROM lv_image_dsc_t assets
 * defined in onboarding_image_assets_data.c. */
#include <stdint.h>

struct g2_generic_animation;

/* ---- ui_onboarding_news_scroll.c ---------------------------------------- */

/* RAM 0x20073f14: container start y per news container (NEWS_CONTAINERS = 4). */
int32_t g2_onboarding_news_start_y_20073f14[4];

/* ---- ui_onboarding_stock_page.c ----------------------------------------- */

/* RAM 0x201280a0 (SSRAM): nine 0x380-byte stock records
 * (g2_onboarding_stock_record_t[STOCK_MAX]); ends at 0x2012a020. */
__attribute__((aligned(4))) uint8_t g2_onboarding_stock_data_201280a0[9][0x380];
/* RAM 0x2012a020 (SSRAM .data): record count, initial value 3 (decoded SSRAM
 * init stream: 03 00). */
uint16_t g2_onboarding_stock_count_2012a020 = 3u;
/* RAM 0x2012a024 / 0x2012a3a4: one-record scratch buffers. */
__attribute__((aligned(4))) uint8_t g2_onboarding_stock_scratch_2012a024[0x380];
__attribute__((aligned(4))) uint8_t g2_onboarding_stock_scratch_2012a3a4[0x388];
/* RAM 0x2006fd8c: g2_onboarding_stock_scroll_t (0x12c bytes: three 0x60-byte
 * containers, count, is_animating, frame). */
__attribute__((aligned(4))) uint8_t g2_onboarding_stock_scroll_2006fd8c[0x12c];
/* RAM 0x20073d88: state block cleared with memset(.., 0x14). */
__attribute__((aligned(4))) uint8_t g2_onboarding_stock_state_20073d88[0x14];
/* RAM 0x200740d4: three container slots. */
int32_t g2_onboarding_stock_slots_200740d4[3];
int32_t g2_onboarding_stock_ext_widget_init_flag_20074dbc; /* RAM 0x20074dbc */
int32_t g2_onboarding_stock_is_animating_20074dc0;         /* RAM 0x20074dc0 */
void *g2_onboarding_stock_ext_fifo_20074dc4;               /* RAM 0x20074dc4 */
int32_t g2_onboarding_stock_state_20074dc8;                /* RAM 0x20074dc8 */
int32_t g2_onboarding_stock_container_index_20074dcc;      /* RAM 0x20074dcc */
void *g2_onboarding_stock_widget_frame_20074dd0;           /* RAM 0x20074dd0 */
void *g2_onboarding_stock_expanded_frame_20074dd4;         /* RAM 0x20074dd4 */
void *g2_onboarding_stock_widget_objs_20074dd8[4];         /* RAM 0x20074dd8..0x20074de7 */
void *g2_onboarding_stock_expanded_objs_20074de8[4];       /* RAM 0x20074de8..0x20074df7 */
/* RAM 0x200042bc (.data): onboarding tile index, initial 0xffffffff (none). */
uint32_t g2_onboarding_stock_tile_index_200042bc = 0xffffffffu;

/* ---- onboarding_animation.c --------------------------------------------- */

/* RAM 0x2007345c: g2_onboarding_animation_config_t (0x30 bytes). */
__attribute__((aligned(4))) uint8_t g2_onboarding_anim_config[0x30];
/* RAM 0x20073eb4: one generic_animation instance per tutorial phase. */
struct g2_generic_animation *g2_onboarding_anim_instance[4];
void *g2_onboarding_anim_parent;          /* RAM 0x2007483c */
uint8_t g2_onboarding_anim_current_phase; /* RAM 0x20074ff1 */
uint8_t g2_onboarding_anim_initialized;   /* RAM 0x20074ff2 */

/* Frame tables (stock .data; values from the init stream). */
extern const uint8_t g2_onboarding_anim_frame_76e99c[]; /* ROM 0x76e99c lv_image_dsc_t */
extern const uint8_t g2_onboarding_anim_frame_76e9b8[]; /* ROM 0x76e9b8 lv_image_dsc_t */
extern const uint8_t g2_onboarding_anim_frame_76e9d4[]; /* ROM 0x76e9d4 lv_image_dsc_t */
extern const uint8_t g2_onboarding_anim_frame_76e9f0[]; /* ROM 0x76e9f0 lv_image_dsc_t */
extern const uint8_t g2_onboarding_anim_frame_76ea0c[]; /* ROM 0x76ea0c lv_image_dsc_t */
extern const uint8_t g2_onboarding_anim_frame_76ea28[]; /* ROM 0x76ea28 lv_image_dsc_t */
extern const uint8_t g2_onboarding_anim_frame_76ea44[]; /* ROM 0x76ea44 lv_image_dsc_t */
extern const uint8_t g2_onboarding_anim_frame_76ea60[]; /* ROM 0x76ea60 lv_image_dsc_t */
extern const uint8_t g2_onboarding_anim_frame_76ea7c[]; /* ROM 0x76ea7c lv_image_dsc_t */
extern const uint8_t g2_onboarding_anim_frame_76ea98[]; /* ROM 0x76ea98 lv_image_dsc_t */
extern const uint8_t g2_onboarding_anim_frame_76eab4[]; /* ROM 0x76eab4 lv_image_dsc_t */
extern const uint8_t g2_onboarding_anim_frame_76ead0[]; /* ROM 0x76ead0 lv_image_dsc_t */
extern const uint8_t g2_onboarding_anim_frame_76eaec[]; /* ROM 0x76eaec lv_image_dsc_t */
extern const uint8_t g2_onboarding_anim_frame_76eb08[]; /* ROM 0x76eb08 lv_image_dsc_t */
extern const uint8_t g2_onboarding_anim_frame_76eb24[]; /* ROM 0x76eb24 lv_image_dsc_t */
extern const uint8_t g2_onboarding_anim_frame_76eb40[]; /* ROM 0x76eb40 lv_image_dsc_t */
extern const uint8_t g2_onboarding_anim_frame_76eb5c[]; /* ROM 0x76eb5c lv_image_dsc_t */
extern const uint8_t g2_onboarding_anim_frame_76eb78[]; /* ROM 0x76eb78 lv_image_dsc_t */
extern const uint8_t g2_onboarding_anim_frame_76eb94[]; /* ROM 0x76eb94 lv_image_dsc_t */
extern const uint8_t g2_onboarding_anim_frame_76ebb0[]; /* ROM 0x76ebb0 lv_image_dsc_t */
extern const uint8_t g2_onboarding_anim_frame_76ebcc[]; /* ROM 0x76ebcc lv_image_dsc_t */
extern const uint8_t g2_onboarding_anim_frame_76ec3c[]; /* ROM 0x76ec3c lv_image_dsc_t */
extern const uint8_t g2_onboarding_anim_frame_76ec58[]; /* ROM 0x76ec58 lv_image_dsc_t */
extern const uint8_t g2_onboarding_anim_frame_76ec74[]; /* ROM 0x76ec74 lv_image_dsc_t */
extern const uint8_t g2_onboarding_anim_frame_76ec90[]; /* ROM 0x76ec90 lv_image_dsc_t */
extern const uint8_t g2_onboarding_anim_frame_76ecac[]; /* ROM 0x76ecac lv_image_dsc_t */
extern const uint8_t g2_onboarding_anim_frame_76ecc8[]; /* ROM 0x76ecc8 lv_image_dsc_t */
extern const uint8_t g2_onboarding_anim_frame_76ece4[]; /* ROM 0x76ece4 lv_image_dsc_t */
extern const uint8_t g2_onboarding_anim_frame_76ed00[]; /* ROM 0x76ed00 lv_image_dsc_t */
extern const uint8_t g2_onboarding_anim_frame_76ed1c[]; /* ROM 0x76ed1c lv_image_dsc_t */
extern const uint8_t g2_onboarding_anim_frame_76ed38[]; /* ROM 0x76ed38 lv_image_dsc_t */
extern const uint8_t g2_onboarding_anim_frame_76ed54[]; /* ROM 0x76ed54 lv_image_dsc_t */
extern const uint8_t g2_onboarding_anim_frame_76ed70[]; /* ROM 0x76ed70 lv_image_dsc_t */
extern const uint8_t g2_onboarding_anim_frame_76ed8c[]; /* ROM 0x76ed8c lv_image_dsc_t */
extern const uint8_t g2_onboarding_anim_frame_76eda8[]; /* ROM 0x76eda8 lv_image_dsc_t */
extern const uint8_t g2_onboarding_anim_frame_76edc4[]; /* ROM 0x76edc4 lv_image_dsc_t */
extern const uint8_t g2_onboarding_anim_frame_76ede0[]; /* ROM 0x76ede0 lv_image_dsc_t */
extern const uint8_t g2_onboarding_anim_frame_76edfc[]; /* ROM 0x76edfc lv_image_dsc_t */
extern const uint8_t g2_onboarding_anim_frame_76ee18[]; /* ROM 0x76ee18 lv_image_dsc_t */
extern const uint8_t g2_onboarding_anim_frame_76ee34[]; /* ROM 0x76ee34 lv_image_dsc_t */
extern const uint8_t g2_onboarding_anim_frame_76ee50[]; /* ROM 0x76ee50 lv_image_dsc_t */

/* RAM 0x20002e50 (.data, 15 x lv_image_dsc_t *; table ends at the next table / 0x20002e8c). */
const void *const g2_onboarding_anim_frames_0[15] = {
    g2_onboarding_anim_frame_76e99c, g2_onboarding_anim_frame_76e9d4, g2_onboarding_anim_frame_76e9f0,
    g2_onboarding_anim_frame_76ea0c, g2_onboarding_anim_frame_76ea28, g2_onboarding_anim_frame_76ea44,
    g2_onboarding_anim_frame_76ea60, g2_onboarding_anim_frame_76ea7c, g2_onboarding_anim_frame_76ea98,
    g2_onboarding_anim_frame_76e9b8, g2_onboarding_anim_frame_76e9b8, g2_onboarding_anim_frame_76e9b8,
    g2_onboarding_anim_frame_76e9b8, g2_onboarding_anim_frame_76e9b8, g2_onboarding_anim_frame_76e9b8,
};

/* RAM 0x20002e8c (.data, 35 x lv_image_dsc_t *; table ends at the next table / 0x20002f18). */
const void *const g2_onboarding_anim_frames_1[35] = {
    g2_onboarding_anim_frame_76ec3c, g2_onboarding_anim_frame_76ed70, g2_onboarding_anim_frame_76eda8,
    g2_onboarding_anim_frame_76edc4, g2_onboarding_anim_frame_76ede0, g2_onboarding_anim_frame_76edfc,
    g2_onboarding_anim_frame_76ee18, g2_onboarding_anim_frame_76ee34, g2_onboarding_anim_frame_76ee50,
    g2_onboarding_anim_frame_76ec58, g2_onboarding_anim_frame_76ec58, g2_onboarding_anim_frame_76ec58,
    g2_onboarding_anim_frame_76ec58, g2_onboarding_anim_frame_76ec58, g2_onboarding_anim_frame_76ec58,
    g2_onboarding_anim_frame_76ec74, g2_onboarding_anim_frame_76ec90, g2_onboarding_anim_frame_76ecac,
    g2_onboarding_anim_frame_76ecc8, g2_onboarding_anim_frame_76ece4, g2_onboarding_anim_frame_76ed00,
    g2_onboarding_anim_frame_76ed1c, g2_onboarding_anim_frame_76ed38, g2_onboarding_anim_frame_76ed54,
    g2_onboarding_anim_frame_76ed8c, g2_onboarding_anim_frame_76ed8c, g2_onboarding_anim_frame_76ed8c,
    g2_onboarding_anim_frame_76ed8c, g2_onboarding_anim_frame_76ed8c, g2_onboarding_anim_frame_76ed8c,
    g2_onboarding_anim_frame_76ed8c, g2_onboarding_anim_frame_76ed8c, g2_onboarding_anim_frame_76ed8c,
    g2_onboarding_anim_frame_76ed8c, g2_onboarding_anim_frame_76ed8c,
};

/* RAM 0x20002f18 (.data, 11 x lv_image_dsc_t *; table ends at the next table / 0x20002f44). */
const void *const g2_onboarding_anim_frames_2[11] = {
    g2_onboarding_anim_frame_76eb5c, g2_onboarding_anim_frame_76eb78, g2_onboarding_anim_frame_76eb94,
    g2_onboarding_anim_frame_76ebb0, g2_onboarding_anim_frame_76ebcc, g2_onboarding_anim_frame_76ebcc,
    g2_onboarding_anim_frame_76ebcc, g2_onboarding_anim_frame_76ebcc, g2_onboarding_anim_frame_76ebcc,
    g2_onboarding_anim_frame_76ebcc, g2_onboarding_anim_frame_76ebcc,
};

/* RAM 0x20002f44 (.data, 54 x lv_image_dsc_t *; table ends at the next table / 0x2000301c). */
const void *const g2_onboarding_anim_frames_3[54] = {
    g2_onboarding_anim_frame_76eab4, g2_onboarding_anim_frame_76ead0, g2_onboarding_anim_frame_76eaec,
    g2_onboarding_anim_frame_76eaec, g2_onboarding_anim_frame_76eaec, g2_onboarding_anim_frame_76eaec,
    g2_onboarding_anim_frame_76eaec, g2_onboarding_anim_frame_76eaec, g2_onboarding_anim_frame_76eaec,
    g2_onboarding_anim_frame_76eaec, g2_onboarding_anim_frame_76eaec, g2_onboarding_anim_frame_76eaec,
    g2_onboarding_anim_frame_76eaec, g2_onboarding_anim_frame_76eaec, g2_onboarding_anim_frame_76eaec,
    g2_onboarding_anim_frame_76eaec, g2_onboarding_anim_frame_76eaec, g2_onboarding_anim_frame_76eaec,
    g2_onboarding_anim_frame_76eaec, g2_onboarding_anim_frame_76eaec, g2_onboarding_anim_frame_76eaec,
    g2_onboarding_anim_frame_76eaec, g2_onboarding_anim_frame_76eaec, g2_onboarding_anim_frame_76eaec,
    g2_onboarding_anim_frame_76eaec, g2_onboarding_anim_frame_76eaec, g2_onboarding_anim_frame_76eaec,
    g2_onboarding_anim_frame_76eaec, g2_onboarding_anim_frame_76eaec, g2_onboarding_anim_frame_76eaec,
    g2_onboarding_anim_frame_76eaec, g2_onboarding_anim_frame_76eaec, g2_onboarding_anim_frame_76eaec,
    g2_onboarding_anim_frame_76eaec, g2_onboarding_anim_frame_76eaec, g2_onboarding_anim_frame_76eaec,
    g2_onboarding_anim_frame_76eaec, g2_onboarding_anim_frame_76eaec, g2_onboarding_anim_frame_76eaec,
    g2_onboarding_anim_frame_76eaec, g2_onboarding_anim_frame_76eaec, g2_onboarding_anim_frame_76eb08,
    g2_onboarding_anim_frame_76eb24, g2_onboarding_anim_frame_76eb40, g2_onboarding_anim_frame_76eb40,
    g2_onboarding_anim_frame_76eb40, g2_onboarding_anim_frame_76eb40, g2_onboarding_anim_frame_76eb40,
    g2_onboarding_anim_frame_76eb40, g2_onboarding_anim_frame_76eb40, g2_onboarding_anim_frame_76eb40,
    g2_onboarding_anim_frame_76eb40, g2_onboarding_anim_frame_76eb40, g2_onboarding_anim_frame_76eb40,
};
