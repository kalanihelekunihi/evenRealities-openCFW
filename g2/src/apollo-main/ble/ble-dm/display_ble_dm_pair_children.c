/* Native Cordio DM/SMP children 0x4d28b0, 0x4b3026, 0x534948,
 * 0x534910, 0x4bb030 and 0x4b73c4. */
#include <stdint.h>
extern uint8_t audio_ble_dm_handler_state[0x18u]; /* selected Wsf/Dm BSS, native 0x20073b78 */
extern uint8_t audio_dm_connection_records[]; /* live connection records */
extern void *WsfMsgAlloc(uint16_t);
extern void WsfMsgSend(uint8_t,void *);
extern void SmpScGetCancelMsgWithReattempt(uint8_t,void *,uint8_t); /* native 0x56d188 */
extern void SmpDmMsgSend(void *); /* native 0x537bd6 */
extern void audio_ble_pair_compare_trace(void); /* native 0x4bd91e */
__attribute__((noinline)) uint32_t DmSecGetCompareValue(const uint8_t *record) {
    uint32_t value=((uint32_t)record[0x0cu]<<24u)|((uint32_t)record[0x0du]<<16u)
                  |((uint32_t)record[0x0eu]<<8u)|record[0x0fu];
    return value%1000000u; /* authenticated ROM 0x534980 */
}
__attribute__((noinline)) void DmSecCompareRsp(uint8_t conn,uint8_t accepted) {
    uint8_t *message=(uint8_t *)WsfMsgAlloc(22u);
    if(!message)return;
    message[0]=conn;message[1]=0u;
    if(!accepted)SmpScGetCancelMsgWithReattempt(conn,message,12u);
    else message[2]=0x16u;
    SmpDmMsgSend(message);
}
