#include <stdint.h>
#include "em9305_ram.h"

/* Native 0x325618..0x325648: when the scan ring's filter byte ((uintptr_t)&em9305_ram_80505c)
 * differs from the configured one (+4 of the config at ((uintptr_t)&em9305_ram_805c5c + 0x1cu)),
 * reinitialise the ring at ((uintptr_t)&em9305_ram_803d58 + 0x12c4u) with the new enable state; then
 * report command status 0. */
extern uint32_t opencfw_em9305_scan_ring_init_316a54(uintptr_t ring, uint32_t enable);
extern uint32_t opencfw_em9305_command_status_30e8c0(uint32_t status);

uint32_t opencfw_em9305_scan_action_325618(void)
{
    uintptr_t config=em9305_ram_805c5c.u32_805c78;
    uint32_t current=em9305_ram_80505c.u8_80505c;
    uint32_t wanted=*(volatile uint8_t *)(config+4u);
    if(current!=wanted)
        (void)opencfw_em9305_scan_ring_init_316a54(((uintptr_t)&em9305_ram_803d58 + 0x12c4u),wanted!=0u);
    return opencfw_em9305_command_status_30e8c0(0u);
}
