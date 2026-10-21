/* Native radio select/release/mode and serial GPIO shifter children:
 * 0x52e072, 0x52e058, 0x52dd1c, 0x52dc98, 0x52dcde. */
#include <stdint.h>

extern volatile uint8_t audio_ble_hci_radio_dispatch_cell_20074f4f;
extern volatile uint8_t audio_ble_radio_mode_cell_20074f53;
extern uint32_t audio_ble_radio_stack_option_55c7e8(uint32_t,uint32_t,uint32_t);
extern uint32_t audio_ble_radio_stack_start_55c32e(uint32_t);
extern void audio_ble_hci_boot_delay_491102(uint32_t);
extern int32_t g2_gpio_hal_write(uint32_t,uint32_t);

static uint32_t word(const uint8_t *p) {uint32_t v;__builtin_memcpy(&v,p,4u);return v;}

uint32_t audio_ble_radio_begin_select_52e072(uint8_t *context) {
    if(context[8u]!=1u)return 12u;
    if(context[9u]!=0u)return 2u;
    context[9u]=1u;
    uint32_t stack=word(context+4u);
    (void)audio_ble_radio_stack_option_55c7e8(stack,0u,1u);
    (void)audio_ble_radio_stack_start_55c32e(stack);
    return 0u;
}

void audio_ble_radio_tx_release_52e058(void *unused) {
    (void)unused;
    audio_ble_hci_boot_delay_491102(0x32u);
    (void)g2_gpio_hal_write(0x95u,1u);
    audio_ble_hci_radio_dispatch_cell_20074f4f=0u;
}

uint32_t audio_ble_radio_io_mode_52dd1c(void) {
    return audio_ble_radio_mode_cell_20074f53;
}

void audio_ble_radio_serial_put_52dc98(uint32_t value) {
    volatile uint32_t *const high=(volatile uint32_t *)(uintptr_t)0x40010440u;
    volatile uint32_t *const low=(volatile uint32_t *)(uintptr_t)0x4001045cu;
    for(uint32_t bit=0;bit<8u;bit++) {
        if((value&0x80u)!=0u)*high=0x80000000u;
        else *low=0x80000000u;
        *high=0x20000000u;
        *low=0x20000000u;
        value<<=1;
    }
    *low=0x80000000u;
}

uint32_t audio_ble_radio_serial_get_52dcde(void) {
    volatile uint32_t *const input=(volatile uint32_t *)(uintptr_t)0x40010408u;
    volatile uint32_t *const high=(volatile uint32_t *)(uintptr_t)0x40010440u;
    volatile uint32_t *const low=(volatile uint32_t *)(uintptr_t)0x4001045cu;
    uint32_t value=0u;
    for(uint32_t bit=0;bit<8u;bit++) {
        value=(value<<1u)|((*input>>30u)&1u);
        *high=0x20000000u;
        *low=0x20000000u;
    }
    return value&0xffu;
}
