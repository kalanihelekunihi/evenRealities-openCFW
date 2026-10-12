/* Cordio dmConnUpdExecute 0x4b6532: source-attributed action table and
 * dispatch. The native diagnostic macro and invalid-event adjacency are
 * explicit contracts pending their separate source/layout recovery. */
#include <stdint.h>
typedef void (*audio_dm_action_t)(void *,const void *);
extern uint8_t audio_ble_dm_master_state_b[12u]; /* 0x20073fd8, initialized by DmConnMaster/SlaveInit */
extern void audio_ble_dm_conn_update_trace_entry(const void *,const void *);
extern uint8_t audio_ble_dm_conn_update_invalid_event_action(const void *);
extern void audio_ble_dm_conn_update_invalid_action(uint8_t);
const uint8_t audio_ble_dm_conn_update_action_table[4u]={0x10u,0x20u,0x11u,0x21u};
static uint32_t rd32(const uint8_t *p){return (uint32_t)p[0]|((uint32_t)p[1]<<8)|
    ((uint32_t)p[2]<<16)|((uint32_t)p[3]<<24);}
void audio_ble_dm_conn_upd_execute_4b6532(void *ccb,const void *message){
    const uint8_t *m=(const uint8_t *)message;
    audio_ble_dm_conn_update_trace_entry(ccb,message);
    uint8_t index=m[2u]&7u;
    uint8_t action=index<4u ? audio_ble_dm_conn_update_action_table[index] :
        audio_ble_dm_conn_update_invalid_event_action(message);
    uint8_t set=action>>4;
    if(set>=3u){audio_ble_dm_conn_update_invalid_action(set);return;}
    uint32_t table_address=rd32(audio_ble_dm_master_state_b+(uint32_t)set*4u);
    if(table_address!=0u){
        const audio_dm_action_t *actions=(const audio_dm_action_t *)(uintptr_t)table_address;
        actions[action&15u](ccb,message);
    }
}
