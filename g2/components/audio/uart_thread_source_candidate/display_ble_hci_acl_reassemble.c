/* Native hciCoreAclReassembly 0x52a962, Cordio HCI ACL input ownership. */
#include <stdint.h>

extern uint8_t audio_ble_hci_controller_state_20071478[]; /* native 0x20071478 */
extern uint8_t *audio_ble_hci_conn_by_handle(uint16_t); /* native hciCoreConnByHandle */
extern void *audio_ble_hci_msg_data_alloc(uint16_t, uint8_t); /* WsfMsgDataAlloc */
extern void audio_ble_wsf_message_free(void *); /* selected 0x4bf9b0 */

static uint16_t rd16(const uint8_t *p) {
    return (uint16_t)((uint16_t)p[0]|((uint16_t)p[1]<<8));
}
static uint32_t rd32(const uint8_t *p) {
    uint32_t v; __builtin_memcpy(&v,p,4u); return v;
}
static void wr32(uint8_t *p,uint32_t v) { __builtin_memcpy(p,&v,4u); }
static void wr16(uint8_t *p,uint16_t v) { __builtin_memcpy(p,&v,2u); }
static uint8_t *ptr(uint8_t *p,uint32_t offset) {
    return (uint8_t *)(uintptr_t)rd32(p+offset);
}
static void setptr(uint8_t *p,uint32_t offset,uint8_t *value) {
    wr32(p+offset,(uint32_t)(uintptr_t)value);
}

uint8_t *audio_ble_hci_acl_reassemble(void *message) {
    uint8_t *packet=(uint8_t *)message;
    uint8_t *result=0;
    uint8_t free_input=1u;
    uint16_t header=rd16(packet);
    uint16_t handle=header&0x0fffu;
    uint16_t kind=header&0x3000u;
    uint16_t length=rd16(packet+2u);
    uint8_t *conn=audio_ble_hci_conn_by_handle(handle);
    if(conn!=0) {
        if(kind==0x2000u) {
            uint8_t *old=ptr(conn,8u);
            if(old!=0) { audio_ble_wsf_message_free(old); setptr(conn,8u,0); }
            uint16_t max=rd16(audio_ble_hci_controller_state_20071478+0x7cu);
            uint16_t wanted=0u;
            if(length<2u) {
                if(length!=0u) wanted=(uint16_t)(max+4u);
            } else {
                uint16_t payload=rd16(packet+4u);
                if((uint32_t)payload+4u<=(uint32_t)max) {
                    if((uint32_t)length<(uint32_t)payload+4u)
                        wanted=(uint16_t)(payload+8u);
                    else { free_input=0u; result=packet; }
                }
            }
            if(wanted!=0u) {
                uint8_t *allocated=(uint8_t *)audio_ble_hci_msg_data_alloc(wanted,0u);
                setptr(conn,8u,allocated);
                if(allocated!=0) {
                    uint8_t *write=allocated;
                    setptr(conn,12u,write);
                    write[0]=(uint8_t)handle;
                    write[1]=(uint8_t)(handle>>8);
                    if(length<2u) { write[2]=0u; write[3]=0u; }
                    else {
                        uint16_t payload=rd16(packet+4u);
                        write[2]=(uint8_t)(payload+4u);
                        write[3]=(uint8_t)((payload+4u)>>8);
                    }
                    write+=4u;
                    __builtin_memcpy(write,packet+4u,length);
                    write+=length;
                    setptr(conn,12u,write);
                    if(length<2u) wr16(conn+0x14u,(uint16_t)(max-length));
                    else wr16(conn+0x14u,(uint16_t)(rd16(packet+4u)+4u-length));
                }
            }
        } else if(kind==0x1000u && ptr(conn,8u)!=0) {
            uint16_t remaining=rd16(conn+0x14u);
            if(remaining<length) {
                audio_ble_wsf_message_free(ptr(conn,8u));
                setptr(conn,8u,0);
            } else {
                uint8_t *write=ptr(conn,12u);
                __builtin_memcpy(write,packet+4u,length);
                uint8_t *allocation=ptr(conn,8u);
                if((uint32_t)(uintptr_t)write-(uint32_t)(uintptr_t)allocation<6u) {
                    uint16_t payload=rd16(allocation+4u);
                    if((uint32_t)rd16(audio_ble_hci_controller_state_20071478+0x7cu)<(uint32_t)payload+4u) {
                        audio_ble_wsf_message_free(allocation);
                        setptr(conn,8u,0);
                    } else {
                        wr16(allocation+2u,(uint16_t)(payload+4u));
                        wr16(conn+0x14u,(uint16_t)(payload+remaining-
                              rd16(audio_ble_hci_controller_state_20071478+0x7cu)+4u));
                    }
                }
                setptr(conn,12u,write+length);
                wr16(conn+0x14u,(uint16_t)(rd16(conn+0x14u)-length));
                if(rd16(conn+0x14u)==0u) {
                    result=ptr(conn,8u);
                    setptr(conn,8u,0);
                }
            }
        }
    }
    if(free_input!=0u) audio_ble_wsf_message_free(packet);
    return result;
}
