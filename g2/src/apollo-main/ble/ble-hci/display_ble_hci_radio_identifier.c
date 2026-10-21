/* Native 0x480d72 radio identifier dispatcher; MMIO 0x40020014 is live. */
#include <stdint.h>

extern void audio_ble_hci_radio_identifier_details_480874(void *);
extern void audio_ble_hci_radio_identifier_caps_480c7c(void *,uint32_t,uint32_t);

uint32_t audio_ble_hci_radio_identifier_480d72(uint8_t mode,void *output)
{
    if (output==0) return 6u;
    uint8_t *bytes=(uint8_t *)output;
    if (mode==1u) {
        audio_ble_hci_radio_identifier_details_480874(output);
        return 0u;
    }
    if (mode!=0u) return 6u;
    volatile const uint32_t *const features=(volatile const uint32_t *)0x40020014u;
    uint32_t value=*features;
    switch (value & 3u) {
        case 0u: bytes[1]=0u;bytes[0]=0u;bytes[2]=0u;break;
        case 1u: bytes[1]=0u;bytes[0]=0u;bytes[2]=1u;break;
        case 2u: bytes[1]=1u;bytes[0]=1u;bytes[2]=1u;break;
        default: bytes[1]=1u;bytes[0]=1u;bytes[2]=2u;break;
    }
    bytes[3]=(uint8_t)((value>>2u)&3u);
    for (unsigned i=0;i<5u;++i) bytes[4u+i]=(uint8_t)((*features>>(6u+i))&1u);
    bytes[9]=(uint8_t)((*features>>19u)&1u);
    bytes[10]=(uint8_t)((*features>>20u)&3u);
    /* Native R2 still holds the output pointer at the BL into 0x480c7c. */
    audio_ble_hci_radio_identifier_caps_480c7c(output,0u,(uint32_t)(uintptr_t)output);
    return 0u;
}
