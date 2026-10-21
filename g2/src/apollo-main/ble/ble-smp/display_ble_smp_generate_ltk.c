/* Native smpGenerateLtk at 0x5379f4; pinned Cordio smp_main.c. */
#include <stdint.h>
extern void *memset(void *destination, int value, unsigned length);
extern void *memcpy(void *destination, const void *source, unsigned length);

extern void SecRand(uint8_t *destination, uint8_t length);
extern void DmSmpCbackExec(void *event);

void smpGenerateLtk(uint8_t *ccb)
{
    uint8_t *scratch = *(uint8_t **)(void *)(ccb + 0x30u);
    const uint8_t key_length = scratch[0x20u];
    SecRand(scratch + 4u, key_length);
    memset(scratch + 4u + key_length, 0, (uint32_t)16u - key_length);
    scratch[0x1cu] = scratch[0x30u];
    scratch[0x1du] = scratch[0x31u];
    memcpy(scratch + 0x14u, scratch + 0x32u, 8u);
    scratch[0x1eu] = 1u;
    scratch[0x1fu] = (ccb[0x40u] & 4u) ? 2u : 1u;
    scratch[2u] = 0x2fu;
    DmSmpCbackExec(scratch);
}
