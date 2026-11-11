#include <stdint.h>

/* Native 0x325618..0x325648: when the scan ring's filter byte (0x80505c)
 * differs from the configured one (+4 of the config at 0x805c78),
 * reinitialise the ring at 0x80501c with the new enable state; then
 * report command status 0. */
extern uint32_t opencfw_em9305_scan_ring_init_316a54(uintptr_t ring, uint32_t enable);
extern uint32_t opencfw_em9305_command_status_30e8c0(uint32_t status);

uint32_t opencfw_em9305_scan_action_325618(void)
{
    uintptr_t config=*(volatile uint32_t *)(uintptr_t)0x805c78u;
    uint32_t current=*(volatile uint8_t *)(uintptr_t)0x80505cu;
    uint32_t wanted=*(volatile uint8_t *)(config+4u);
    if(current!=wanted)
        (void)opencfw_em9305_scan_ring_init_316a54(0x80501cu,wanted!=0u);
    return opencfw_em9305_command_status_30e8c0(0u);
}
