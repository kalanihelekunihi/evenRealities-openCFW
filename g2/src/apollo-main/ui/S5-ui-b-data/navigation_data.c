/* Navigation UI storage (S5-ui-b storage-definition pass, 2.2.6.10).
 *
 * Stock owners: app\gui\navigation\navigation_ui.c (ui/a-48..a-51
 * navigation-ui), navigation_main.c (ui/a-60-navigation-main) and
 * navigation_data_handler.c / the navigation pb sender (ui/a-60-navigation-data,
 * ui/a-61-navigation-data). Objects declared in the a-48 private header are
 * defined with the header's types (the header is included so the compiler
 * checks every definition against it); the others use the referencing
 * declarations' types and sizes.
 *
 * Buffer sizes are consistent with the stock layout: 0x202a6670 + 0x1a700 =
 * 0x202c0d70, 0x202e4fc8 + 0xea7c = 0x202f3a44, 0x20329600 + 0x4674 =
 * 0x2032dc74, 0x20356db0 + 0x2024 = 0x20358dd4.
 *
 * .data values come from the decoded 0x20000000 init stream (scatter record
 * 0x75d3f4); ROM bytes from ota_s200_firmware_ota.bin. Image assets (map
 * marker, corners, clocks, turn/type icons, calibrate frames) are in
 * navigation_image_assets_data.c. The nanopb descriptor
 * g2_nav_msg_fields_7798a4 is generated code and is not defined here. */
#include <stdint.h>
#include "../a-48-navigation-ui/navigation_ui_private.h"

