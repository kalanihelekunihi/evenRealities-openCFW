/* SPDX-License-Identifier: MIT
 * Image-B 0x1000a470 FFT VAD policy, including the native mode 1/2/3
 * transitions that the retained decompiler incorrectly marked unreachable.
 * Runtime mode SRAM and audio MMIO remain placement/hardware contracts.
 */
#include <stdint.h>

typedef struct {
    uint32_t vad_state_l;
    uint32_t vad_state_m;
    uint32_t vad_state_h;
    uint16_t vad_state_index;
} gx8002_image_b_fftvad_state;

typedef struct {
    uint8_t w1;
    uint8_t w2;
    uint8_t w3;
} gx8002_image_b_fftvad_w;

typedef struct {
    uint16_t chipping_1;
    uint16_t chipping_2;
    uint16_t chipping_3;
    uint16_t chipping_4;
} gx8002_image_b_fftvad_chipping;

_Static_assert(sizeof(gx8002_image_b_fftvad_state) == 16u,
               "native VAD state stack extent");
_Static_assert(sizeof(gx8002_image_b_fftvad_chipping) == 8u,
               "native VAD chipping argument extent");

extern uint32_t gx8002_image_b_audio_read_status_10005cb0(void);
extern int32_t gx8002_image_b_set_fftvad_curve_1_10005b34(
    uint32_t a, uint32_t b);
extern int32_t gx8002_image_b_set_fftvad_curve_2_10005b68(
    uint32_t a, uint32_t b);
extern int32_t gx8002_image_b_set_fftvad_curve_3_10005b9c(
    uint16_t a, int16_t b);
extern int32_t gx8002_image_b_set_fftvad_curve_4_10005bdc(
    uint32_t a, uint32_t b);
extern int32_t gx8002_image_b_set_fftvad_curve_5_10005c10(uint32_t value);
extern int32_t gx8002_image_b_set_fftvad_chipping_10005c30(
    gx8002_image_b_fftvad_chipping chipping);
extern int32_t gx8002_image_b_set_fftvad_w_10005af8(
    gx8002_image_b_fftvad_w w);
extern int32_t gx8002_image_b_get_fftvad_state_10005c80(
    gx8002_image_b_fftvad_state *state);
extern int gx8002_image_b_heap_log_10009934(const char *format, ...);

static void program_mode(uint32_t mode)
{
    if (mode == 1u) {
        (void)gx8002_image_b_set_fftvad_curve_1_10005b34(1024u, 3840u);
        (void)gx8002_image_b_set_fftvad_curve_2_10005b68(1229u, 1536u);
        (void)gx8002_image_b_set_fftvad_curve_3_10005b9c(1229u, 8192);
    } else {
        (void)gx8002_image_b_set_fftvad_curve_1_10005b34(1229u, 3840u);
        (void)gx8002_image_b_set_fftvad_curve_2_10005b68(1229u, 1280u);
        (void)gx8002_image_b_set_fftvad_curve_3_10005b9c(1229u, 4096);
    }
    if (mode == 4u)
        (void)gx8002_image_b_set_fftvad_curve_4_10005bdc(2560u, 1024u);
    else
        (void)gx8002_image_b_set_fftvad_curve_4_10005bdc(1843u, 819u);
    (void)gx8002_image_b_set_fftvad_curve_5_10005c10(
        mode == 4u ? 3072u : 2560u);

    gx8002_image_b_fftvad_chipping chipping = {655u, 262u, 131u, 33u};
    (void)gx8002_image_b_set_fftvad_chipping_10005c30(chipping);
    gx8002_image_b_fftvad_w w = {
        mode == 4u ? 3u : 1u,
        mode == 4u ? 0u : 1u,
        mode == 3u ? 3u : mode == 4u ? 0u : 10u,
    };
    (void)gx8002_image_b_set_fftvad_w_10005af8(w);
}

uint32_t gx8002_image_b_audio_vad_policy_at_1000a470(
    uint32_t status, volatile uint32_t *mode_state)
{
    uint32_t desired = 0u;
    const char *message = 0;
    if (status <= UINT32_C(0x002fffff)) {
        desired = 4u;
    } else if (status - UINT32_C(0x00300000) <= UINT32_C(0x002fffff)) {
        desired = 3u;
        message = "[LVP_AUD]vad param 3 [%d]\n";
    } else if (status - UINT32_C(0x00600000) <= UINT32_C(0x00e00000)) {
        desired = 2u;
        message = "[LVP_AUD]vad param 2 [%d]\n";
    } else if (status > UINT32_C(0x01400000)) {
        desired = 1u;
        message = "[LVP_AUD]vad param 1 [%d]\n";
    }

    if (desired != 0u && *mode_state != desired) {
        if (message != 0)
            (void)gx8002_image_b_heap_log_10009934(message, status);
        *mode_state = desired;
        program_mode(desired);
    }

    gx8002_image_b_fftvad_state vad;
    (void)gx8002_image_b_get_fftvad_state_10005c80(&vad);
    uint32_t position = ((uint32_t)vad.vad_state_index + 94u) % 95u;
    uint32_t selected = position < 32u ? vad.vad_state_l
        : position < 64u ? vad.vad_state_m : vad.vad_state_h;
    uint32_t bit = position < 32u ? position
        : position < 64u ? position - 32u : position - 64u;
    uint32_t detected = (selected & (UINT32_C(1) << bit)) != 0u;
    if (*mode_state == 1u) detected = 1u;
    return detected;
}

uint32_t gx8002_image_b_audio_vad_policy_1000a470(void)
{
    uint32_t status = gx8002_image_b_audio_read_status_10005cb0();
    volatile uint32_t *mode_state =
        (volatile uint32_t *)(uintptr_t)UINT32_C(0x2002cb84);
    return gx8002_image_b_audio_vad_policy_at_1000a470(
        status, mode_state);
}
