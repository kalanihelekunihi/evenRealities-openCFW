#include <stdint.h>
extern uint32_t r1_kv_class_read(void *,void *,uint32_t);
extern void *volatile r1_r_size_kv_handle;
extern uint32_t r1_phone_connection_handle_get(void);
extern uint32_t r1_ble_thread_message_encode(uint32_t,uint32_t,uint32_t,const void *);
/* An unavailable cached size requires recovery, independent of caller scratch
 * registers. Successful reads retain the stock zero/erased-byte decision. */
uint32_t r1_nv_recovery_needed_query_boundary(void)
{
 uint8_t value=0;
 if(r1_kv_class_read(r1_r_size_kv_handle,&value,1))return 1;
 return value==0 || value==255;
}
/* The encoder copies this one byte into its owned queue allocation before
 * returning; no callback stack storage escapes. */
void r1_protocol_time_timeout_callback(uint32_t argument)
{
 uint8_t value=(uint8_t)argument;
 uint32_t handle=r1_phone_connection_handle_get();
 (void)r1_ble_thread_message_encode(handle,8,1,&value);
}
