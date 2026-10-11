/* Native Cordio ATT handler/server/indication/client initialization
 * 0x4b511e, 0x5351dc, 0x533e40, 0x531b1c. */
#include <stdint.h>
uint8_t audio_ble_att_common_state[0x64u]; /* RAM 0x200610ac */
uint8_t audio_ble_atts_state[0x268u]; /* RAM 0x2006e5f0 */
uint8_t audio_ble_attc_state[0x1b8u]; /* RAM 0x2006f904 */
extern const uint8_t audio_ble_att_table_main[]; /* ROM 0x7851e0 */
extern const uint8_t audio_ble_att_table_secondary[]; /* ROM 0x7851f0 */
extern const uint8_t audio_ble_atts_ind_table[]; /* ROM 0x7852c0 */
extern const uint8_t audio_ble_atts_table[]; /* ROM 0x7852f0 */
extern const uint8_t audio_ble_attc_table[]; /* ROM 0x785250 */
extern void audio_ble_att_l2c_data_callback_4b4de0(void);
extern void audio_ble_att_l2c_control_callback_4b4e08(void);
extern void audio_ble_att_dm_conn_callback_4b4e50(void);
extern void audio_ble_atts_callback_4b4ee6(void);
extern void L2cRegister(uint16_t,void (*)(void),void (*)(void));
extern void DmConnRegister(uint32_t,void (*)(void));
static void put(uint8_t *base,uint32_t offset,const void *value) {
    *(const void **)(void *)(base+offset)=value;
}
void AttHandlerInit(uint8_t handler) {
    audio_ble_att_common_state[0x60u]=handler;
    put(audio_ble_att_common_state,0x3cu,audio_ble_att_table_main);
    put(audio_ble_att_common_state,0x40u,audio_ble_att_table_main);
    put(audio_ble_att_common_state,0x44u,audio_ble_att_table_secondary);
    put(audio_ble_att_common_state,0x48u,audio_ble_att_table_secondary);
    L2cRegister(4u,audio_ble_att_l2c_data_callback_4b4de0,
                audio_ble_att_l2c_control_callback_4b4e08);
    DmConnRegister(0u,audio_ble_att_dm_conn_callback_4b4e50);
}
void AttsInit(void) {
    *(uint32_t *)(void *)(audio_ble_atts_state+0x258u)=0u;
    *(uint32_t *)(void *)(audio_ble_atts_state+0x25cu)=0u;
    put(audio_ble_atts_state,0x260u,audio_ble_att_table_main);
    put(audio_ble_atts_state,0x264u,audio_ble_atts_callback_4b4ee6);
    for(uint32_t group=0;group<3u;group++)
        for(uint32_t slot=0;slot<3u;slot++) {
            uint8_t *row=audio_ble_atts_state+group*0xc0u+slot*0x40u;
            put(row,0x10u,audio_ble_att_common_state+group*0x14u);
            row[0x24u]=(uint8_t)(group+1u);
            row[0x25u]=(uint8_t)slot;
        }
    put(audio_ble_att_common_state,0x40u,audio_ble_atts_table);
}
void AttsIndInit(void) {
    for(uint32_t group=0;group<3u;group++)
        for(uint32_t slot=0;slot<3u;slot++) {
            uint8_t *row=audio_ble_atts_state+group*0xc0u+slot*0x40u;
            row[0x0cu]=audio_ble_att_common_state[0x60u];
            *(uint16_t *)(void *)(row+8u)=(uint16_t)(group+1u);
        }
    put(audio_ble_atts_state,0x260u,audio_ble_atts_ind_table);
}
void AttcInit(void) {
    *(uint32_t *)(void *)(audio_ble_attc_state+0x1b0u)=0u;
    audio_ble_attc_state[0x1b4u]=1u;
    for(uint32_t group=0;group<3u;group++)
        for(uint32_t slot=0;slot<3u;slot++) {
            uint8_t *row=audio_ble_attc_state+group*0x84u+slot*0x2cu;
            put(row,0u,audio_ble_att_common_state+group*0x14u);
            row[0x24u]=audio_ble_att_common_state[0x60u];
            *(uint16_t *)(void *)(row+0x20u)=(uint16_t)(group+1u);
            row[0x28u]=(uint8_t)slot;
            row[0x29u]=(uint8_t)(group+1u);
        }
    put(audio_ble_att_common_state,0x3cu,audio_ble_attc_table);
}
