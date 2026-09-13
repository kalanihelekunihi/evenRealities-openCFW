/* SPDX-License-Identifier: MIT */
/* Stock-specific LvpAudioInQueryFFTVad tuning; qualification pending. */
#include <driver/gx_audio_in.h>
extern int printf(const char *, ...);
extern const char open_cfw_vad_level_4_message[];
extern const char open_cfw_vad_level_3_message[];
extern const char open_cfw_vad_level_2_message[];
extern const char open_cfw_vad_level_1_message[];
#define LEVEL (*(volatile unsigned int *)0x2002dfa4)
int open_cfw_gx8002_audio_input_query_vad(unsigned int *sdc_addr)
{
    (void)sdc_addr;
    unsigned int noise = gx_audio_in_get_distance_noise_smooth();
    unsigned int next = 0;
    if (noise < 3145728 && LEVEL != 4) {
        printf(open_cfw_vad_level_4_message, noise); next = 4;
    } else if (noise >= 3145728 && noise < 6291456 && LEVEL != 3) {
        printf(open_cfw_vad_level_3_message, noise); next = 3;
    } else if (noise >= 6291456 && noise <= 20971520 && LEVEL != 2) {
        printf(open_cfw_vad_level_2_message, noise); next = 2;
    } else if (noise > 20971520 && LEVEL != 1) {
        printf(open_cfw_vad_level_1_message, noise); next = 1;
    }
    if (next) {
        LEVEL = next;
        gx_audio_in_set_fftvad_curve_1(1024, 3840);
        gx_audio_in_set_fftvad_curve_2(1229, 1536);
        gx_audio_in_set_fftvad_curve_3(1229, 8192);
        gx_audio_in_set_fftvad_curve_4(1843, 819);
        gx_audio_in_set_fftvad_curve_5(2560);
        GX_AUDIO_IN_FFTVAD_CHIPPING chipping;
        chipping.chipping_1 = 655;
        chipping.chipping_2 = 262;
        chipping.chipping_3 = 131;
        chipping.chipping_4 = 33;
        gx_audio_in_set_fftvad_chipping(chipping);
        GX_AUDIO_IN_FFTVAD_W weights = {0};
        weights.w1 = 1; weights.w2 = 1; weights.w3 = 0;
        gx_audio_in_set_fftvad_w(weights);
    }
    GX_AUDIO_IN_FFTVAD_STATE state;
    gx_audio_in_get_fftvad_state(&state);
    unsigned int bit = (state.vad_state_index + 94u) % 95u;
    unsigned int value = bit < 32 ? state.vad_state_l : bit < 64 ? state.vad_state_m : state.vad_state_h;
    unsigned int shift = bit < 32 ? bit : bit < 64 ? bit - 32 : bit - 64;
    return LEVEL == 1 ? 1 : (value >> shift) & 1;
}
