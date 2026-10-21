/* Native 0x4d3f3c read-selector dispatch; its hardware child stays real. */
#include <stdint.h>

extern uint32_t audio_ble_hci_radio_read_region_4d3dda(uint8_t,uint32_t,uint32_t,uint32_t *);

uint32_t audio_ble_hci_radio_read_word_4d3f3c(uint8_t region,uint32_t offset,
                                                uint32_t length,uint32_t *output)
{
    if (region==1u || region==3u || region==5u)
        return audio_ble_hci_radio_read_region_4d3dda(region,offset,length,output);
    return 6u;
}
