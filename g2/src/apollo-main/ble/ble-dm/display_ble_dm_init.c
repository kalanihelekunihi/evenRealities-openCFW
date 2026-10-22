/* Native Cordio DM init bodies. The compressed-SRAM control block at
 * 0x20000694 and ROM dispatch tables remain typed product data contracts. */
#include <stdint.h>
extern uint8_t audio_ble_dm_config[]; /* source-initialized RAM 0x20000694 */
extern const uint8_t audio_ble_dm_adv_table[]; /* ROM 0x78a808 */
extern const uint8_t audio_ble_dm_phy_table[]; /* ROM 0x78a85c */
extern const uint8_t audio_ble_dm_master_table_a[]; /* ROM 0x78d424 */
extern const uint8_t audio_ble_dm_master_table_b[]; /* ROM 0x78d41c */
extern const uint8_t audio_ble_dm_slave_table_a[]; /* ROM 0x785be0 */
extern const uint8_t audio_ble_dm_slave_table_b[]; /* ROM 0x78d42c */
extern const uint8_t audio_ble_dm_security_table[]; /* ROM 0x78a898 */
extern const uint8_t audio_ble_dm_security_state_table[]; /* ROM 0x7856b0 */
extern const uint8_t audio_ble_dm_lesc_table[]; /* ROM 0x78a8a4 */
extern const uint8_t audio_ble_dm_priv_table_a[]; /* ROM 0x78a868 */
extern const uint8_t audio_ble_dm_priv_table_b[]; /* ROM 0x78a874 */
extern void WsfTaskLock(void); /* native 0x52b8c8 */
extern void WsfTaskUnlock(void); /* native 0x52b8d0 */
extern void audio_ble_dm_adv_lower(void); /* native dmAdvInit */
extern void HciSetLeSupFeat(uint32_t,uint32_t,uint32_t);
extern uint32_t audio_ble_dm_adv_ready_cell; /* opencfw U5: now provided by the Cordio unit */
/* RAM 0x200744f4 */
uint8_t audio_ble_dm_master_state_a[12u]; /* RAM 0x20073fe4 */
extern uint8_t audio_ble_dm_master_state_b[12u]; /* opencfw U5: now provided by the Cordio unit */
/* RAM 0x20073fd8 */
const void *audio_ble_dm_security_state[2]; /* RAM 0x20074114 */
static void put(uint32_t offset,const void *table) {
    *(const void **)(void *)(audio_ble_dm_config+offset)=table;
}
void DmAdvInit(void) { /* 0x4bac2c */
    WsfTaskLock();
    put(0u,audio_ble_dm_adv_table);
    audio_ble_dm_adv_lower();
    audio_ble_dm_adv_ready_cell=0u;
    WsfTaskUnlock();
}
void DmConnMasterInit(void) { /* 0x536a98 */
    WsfTaskLock();
    *(const void **)(void *)(audio_ble_dm_master_state_a+4u)=audio_ble_dm_master_table_a;
    *(const void **)(void *)(audio_ble_dm_master_state_b+4u)=audio_ble_dm_master_table_b;
    WsfTaskUnlock();
}
void DmConnSlaveInit(void) { /* 0x536b18 */
    WsfTaskLock();
    *(const void **)(void *)(audio_ble_dm_master_state_a+8u)=audio_ble_dm_slave_table_a;
    *(const void **)(void *)(audio_ble_dm_master_state_b+8u)=audio_ble_dm_slave_table_b;
    WsfTaskUnlock();
}
void DmSecInit(void) { /* 0x4d250c */
    put(0x14u,audio_ble_dm_security_table);
    audio_ble_dm_security_state[0]=audio_ble_dm_security_state_table;
    audio_ble_dm_security_state[1]=audio_ble_dm_security_state[0];
}
void DmSecLescInit(void) { /* 0x53496a */
    put(0x20u,audio_ble_dm_lesc_table);
}
