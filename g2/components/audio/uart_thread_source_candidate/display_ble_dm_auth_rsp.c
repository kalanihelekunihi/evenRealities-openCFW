/* Cordio DmSecAuthRsp, native Main 0x4d24d4. */
#include <stdint.h>
extern void *WsfMsgAlloc(uint16_t);
extern void SmpDmMsgSend(void *);

void DmSecAuthRsp(uint8_t conn,uint8_t length,const uint8_t *auth) {
    uint8_t *message=(uint8_t *)WsfMsgAlloc(22u);
    if(!message)return;
    message[0]=conn;
    message[1]=0u;
    message[2]=4u;
    message[20]=length;
    if(auth)__builtin_memcpy(message+4u,auth,length);
    SmpDmMsgSend(message);
}
