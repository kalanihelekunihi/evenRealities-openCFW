/* SPDX-License-Identifier: MIT
 * Image-A stage2 initialized SRAM 0x10026b94..0x10026bc7 and
 * 0x10026c1c..0x10026c73. The 0x2002 aliases used by XIP require
 * final linker/copy qualification. Source values below are stock data.
 */
#include <stddef.h>
#include <stdint.h>

__attribute__((section(".gx8002.xip.aout_route")))
const char gx8002_aout_route_name[] = "0 route play";
_Static_assert(sizeof(gx8002_aout_route_name) == 13u,
               "stock XIP route literal extent");

struct gx8002_aout_context {
    const char *route_name;           /* +0x00 */
    uint8_t allocated;                /* +0x04 */
    uint8_t reserved_05_07[3];
    uint32_t owner_word;              /* +0x08; allocation guard */
    uint8_t mode;                     /* +0x0c; allocation guard */
    uint8_t reserved_0d_0f[3];
    uint16_t mute_state;              /* +0x10 */
    int16_t requested_db;             /* +0x12 */
    uint32_t control_word;            /* +0x14 */
    uint8_t requested_mode;           /* +0x18 */
    uint8_t sample_width;             /* +0x19 */
    uint8_t frame_state;              /* +0x1a */
    uint8_t callback_active;          /* +0x1b */
    uint32_t frame_done;              /* +0x1c */
    uint32_t sample_first;            /* +0x20 */
    uint32_t sample_last;             /* +0x24 */
    uintptr_t frame_over_callback;    /* +0x28 */
    uintptr_t idle_callback;          /* +0x2c */
    uintptr_t hardware_configuration; /* +0x30 */
};
_Static_assert(sizeof(struct gx8002_aout_context) == 52u,
               "stock AOUT context extent");
_Static_assert(offsetof(struct gx8002_aout_context, allocated) == 4u &&
               offsetof(struct gx8002_aout_context, mode) == 12u &&
               offsetof(struct gx8002_aout_context, sample_width) == 25u &&
               offsetof(struct gx8002_aout_context, hardware_configuration) == 48u,
               "stock AOUT context field offsets");

__attribute__((section(".gx8002.sram.aout_context"), aligned(4)))
struct gx8002_aout_context gx8002_aout_product_context = {
    .route_name = gx8002_aout_route_name
};

/* The first two words feed playback control bits; I2S/DAC consumers
 * identify their later offsets. The remaining named slots retain the
 * exact initialized product values without assigning unknown meaning. */
struct gx8002_aout_configuration {
    uint32_t playback_bit1_source;    /* +0x00 */
    uint32_t playback_bit0_source;    /* +0x04 */
    uint32_t i2s_08;                  /* +0x08 */
    uint32_t i2s_0c;                  /* +0x0c */
    uint32_t pcm_rate_code;           /* +0x10 */
    uint32_t i2s_14;                  /* +0x14 */
    uint32_t i2s_18;                  /* +0x18 */
    uint32_t i2s_1c;                  /* +0x1c */
    uint32_t i2s_20;                  /* +0x20 */
    uint32_t i2s_24;                  /* +0x24 */
    uint32_t i2s_28;                  /* +0x28 */
    uint32_t i2s_2c;                  /* +0x2c */
    uint32_t dac_30;                  /* +0x30 */
    uint32_t dac_34;                  /* +0x34 */
    uint32_t dac_38;                  /* +0x38 */
    uint32_t dac_3c;                  /* +0x3c */
    uint32_t dac_40;                  /* +0x40 */
    uint32_t dac_44;                  /* +0x44 */
    uint32_t dac_48;                  /* +0x48 */
    uint32_t dac_4c;                  /* +0x4c */
    uint32_t dac_50;                  /* +0x50 */
    uint32_t dac_54;                  /* +0x54 */
};
_Static_assert(sizeof(struct gx8002_aout_configuration) == 88u,
               "stock AOUT configuration extent");

__attribute__((section(".gx8002.sram.aout_configuration"), aligned(4)))
struct gx8002_aout_configuration gx8002_aout_product_configuration = {
    .playback_bit0_source = 1u,
    .i2s_1c = 1u,
    .dac_34 = UINT32_C(0xff0f0003),
    .dac_38 = 3u,
    .dac_40 = UINT32_C(0xfff00003),
    .dac_44 = 3u,
    .dac_4c = 4u,
    .dac_54 = 1u
};
