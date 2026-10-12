/* Pinned Cordio dm_dev.c/dm_adv.c address providers,
 * native Main 0x4b304c and 0x4b32b8. */
#include <stdint.h>
extern uint8_t audio_ble_dm_handler_state[]; /* native dmCb 0x20073b78 */
extern void HciLeSetRandAddrCmd(const uint8_t *address);
extern void WsfTaskLock(void);
extern void WsfTaskUnlock(void);
void DmDevSetRandAddr(const uint8_t *address)
{
    for (uint8_t i=0u;i<6u;i++) audio_ble_dm_handler_state[i]=address[i];
    HciLeSetRandAddrCmd(address);
}
void DmAdvSetAddrType(uint8_t type)
{
    WsfTaskLock();
    audio_ble_dm_handler_state[0x0eu]=type;
    WsfTaskUnlock();
}
