/* Native 0x480c7c. Caller supplies its preserved R2 as seed_r2. */
#include <stdint.h>

extern uint32_t audio_ble_hci_radio_read_word_4d3f3c(uint8_t,uint32_t,uint32_t,uint32_t *);

void audio_ble_hci_radio_identifier_caps_480c7c(void *output,
                                                   uint32_t ignored_r1,
                                                   uint32_t seed_r2)
{
    (void)ignored_r1;
    uint32_t word=seed_r2;
    uint32_t status=audio_ble_hci_radio_read_word_4d3f3c(1u,0x244u,1u,&word);
    uint32_t *const fields=(uint32_t *)output;
    fields[3u]=0u;
    if (status==0u) {
        uint32_t revision=*(volatile const uint32_t *)0x4002000cu;
        if (((revision>>4u)&15u)==2u && (revision&15u)>1u && word<255u) {
            if ((*(volatile const uint32_t *)0x4002000cu&15u)!=3u) --word;
            fields[3u]=0x30200u|(word&0xffu);
        } else {
            fields[3u]=0x10000u|(word&0xffu);
        }
    } else {
        fields[3u]=word&0xffu;
    }
}
