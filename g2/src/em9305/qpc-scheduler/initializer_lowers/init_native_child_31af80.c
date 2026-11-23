#include <stdint.h>
#include "em9305_ram.h"

/* Native 0x31af80..0x31afd2: load the encryption request stored at
 * ((uintptr_t)&em9305_ram_8027e0 + 0x3cu): 8-byte random to record+445, diversifier halfword (((uintptr_t)&em9305_ram_8027e0 + 0x44u))
 * to +454, 8-byte SKD (((uintptr_t)&em9305_ram_8027e0 + 0x46u)) to +421 and 4-byte IV (((uintptr_t)&em9305_ram_8027e0 + 0x4eu)) to
 * +437; then draw the local 4-byte IV (+441) and 8-byte SKD (+429). */
extern void *opencfw_em9305_memcpy(void *,const void *,uint32_t);
extern uint32_t opencfw_em9305_radio_random_bytes_310038(uintptr_t,uint32_t);

uint32_t opencfw_em9305_child_31af80(uintptr_t record)
{
    (void)opencfw_em9305_memcpy((void *)(record+445u),(const void *)((uintptr_t)&em9305_ram_8027e0 + 0x3cu),8u);
    *(volatile uint16_t *)(record+454u)=em9305_ram_8027e0.u16_802824;
    (void)opencfw_em9305_memcpy((void *)(record+421u),(const void *)((uintptr_t)&em9305_ram_8027e0 + 0x46u),8u);
    (void)opencfw_em9305_memcpy((void *)(record+437u),(const void *)((uintptr_t)&em9305_ram_8027e0 + 0x4eu),4u);
    (void)opencfw_em9305_radio_random_bytes_310038(record+441u,4u);
    return opencfw_em9305_radio_random_bytes_310038(record+429u,8u);
}
