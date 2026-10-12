/* SPDX-License-Identifier: MIT
 * Native image-B audio-output initialized state. The root is read by
 * 0x100067ec; 0x10006a80 returns the state address at 0x20016d0c.
 * All zero fields and the six nonzero words are authenticated stock data.
 */
#include <stdint.h>

struct gx8002_image_b_audio_out_root {
    const char *name;
    uint8_t initialized;
    uint8_t reserved_after_flag[3];
    uint32_t route_or_slot;
    uint8_t mode;
    uint8_t reserved_after_mode[3];
    uint8_t live_state[36];
};

_Static_assert(sizeof(struct gx8002_image_b_audio_out_root) == 52u,
               "native audio-output root extent");
_Static_assert(sizeof(uintptr_t) == 4u, "image-B data pointer ABI");

__attribute__((section(".data.image_b.audio_out_root"), aligned(4)))
struct gx8002_image_b_audio_out_root gx8002_image_b_audio_out_root_20016c84 = {
    .name = "0 route play",
};

/* 21 native words through the highest +0x50 access in the two hardware
 * configuration callbacks. Word 7 is a live gate; the remaining named
 * initial values feed register-control fields or output extension slots. */
__attribute__((section(".data.image_b.audio_out_state"), aligned(4)))
uint32_t gx8002_image_b_audio_out_state_20016d0c[21] = {
    [7] = 1u,
    [13] = UINT32_C(0xff0f0003),
    [14] = 3u,
    [16] = UINT32_C(0xfff00003),
    [17] = 3u,
    [19] = 4u,
};
