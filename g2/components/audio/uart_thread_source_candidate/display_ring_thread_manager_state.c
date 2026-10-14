/* Apollo Main compressed SRAM record 0x75d3f4 initializes the observed
 * ring-thread manager at 0x20004120. Opaque native code addresses occupy
 * the first eight bytes; thread/queue handles begin at +8/+12. Absolute
 * placement and any wider native allocation remain separate gates. */
#include <stdint.h>

struct ring_thread_manager {uint8_t reserved[8];void *thread;void *queue;};
_Static_assert(sizeof(struct ring_thread_manager)==16u,"ring manager ABI");
struct ring_thread_manager audio_uart_ring_thread_manager = {
    {0xa5u,0x4du,0x4cu,0x00u,0xd1u,0x4du,0x4cu,0x00u},
    0,0,
};
