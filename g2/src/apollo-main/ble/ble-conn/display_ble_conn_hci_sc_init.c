/* Native Cordio DM connection/HCI LE feature/SMP SC setup and timer stop. */
#include <stdint.h>
extern uint8_t audio_ble_dm_config[]; /* compressed SRAM 0x20000694 */
extern uint8_t audio_ble_dm_master_state_a[]; /* RAM 0x20073fe4 */
extern uint8_t audio_ble_dm_master_state_b[]; /* RAM 0x20073fd8 */
extern const uint8_t audio_ble_dm_conn_table_a[]; /* ROM 0x78a820 */
extern const uint8_t audio_ble_dm_conn_table_b[]; /* ROM 0x78a82c */
extern const uint8_t audio_ble_dm_conn_table_c[]; /* ROM 0x78a838 */
extern const uint8_t audio_ble_dm_conn_state_table_a[]; /* ROM 0x776a84 */
extern const uint8_t audio_ble_dm_conn_state_table_b[]; /* ROM 0x78efec */
extern uint32_t audio_ble_hci_le_supported_features[2]; /* compressed SRAM 0x20000028 */
extern uint8_t audio_ble_smp_handler_state[]; /* RAM 0x20070aec */
extern uint8_t audio_ble_smp_sc_rows[]; /* RAM 0x200728f4 */
extern void audio_ble_smp_sc_handler_5e2784(void);
extern void audio_ble_smp_sc_callback_5e2aba(void);
extern void WsfTaskLock(void);
extern void WsfTaskUnlock(void);
extern void audio_wsf_timer_remove(void *); /* native wsfTimerRemove 0x52a3fc */
static void put(uint8_t *base,uint32_t offset,const void *value) {
    *(const void **)(void *)(base+offset)=value;
}
void HciSetLeSupFeat(uint32_t lo,uint32_t hi,uint8_t enable) { /* 0x52acd6 */
    if(enable==0u) {
        audio_ble_hci_le_supported_features[0]&=~lo;
        audio_ble_hci_le_supported_features[1]&=~hi;
    } else {
        audio_ble_hci_le_supported_features[0]|=lo;
        audio_ble_hci_le_supported_features[1]|=hi;
    }
}
void SmpScInit(void) { /* 0x56cf74 */
    for(uint32_t i=0;i<3u;i++)
        put(audio_ble_smp_handler_state,i*0x4cu+0x48u,
            audio_ble_smp_sc_rows+i*0x1cu);
    put(audio_ble_smp_handler_state,0xf0u,audio_ble_smp_sc_handler_5e2784);
    put(audio_ble_smp_handler_state,0xf4u,audio_ble_smp_sc_callback_5e2aba);
    audio_ble_smp_handler_state[0xf8u]=1u;
}
void WsfTimerStop(void *timer) { /* 0x52a4d2 */
    WsfTaskLock();
    audio_wsf_timer_remove(timer);
    WsfTaskUnlock();
}
