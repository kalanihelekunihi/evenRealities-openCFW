/* Native EABI-style movement at 0x2775c has no ISO memmove return contract.
 * Preserve observed R0: source on backward-overlap path, destination end on
 * forward path. Unchanged upstream memmove supplies overlap-safe data movement. */
#include <stdint.h>
#include <stddef.h>
#include <string.h>
void *r1_native_memory_move(void *destination,const void *source,size_t length) {
    uintptr_t dst=(uintptr_t)destination,src=(uintptr_t)source;
    (void)memmove(destination,source,length);
    return (void *)((uint32_t)(dst-src)<length ? src : dst+length);
}
