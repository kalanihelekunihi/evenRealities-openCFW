/* Native cold pointer at0x20006960 resolves to type1 TX veneer0x3407c.
 * Retain a symbolic C relocation so the shared provider owns its implementation.
 * Runtime registration, warm-start ordering and concurrency remain gated. */
#include <stdint.h>
extern int32_t r1_ble_tx_queue_dispatch_type1(uint32_t,const void *,uint32_t);
volatile uintptr_t r1_fragment_send_callback
    __attribute__((section(".r1.fragment.send_callback"))) =
    (uintptr_t)&r1_ble_tx_queue_dispatch_type1;
