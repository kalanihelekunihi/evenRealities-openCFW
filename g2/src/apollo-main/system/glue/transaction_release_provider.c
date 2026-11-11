#include <stdint.h>

extern void audio_file_heap_free(void *);

/* Single-access unaligned word and halfword (LDR/STR/STRH tolerate
 * misalignment on this core: CCR.UNALIGN_TRP is clear). */
typedef uint32_t unaligned_u32 __attribute__((aligned(1)));
typedef uint16_t unaligned_u16 __attribute__((aligned(1)));

/* Apollo MAIN 0x57c640. Packet pointer and length are at unaligned offsets
 * 14 and 18; stock reloads the pointer after the null test. */
void audio_release_transaction(void *opaque) {
    if (!opaque) return;
    volatile unaligned_u32 *const packet_slot =
        (volatile unaligned_u32 *)(void *)((uint8_t *)opaque + 14);
    volatile unaligned_u16 *const length_slot =
        (volatile unaligned_u16 *)(void *)((uint8_t *)opaque + 18);
    if (!*packet_slot) return;
    audio_file_heap_free((void *)(uintptr_t)*packet_slot);
    *packet_slot = 0u;
    *length_slot = 0u;
}
