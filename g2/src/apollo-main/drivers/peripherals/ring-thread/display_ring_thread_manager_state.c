/* Apollo Main compressed SRAM record 0x75d3f4 initializes the observed
 * ring-thread manager at 0x20004120. Opaque native code addresses occupy
 * the first eight bytes; thread/queue handles begin at +8/+12. Absolute
 * placement and any wider native allocation remain separate gates. */
#include <stdint.h>

/* Sim-test fix (2026-10-26): the stock init words 0x004c4da5/0x004c4dd1 are
 * Thumb pointers to thread_ring_create 0x4c4da4 / thread_ring_terminate
 * 0x4c4dd0 (g2/symbols/apollo_main.tsv); thread_manager_threads_init_4c953e
 * calls +0 via blx. As raw stock bytes they faulted (INVSTATE) in Renode.
 * Now relocated to our symbols. Layout unchanged. */
void thread_ring_create(void);
void thread_ring_terminate(void);
struct ring_thread_manager {void (*init)(void);void (*deinit)(void);void *thread;void *queue;};
_Static_assert(sizeof(struct ring_thread_manager)==16u,"ring manager ABI");
struct ring_thread_manager audio_uart_ring_thread_manager = {
    thread_ring_create,thread_ring_terminate,
    0,0,
};
