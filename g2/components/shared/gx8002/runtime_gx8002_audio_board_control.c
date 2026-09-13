/* SPDX-License-Identifier: MIT
 * Recovered board control ABI, corroborated by the pinned NationalChip
 * grus_gx8002_slight_1v/audio_board.c gain map and DMIC initialization.
 */
#include <stdint.h>
extern unsigned char open_cfw_audio_board_state[] __attribute__((aligned(4)));
extern const char open_cfw_dmic_channels[], open_cfw_dmic_gain[];
extern int printf(const char *, ...);
void *open_cfw_audio_board_get(void) { return open_cfw_audio_board_state; }
__attribute__((noinline)) int open_cfw_audio_board_gain(unsigned gain) {
    return gain <= 9 ? (int)(gain * 6) : 0;
}
void open_cfw_audio_board_init(void) {
    printf(open_cfw_dmic_channels, 2);
    unsigned config=*(volatile uint16_t *)(open_cfw_audio_board_state+32);
    printf(open_cfw_dmic_gain, open_cfw_audio_board_gain((config>>6)&15));
}
