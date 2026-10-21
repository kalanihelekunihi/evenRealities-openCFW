/* Native 0x56cfec/0x56d054/0x56d0a8/0x56d0fc, pinned Cordio SC senders. */
#include <stdint.h>
extern void DmConnSetIdle(uint8_t,uint16_t,uint8_t);
extern void smpStartRspTimer(void *ccb);
extern uint8_t *smpMsgAlloc(uint16_t length);
extern void WStrReverseCpy(uint8_t *destination,const uint8_t *source,uint16_t size);
extern void smpSendPkt(void *ccb,uint8_t *packet);
extern void smpSmExecute(void *ccb,void *message);

static void failed(void *ccb,uint8_t *message) {
    message[3]=8u;
    message[2]=3u;
    smpSmExecute(ccb,message);
}
static void prepare(void *ccb) {
    DmConnSetIdle(((const uint8_t *)ccb)[0x3du],1u,1u);
    smpStartRspTimer(ccb);
}
static void send16(void *ccb,uint8_t *message,const uint8_t *data,uint8_t opcode) {
    prepare(ccb);
    uint8_t *packet=smpMsgAlloc(0x19u);
    if (!packet) { failed(ccb,message); return; }
    packet[8]=opcode;
    WStrReverseCpy(packet+9u,data,16u);
    smpSendPkt(ccb,packet);
}
void smpScSendDHKeyCheck(void *ccb,uint8_t *message,const uint8_t *check) {
    send16(ccb,message,check,0x0du);
}
void smpScSendRand(void *ccb,uint8_t *message,const uint8_t *random) {
    send16(ccb,message,random,4u);
}
void smpScSendPairCnf(void *ccb,uint8_t *message,const uint8_t *confirm) {
    send16(ccb,message,confirm,3u);
}
void smpScSendPubKey(void *ccb,uint8_t *message) {
    prepare(ccb);
    uint8_t *packet=smpMsgAlloc(0x49u);
    if (!packet) { failed(ccb,message); return; }
    packet[8]=0x0cu;
    const uint8_t *sc=*(const uint8_t *const *)(const void *)((const uint8_t *)ccb+0x48u);
    const uint8_t *public_key=*(const uint8_t *const *)(const void *)(sc+0x0cu);
    WStrReverseCpy(packet+9u,public_key,32u);
    WStrReverseCpy(packet+0x29u,public_key+32u,32u);
    smpSendPkt(ccb,packet);
}