/* ---- navigation_ui.c: page objects and state (RAM 0x20074718..0x20074813) */
void *g2_navigation_page_root_20074718;              /* RAM 0x20074718 */
uint32_t g2_navigation_var_20074720;                 /* RAM 0x20074720 */
g2_ui_fifo_t *g2_nav_event_fifo_20074734;            /* RAM 0x20074734 map page events */
g2_ui_fifo_t *g2_nav_list_event_fifo_20074738;       /* RAM 0x20074738 list page events */
uint32_t g2_nav_container_b_shown_2007473c;          /* RAM 0x2007473c */
void *g2_navigation_startup_obj_20074740;            /* RAM 0x20074740 */
uint32_t g2_navigation_var_20074744;                 /* RAM 0x20074744 tick counter */
uint32_t g2_nav_var_20074748;                        /* RAM 0x20074748 exit countdown */
uint32_t g2_nav_var_2007474c;                        /* RAM 0x2007474c exit page active */
g2_generic_animation_t *g2_nav_calibrate_anim_20074750; /* RAM 0x20074750 */
uint32_t g2_nav_var_20074754;                        /* RAM 0x20074754 selected location index */
uint32_t g2_nav_var_20074758;                        /* RAM 0x20074758 */
uint32_t g2_navigation_clock_hour_2007475c;          /* RAM 0x2007475c */
uint32_t g2_navigation_clock_minute_20074760;        /* RAM 0x20074760 */
void *g2_nav_b_clock_label_20074764;                 /* RAM 0x20074764 */
void *g2_navigation_b_text_c8_label_20074768;        /* RAM 0x20074768 */
void *g2_navigation_b_text_88_label_2007476c;        /* RAM 0x2007476c */
void *g2_navigation_b_text_148_label_20074770;       /* RAM 0x20074770 */
void *g2_navigation_b_clock_icon_20074774;           /* RAM 0x20074774 */
void *g2_navigation_b_text_108_label_20074778;       /* RAM 0x20074778 */
void *g2_nav_max_map_img_2007477c;                   /* RAM 0x2007477c */
void *g2_nav_b_loading_label_20074780;               /* RAM 0x20074780 */
void *g2_navigation_a_marker_img_20074784;           /* RAM 0x20074784 */
void *g2_navigation_a_corner_tl_img_20074788;        /* RAM 0x20074788 */
void *g2_navigation_a_corner_tr_img_2007478c;        /* RAM 0x2007478c */
void *g2_navigation_a_corner_bl_img_20074790;        /* RAM 0x20074790 */
void *g2_navigation_a_corner_br_img_20074794;        /* RAM 0x20074794 */
void *g2_navigation_c_recalculating_label_20074798;  /* RAM 0x20074798 */
void *g2_navigation_location_container_2007479c;     /* RAM 0x2007479c */
void *g2_navigation_location_content_200747a0;       /* RAM 0x200747a0 */
int32_t g2_navigation_location_selected_200747a4;    /* RAM 0x200747a4 */
int32_t g2_navigation_location_scroll_offset_200747a8; /* RAM 0x200747a8 */
void *g2_navigation_mode_container_200747ac;         /* RAM 0x200747ac */
void *g2_navigation_mode_content_200747b0;           /* RAM 0x200747b0 */
int32_t g2_navigation_mode_selected_200747b4;        /* RAM 0x200747b4 */
int32_t g2_navigation_mode_scroll_offset_200747b8;   /* RAM 0x200747b8 */
void *g2_navigation_map_page_200747bc;               /* RAM 0x200747bc */
void *g2_navigation_container_a_200747c0;            /* RAM 0x200747c0 */
void *g2_navigation_container_b_200747c4;            /* RAM 0x200747c4 */
void *g2_nav_container_c_200747c8;                   /* RAM 0x200747c8 */
void *g2_navigation_a_turn_icon_200747cc;            /* RAM 0x200747cc */
void *g2_navigation_a_turn_label_200747d0;           /* RAM 0x200747d0 */
void *g2_navigation_a_road_label_200747d4;           /* RAM 0x200747d4 */
void *g2_navigation_a_text_c8_label_200747d8;        /* RAM 0x200747d8 */
void *g2_navigation_a_text_88_label_200747dc;        /* RAM 0x200747dc */
void *g2_nav_a_clock_label_200747e0;                 /* RAM 0x200747e0 */
void *g2_navigation_a_clock_icon_200747e4;           /* RAM 0x200747e4 */
void *g2_nav_a_compass_img_200747e8;                 /* RAM 0x200747e8 */
void *g2_nav_a_loading_label_200747ec;               /* RAM 0x200747ec */
uint32_t g2_navigation_var_200747f0;                 /* RAM 0x200747f0 */
uint32_t g2_navigation_var_200747f4;                 /* RAM 0x200747f4 */
uint32_t g2_navigation_var_200747f8;                 /* RAM 0x200747f8 */
uint32_t g2_navigation_var_200747fc;                 /* RAM 0x200747fc */
void *g2_navigation_calibrate_page_20074800;         /* RAM 0x20074800 */
void *g2_navigation_calibrate_label_20074804;        /* RAM 0x20074804 */
uint32_t g2_nav_compass_enabled_20074808;            /* RAM 0x20074808 */
int32_t g2_nav_compass_heading_2007480c;             /* RAM 0x2007480c degrees */
int32_t g2_nav_compass_heading_last_20074810;        /* RAM 0x20074810 */

uint8_t g2_navigation_flag_20074fe6;                 /* RAM 0x20074fe6 */
uint8_t g2_nav_flag_20074fe7;                        /* RAM 0x20074fe7 mode 1 walk / 2 bike */
uint8_t g2_navigation_location_animating_20074fe8;   /* RAM 0x20074fe8 */
uint8_t g2_navigation_mode_animating_20074fe9;       /* RAM 0x20074fe9 */
uint8_t g2_navigation_flag_20074fea;                 /* RAM 0x20074fea */
uint8_t g2_navigation_flag_20074feb;                 /* RAM 0x20074feb */
uint8_t g2_nav_animation_running_20074fec;           /* RAM 0x20074fec */
uint8_t g2_navigation_ui_state_20074fed;             /* RAM 0x20074fed */
uint8_t g2_nav_compass_shown_20074fee;               /* RAM 0x20074fee */

/* ---- navigation_main.c (ui/a-60-navigation-main) ------------------------ */
uint32_t g2_nav_opacity_lowered_20074724;            /* RAM 0x20074724 */
uint32_t g2_nav_start_tick_20074728;                 /* RAM 0x20074728 */
uint32_t g2_nav_fadeout_pending_2007472c;            /* RAM 0x2007472c */
void *g2_nav_ui_context_20074730;                    /* RAM 0x20074730 */

