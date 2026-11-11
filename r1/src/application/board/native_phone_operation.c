#include <stdint.h>
extern uint32_t r1_phone_connection_handle_get(void);
extern uint32_t r1_protocol_response_send_0x100(uint32_t,uint32_t,uint32_t,uint32_t,const void *,uint32_t);
/* Only the declared payload and response result are public C state. */
uint32_t r1_phone_cmd_send_op1(const void *payload,uint32_t first,uint32_t second)
{
 if(!payload)return 0;
 uint32_t handle=r1_phone_connection_handle_get();
 return r1_protocol_response_send_0x100(handle,1,first,second,payload,7);
}
