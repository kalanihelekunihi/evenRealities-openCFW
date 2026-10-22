/* Even AI animation storage (S5-ui-b storage-definition pass, 2.2.6.10).
 *
 * Stock owner: app\gui\EvenAI\even_ai_animation.c (ui/a-53-even-ai). Sizes
 * from the referencing declarations; .data values from the decoded 0x20000000
 * init stream (scatter record 0x75d3f4). Frame images are defined in
 * even_ai_image_assets_data.c (the 24x24 loading frames 0x76c1e8..0x76c488
 * by S4-ui-a ui_image_assets_data.c). */
#include <stdint.h>

/* RAM 0x200730f4: g2_even_ai_anim_sync_t[4] (4 x 0x10 bytes). */
__attribute__((aligned(4))) uint8_t g2_even_ai_anim_sync_200730f4[4][0x10];
/* RAM 0x200733c8: g2_even_ai_anim_presets_t (0x34 bytes). */
__attribute__((aligned(4))) uint8_t g2_even_ai_anim_presets_200733c8[0x34];
/* RAM 0x20073e44: g2_generic_animation_t *[EVEN_AI_ANIM_PHASES]. */
void *g2_even_ai_anims_20073e44[4];
void *g2_even_ai_anim_parent_20074584;     /* RAM 0x20074584 */
uint32_t g2_even_ai_anim_hold_tick_20074588; /* RAM 0x20074588 */
uint8_t g2_even_ai_anim_phase_20074fc1;     /* RAM 0x20074fc1 */
uint8_t g2_even_ai_anim_initialized_20074fc2; /* RAM 0x20074fc2 */
/* RAM 0x20004547 / 0x20004548 (.data): both 0xff (no phase shown yet). */
uint8_t g2_even_ai_anim_shown_phase_20004547 = 0xffu;
int8_t g2_even_ai_anim_last_phase_20004548 = -1;