/* ---- navigation_ui.c lists, images and buffers -------------------------- */
char g2_nav_temp_buf_200705ec[0x100];                /* RAM 0x200705ec */
void *g2_navigation_location_items_20072c68[NAV_MAX_LOCATIONS]; /* RAM 0x20072c68 */
nav_image_dsc_t g2_navigation_max_map_dsc_20073aac;  /* RAM 0x20073aac */
/* RAM 0x20073ac8: rotated compass lv_image_dsc_t (nav_rot_image_dsc_t in
 * ui/a-51-navigation-ui/navigation_ui_rotated_img.c, 0x1c bytes; same
 * layout as nav_image_dsc_t). */
__attribute__((aligned(4))) uint8_t g2_nav_rotated_img_dsc_20073ac8[0x1c];
void *g2_navigation_mode_items_20074160[NAV_MODE_COUNT]; /* RAM 0x20074160 */
uint8_t g2_nav_buf_200f4784[0x40];                   /* RAM 0x200f4784 (SSRAM) selected name */
uint8_t g2_navigation_max_map_buf_202a6670[NAV_MAX_MAP_L8_SIZE]; /* RAM 0x202a6670 L8 pixels */
g2_navigation_ui_data_t g2_navigation_ui_data_202c0d70; /* RAM 0x202c0d70 */
uint8_t g2_nav_buf_202e4fc8[0xea7c];                 /* RAM 0x202e4fc8 max map cache */
uint8_t g2_navigation_max_map_decode_202f3a44[NAV_MAX_MAP_SIZE]; /* RAM 0x202f3a44 BMP */
/* ROT_SRC = 170, ROT_OUT = 120 (navigation_ui_rotated_img.c). */
uint8_t g2_nav_rotated_img_gray_2030b400[170 * 170];   /* RAM 0x2030b400 decoded L8 */
uint8_t g2_nav_rotated_img_canvas_20312500[170 * 170]; /* RAM 0x20312500 rotated */
uint8_t g2_nav_buf_20329600[0x4674];                 /* RAM 0x20329600 mini map cache */
uint8_t g2_navigation_mini_map_decode_2032dc74[NAV_MINI_MAP_SIZE]; /* RAM 0x2032dc74 BMP */
uint8_t g2_nav_rotated_img_out_20339bb0[120 * 120];  /* RAM 0x20339bb0 shown pixels */
g2_navigation_location_list_t g2_navigation_location_list_20376c38; /* RAM 0x20376c38 */
g2_navigation_info_t g2_navigation_info_staging_2037bdd0; /* RAM 0x2037bdd0 */

/* ---- navigation data / pb (ui/a-60-navigation-data, a-61-navigation-data) */
/* NAV_TX_BUF_SIZE = 10000, NAV_MSG_SIZE = 0x2024 (g2_nav_msg_t). */
uint8_t g2_nav_tx_buf_20350430[10000];               /* RAM 0x20350430 */
__attribute__((aligned(4))) uint8_t g2_navigation_pb_rx_msg_20356db0[0x2024]; /* RAM 0x20356db0 */
__attribute__((aligned(4))) uint8_t g2_nav_msg_shared_20358dd4[0x2024];       /* RAM 0x20358dd4 */

/* ---- .data -------------------------------------------------------------- */
/* RAM 0x20002cfc (.data): heartbeat counter, reset value 20. */
uint32_t g2_nav_var_20002cfc = 20u;
/* RAM 0x20002d00 (.data): i18n keys of the two travel modes. */
const char *g2_navigation_mode_names_20002d00[NAV_MODE_COUNT] = {
    "ID_NAVIGATE_WALK", /* ROM 0x781354 */
    "ID_NAVIGATE_CYCLING", /* ROM 0x781368 */
};

