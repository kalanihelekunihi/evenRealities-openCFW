/* Native HciLeStartEncryptionCmd 0x52b5a2; pinned Cordio hci_cmd.c. */
#include <stdint.h>
extern uint8_t *hciCmdAlloc(uint16_t opcode,uint8_t parameter_length);
extern void hciCmdSend(uint8_t *command);
void HciLeStartEncryptionCmd(uint16_t handle,const uint8_t *random,
                             uint16_t ediv,const uint8_t *key)
{
    uint8_t *command=hciCmdAlloc(0x2019u,0x1cu);
    if (!command) return;
    command[3u]=(uint8_t)handle;
    command[4u]=(uint8_t)(handle>>8u);
    __builtin_memcpy(command+5u,random,8u);
    command[0x0du]=(uint8_t)ediv;
    command[0x0eu]=(uint8_t)(ediv>>8u);
    __builtin_memcpy(command+0x0fu,key,16u);
    hciCmdSend(command);
}
