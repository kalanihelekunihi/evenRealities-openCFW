/* Native 0x56cdc0/0x56ce4e, pinned Cordio smp_sc_main.c scratch lifecycle. */
#include <stdint.h>
extern void *WsfBufAlloc(uint16_t length);
extern void WsfBufFree(void *block);

static uint32_t *sc_fields(void *ccb) {
    uint8_t *sc=*(uint8_t **)(void *)((uint8_t *)ccb+0x48u);
    return (uint32_t *)(void *)sc;
}

uint8_t SmpScAllocScratchBuffers(void *ccb) {
    uint32_t *sc=sc_fields(ccb);
    static const uint8_t offsets[5]={0x14u,0x08u,0x18u,0x0cu,0x10u};
    static const uint8_t sizes[5]={0x60u,0x40u,0x20u,0x40u,0x20u};
    for (uint32_t i=0;i<5u;i++) {
        uint32_t *slot=sc+offsets[i]/4u;
        if (*slot==0u) *slot=(uint32_t)(uintptr_t)WsfBufAlloc(sizes[i]);
    }
    for (uint32_t i=0;i<5u;i++)
        if (sc[offsets[i]/4u]==0u) return 0u;
    return 1u;
}

void SmpScFreeScratchBuffers(void *ccb) {
    uint32_t *sc=sc_fields(ccb);
    static const uint8_t offsets[5]={0x14u,0x08u,0x18u,0x0cu,0x10u};
    for (uint32_t i=0;i<5u;i++) {
        uint32_t *slot=sc+offsets[i]/4u;
        if (*slot!=0u) {
            WsfBufFree((void *)(uintptr_t)*slot);
            *slot=0u;
        }
    }
}
