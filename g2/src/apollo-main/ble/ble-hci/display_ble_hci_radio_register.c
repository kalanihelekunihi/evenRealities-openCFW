/* Native 0x48162c command/event callback registration. */
#include <stdint.h>

/* Live writable bases from literal cells 0x481810/14, 0x700 bytes apart. */
extern volatile uint32_t audio_ble_hci_radio_dispatch_handlers_20068228[];
extern volatile uint32_t audio_ble_hci_radio_dispatch_contexts_20068928[];

uint32_t audio_ble_hci_radio_register_48162c(uint8_t target,uint32_t event,
                                               const void *handler,uint32_t context)
{
    uint32_t slot=((event>>5u)*32u)+(event&31u);
    uint32_t pointer=(uint32_t)(uintptr_t)handler;
    if (target==0u || target==2u) {
        audio_ble_hci_radio_dispatch_handlers_20068228[slot]=pointer;
        audio_ble_hci_radio_dispatch_contexts_20068928[slot]=context;
    }
    if (target==1u || target==2u) {
        slot+=7u*32u;
        audio_ble_hci_radio_dispatch_handlers_20068228[slot]=pointer;
        audio_ble_hci_radio_dispatch_contexts_20068928[slot]=context;
    }
    if (target>2u) return 6u;
    return 0u;
}
