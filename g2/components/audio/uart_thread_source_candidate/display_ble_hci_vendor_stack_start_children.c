/* Native vendor stack start guard 0x55bd2e and DMA setup 0x55c0dc.
 * The 0x55c548 ROM slot authenticates vendor MMIO base 0x40050000. */
#include <stdint.h>
extern int32_t audio_ble_vendor_dma_queue_538d58(uint32_t,const void *,void *);
static uint32_t get(const uint8_t *p) {uint32_t v;__builtin_memcpy(&v,p,4u);return v;}
static void put(uint8_t *p,uint32_t v) {__builtin_memcpy(p,&v,4u);}

uint32_t audio_ble_vendor_stack_start_guard_55bd2e(uint32_t index,uint32_t mode) {
    volatile uint32_t *reg=(volatile uint32_t *)(uintptr_t)(0x40050000u+index*0x1000u+0x11cu);
    uint32_t value=*reg;
    if(((value&0xfu)>>1)==mode)*reg=1u;
    else if(((value&0xffu)>>5)==mode)*reg=0x10u;
    else return 0u;
    return 1u;
}

int32_t audio_ble_vendor_stack_dma_prepare_55c0dc(void *record,uint32_t width,
                                                    uint32_t count,uint32_t high) {
    uint8_t *row=(uint8_t *)record;
    put(row+0x828u,0u);put(row+0x20u,0u);put(row+0x85cu,0u);
    uint32_t parameters[4]={width>>1,count,(count&0xffffff00u)|1u,high};
    int32_t result=audio_ble_vendor_dma_queue_538d58(
        get(row+4u)&0xffu,parameters,row+0x828u);
    if(result==0)put(row+0x20u,0x100u);
    return result;
}