extern const uint8_t g2_navigation_calibrate_frame_771e70[]; /* ROM 0x771e70 lv_image_dsc_t */
extern const uint8_t g2_navigation_calibrate_frame_771e8c[]; /* ROM 0x771e8c lv_image_dsc_t */
extern const uint8_t g2_navigation_calibrate_frame_771ea8[]; /* ROM 0x771ea8 lv_image_dsc_t */
extern const uint8_t g2_navigation_calibrate_frame_771ec4[]; /* ROM 0x771ec4 lv_image_dsc_t */
extern const uint8_t g2_navigation_calibrate_frame_771ee0[]; /* ROM 0x771ee0 lv_image_dsc_t */
extern const uint8_t g2_navigation_calibrate_frame_771efc[]; /* ROM 0x771efc lv_image_dsc_t */
extern const uint8_t g2_navigation_calibrate_frame_771f18[]; /* ROM 0x771f18 lv_image_dsc_t */
extern const uint8_t g2_navigation_calibrate_frame_771f34[]; /* ROM 0x771f34 lv_image_dsc_t */
extern const uint8_t g2_navigation_calibrate_frame_771f50[]; /* ROM 0x771f50 lv_image_dsc_t */
extern const uint8_t g2_navigation_calibrate_frame_771f6c[]; /* ROM 0x771f6c lv_image_dsc_t */
extern const uint8_t g2_navigation_calibrate_frame_771f88[]; /* ROM 0x771f88 lv_image_dsc_t */
extern const uint8_t g2_navigation_calibrate_frame_771fa4[]; /* ROM 0x771fa4 lv_image_dsc_t */
extern const uint8_t g2_navigation_calibrate_frame_771fc0[]; /* ROM 0x771fc0 lv_image_dsc_t */
extern const uint8_t g2_navigation_calibrate_frame_771fdc[]; /* ROM 0x771fdc lv_image_dsc_t */
extern const uint8_t g2_navigation_calibrate_frame_771ff8[]; /* ROM 0x771ff8 lv_image_dsc_t */
extern const uint8_t g2_navigation_calibrate_frame_772014[]; /* ROM 0x772014 lv_image_dsc_t */
extern const uint8_t g2_navigation_calibrate_frame_772030[]; /* ROM 0x772030 lv_image_dsc_t */
extern const uint8_t g2_navigation_calibrate_frame_77204c[]; /* ROM 0x77204c lv_image_dsc_t */
extern const uint8_t g2_navigation_calibrate_frame_772068[]; /* ROM 0x772068 lv_image_dsc_t */
extern const uint8_t g2_navigation_calibrate_frame_772084[]; /* ROM 0x772084 lv_image_dsc_t */
extern const uint8_t g2_navigation_calibrate_frame_7720a0[]; /* ROM 0x7720a0 lv_image_dsc_t */
extern const uint8_t g2_navigation_calibrate_frame_7720bc[]; /* ROM 0x7720bc lv_image_dsc_t */
extern const uint8_t g2_navigation_calibrate_frame_7720d8[]; /* ROM 0x7720d8 lv_image_dsc_t */
extern const uint8_t g2_navigation_calibrate_frame_7720f4[]; /* ROM 0x7720f4 lv_image_dsc_t */
extern const uint8_t g2_navigation_calibrate_frame_772110[]; /* ROM 0x772110 lv_image_dsc_t */
extern const uint8_t g2_navigation_calibrate_frame_77212c[]; /* ROM 0x77212c lv_image_dsc_t */
extern const uint8_t g2_navigation_calibrate_frame_772148[]; /* ROM 0x772148 lv_image_dsc_t */
extern const uint8_t g2_navigation_calibrate_frame_772164[]; /* ROM 0x772164 lv_image_dsc_t */
extern const uint8_t g2_navigation_calibrate_frame_772180[]; /* ROM 0x772180 lv_image_dsc_t */
extern const uint8_t g2_navigation_calibrate_frame_77219c[]; /* ROM 0x77219c lv_image_dsc_t */
extern const uint8_t g2_navigation_calibrate_frame_7721b8[]; /* ROM 0x7721b8 lv_image_dsc_t */
extern const uint8_t g2_navigation_calibrate_frame_7721d4[]; /* ROM 0x7721d4 lv_image_dsc_t */
extern const uint8_t g2_navigation_calibrate_frame_7721f0[]; /* ROM 0x7721f0 lv_image_dsc_t */
extern const uint8_t g2_navigation_calibrate_frame_77220c[]; /* ROM 0x77220c lv_image_dsc_t */
extern const uint8_t g2_navigation_calibrate_frame_772228[]; /* ROM 0x772228 lv_image_dsc_t */
extern const uint8_t g2_navigation_calibrate_frame_772244[]; /* ROM 0x772244 lv_image_dsc_t */
extern const uint8_t g2_navigation_calibrate_frame_772260[]; /* ROM 0x772260 lv_image_dsc_t */
extern const uint8_t g2_navigation_calibrate_frame_77227c[]; /* ROM 0x77227c lv_image_dsc_t */
extern const uint8_t g2_navigation_calibrate_frame_772298[]; /* ROM 0x772298 lv_image_dsc_t */
extern const uint8_t g2_navigation_calibrate_frame_7722b4[]; /* ROM 0x7722b4 lv_image_dsc_t */
extern const uint8_t g2_navigation_calibrate_frame_7722d0[]; /* ROM 0x7722d0 lv_image_dsc_t */
extern const uint8_t g2_navigation_calibrate_frame_7722ec[]; /* ROM 0x7722ec lv_image_dsc_t */
extern const uint8_t g2_navigation_calibrate_frame_772308[]; /* ROM 0x772308 lv_image_dsc_t */
extern const uint8_t g2_navigation_calibrate_frame_772324[]; /* ROM 0x772324 lv_image_dsc_t */
extern const uint8_t g2_navigation_calibrate_frame_772340[]; /* ROM 0x772340 lv_image_dsc_t */
extern const uint8_t g2_navigation_calibrate_frame_77235c[]; /* ROM 0x77235c lv_image_dsc_t */
extern const uint8_t g2_navigation_calibrate_frame_772378[]; /* ROM 0x772378 lv_image_dsc_t */
extern const uint8_t g2_navigation_calibrate_frame_772394[]; /* ROM 0x772394 lv_image_dsc_t */
extern const uint8_t g2_navigation_calibrate_frame_7723b0[]; /* ROM 0x7723b0 lv_image_dsc_t */
extern const uint8_t g2_navigation_calibrate_frame_7723cc[]; /* ROM 0x7723cc lv_image_dsc_t */
extern const uint8_t g2_navigation_calibrate_frame_7723e8[]; /* ROM 0x7723e8 lv_image_dsc_t */
extern const uint8_t g2_navigation_calibrate_frame_772404[]; /* ROM 0x772404 lv_image_dsc_t */
extern const uint8_t g2_navigation_calibrate_frame_772420[]; /* ROM 0x772420 lv_image_dsc_t */
extern const uint8_t g2_navigation_calibrate_frame_77243c[]; /* ROM 0x77243c lv_image_dsc_t */
extern const uint8_t g2_navigation_calibrate_frame_772458[]; /* ROM 0x772458 lv_image_dsc_t */
extern const uint8_t g2_navigation_calibrate_frame_772474[]; /* ROM 0x772474 lv_image_dsc_t */
extern const uint8_t g2_navigation_calibrate_frame_772490[]; /* ROM 0x772490 lv_image_dsc_t */
extern const uint8_t g2_navigation_calibrate_frame_7724ac[]; /* ROM 0x7724ac lv_image_dsc_t */
extern const uint8_t g2_navigation_calibrate_frame_7724c8[]; /* ROM 0x7724c8 lv_image_dsc_t */
extern const uint8_t g2_navigation_calibrate_frame_7724e4[]; /* ROM 0x7724e4 lv_image_dsc_t */
extern const uint8_t g2_navigation_calibrate_frame_772500[]; /* ROM 0x772500 lv_image_dsc_t */
extern const uint8_t g2_navigation_calibrate_frame_77251c[]; /* ROM 0x77251c lv_image_dsc_t */
extern const uint8_t g2_navigation_calibrate_frame_772538[]; /* ROM 0x772538 lv_image_dsc_t */
extern const uint8_t g2_navigation_calibrate_frame_772554[]; /* ROM 0x772554 lv_image_dsc_t */

