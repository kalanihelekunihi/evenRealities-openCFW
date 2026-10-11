/* Ambiq UART buffer/configure native 0x58e09e. The 0x20000d9c config
 * contents are product data; this source uses its authenticated offsets
 * without inventing field values. Baud-divider child0x58de38 stays code. */
#include <stdint.h>
extern uint32_t audio_uart_pin_mux_enable(uint32_t,uint32_t); /* 0x4c44bc */
extern uint32_t audio_uart_divider_configure(uint32_t,uint32_t,uint32_t *); /* 0x58de38 */
static volatile uint32_t *reg_at(uint32_t instance,uint32_t offset) {
    return (volatile uint32_t *)(uintptr_t)(0x40039000u+instance*0x1000u+offset);
}
uint32_t audio_uart_sync_driver_buffer(void *handle,void *configuration) {
    if(handle==0 || (*(uint32_t *)handle&0x1ffffffu)!=0x1ea9e06u) return 2u;
    uint8_t *state=(uint8_t *)handle;
    const uint8_t *cfg=(const uint8_t *)configuration;
    uint32_t instance=*(uint32_t *)(state+0x28u);
    volatile uint32_t *control=reg_at(instance,0x30u);
    *control=0u;
    *control|=8u;
    uint32_t revision=*(volatile uint32_t *)(uintptr_t)0x4002000cu&0xffu;
    uint8_t mode=cfg[12u];
    if(mode>=2u || (mode==1u && revision==0x21u)) return 6u;
    uint8_t pin=(mode==0u)?4u:6u;
    state[0x118u]=pin;
    uint32_t requested=*(const uint32_t *)cfg;
    if(requested<0x16e361u) {
        if(revision>0x21u)
            *(volatile uint32_t *)(uintptr_t)0x400201b0u &=
                ~(0x400000u<<(instance&0xffu));
        uint32_t field=(pin==6u)?6u:1u;
        *control=(*control&~0x70u)|(field<<4);
    } else {
        if(revision>0x21u)
            *(volatile uint32_t *)(uintptr_t)0x400201b0u |=
                0x400000u<<(instance&0xffu);
        uint32_t field=(pin==6u)?6u:5u;
        *control=(*control&~0x70u)|(field<<4);
    }
    (void)audio_uart_pin_mux_enable(pin,(instance+11u)&0xffu);
    *control&=~1u;
    *control&=~0x200u;
    *control&=~0x100u;
    uint32_t divider=audio_uart_divider_configure(instance,requested,
                                                    (uint32_t *)(state+0x30u));
    if(divider!=0u) return divider;
    *control&=~0x4000u;
    *control&=~0x8000u;
    *control|=*(const uint16_t *)(cfg+8u);
    uint8_t framing=cfg[5u];
    uint32_t b1=0u,b2=0u;
    if(framing==0u) b1=1u;
    else if(framing==1u) {b1=1u;b2=1u;}
    volatile uint32_t *line=reg_at(instance,0x2cu);
    *line&=~1u;
    *line=(*line&~2u)|(b1<<1);
    *line=(*line&~4u)|(b2<<2);
    *line=(*line&~8u)|((cfg[6u]&1u)<<3);
    *line|=0x10u;
    *line=(*line&~0x60u)|((cfg[4u]&3u)<<5);
    *line&=~0x80u;
    volatile uint32_t *data=reg_at(instance,0x34u);
    *data=(*data&~7u)|(cfg[10u]&7u);
    *data=(*data&~0x38u)|((cfg[11u]&7u)<<3);
    *control|=1u;
    *control|=0x200u;
    *control|=0x100u;
    return 0u;
}