extern const uint8_t g2_even_ai_anim_frame_7683c8[]; /* ROM 0x7683c8 lv_image_dsc_t */
extern const uint8_t g2_even_ai_anim_frame_7683e4[]; /* ROM 0x7683e4 lv_image_dsc_t */
extern const uint8_t g2_even_ai_anim_frame_768400[]; /* ROM 0x768400 lv_image_dsc_t */
extern const uint8_t g2_even_ai_anim_frame_76841c[]; /* ROM 0x76841c lv_image_dsc_t */
extern const uint8_t g2_even_ai_anim_frame_768438[]; /* ROM 0x768438 lv_image_dsc_t */
extern const uint8_t g2_even_ai_anim_frame_768454[]; /* ROM 0x768454 lv_image_dsc_t */
extern const uint8_t g2_even_ai_anim_frame_768470[]; /* ROM 0x768470 lv_image_dsc_t */
extern const uint8_t g2_even_ai_anim_frame_76848c[]; /* ROM 0x76848c lv_image_dsc_t */
extern const uint8_t g2_even_ai_anim_frame_7684a8[]; /* ROM 0x7684a8 lv_image_dsc_t */
extern const uint8_t g2_even_ai_anim_frame_7684c4[]; /* ROM 0x7684c4 lv_image_dsc_t */
extern const uint8_t g2_even_ai_anim_frame_7684e0[]; /* ROM 0x7684e0 lv_image_dsc_t */
extern const uint8_t g2_even_ai_anim_frame_7684fc[]; /* ROM 0x7684fc lv_image_dsc_t */
extern const uint8_t g2_even_ai_anim_frame_768518[]; /* ROM 0x768518 lv_image_dsc_t */
extern const uint8_t g2_even_ai_anim_frame_768534[]; /* ROM 0x768534 lv_image_dsc_t */
extern const uint8_t g2_even_ai_anim_frame_768550[]; /* ROM 0x768550 lv_image_dsc_t */
extern const uint8_t g2_even_ai_anim_frame_76856c[]; /* ROM 0x76856c lv_image_dsc_t */
extern const uint8_t g2_even_ai_anim_frame_768588[]; /* ROM 0x768588 lv_image_dsc_t */
extern const uint8_t g2_even_ai_anim_frame_7685a4[]; /* ROM 0x7685a4 lv_image_dsc_t */
extern const uint8_t g2_even_ai_anim_frame_7685c0[]; /* ROM 0x7685c0 lv_image_dsc_t */
extern const uint8_t g2_even_ai_anim_frame_7685dc[]; /* ROM 0x7685dc lv_image_dsc_t */
extern const uint8_t g2_even_ai_anim_frame_7685f8[]; /* ROM 0x7685f8 lv_image_dsc_t */
extern const uint8_t g2_even_ai_anim_frame_768614[]; /* ROM 0x768614 lv_image_dsc_t */
extern const uint8_t g2_even_ai_anim_frame_768630[]; /* ROM 0x768630 lv_image_dsc_t */
extern const uint8_t g2_even_ai_anim_frame_76864c[]; /* ROM 0x76864c lv_image_dsc_t */
extern const uint8_t g2_even_ai_anim_frame_768668[]; /* ROM 0x768668 lv_image_dsc_t */
extern const uint8_t g2_even_ai_anim_frame_768684[]; /* ROM 0x768684 lv_image_dsc_t */
extern const uint8_t g2_even_ai_anim_frame_7686a0[]; /* ROM 0x7686a0 lv_image_dsc_t */
extern const uint8_t g2_even_ai_anim_frame_7686bc[]; /* ROM 0x7686bc lv_image_dsc_t */
extern const uint8_t g2_even_ai_anim_frame_7686d8[]; /* ROM 0x7686d8 lv_image_dsc_t */
extern const uint8_t g2_even_ai_anim_frame_7686f4[]; /* ROM 0x7686f4 lv_image_dsc_t */
extern const uint8_t g2_even_ai_anim_frame_768710[]; /* ROM 0x768710 lv_image_dsc_t */
extern const uint8_t g2_even_ai_anim_frame_76872c[]; /* ROM 0x76872c lv_image_dsc_t */
extern const uint8_t g2_even_ai_anim_frame_768748[]; /* ROM 0x768748 lv_image_dsc_t */
extern const uint8_t g2_even_ai_anim_frame_768764[]; /* ROM 0x768764 lv_image_dsc_t */
extern const uint8_t g2_even_ai_anim_frame_768780[]; /* ROM 0x768780 lv_image_dsc_t */
extern const uint8_t g2_even_ai_anim_frame_76879c[]; /* ROM 0x76879c lv_image_dsc_t */
extern const uint8_t g2_even_ai_anim_frame_7687b8[]; /* ROM 0x7687b8 lv_image_dsc_t */
extern const uint8_t g2_even_ai_anim_frame_7687d4[]; /* ROM 0x7687d4 lv_image_dsc_t */
extern const uint8_t g2_even_ai_anim_frame_7687f0[]; /* ROM 0x7687f0 lv_image_dsc_t */
extern const uint8_t g2_even_ai_anim_frame_76880c[]; /* ROM 0x76880c lv_image_dsc_t */
extern const uint8_t g2_even_ai_anim_frame_768828[]; /* ROM 0x768828 lv_image_dsc_t */
extern const uint8_t g2_even_ai_anim_frame_768844[]; /* ROM 0x768844 lv_image_dsc_t */
extern const uint8_t g2_even_ai_anim_frame_768860[]; /* ROM 0x768860 lv_image_dsc_t */
extern const uint8_t g2_even_ai_anim_frame_76887c[]; /* ROM 0x76887c lv_image_dsc_t */
extern const uint8_t g2_even_ai_anim_frame_768898[]; /* ROM 0x768898 lv_image_dsc_t */
extern const uint8_t g2_even_ai_anim_frame_7688b4[]; /* ROM 0x7688b4 lv_image_dsc_t */
extern const uint8_t g2_even_ai_anim_frame_7688d0[]; /* ROM 0x7688d0 lv_image_dsc_t */
extern const uint8_t g2_even_ai_anim_frame_7688ec[]; /* ROM 0x7688ec lv_image_dsc_t */
extern const uint8_t g2_even_ai_anim_frame_768908[]; /* ROM 0x768908 lv_image_dsc_t */
extern const uint8_t g2_even_ai_anim_frame_768924[]; /* ROM 0x768924 lv_image_dsc_t */
extern const uint8_t g2_even_ai_anim_frame_768940[]; /* ROM 0x768940 lv_image_dsc_t */
extern const uint8_t g2_even_ai_anim_frame_76895c[]; /* ROM 0x76895c lv_image_dsc_t */
extern const uint8_t g2_even_ai_anim_frame_768978[]; /* ROM 0x768978 lv_image_dsc_t */
extern const uint8_t g2_img_dsc_76c1e8[]; /* ROM 0x76c1e8 lv_image_dsc_t */
extern const uint8_t g2_img_dsc_76c204[]; /* ROM 0x76c204 lv_image_dsc_t */
extern const uint8_t g2_img_dsc_76c220[]; /* ROM 0x76c220 lv_image_dsc_t */
extern const uint8_t g2_img_dsc_76c23c[]; /* ROM 0x76c23c lv_image_dsc_t */
extern const uint8_t g2_img_dsc_76c258[]; /* ROM 0x76c258 lv_image_dsc_t */
extern const uint8_t g2_img_dsc_76c274[]; /* ROM 0x76c274 lv_image_dsc_t */
extern const uint8_t g2_img_dsc_76c290[]; /* ROM 0x76c290 lv_image_dsc_t */
extern const uint8_t g2_img_dsc_76c2ac[]; /* ROM 0x76c2ac lv_image_dsc_t */
extern const uint8_t g2_img_dsc_76c2c8[]; /* ROM 0x76c2c8 lv_image_dsc_t */
extern const uint8_t g2_img_dsc_76c2e4[]; /* ROM 0x76c2e4 lv_image_dsc_t */
extern const uint8_t g2_img_dsc_76c300[]; /* ROM 0x76c300 lv_image_dsc_t */
extern const uint8_t g2_img_dsc_76c31c[]; /* ROM 0x76c31c lv_image_dsc_t */
extern const uint8_t g2_img_dsc_76c338[]; /* ROM 0x76c338 lv_image_dsc_t */
extern const uint8_t g2_img_dsc_76c354[]; /* ROM 0x76c354 lv_image_dsc_t */
extern const uint8_t g2_img_dsc_76c370[]; /* ROM 0x76c370 lv_image_dsc_t */
extern const uint8_t g2_img_dsc_76c38c[]; /* ROM 0x76c38c lv_image_dsc_t */
extern const uint8_t g2_img_dsc_76c3a8[]; /* ROM 0x76c3a8 lv_image_dsc_t */
extern const uint8_t g2_img_dsc_76c3c4[]; /* ROM 0x76c3c4 lv_image_dsc_t */
extern const uint8_t g2_img_dsc_76c3e0[]; /* ROM 0x76c3e0 lv_image_dsc_t */
extern const uint8_t g2_img_dsc_76c3fc[]; /* ROM 0x76c3fc lv_image_dsc_t */
extern const uint8_t g2_img_dsc_76c418[]; /* ROM 0x76c418 lv_image_dsc_t */
extern const uint8_t g2_img_dsc_76c434[]; /* ROM 0x76c434 lv_image_dsc_t */
extern const uint8_t g2_img_dsc_76c450[]; /* ROM 0x76c450 lv_image_dsc_t */
extern const uint8_t g2_img_dsc_76c46c[]; /* ROM 0x76c46c lv_image_dsc_t */
extern const uint8_t g2_img_dsc_76c488[]; /* ROM 0x76c488 lv_image_dsc_t */

