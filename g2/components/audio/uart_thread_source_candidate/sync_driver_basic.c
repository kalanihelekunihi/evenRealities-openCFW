/* Ambiq UART driver bind 0x58dae4 and interrupt enable 0x58e782.
 * Driver-state RAM is a typed product contract at 0x2006a02c; UART MMIO
 * base 0x40039000 and 0x1ea9e06 handle magic are authenticated ROM words. */
#include <stdint.h>
extern uint8_t g2_uart_driver_state[4u*0x11cu]; /* RAM0x2006a02c */
static uint32_t load32(const uint8_t *p) {return *(const uint32_t *)p;}
static void store32(uint8_t *p,uint32_t v) {*(uint32_t *)p=v;}
uint32_t audio_uart_sync_driver_bind(uint32_t instance,void **output) {
    if(instance>=4u) return 5u;
    if(output==0) return 6u;
    if(*output!=0 && (load32((const uint8_t *)*output)&0x1ffffffu)==0x1ea9e06u)
        return 7u;
    uint8_t *state=g2_uart_driver_state+instance*0x11cu;
    store32(state,load32(state)|0x1000000u);
    store32(state,(load32(state)&0xff000000u)|0x0ea9e06u);
    store32(state+0x28u,instance);
    state[4]=0u;store32(state+0x30u,0u);
    state[0x11au]=0u;state[0x119u]=0u;
    state[0xdcu]=0u;state[0xddu]=0u;
    store32(state+0xd8u,0u);store32(state+0x9cu,0u);
    state[0xdeu]=1u;
    *output=state;
    return 0u;
}
uint32_t audio_uart_sync_driver_baud(void *handle,uint32_t bits) {
    if(handle==0 || (load32((const uint8_t *)handle)&0x1ffffffu)!=0x1ea9e06u)
        return 2u;
    uint8_t *state=(uint8_t *)handle;
    uint32_t instance=load32(state+0x28u);
    volatile uint32_t *enable=(volatile uint32_t *)(uintptr_t)
        (0x40039000u+instance*0x1000u+0x38u);
    *enable|=bits;
    return 0u;
}
