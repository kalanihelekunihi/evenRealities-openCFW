#include "native_ble_state_reports.h"
#include "../board/native_battery_context.h"
extern uint32_t r1_charge_state_byte_get(void),r1_charge_state_is_active(void);
extern uint32_t r1_glasses_tag_frame_send(uint32_t,uint32_t);
extern int32_t r1_ble_tx_queue_dispatch_type2(uint32_t,const void *,uint32_t);
extern uint32_t r1_phone_connection_handle_get(void);
extern uint32_t r1_protocol_response_send_0x100(uint32_t,uint32_t,uint32_t,uint32_t,const void *,uint32_t);
void r1_charge_state_cache_update(void)
{
 uint32_t level=r1_charge_state_byte_get();r1_battery_runtime_context[0]=(uint8_t)level;
 uint32_t active=r1_charge_state_is_active();(void)r1_glasses_tag_frame_send(level,active);
}
void r1_ear_worn_state_notify(uint32_t connection)
{
 if(connection==65535u)return;
 _Alignas(4) uint8_t record[36]={0};record[1]=1;record[2]=150;
 (void)r1_ble_tx_queue_dispatch_type2(connection,record,4);
}
uint32_t r1_phone_cmd_send_op8(const void *payload,uint32_t first,uint32_t second)
{
 if(!payload)return 0;
 uint32_t connection=r1_phone_connection_handle_get();
 return r1_protocol_response_send_0x100(connection,8,first,second,payload,1);
}
