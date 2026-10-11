#include <stdint.h>

extern void audio_file_heap_free(void *);

/* Apollo MAIN 0x57c640. Packet pointer and length are at unaligned offsets. */
void audio_release_transaction(void *opaque) {
    if (!opaque) return;
    uint32_t packet;
    __asm volatile("ldr.w %0, [%1, #14]" : "=r"(packet) : "r"(opaque) : "memory");
    if (!packet) return;
    __asm volatile("ldr.w %0, [%1, #14]" : "=r"(packet) : "r"(opaque) : "memory");
    audio_file_heap_free((void *)(uintptr_t)packet);
    uint32_t zero = 0;
    __asm volatile("str.w %0, [%1, #14]\n"
                   "strh %0, [%1, #18]"
                   : : "r"(zero), "r"(opaque) : "memory");
}