/* RAM 0x200009c0 (.data, 18 frames). */
const void *const g2_even_ai_anim_frames_200009c0[18] = {
    g2_even_ai_anim_frame_7685dc, g2_even_ai_anim_frame_7686f4, g2_even_ai_anim_frame_768710,
    g2_even_ai_anim_frame_76872c, g2_even_ai_anim_frame_768748, g2_even_ai_anim_frame_768764,
    g2_even_ai_anim_frame_768780, g2_even_ai_anim_frame_76879c, g2_even_ai_anim_frame_7687b8,
    g2_even_ai_anim_frame_7685f8, g2_even_ai_anim_frame_768614, g2_even_ai_anim_frame_768630,
    g2_even_ai_anim_frame_76864c, g2_even_ai_anim_frame_768668, g2_even_ai_anim_frame_768684,
    g2_even_ai_anim_frame_7686a0, g2_even_ai_anim_frame_7686bc, g2_even_ai_anim_frame_7686d8,
};

/* RAM 0x20000a08 (.data, 19 frames). */
const void *const g2_even_ai_anim_frames_20000a08[19] = {
    g2_even_ai_anim_frame_7683c8, g2_even_ai_anim_frame_7684fc, g2_even_ai_anim_frame_768518,
    g2_even_ai_anim_frame_768534, g2_even_ai_anim_frame_768550, g2_even_ai_anim_frame_76856c,
    g2_even_ai_anim_frame_768588, g2_even_ai_anim_frame_7685a4, g2_even_ai_anim_frame_7685c0,
    g2_even_ai_anim_frame_7683e4, g2_even_ai_anim_frame_768400, g2_even_ai_anim_frame_76841c,
    g2_even_ai_anim_frame_768438, g2_even_ai_anim_frame_768454, g2_even_ai_anim_frame_768470,
    g2_even_ai_anim_frame_76848c, g2_even_ai_anim_frame_7684a8, g2_even_ai_anim_frame_7684c4,
    g2_even_ai_anim_frame_7684e0,
};

