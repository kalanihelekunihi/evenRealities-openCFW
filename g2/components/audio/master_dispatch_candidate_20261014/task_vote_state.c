#include <stdint.h>

/* Native RAM 0x200700e0: 32 eight-byte task slots, count at +0x100,
 * and the observed enable byte at +0x104. Startup values remain open. */
volatile uint8_t audio_task_vote_state_200700e0[0x105] __attribute__((aligned(4)));
