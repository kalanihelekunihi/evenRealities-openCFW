/* Native MX25U power sequencer 0x4c26e0. The register bank base0x40060000,
 * device magic0x01bebebe and transfer offsets are authenticated in ROM.
 * Child HAL operations remain explicit typed dependencies. */
#include <stdint.h>
extern uint32_t audio_power_peripheral_on(uint32_t); /* selected0x47f5b8 */
extern uint32_t audio_power_peripheral_off(uint32_t); /* selected0x47f7ae */
extern uint32_t audio_uart_pin_mux_enable(uint32_t,uint32_t); /* selected0x4c44bc */
extern uint32_t audio_uart_font_pin_mux_disable(uint32_t); /* 0x4c45a4 */
extern void audio_uart_font_mspi_transition(uint32_t,uint32_t,uint32_t,uint32_t); /* 0x4c0758 */
extern void audio_uart_font_mspi_suspend(void *); /* 0x4bfd44 */
extern void audio_uart_font_mspi_resume(void *); /* 0x4bfd62 */
extern void audio_uart_font_power_prepare(void *,uint32_t); /* 0x4c235c */
extern void audio_delay_us_selected(uint32_t); /* selected0x4807a0 */
static const uint16_t register_offsets[]={0x80u,0x84u,0x88u,0x8cu,0x90u,0x94u,
    0x98u,0x9cu,0xa0u,0xa4u,0xa8u,0x30u,0x44u,0x48u,0x4cu,
    0x2a8u,0x2b8u,0x2c0u,0x2c4u,0x200u,0x2b4u,0x114u,0x118u,0x20u,0x2a0u};
static const uint16_t save_offsets[]={0x864u,0x868u,0x86cu,0x870u,0x874u,
    0x878u,0x87cu,0x880u,0x884u,0x888u,0x88cu,0x890u,0x894u,
    0x898u,0x89cu,0x8a4u,0x8a8u,0x8acu,0x8b0u,0x8b4u,
    0x8b8u,0x8bcu,0x8c0u,0x8c4u,0x8a0u};
static uint32_t w(const void *p,uint32_t o) {
    return *(const uint32_t *)(const void *)((const uint8_t *)p+o);
}
static void s(void *p,uint32_t o,uint32_t v) {
    *(uint32_t *)(void *)((uint8_t *)p+o)=v;
}
static volatile uint8_t *registers(uint32_t unit) {
    return (volatile uint8_t *)(uintptr_t)(0x40060000u+(unit<<12u));
}
static uint32_t rw(volatile uint8_t *bank,uint32_t o) {
    return *(volatile uint32_t *)(void *)(bank+o);
}
static void sw(volatile uint8_t *bank,uint32_t o,uint32_t v) {
    *(volatile uint32_t *)(void *)(bank+o)=v;
}
int32_t audio_uart_font_flash_power(void *device,uint8_t mode,uint8_t preserve) {
    if(device==0 || (w(device,0u)&0x01ffffffu)!=0x01bebebeu) return 2;
    uint8_t *state=(uint8_t *)device;
    uint32_t unit=w(device,4u);
    uint32_t channel=(uint8_t)(unit+16u);
    uint8_t request=(uint8_t)mode;
    uint8_t keep=(uint8_t)preserve;
    if(request==0u) {
        if(keep!=0u && state[0x860u]==0u) return 7;
        (void)audio_power_peripheral_on(channel);
        if(keep==0u) {
            state[0x8c9u]=4u;
            uint32_t status=audio_uart_pin_mux_enable(4u,channel);
            if(status!=0u) return (int32_t)status;
            audio_uart_font_mspi_transition(unit,1u,1u,8u);
            return 0;
        }
        if(state[0x8c9u]==7u) return 7;
        uint32_t status=audio_uart_pin_mux_enable(state[0x8c9u],channel);
        if(status!=0u) return (int32_t)status;
        audio_uart_font_mspi_transition(unit,1u,0u,0u);
        volatile uint8_t *bank=registers(unit);
        for(uint32_t i=0u;i<24u;i++) {
            uint32_t value=i==20u ? state[0x8b8u] : w(device,save_offsets[i]);
            sw(bank,register_offsets[i],value);
        }
        sw(bank,0x2a0u,w(device,0x8a0u)&~1u);
        if((state[0x8a0u]&1u)!=0u) audio_uart_font_mspi_suspend(device);
        state[0x860u]=0u;
        return 0;
    }
    if(request>2u) return 6;
    if(w(device,0x840u)!=0u || w(device,0x20u)!=0u) return 3;
    volatile uint8_t *bank=registers(unit);
    if(keep!=0u) {
        for(uint32_t i=0u;i<25u;i++) {
            uint32_t offset=i==20u?0x2b0u:register_offsets[i];
            s(device,save_offsets[i],rw(bank,offset));
        }
        if((rw(bank,0x2a0u)&1u)!=0u) audio_uart_font_mspi_resume(device);
        state[0x860u]=1u;
    }
    audio_uart_font_power_prepare(device,0x1fffu);
    if((rw(bank,0x90u)&1u)!=0u) audio_delay_us_selected(w(device,0x8ccu));
    (void)audio_power_peripheral_off(channel);
    audio_uart_font_mspi_transition(unit,0u,0u,0u);
    return (int32_t)audio_uart_font_pin_mux_disable(channel);
}
