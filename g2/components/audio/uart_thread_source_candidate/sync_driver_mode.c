/* Ambiq UART enable/disable/backup native 0x58dbb8. Pin-mux operations
 * 0x4c44bc/0x4c4530 remain typed children; peripheral power children use
 * selected C providers at 0x47f5b8/0x47f7ae. */
#include <stdint.h>
extern uint32_t audio_power_peripheral_on(uint32_t); /* selected 0x47f5b8 */
extern uint32_t audio_power_peripheral_off(uint32_t); /* selected 0x47f7ae */
extern uint32_t audio_uart_pin_mux_enable(uint32_t,uint32_t); /* 0x4c44bc */
extern uint32_t audio_uart_pin_mux_disable(uint32_t,uint32_t); /* 0x4c4530 */
static uint32_t read_word(const uint8_t *p,uint32_t off) {
    return *(const uint32_t *)(p+off);
}
static void write_word(uint8_t *p,uint32_t off,uint32_t value) {
    *(uint32_t *)(p+off)=value;
}
uint32_t audio_uart_sync_driver_mode(void *handle,uint32_t mode,uint32_t backup) {
    if(handle==0 || (read_word((const uint8_t *)handle,0u)&0x1ffffffu)!=0x1ea9e06u)
        return 2u;
    uint8_t *state=(uint8_t *)handle;
    uint32_t instance=read_word(state,0x28u);
    uintptr_t peripheral=(uintptr_t)(0x40039000u+instance*0x1000u);
    static const uint8_t offsets[8]={0x20u,0x24u,0x28u,0x2cu,
                                      0x30u,0x34u,0x38u,0x48u};
    uint32_t pin=(instance+11u)&0xffu;
    if(mode==0u) {
        if(backup!=0u && state[4]==0u) return 7u;
        (void)audio_power_peripheral_on(pin);
        if(backup!=0u) {
            if(read_word(state,0x30u)>=0x16e361u &&
               (*(volatile uint32_t *)(uintptr_t)0x4002000cu&0xffu)>0x21u)
                *(volatile uint32_t *)(uintptr_t)0x400201b0u |=
                    0x400000u<<(instance&0xffu);
            (void)audio_uart_pin_mux_enable(state[0x118u],pin);
            for(uint32_t i=0u;i<8u;++i)
                *(volatile uint32_t *)(peripheral+offsets[i])=
                    read_word(state,0x8u+i*4u);
            state[4]=0u;
        }
        return 0u;
    }
    if(mode!=1u && mode!=2u) return 6u;
    if(backup!=0u) {
        for(uint32_t i=0u;i<8u;++i)
            write_word(state,0x8u+i*4u,
                       *(volatile uint32_t *)(peripheral+offsets[i]));
        state[4]=1u;
    }
    if(read_word(state,0x30u)>=0x16e361u &&
       (*(volatile uint32_t *)(uintptr_t)0x4002000cu&0xffu)>0x21u)
        *(volatile uint32_t *)(uintptr_t)0x400201b0u &=
            ~(0x400000u<<(instance&0xffu));
    (void)audio_uart_pin_mux_disable(state[0x118u],pin);
    *(volatile uint32_t *)(peripheral+0x44u)=UINT32_MAX; /* 0x58e7e4 */
    *(volatile uint32_t *)(peripheral+0x30u)=0u;
    (void)audio_power_peripheral_off(pin);
    return 0u;
}
