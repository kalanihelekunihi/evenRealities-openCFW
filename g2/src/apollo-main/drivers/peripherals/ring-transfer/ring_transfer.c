/* Experimental full valid-path reductions of native ring transfer helpers
 * 0x57e0f0 (write) and 0x57e220 (read). Fatal invalid paths remain typed
 * contracts of the native port mask/assert routine. */
#include <stdint.h>

extern uint32_t audio_uart_ring_write_copy(void *, const void *, uint32_t,
                                            uint32_t);
extern uint32_t audio_uart_ring_read_copy(void *, void *, uint32_t,
                                           uint32_t);

uint32_t audio_uart_ring_write(void *descriptor, const void *source,
                               uint32_t requested, uint32_t available) {
    uint8_t *d = (uint8_t *)descriptor;
    uint32_t offset = *(uint32_t *)(d + 4u);
    if ((d[28] & 1u) != 0u) {
        if (available < 4u) requested = 0u;
        else offset = audio_uart_ring_write_copy(descriptor, &requested,
                                                 4u, offset);
    } else if (available <= requested) {
        requested = available;
    }
    if (requested != 0u) {
        offset = audio_uart_ring_write_copy(descriptor, source, requested,
                                            offset);
        *(uint32_t *)(d + 4u) = offset;
    }
    return requested;
}

uint32_t audio_uart_ring_read(void *descriptor, void *destination,
                              uint32_t requested, uint32_t available) {
    uint8_t *d = (uint8_t *)descriptor;
    uint32_t offset = *(uint32_t *)d;
    if ((d[28] & 1u) != 0u) {
        uint32_t header_length = 0u;
        uint32_t payload_available = available - 4u;
        offset = audio_uart_ring_read_copy(descriptor, &header_length, 4u,
                                           offset);
        requested = requested < header_length ? 0u : header_length;
        available = payload_available;
    }
    if (requested < available) available = requested;
    if (available != 0u) {
        offset = audio_uart_ring_read_copy(descriptor, destination,
                                           available, offset);
        *(uint32_t *)d = offset;
    }
    return available;
}
