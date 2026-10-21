/* Cordio app discovery event children, native 0x5320c2/0x532124/0x53223c/0x53228e/0x5322bc.
 * The row base and callback are product runtime cells, initialized elsewhere. */
#include <stdint.h>

extern uint8_t audio_ble_subsystem_rows_200733fc[];
extern uintptr_t audio_ble_service_dispatch_20074348;
extern const void *audio_ble_profile_dispatch_slot; /* selected producer 0x535488 -> RAM 0x20074360 */
extern uint8_t *audio_ble_pair_record(uint8_t);
extern void audio_ble_service_discovery_start(uint8_t);
extern void audio_ble_service_discovery_followup_5336e0(uint8_t);
extern void audio_ble_discovery_config_resume(uint8_t,uint32_t);
extern void audio_ble_dm_conn_set_idle(uint8_t,uint8_t,uint8_t);
extern void audio_ble_pair_record_clear_a(uint8_t *,uint8_t);
extern void audio_ble_pair_record_clear_b(uint8_t *,uint8_t);
extern void audio_ble_pair_record_attach(uint8_t *,uint32_t);
extern uint8_t audio_ble_connection_is_active_4bad26(uint8_t);
extern uint8_t audio_ble_discovery_connection_records_200717b0[];
extern void g2_wsf_candidate_buffer_free_word(uint32_t);
extern void audio_uart_buffer_zero(void *,uint32_t,uint32_t);

static uint32_t row_word(const uint8_t *p) {
    return (uint32_t)p[0]|((uint32_t)p[1]<<8)|((uint32_t)p[2]<<16)|((uint32_t)p[3]<<24);
}
static void clear_row_word(uint8_t *p) { for(unsigned i=0;i<4;i++)p[i]=0; }
static uint8_t *row_for(uint8_t connection) {
    return audio_ble_subsystem_rows_200733fc+((uint32_t)connection-1u)*16u;
}
static const uint8_t *discovery_mode_bytes(void) {
    return (const uint8_t *)audio_ble_profile_dispatch_slot;
}

void audio_ble_discovery_close_5320c2(const uint8_t *message) {
    const uint8_t connection=message[0];
    uint8_t *row=row_for(connection);
    row[12]=row[8]=row[9]=row[13]=row[14]=row[11]=0;
    ((void (*)(uint8_t,uint8_t))audio_ble_service_dispatch_20074348)(connection,0);
    const uint32_t target=row_word(row+4);
    if(target!=0) audio_uart_buffer_zero((void *)(uintptr_t)target,(uint32_t)row[10]<<1,0);
    if(discovery_mode_bytes()[0]==0)audio_ble_service_discovery_start(connection);
}

void audio_ble_discovery_idle_532124(const uint8_t *message) {
    const uint8_t connection=message[0];
    uint8_t *row=row_for(connection);
    row[11]=0;
    audio_ble_dm_conn_set_idle(connection,8,0);
    uint8_t *record=audio_ble_pair_record(connection);
    if(record!=0)audio_ble_pair_record_clear_a(record,0);
    const uint32_t allocation=row_word(row);
    if(allocation!=0){g2_wsf_candidate_buffer_free_word(allocation);clear_row_word(row);}
}

void audio_ble_discovery_resume_53223c(const uint8_t *message) {
    const uint8_t connection=message[0];
    uint8_t *row=row_for(connection);
    if(message[4]==0 || row[12]!=0)return;
    if(discovery_mode_bytes()[0]==0){
        if(row[13]!=0){
            row[13]=0;
            const uint32_t allocation=row_word(row);
            if(allocation!=0)audio_ble_discovery_config_resume(connection,allocation);
        }
    }else audio_ble_service_discovery_start(connection);
    row[12]=1;
}

void audio_ble_discovery_pending_53228e(const uint8_t *message) {
    uint8_t *row=row_for(message[0]);
    if(row[12]==0 && discovery_mode_bytes()[1]!=0)
        audio_ble_service_discovery_followup_5336e0(message[0]);
}

void audio_ble_discovery_complete_532174(const uint8_t *message) {
    const uint8_t connection=message[0];
    uint8_t *row=row_for(connection);
    if(row[12]!=0)return;
    uint8_t *record=audio_ble_pair_record(connection);
    if(record!=0 && audio_ble_connection_is_active_4bad26(connection)!=0 && record[0x86]!=0){
        const uint32_t offset=((uint32_t)((uint16_t)message[0]|((uint16_t)message[1]<<8))-1u)*0x30u;
        const uint32_t linked=row_word(audio_ble_discovery_connection_records_200717b0+offset);
        audio_ble_pair_record_clear_b((uint8_t *)(uintptr_t)linked,0);
    }
    if(audio_ble_connection_is_active_4bad26(connection)==0 || row[9]==0){
        if(discovery_mode_bytes()[0]!=0)audio_ble_service_discovery_start(connection);
    }else{
        if(record!=0){
            audio_ble_pair_record_clear_a(record,row[9]);
            if((row[9]==4 || row[9]==8) && row_word(row+4)!=0)
                audio_ble_pair_record_attach(record,row_word(row+4));
        }
        if(row[13]!=0){
            row[13]=0;
            const uint32_t allocation=row_word(row);
            if(allocation!=0)audio_ble_discovery_config_resume(connection,allocation);
        }
    }
    row[12]=1;
}
void audio_ble_discovery_event_5322bc(const uint8_t *message) {
    switch(message[2]){
    case 0x27:audio_ble_discovery_close_5320c2(message);break;
    case 0x28:audio_ble_discovery_idle_532124(message);break;
    case 0x2a:audio_ble_discovery_complete_532174(message);break;
    case 0x2b:audio_ble_discovery_pending_53228e(message);break;
    case 0x2c:audio_ble_discovery_resume_53223c(message);break;
    default:break;
    }
}
