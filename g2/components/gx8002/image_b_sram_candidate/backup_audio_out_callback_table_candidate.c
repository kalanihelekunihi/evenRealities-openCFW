/* SPDX-License-Identifier: MIT
 * Typed audio-output callback table at stock image-B
 * 0x10016cb8..0x10016d0c (DRAM alias 0x20016cb8). All nonzero entries now
 * name candidate C providers. Native error/side-effect equivalence remains
 * a separate admission gate after source selection.
 */
#include <stdint.h>

#define TARGET(hexaddr) gx8002_image_b_audio_out_target_##hexaddr
extern void gx8002_image_b_audio_out_alloc_native_100067ec(void);
extern void gx8002_image_b_audio_out_power_up_1000663c(void);
extern void gx8002_image_b_audio_out_power_down_1000660c(void);
extern void gx8002_image_b_audio_out_disable_routes_100065bc(void);
extern void gx8002_image_b_audio_out_enable_routes_1000657c(void);
extern void gx8002_image_b_audio_out_clear_runtime_10006540(void);
extern void gx8002_image_b_audio_out_set_buffers_100064ec(void);
extern void gx8002_image_b_audio_out_pcm_config_100061f4(void);
extern void gx8002_image_b_audio_out_config_hardware_1000687c(void);
extern void gx8002_image_b_audio_out_config_dac_1000694c(void);
extern void gx8002_image_b_audio_out_config_route_10005ff4(void);
extern void gx8002_image_b_audio_out_push_descriptor_10006774(void);
extern void gx8002_image_b_audio_out_dac_start_wait_100061bc(void);
extern void gx8002_image_b_audio_out_set_db_1000602c(void);
extern void gx8002_image_b_audio_out_get_db_1000609c(void);
extern void gx8002_image_b_audio_out_dac_mute_100060ec(void);
extern void gx8002_image_b_audio_out_status_halfword_10006124(void);
extern void gx8002_image_b_audio_out_route_mode_1000612c(void);
extern void gx8002_image_b_audio_out_dac_high_word_10006194(void);
extern void gx8002_image_b_audio_out_dac_read_100061b4(void);

_Static_assert(sizeof(uintptr_t) == 4u, "image-B callback pointer ABI");
__attribute__((section(".data.image_b.audio_out_callback_table"), aligned(4)))
uintptr_t gx8002_image_b_audio_out_callback_table_candidate[21] = {
    (uintptr_t)&gx8002_image_b_audio_out_alloc_native_100067ec,
    (uintptr_t)&gx8002_image_b_audio_out_power_up_1000663c,
    (uintptr_t)&gx8002_image_b_audio_out_power_down_1000660c,
    (uintptr_t)&gx8002_image_b_audio_out_disable_routes_100065bc,
    (uintptr_t)&gx8002_image_b_audio_out_enable_routes_1000657c,
    (uintptr_t)&gx8002_image_b_audio_out_clear_runtime_10006540,
    (uintptr_t)&gx8002_image_b_audio_out_set_buffers_100064ec,
    (uintptr_t)&gx8002_image_b_audio_out_pcm_config_100061f4,
    (uintptr_t)&gx8002_image_b_audio_out_config_hardware_1000687c,
    (uintptr_t)&gx8002_image_b_audio_out_config_dac_1000694c,
    (uintptr_t)&gx8002_image_b_audio_out_config_route_10005ff4,
    (uintptr_t)&gx8002_image_b_audio_out_push_descriptor_10006774,
    0u,
    (uintptr_t)&gx8002_image_b_audio_out_dac_start_wait_100061bc,
    (uintptr_t)&gx8002_image_b_audio_out_set_db_1000602c,
    (uintptr_t)&gx8002_image_b_audio_out_get_db_1000609c,
    (uintptr_t)&gx8002_image_b_audio_out_dac_mute_100060ec,
    (uintptr_t)&gx8002_image_b_audio_out_status_halfword_10006124,
    (uintptr_t)&gx8002_image_b_audio_out_route_mode_1000612c,
    (uintptr_t)&gx8002_image_b_audio_out_dac_high_word_10006194,
    (uintptr_t)&gx8002_image_b_audio_out_dac_read_100061b4,
};
