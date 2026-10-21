/* Experimental source reduction of native ring copy helpers 0x57e268 and
 * 0x57e2f6. Descriptor offsets are authenticated in the Apollo corpus. */
#include <stdint.h>

extern void offline_assert(void) __attribute__((noreturn));
extern void audio_uart_checksum_copy(void *destination, const void *source,
                                     uint32_t count);

static uint32_t ring_capacity(const void *descriptor) {
    return *(const uint32_t *)((const uint8_t *)descriptor + 8u);
}

static uint8_t *ring_storage(const void *descriptor) {
    return (uint8_t *)(uintptr_t)*(const uint32_t *)
        ((const uint8_t *)descriptor + 24u);
}

uint32_t audio_uart_ring_write_copy(void *descriptor, const void *source,
                                    uint32_t count, uint32_t offset) {
    uint32_t capacity = ring_capacity(descriptor);
    if (count == 0u) offline_assert();
    uint32_t first = count;
    if (capacity - offset < first) first = capacity - offset;
    if (first + offset > capacity) offline_assert();
    audio_uart_checksum_copy(ring_storage(descriptor) + offset, source, first);
    if (first < count) {
        if (capacity < count - first) offline_assert();
        audio_uart_checksum_copy(ring_storage(descriptor),
                                 (const uint8_t *)source + first,
                                 count - first);
    }
    uint32_t next = count + offset;
    return next >= capacity ? next - capacity : next;
}

uint32_t audio_uart_ring_read_copy(void *descriptor, void *destination,
                                   uint32_t count, uint32_t offset) {
    uint32_t capacity = ring_capacity(descriptor);
    if (count == 0u) offline_assert();
    uint32_t first = count;
    if (capacity - offset < first) first = capacity - offset;
    if (first > count || first + offset > capacity) offline_assert();
    audio_uart_checksum_copy(destination, ring_storage(descriptor) + offset,
                             first);
    if (first < count) {
        audio_uart_checksum_copy((uint8_t *)destination + first,
                                 ring_storage(descriptor), count - first);
    }
    uint32_t next = count + offset;
    return next >= capacity ? next - capacity : next;
}
