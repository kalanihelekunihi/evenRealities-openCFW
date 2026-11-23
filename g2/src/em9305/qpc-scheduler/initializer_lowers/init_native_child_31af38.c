#include <stdint.h>
#include "em9305_ram.h"

/* Native 0x31af38..0x31af80: load the encryption request from the current
 * packet (*((uintptr_t)&em9305_ram_805c5c + 0x10u)): 16-byte key (+0xe) to record+405, 8-byte random
 * (+4) to +445 and the diversifier halfword (+0xc) to +454; then draw the
 * local 4-byte IV (+437) and 8-byte SKD (+421). */
extern void *opencfw_em9305_memcpy(void *,const void *,uint32_t);
extern uint32_t opencfw_em9305_radio_random_bytes_310038(uintptr_t,uint32_t);

uint32_t opencfw_em9305_child_31af38(uintptr_t record)
{
    uintptr_t request=em9305_ram_805c5c.u32_805c6c;
    (void)opencfw_em9305_memcpy((void *)(record+405u),(const void *)(request+0xeu),16u);
    (void)opencfw_em9305_memcpy((void *)(record+445u),(const void *)(request+4u),8u);
    *(volatile uint16_t *)(record+454u)=*(volatile uint16_t *)(request+0xcu);
    (void)opencfw_em9305_radio_random_bytes_310038(record+437u,4u);
    return opencfw_em9305_radio_random_bytes_310038(record+421u,8u);
}
