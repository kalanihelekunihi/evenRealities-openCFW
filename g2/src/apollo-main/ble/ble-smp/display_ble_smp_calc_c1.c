/* Native smpCalcC1Part1/Part2 0x537742/0x53786c; pinned Cordio smp_main.c. */
#include <stdint.h>
extern uint8_t audio_ble_smp_handler_state[];
extern uint8_t *DmConnLocalRpa(uint8_t connection);
extern uint8_t *DmConnPeerRpa(uint8_t connection);
extern uint8_t *DmConnLocalAddr(uint8_t connection);
extern uint8_t *DmConnPeerAddr(uint8_t connection);
extern uint8_t DmConnLocalAddrType(uint8_t connection);
extern uint8_t DmConnPeerAddrType(uint8_t connection);
extern uint8_t BdaIsZeros(const uint8_t *address);
extern uint8_t SecAes(uint8_t *key,uint8_t *plain,uint8_t handler,
                      uint16_t connection,uint8_t event);
extern void smpSmExecute(uint8_t *ccb,void *event);

static void c1_encrypt(uint8_t *ccb,uint8_t *key,uint8_t plain[16])
{
    const uint8_t token=SecAes(key,plain,audio_ble_smp_handler_state[0xecu],
                               ccb[0x3du],0x0bu);
    ccb[0x41u]=token;
    if (token==0xffu) {
        uint8_t event[4]={0x0bu,0u,3u,8u};
        smpSmExecute(ccb,event);
    }
}

void smpCalcC1Part1(uint8_t *ccb,uint8_t *key,uint8_t *random)
{
    const uint8_t connection=ccb[0x3du];
    const uint8_t initiator=ccb[0x3au];
    uint8_t initiator_type,responder_type;
    if (initiator) {
        initiator_type=BdaIsZeros(DmConnLocalRpa(connection))?
            DmConnLocalAddrType(connection):1u;
        responder_type=BdaIsZeros(DmConnPeerRpa(connection))?
            DmConnPeerAddrType(connection):1u;
    } else {
        initiator_type=BdaIsZeros(DmConnPeerRpa(connection))?
            DmConnPeerAddrType(connection):1u;
        responder_type=BdaIsZeros(DmConnLocalRpa(connection))?
            DmConnLocalAddrType(connection):1u;
    }
    uint8_t plain[16];
    plain[0]=(uint8_t)(initiator_type^random[0]);
    plain[1]=(uint8_t)(responder_type^random[1]);
    for (uint8_t i=0;i<7u;i++) plain[2u+i]=(uint8_t)(ccb[0x20u+i]^random[2u+i]);
    for (uint8_t i=0;i<7u;i++) plain[9u+i]=(uint8_t)(ccb[0x27u+i]^random[9u+i]);
    c1_encrypt(ccb,key,plain);
}

void smpCalcC1Part2(uint8_t *ccb,uint8_t *key,uint8_t *part1)
{
    const uint8_t connection=ccb[0x3du];
    uint8_t *initiator_address,*responder_address;
    if (ccb[0x3au]) {
        initiator_address=DmConnLocalRpa(connection);
        if (BdaIsZeros(initiator_address)) initiator_address=DmConnLocalAddr(connection);
        responder_address=DmConnPeerRpa(connection);
        if (BdaIsZeros(responder_address)) responder_address=DmConnPeerAddr(connection);
    } else {
        initiator_address=DmConnPeerRpa(connection);
        if (BdaIsZeros(initiator_address)) initiator_address=DmConnPeerAddr(connection);
        responder_address=DmConnLocalRpa(connection);
        if (BdaIsZeros(responder_address)) responder_address=DmConnLocalAddr(connection);
    }
    uint8_t plain[16];
    for (uint8_t i=0;i<6u;i++) plain[i]=(uint8_t)(responder_address[i]^part1[i]);
    for (uint8_t i=0;i<6u;i++) plain[6u+i]=(uint8_t)(initiator_address[i]^part1[6u+i]);
    for (uint8_t i=12u;i<16u;i++) plain[i]=part1[i];
    c1_encrypt(ccb,key,plain);
}
