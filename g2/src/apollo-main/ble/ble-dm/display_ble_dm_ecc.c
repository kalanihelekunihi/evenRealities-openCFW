/* Native Cordio ECC request/response chain 0x5348ec, 0x53673e,
 * 0x52b1f4 and key copy 0x5348fc. */
#include <stdint.h>
extern uint8_t audio_ble_dm_handler_state[]; /* selected 0x20073b78 */
extern uint8_t audio_ble_ecc_key_storage[]; /* live 0x200726d0 */
extern uint8_t audio_ble_stack_state_20072cb8[]; /* selected secCb public-key queue at +0x28 */
extern void *WsfMsgAlloc(uint16_t);
extern void WsfMsgEnq(void *,uint8_t,void *);
extern void *audio_ble_hci_cmd_alloc_52ae38(uint16_t,uint16_t); /* selected hciCmdAlloc */
extern void audio_ble_hci_cmd_send(void *); /* selected hciCmdSend */

void HciLeReadLocalP256PubKey(void) {
    void *command=audio_ble_hci_cmd_alloc_52ae38(0x2025u,0u);
    if(command)audio_ble_hci_cmd_send(command);
}
uint32_t audio_ble_dm_ecc_request(uint8_t handler,uint16_t conn,uint8_t event) {
    uint8_t *message=(uint8_t *)WsfMsgAlloc(0x9cu);
    if(!message)return 0u;
    message[0]=(uint8_t)conn;message[1]=(uint8_t)(conn>>8u);
    message[2]=event;
    message[0x34u]=2u;
    WsfMsgEnq(audio_ble_stack_state_20072cb8+0x28u,handler,message);
    HciLeReadLocalP256PubKey();
    return 1u;
}
void DmSecGenerateEccKeyReq(void) {
    (void)audio_ble_dm_ecc_request(audio_ble_dm_handler_state[0x0cu],0u,0x41u);
}
void DmSecSetEccKey(const void *key) {
    __builtin_memcpy(audio_ble_ecc_key_storage,key,0x60u);
}