/* RAM 0x20000a54 (.data, 25 frames). */
const void *const g2_even_ai_anim_frames_20000a54[25] = {
    g2_img_dsc_76c1e8, g2_img_dsc_76c31c, g2_img_dsc_76c3e0,
    g2_img_dsc_76c3fc, g2_img_dsc_76c418, g2_img_dsc_76c434,
    g2_img_dsc_76c450, g2_img_dsc_76c46c, g2_img_dsc_76c488,
    g2_img_dsc_76c204, g2_img_dsc_76c220, g2_img_dsc_76c23c,
    g2_img_dsc_76c258, g2_img_dsc_76c274, g2_img_dsc_76c290,
    g2_img_dsc_76c2ac, g2_img_dsc_76c2c8, g2_img_dsc_76c2e4,
    g2_img_dsc_76c300, g2_img_dsc_76c338, g2_img_dsc_76c354,
    g2_img_dsc_76c370, g2_img_dsc_76c38c, g2_img_dsc_76c3a8,
    g2_img_dsc_76c3c4,
};

/* RAM 0x20000ab8 (.data, 16 frames). */
const void *const g2_even_ai_anim_frames_20000ab8[16] = {
    g2_even_ai_anim_frame_7687d4, g2_even_ai_anim_frame_7688b4, g2_even_ai_anim_frame_7688d0,
    g2_even_ai_anim_frame_7688ec, g2_even_ai_anim_frame_768908, g2_even_ai_anim_frame_768924,
    g2_even_ai_anim_frame_768940, g2_even_ai_anim_frame_76895c, g2_even_ai_anim_frame_768978,
    g2_even_ai_anim_frame_7687f0, g2_even_ai_anim_frame_76880c, g2_even_ai_anim_frame_768828,
    g2_even_ai_anim_frame_768844, g2_even_ai_anim_frame_768860, g2_even_ai_anim_frame_76887c,
    g2_even_ai_anim_frame_768898,
};