/* RAM 0x20002d08 (.data): 64 compass-calibration frames (ends at 0x20002e08). */
const void *const g2_navigation_calibrate_frames_20002d08[64] = {
    g2_navigation_calibrate_frame_771e70, g2_navigation_calibrate_frame_771fa4, g2_navigation_calibrate_frame_7720d8,
    g2_navigation_calibrate_frame_77220c, g2_navigation_calibrate_frame_772340, g2_navigation_calibrate_frame_772474,
    g2_navigation_calibrate_frame_77251c, g2_navigation_calibrate_frame_772538, g2_navigation_calibrate_frame_772554,
    g2_navigation_calibrate_frame_771e8c, g2_navigation_calibrate_frame_771ea8, g2_navigation_calibrate_frame_771ec4,
    g2_navigation_calibrate_frame_771ee0, g2_navigation_calibrate_frame_771efc, g2_navigation_calibrate_frame_771f18,
    g2_navigation_calibrate_frame_771f34, g2_navigation_calibrate_frame_771f50, g2_navigation_calibrate_frame_771f6c,
    g2_navigation_calibrate_frame_771f88, g2_navigation_calibrate_frame_771fc0, g2_navigation_calibrate_frame_771fdc,
    g2_navigation_calibrate_frame_771ff8, g2_navigation_calibrate_frame_772014, g2_navigation_calibrate_frame_772030,
    g2_navigation_calibrate_frame_77204c, g2_navigation_calibrate_frame_772068, g2_navigation_calibrate_frame_772084,
    g2_navigation_calibrate_frame_7720a0, g2_navigation_calibrate_frame_7720bc, g2_navigation_calibrate_frame_7720f4,
    g2_navigation_calibrate_frame_772110, g2_navigation_calibrate_frame_77212c, g2_navigation_calibrate_frame_772148,
    g2_navigation_calibrate_frame_772164, g2_navigation_calibrate_frame_772180, g2_navigation_calibrate_frame_77219c,
    g2_navigation_calibrate_frame_7721b8, g2_navigation_calibrate_frame_7721d4, g2_navigation_calibrate_frame_7721f0,
    g2_navigation_calibrate_frame_772228, g2_navigation_calibrate_frame_772244, g2_navigation_calibrate_frame_772260,
    g2_navigation_calibrate_frame_77227c, g2_navigation_calibrate_frame_772298, g2_navigation_calibrate_frame_7722b4,
    g2_navigation_calibrate_frame_7722d0, g2_navigation_calibrate_frame_7722ec, g2_navigation_calibrate_frame_772308,
    g2_navigation_calibrate_frame_772324, g2_navigation_calibrate_frame_77235c, g2_navigation_calibrate_frame_772378,
    g2_navigation_calibrate_frame_772394, g2_navigation_calibrate_frame_7723b0, g2_navigation_calibrate_frame_7723cc,
    g2_navigation_calibrate_frame_7723e8, g2_navigation_calibrate_frame_772404, g2_navigation_calibrate_frame_772420,
    g2_navigation_calibrate_frame_77243c, g2_navigation_calibrate_frame_772458, g2_navigation_calibrate_frame_772490,
    g2_navigation_calibrate_frame_7724ac, g2_navigation_calibrate_frame_7724c8, g2_navigation_calibrate_frame_7724e4,
    g2_navigation_calibrate_frame_772500,
};

/* ROM 0x762870: {frames 0x20002d08, 64 frames, 50 ms, mode 0 loop, 32x32,
 * color_a {0, 0, 0} opa 0xff, bg {0, 0, 0} opa 0}. */
const g2_generic_animation_config_t g2_navigation_calibrate_anim_config_762870 = {
    g2_navigation_calibrate_frames_20002d08, 64u, 50u, 0u, {0u, 0u, 0u}, 32, 32,
    {0u, 0u, 0u}, 0xffu, {0u, 0u, 0u}, 0u,
};
