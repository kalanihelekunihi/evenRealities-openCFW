/* Native HCI radio prepare and IRQ setup 0x52f38c/
 * 0x4b4786/0x4b4768. The 0x4b4d30/34/38 literal slots are NVIC MMIO. */
#include <stdint.h>
extern uint8_t *audio_ble_hci_radio_mode_state_50938e(uint32_t);
extern void audio_ble_hci_radio_state_prepare_5118e0(void);

/* 0x53006c is am_hal_queue_init (AmbiqSuite 5.1.0 hal/am_hal_queue.c);
 * audio_ble_hci_radio_scheduler_53006c is a payload defsym alias of it. */

uint32_t audio_ble_hci_radio_prepare_body(uint32_t unused,uint32_t scratch,
                                           uint32_t high,uint32_t saved_r7) {
    (void)unused;(void)scratch;(void)high;
    uint8_t *state=audio_ble_hci_radio_mode_state_50938e(0u);
    if(state[0]==1u)audio_ble_hci_radio_state_prepare_5118e0();
    return saved_r7;
}
__attribute__((naked)) uint32_t audio_ble_hci_radio_prepare_52f38c(void) {
    __asm volatile("mov r3, r7\n\tb audio_ble_hci_radio_prepare_body");
}

void audio_ble_hci_radio_mux_on_4b4786(int16_t irq,uint32_t priority) {
    uint8_t encoded=(uint8_t)(priority<<4);
    if(irq<0) {
        ((volatile uint8_t *)(uintptr_t)(0xe000ed18u-4u))[(uint16_t)irq&0xfu]=encoded;
    } else {
        ((volatile uint8_t *)(uintptr_t)0xe000e400u)[(uint16_t)irq]=encoded;
    }
}
void audio_ble_hci_radio_mux_request_4b4768(uint16_t irq) {
    if((int16_t)irq>=0)
        ((volatile uint32_t *)(uintptr_t)0xe000e100u)[(int16_t)irq>>5]=1u<<(irq&31u);
}
