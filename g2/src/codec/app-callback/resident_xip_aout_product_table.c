/* SPDX-License-Identifier: MIT
 * Native image-A stage2 SRAM 0x10026bc8..0x10026c1b (runtime alias
 * 0x20026bc8): 21 function-pointer words. Source image SHA-256
 * b5466e260001986f04418e55cdc810ea9654f2f6b1c3ef24dbd95af7b3995f8a.
 * Each nonzero word names an independently reconstructed XIP body.
 * Final SRAM placement, copy and alias semantics remain linker obligations.
 */
#include <stdint.h>

extern uint32_t gx8002_xip_aout_alloc_playback_10205254(uint32_t);
extern uint32_t gx8002_xip_aout_hw_initialize_10204f18(uint32_t);
extern uint32_t gx8002_xip_aout_exit_10205344(void);
extern uint32_t gx8002_xip_aout_suspend_10204ec0(volatile uint8_t *);
extern uint32_t gx8002_xip_aout_resume_1020521c(volatile uint8_t *);
extern int32_t gx8002_xip_aout_free_102052e0(volatile uint8_t *);
extern int32_t gx8002_xip_aout_config_buffer_10204e6c(
    uint32_t, const uint32_t *);
extern int32_t gx8002_xip_aout_config_pcm_10204d38(
    volatile uint8_t *, const volatile uint8_t *);
extern int32_t gx8002_xip_aout_config_i2s_10204c64(
    volatile uint8_t *, const volatile uint8_t *);
extern int32_t gx8002_xip_aout_config_dac_10204c90(
    volatile uint8_t *, const volatile uint8_t *);
extern uint32_t gx8002_xip_aout_config_cb_10205318(
    volatile uint8_t *, const uint32_t *);
extern uint32_t gx8002_xip_aout_push_frame_102051a8(
    volatile uint8_t *, const void *);
extern uint32_t gx8002_xip_aout_drain_frame_10204d04(volatile uint8_t *);
extern uint32_t gx8002_xip_aout_set_db_10204f90(
    volatile uint8_t *, int32_t);
extern uint32_t gx8002_xip_aout_get_db_10204ff0(
    const volatile uint8_t *, uint16_t *);
extern uint32_t gx8002_xip_aout_set_mute_1020508c(
    volatile uint8_t *, uint32_t);
extern int32_t gx8002_xip_aout_get_mute_10204cd4(const void *);
extern uint32_t gx8002_xip_aout_set_channel_1020502c(uint32_t, uint32_t);
extern uint32_t gx8002_xip_aout_set_fixed_src_10204cdc(uint32_t, uint32_t);
extern uint32_t gx8002_xip_aout_get_sdc_addr_10204cfc(void);

struct gx8002_aout_product_ops {
    uint32_t (*alloc)(uint32_t);
    uint32_t (*initialize)(uint32_t);
    uint32_t (*exit)(void);
    uint32_t (*suspend)(volatile uint8_t *);
    uint32_t (*resume)(volatile uint8_t *);
    int32_t (*free)(volatile uint8_t *);
    int32_t (*config_buffer)(uint32_t, const uint32_t *);
    int32_t (*config_pcm)(volatile uint8_t *, const volatile uint8_t *);
    int32_t (*config_i2s)(volatile uint8_t *, const volatile uint8_t *);
    int32_t (*config_dac)(volatile uint8_t *, const volatile uint8_t *);
    uint32_t (*config_cb)(volatile uint8_t *, const uint32_t *);
    uint32_t (*push_frame)(volatile uint8_t *, const void *);
    uintptr_t reserved_zero;
    uint32_t (*drain_frame)(volatile uint8_t *);
    uint32_t (*set_db)(volatile uint8_t *, int32_t);
    uint32_t (*get_db)(const volatile uint8_t *, uint16_t *);
    uint32_t (*set_mute)(volatile uint8_t *, uint32_t);
    int32_t (*get_mute)(const void *);
    uint32_t (*set_channel)(uint32_t, uint32_t);
    uint32_t (*set_fixed_src)(uint32_t, uint32_t);
    uint32_t (*get_sdc_addr)(void);
};

_Static_assert(sizeof(struct gx8002_aout_product_ops) == 84u,
               "stock AOUT operation table has 21 four-byte slots");

__attribute__((section(".gx8002.sram.aout_operations"), aligned(4)))
struct gx8002_aout_product_ops gx8002_aout_product_operations = {
    .alloc = gx8002_xip_aout_alloc_playback_10205254,
    .initialize = gx8002_xip_aout_hw_initialize_10204f18,
    .exit = gx8002_xip_aout_exit_10205344,
    .suspend = gx8002_xip_aout_suspend_10204ec0,
    .resume = gx8002_xip_aout_resume_1020521c,
    .free = gx8002_xip_aout_free_102052e0,
    .config_buffer = gx8002_xip_aout_config_buffer_10204e6c,
    .config_pcm = gx8002_xip_aout_config_pcm_10204d38,
    .config_i2s = gx8002_xip_aout_config_i2s_10204c64,
    .config_dac = gx8002_xip_aout_config_dac_10204c90,
    .config_cb = gx8002_xip_aout_config_cb_10205318,
    .push_frame = gx8002_xip_aout_push_frame_102051a8,
    .reserved_zero = 0u,
    .drain_frame = gx8002_xip_aout_drain_frame_10204d04,
    .set_db = gx8002_xip_aout_set_db_10204f90,
    .get_db = gx8002_xip_aout_get_db_10204ff0,
    .set_mute = gx8002_xip_aout_set_mute_1020508c,
    .get_mute = gx8002_xip_aout_get_mute_10204cd4,
    .set_channel = gx8002_xip_aout_set_channel_1020502c,
    .set_fixed_src = gx8002_xip_aout_set_fixed_src_10204cdc,
    .get_sdc_addr = gx8002_xip_aout_get_sdc_addr_10204cfc,
};
