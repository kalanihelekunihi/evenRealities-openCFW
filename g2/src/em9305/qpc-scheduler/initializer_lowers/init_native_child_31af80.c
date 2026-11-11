#include <stdint.h>

/* Native 0x31af80..0x31afd2: load the encryption request stored at
 * 0x80281c: 8-byte random to record+445, diversifier halfword (0x802824)
 * to +454, 8-byte SKD (0x802826) to +421 and 4-byte IV (0x80282e) to
 * +437; then draw the local 4-byte IV (+441) and 8-byte SKD (+429). */
extern void *opencfw_em9305_memcpy(void *,const void *,uint32_t);
extern uint32_t opencfw_em9305_radio_random_bytes_310038(uintptr_t,uint32_t);

uint32_t opencfw_em9305_child_31af80(uintptr_t record)
{
    (void)opencfw_em9305_memcpy((void *)(record+445u),(const void *)(uintptr_t)0x80281cu,8u);
    *(volatile uint16_t *)(record+454u)=*(volatile uint16_t *)(uintptr_t)0x802824u;
    (void)opencfw_em9305_memcpy((void *)(record+421u),(const void *)(uintptr_t)0x802826u,8u);
    (void)opencfw_em9305_memcpy((void *)(record+437u),(const void *)(uintptr_t)0x80282eu,4u);
    (void)opencfw_em9305_radio_random_bytes_310038(record+441u,4u);
    return opencfw_em9305_radio_random_bytes_310038(record+429u,8u);
}
