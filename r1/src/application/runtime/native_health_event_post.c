/* Reconstructed locked R1 2.2.6.0009 event wrappers and payload/ACK adapters.
 * Registry storage and transport are separate source providers. */
#include "native_health_event_post.h"
#include "../board/native_battery_memory.h"
#include <stddef.h>
/* Only the authenticated context word at native 0x20006824 is owned here. */
volatile uint32_t r1_sync_block_field __attribute__((section(".r1.sync.block.field"),aligned(4)))=0;
uint32_t r1_sync_block_field_get(void){return r1_sync_block_field;}
extern uint32_t r1_phone_connection_handle_get(void);
extern uint32_t r1_protocol_send_flag_set_a(uint32_t,uint32_t,uint32_t,uint32_t,uint32_t);
extern uint32_t r1_ack_record_register(const volatile uint8_t *,uint32_t,volatile uint8_t *,volatile uint16_t *);
extern uint32_t r1_ack_record_remove(uint32_t,uint32_t,uint32_t,uint32_t);
extern void *pvPortMalloc(size_t);
extern void vPortFree(void *);
uint32_t r1_ack_record_register_typed(uint32_t opcode,uint32_t sequence,uint32_t timestamp,volatile uint8_t *context,volatile uint16_t *identifier)
{
    /* Native eight-byte template at 0x9a444: 00 02 00 00 00 00 00 00. */
    uint8_t header[8]={0,2,0,0,0,0,0,0};
    header[2]=(uint8_t)(opcode>>8);header[3]=(uint8_t)opcode;
    write16(header+4,sequence);
    return r1_ack_record_register(header,timestamp,context,identifier);
}
uint32_t r1_ack_record_remove_type2(uint32_t opcode,uint32_t identifier)
{return r1_ack_record_remove(2,opcode>>8,(uint8_t)opcode,identifier);}
static void copy(volatile uint8_t *to,const volatile uint8_t *from,uint32_t length)
{
    uint32_t destination=(uint32_t)(uintptr_t)to,source=(uint32_t)(uintptr_t)from;
    if(destination-source<length){for(uint32_t i=length;i;--i)to[i-1u]=from[i-1u];}
    else if(((destination|source)&3u)==0){uint32_t i=0;for(;length-i>=4;i+=4)write32(to+i,read32(from+i));for(;i<length;++i)to[i]=from[i];}
    else for(uint32_t i=0;i<length;++i)to[i]=from[i];
}
uint32_t r1_protocol_payload_copy_send(uint32_t handle,uint32_t opcode,uint32_t flags,uint32_t sequence,const volatile uint8_t *payload,uint32_t length,uint32_t field)
{
    uint32_t allocated=(uint16_t)(length+4u);
    volatile uint8_t *buffer=pvPortMalloc(allocated);
    if(!buffer)return 0;
    copy(buffer,payload,length);write32((volatile uint8_t *)(uintptr_t)((uint32_t)(uintptr_t)buffer+length),field);
    uint32_t result=r1_protocol_health_sample_send(handle,opcode,flags,sequence,buffer,allocated);
    vPortFree((void *)(uintptr_t)buffer);
    return result;
}
static uint32_t post(uint32_t opcode,const volatile uint8_t *payload,uint32_t length,uint32_t field,uint32_t sequence,uint32_t timestamp,volatile uint8_t *context)
{
    if(!payload || !length)return r1_protocol_send_flag_set_a(r1_phone_connection_handle_get(),opcode,2,sequence,0)!=0;
    volatile uint16_t identifier=0;
    if(timestamp && !r1_ack_record_register_typed(opcode,sequence,timestamp,context,&identifier)){
        vPortFree((void *)(uintptr_t)context);return 0;
    }
    uint32_t result=r1_protocol_payload_copy_send(r1_phone_connection_handle_get(),opcode,1,sequence,payload,length,field);
    if(!result && timestamp){
        (void)r1_ack_record_remove_type2(opcode,identifier);
        vPortFree((void *)(uintptr_t)context);
    }
    return result;
}
#define EVENT_POST(name,opcode) uint32_t name(const volatile uint8_t *payload,uint32_t length,uint32_t field,uint32_t sequence,uint32_t timestamp,volatile uint8_t *context){return post(opcode,payload,length,field,sequence,timestamp,context);}
EVENT_POST(r1_event_post_module1,0x101)
EVENT_POST(r1_event_post_module2,0x201)
EVENT_POST(r1_event_post_module4,0x401)
EVENT_POST(r1_event_post_module5,0x501)
EVENT_POST(r1_event_post_module6,0x601)
#undef EVENT_POST
/* Stock 0x836ba: direct 0x601 transport with caller-selected flags and
 * sequence, without the module6 ACK/context registration path. */
uint32_t r1_event_post_0x601(const volatile uint8_t *payload,uint32_t length,
                              uint32_t field,uint32_t flags,uint32_t sequence)
{
    uint32_t handle=r1_phone_connection_handle_get();
    if (!payload || !length)
        return r1_protocol_send_flag_set_a(handle,0x601,2,sequence,0)!=0;
    return r1_protocol_payload_copy_send(handle,0x601,flags,sequence,
                                         payload,length,field);
}
