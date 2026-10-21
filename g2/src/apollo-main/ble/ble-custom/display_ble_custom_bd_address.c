/* Native HciVscSetCustom_BDAddr 0x4b4cd2. */
#include <stdint.h>
extern uint8_t audio_ble_custom_bd_address[6]; /* product RAM 0x20074148 */
extern void *audio_queue_copy_bytes(void *,const void *,uint32_t); /* selected 0x439be4 */
uint32_t audio_ble_hci_set_custom_bdaddr(const uint8_t *address) {
    if(address==0) return 0u;
    uint32_t nonzero=0u;
    for(uint32_t i=0;i<6u;i++) nonzero|=address[i];
    if(nonzero==0u) return 0u;
    (void)audio_queue_copy_bytes(audio_ble_custom_bd_address,address,6u);
    return 1u;
}
