/* Native Cordio DM L2CAP event bridges 0x55bc96, 0x56e580, 0x56e5a4.
 * Their stack event records inherit raw caller register bytes. The ARM
 * entry shims preserve those bytes instead of manufacturing C locals. */
#include <stdint.h>
extern uint8_t *audio_ble_dm_conn_ccb_by_handle_4b601c(uint16_t);
extern void audio_ble_dm_conn_upd_execute_4b6532(uint8_t *,const uint8_t *);
extern uint8_t audio_dm_connection_records[]; /* native dmConnCb 0x200712a4 */
static void put32(uint8_t *p,uint32_t v){p[0]=(uint8_t)v;p[1]=(uint8_t)(v>>8);p[2]=(uint8_t)(v>>16);p[3]=(uint8_t)(v>>24);}
__attribute__((used)) void audio_ble_dm_l2c_conn_update_ind_impl(uint32_t id,uint32_t handle,
                                                                   uint32_t params,uint32_t ambient_r3){
    uint8_t event[12];put32(event,handle);put32(event+4u,params);put32(event+8u,ambient_r3);
    uint8_t *ccb=audio_ble_dm_conn_ccb_by_handle_4b601c((uint16_t)handle);
    if(ccb!=0){event[2u]=0x72u;event[8u]=(uint8_t)id;audio_ble_dm_conn_upd_execute_4b6532(ccb,event);}
}
__attribute__((naked)) void audio_ble_dm_l2c_conn_update_ind_55bc96(uint8_t id,uint16_t handle,
                                                                       const uint16_t *params){
    __asm__ volatile("b.w audio_ble_dm_l2c_conn_update_ind_impl");
}
__attribute__((used)) void audio_ble_dm_l2c_conn_update_cnf_impl(uint32_t handle,uint32_t result,
                                                                   uint32_t ambient_r2,uint32_t ambient_r3){
    uint8_t event[8];put32(event,ambient_r2);put32(event+4u,ambient_r3);
    uint8_t *ccb=audio_ble_dm_conn_ccb_by_handle_4b601c((uint16_t)handle);
    if(ccb!=0){event[2u]=0x73u;event[4u]=(uint8_t)result;event[5u]=(uint8_t)(result>>8);
        audio_ble_dm_conn_upd_execute_4b6532(ccb,event);}
}
__attribute__((naked)) void audio_ble_dm_l2c_conn_update_cnf_56e580(uint16_t handle,uint16_t result){
    __asm__ volatile("b.w audio_ble_dm_l2c_conn_update_cnf_impl");
}
__attribute__((used)) void audio_ble_dm_l2c_cmd_rej_ind_impl(uint32_t handle,uint32_t reason,uint32_t ambient_r5){
    uint8_t event[8];event[0u]=(uint8_t)ambient_r5;event[1u]=(uint8_t)(ambient_r5>>8);
    event[2u]=0x77u;event[3u]=0u;event[4u]=(uint8_t)reason;event[5u]=(uint8_t)(reason>>8);
    event[6u]=(uint8_t)handle;event[7u]=(uint8_t)(handle>>8);
    uint32_t raw=*(const uint32_t *)(const void *)(audio_dm_connection_records+0x9cu);
    ((void (*)(const uint8_t *))(uintptr_t)raw)(event);
}
__attribute__((naked)) void audio_ble_dm_l2c_cmd_rej_ind_56e5a4(uint16_t handle,uint16_t reason){
    __asm__ volatile("mov r2, r5\n b.w audio_ble_dm_l2c_cmd_rej_ind_impl");
}
