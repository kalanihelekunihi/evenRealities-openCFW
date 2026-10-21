/* The delayed-block insert and public list insert use Apollo vListInsert
 * at 0x4560b2 with the same two-pointer, void-return ABI. */
#include "../../rtos/timer/timer-wake-providers/sorted.c"

__asm__(".global audio_block_sorted_insert\n"
        ".set audio_block_sorted_insert, audio_public_list_insert\n");
