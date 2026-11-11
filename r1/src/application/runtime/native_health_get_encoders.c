/* Stock 0x83930, 0x83972 and 0x83c20: source-level health GET encoders.
 * Each wrapper sends a fixed-size payload when present and otherwise posts
 * the no-data flag. The existing transport helper below owns the wire header. */
#include <stdint.h>
#include "native_health_event_post.h"
extern uint32_t r1_phone_connection_handle_get(void);
extern uint32_t r1_protocol_send_flag_set_a(uint32_t,uint32_t,uint32_t,uint32_t,uint32_t);

static uint32_t r1_health_get_encode(const volatile uint8_t *payload,
                                     uint32_t flags,uint32_t sequence,
                                     uint32_t opcode,uint32_t length)
{
    uint32_t handle=r1_phone_connection_handle_get();
    if (payload)
        return r1_protocol_health_sample_send(handle,opcode,flags,sequence,payload,length);
    return r1_protocol_send_flag_set_a(handle,opcode,2u,sequence,0u)!=0u;
}
uint32_t r1_health_get_hr_encode(const volatile uint8_t *payload,
                                 uint32_t flags,uint32_t sequence)
{
    return r1_health_get_encode(payload,flags,sequence,258u,8u);
}
uint32_t r1_health_get_hrv_encode(const volatile uint8_t *payload,
                                  uint32_t flags,uint32_t sequence)
{
    return r1_health_get_encode(payload,flags,sequence,1026u,9u);
}
uint32_t r1_health_get_spo2_encode(const volatile uint8_t *payload,
                                   uint32_t flags,uint32_t sequence)
{
    return r1_health_get_encode(payload,flags,sequence,514u,8u);
}


extern uint32_t r1_protocol_send_response(uint32_t,const void *,const void *,uint32_t);
/* Stock 0x82ef4: canonical eight-byte response header, inverted backend result. */
uint32_t r1_protocol_health_sample_send(uint32_t handle,uint32_t opcode,uint32_t flags,uint32_t sequence,const volatile uint8_t *payload,uint32_t length)
{
 if(handle==0xffffu)return 0;
 uint32_t header[2]={(uint8_t)((flags^1u)|2u)|0x200u|(((opcode>>8)&255u)<<16)|((opcode&255u)<<24),(uint16_t)sequence};
 return r1_protocol_send_response(handle,header,(const void *)(uintptr_t)payload,length)==0;
}
