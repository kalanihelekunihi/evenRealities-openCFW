#include <stdint.h>

static volatile uint32_t *word_ptr(const uint8_t *dma,uint32_t offset)
{
    return *(volatile uint32_t * const *)(const void *)(dma+offset);
}

uint32_t case_dma_abort(void *opaque)
{
    if (!opaque)return 1u;
    uint8_t *dma=opaque;
    if (dma[0x25]!=2u) {
        *(uint32_t *)(void *)(dma+0x3c)=4u;
        dma[0x24]=0u;
        return 1u;
    }
    volatile uint32_t *channel=word_ptr(dma,0);
    channel[0]&=~0xeu;
    *word_ptr(dma,0x48)&=~0x100u;
    channel[0]&=~1u;
    word_ptr(dma,0x40)[1]=1u<<(*(uint32_t *)(void *)(dma+0x44)&0x1cu);
    word_ptr(dma,0x4c)[1]=*(uint32_t *)(void *)(dma+0x50);
    volatile uint32_t *mux=word_ptr(dma,0x54);
    if (mux) {
        mux[0]&=~0x100u;
        word_ptr(dma,0x58)[1]=*(uint32_t *)(void *)(dma+0x5c);
    }
    dma[0x25]=1u;
    dma[0x24]=0u;
    return 0u;
}

uint32_t case_dma_abort_it(void *opaque)
{
    uint8_t *dma=opaque; /* stock 0x080048e6 dereferences; null is outside contract */
    if (dma[0x25]!=2u) {
        *(uint32_t *)(void *)(dma+0x3c)=4u;
        return 1u;
    }
    volatile uint32_t *channel=word_ptr(dma,0);
    channel[0]&=~0xeu;
    channel[0]&=~1u;
    *word_ptr(dma,0x48)&=~0x100u;
    word_ptr(dma,0x40)[1]=1u<<(*(uint32_t *)(void *)(dma+0x44)&0x1cu);
    word_ptr(dma,0x4c)[1]=*(uint32_t *)(void *)(dma+0x50);
    volatile uint32_t *mux=word_ptr(dma,0x54);
    if (mux) {
        mux[0]&=~0x100u;
        word_ptr(dma,0x58)[1]=*(uint32_t *)(void *)(dma+0x5c);
    }
    dma[0x25]=1u;
    dma[0x24]=0u;
    void (*callback)(uint8_t *)=*(void (**)(uint8_t *))(void *)(dma+0x38);
    if (callback)callback(dma);
    return 0u;
}
