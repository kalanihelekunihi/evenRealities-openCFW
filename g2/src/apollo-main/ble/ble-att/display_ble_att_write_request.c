/* Native Cordio ATT write scheduler 0x533c6c. Product registration and
 * connection records remain live typed contracts. */
#include <stdint.h>
extern void WsfTaskLock(void);                      /* 0x52b8c8 */
extern void WsfTaskUnlock(void);                    /* 0x52b8d0 */
extern uint8_t *audio_ble_att_registration_lookup(uint8_t,uint8_t); /* 0x534f14 */
extern uint32_t audio_ble_att_connection_valid(uint8_t,uint16_t);   /* 0x52c928 */
extern void audio_ble_att_send_error(uint8_t,uint16_t,uint8_t);     /* 0x533934 */
extern void *audio_wsf_msg_alloc(uint16_t);         /* 0x4bf99e */
extern void audio_wsf_msg_send(uint8_t,void *);     /* 0x4bf9ba */
extern void g2_wsf_candidate_buffer_free_word(uint32_t); /* selected 0x5304d4 */
extern void *audio_queue_copy_bytes(void *,const void *,uint32_t); /* 0x439be4 */
extern uint8_t audio_ble_att_runtime[];             /* live struct 0x200610ac */

static uint16_t half(const uint8_t *p) {
    return (uint16_t)p[0]|(uint16_t)((uint16_t)p[1]<<8);
}
static uint32_t word(const uint8_t *p) {
    return (uint32_t)p[0]|((uint32_t)p[1]<<8)|
           ((uint32_t)p[2]<<16)|((uint32_t)p[3]<<24);
}
static void put_half(uint8_t *p,uint16_t v) {
    p[0]=(uint8_t)v;p[1]=(uint8_t)(v>>8);
}
static void put_word(uint8_t *p,uint32_t v) {
    p[0]=(uint8_t)v;p[1]=(uint8_t)(v>>8);
    p[2]=(uint8_t)(v>>16);p[3]=(uint8_t)(v>>24);
}
static void free_message(void *message) {
    g2_wsf_candidate_buffer_free_word((uint32_t)(uintptr_t)message-8u);
}
static void release_input(uint32_t payload,uint8_t opcode) {
    uint32_t header=(opcode==0x1bu||opcode==0x1du)?11u:0u;
    free_message((void *)(uintptr_t)(payload-header));
}

uint32_t audio_ble_att_write_request(uint8_t connection,uint16_t attribute,
                                      uint8_t registration,uint32_t length,
                                      uint32_t payload,uint8_t opcode,
                                      uint8_t owns_payload) {
    uint16_t maximum=0;
    uint8_t blocked=0;
    WsfTaskLock();
    uint8_t *record=audio_ble_att_registration_lookup(connection,registration);
    if(record) {
        uint8_t *limits=(uint8_t *)(uintptr_t)word(record+16u);
        const uint8_t *slot=limits+(uint32_t)registration*4u;
        maximum=half(slot);
        blocked=(slot[2]>>2)&1u;
    }
    WsfTaskUnlock();
    uint32_t result=length;
    uint8_t queued=0;
    if(maximum!=0u) {
        if(blocked) {
            audio_ble_att_send_error(connection,attribute,0x71u);
        } else if(audio_ble_att_connection_valid(connection,attribute)!=0u) {
            if((uint32_t)maximum<(length&0xffffu)+3u) {
                audio_ble_att_send_error(connection,attribute,0x77u);
            } else {
                uint8_t *message=(uint8_t *)audio_wsf_msg_alloc(12u);
                if(message) {
                    put_half(message,connection);
                    message[2]=0x21u;
                    message[8]=registration;
                    uint8_t *buffer;
                    if(owns_payload==0u)
                        buffer=(uint8_t *)audio_wsf_msg_alloc((uint16_t)(length+11u));
                    else buffer=(uint8_t *)(uintptr_t)(payload-11u);
                    put_word(message+4u,(uint32_t)(uintptr_t)buffer);
                    if(!buffer)free_message(message);
                    else {
                        put_half(buffer,(uint16_t)(length+3u));
                        put_half(buffer+2u,attribute);
                        buffer[8]=opcode;
                        buffer[9]=(uint8_t)attribute;
                        buffer[10]=(uint8_t)(attribute>>8);
                        if(owns_payload==0u) {
                            result=payload;
                            (void)audio_queue_copy_bytes(buffer+11u,
                                                         (const void *)(uintptr_t)payload,
                                                         length&0xffffu);
                        }
                        audio_wsf_msg_send(audio_ble_att_runtime[96u],message);
                        queued=1u;
                    }
                }
            }
        }
    }
    if(!queued && owns_payload)release_input(payload,opcode);
    return result;
}
