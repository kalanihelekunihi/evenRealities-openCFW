/* Native HciLeEncryptCmd 0x52b266, pinned Cordio hci_cmd.c. */
#include <stdint.h>
extern void *audio_ble_hci_cmd_alloc_52ae38(uint16_t opcode,uint16_t length);
extern void audio_ble_hci_cmd_send(void *command);
extern void *memcpy(void *destination,const void *source,unsigned long length);
void HciLeEncryptCmd(const uint8_t *key,const uint8_t *plain) {
    uint8_t *command=audio_ble_hci_cmd_alloc_52ae38(0x2017u,0x20u);
    if (command) {
        memcpy(command+3u,key,16u);
        memcpy(command+0x13u,plain,16u);
        audio_ble_hci_cmd_send(command);
    }
}
