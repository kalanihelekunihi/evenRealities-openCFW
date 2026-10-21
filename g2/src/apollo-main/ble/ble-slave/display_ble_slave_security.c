/* Native _bleSlaveSecReq 0x46df7e and connected Cordio 0x4b4684,
 * DmSecSlaveReq 0x52bb00. Live profile pointer cell is 0x20074358. */
#include <stdint.h>

extern const uint8_t *audio_ble_comm_profile_slot;
extern uint8_t DmConnSecLevel(uint8_t);
extern void *WsfMsgAlloc(uint16_t);
extern void SmpDmMsgSend(void *);
extern uint32_t audio_log_level(void);
extern void audio_log_extended(uint8_t,const char *,const char *,const char *,uint32_t,const char *,...);
extern uint32_t compressed_log_output(uint32_t,const char *,const char *,...);

static const char module[]="ble.Slave";
static const char source[]="D:\\01_workspace\\s200_ap510b_iar_git\\platform\\ble\\app_ble_peripheral.c";
static const char function[]="_bleSlaveSecReq";
static const char message[]="AppSlaveSecurityReq connId = %d";
static const char message_short[]="[ble.Slave]AppSlaveSecurityReq connId = %d";

void audio_ble_dm_sec_slave_req_body(uint32_t connection,uint32_t policy)
{
    uint8_t *packet=WsfMsgAlloc(6u);
    if (packet==0) return;
    packet[0]=(uint8_t)connection;
    packet[1]=0u;
    packet[2]=5u;
    packet[4]=(uint8_t)policy;
    SmpDmMsgSend(packet);
}

/* Native saved fourth argument is returned in R0 on either path. */
__attribute__((naked)) uint32_t audio_ble_dm_sec_slave_req(
    uint8_t connection __attribute__((unused)),uint8_t policy __attribute__((unused)),
    uint32_t unused __attribute__((unused)),uint32_t inherited __attribute__((unused)))
{
    __asm__ volatile(
        "push {r3, r4, r5, lr}\n"
        "bl audio_ble_dm_sec_slave_req_body\n"
        "pop {r0, r4, r5, pc}\n");
}

void audio_ble_slave_security_apply(uint8_t connection)
{
    if (DmConnSecLevel(connection)==0u)
        (void)audio_ble_dm_sec_slave_req(connection,audio_ble_comm_profile_slot[0],0u,0u);
}

void audio_ble_slave_security_request_body(uint32_t connection,uint32_t *saved)
{
    uint8_t id=(uint8_t)connection;
    if (audio_log_level()&2u) {
        saved[0]=0x138u;
        saved[1]=(uint32_t)(uintptr_t)message;
        saved[2]=id;
        audio_log_extended(4u,module,source,function,0x138u,message,id);
    }
    if ((audio_log_level()&1u)||(audio_log_level()&4u))
        (void)compressed_log_output(0x10400000u,message_short,message_short,id);
    audio_ble_slave_security_apply(id);
}

/* The native six-word frame returns saved R0/R1, including log overwrites. */
__attribute__((naked)) uint64_t audio_ble_slave_security_request(
    uint8_t connection __attribute__((unused)),...)
{
    __asm__ volatile(
        "push {r0, r1, r2, r3, r4, lr}\n"
        "mov r1, sp\n"
        "bl audio_ble_slave_security_request_body\n"
        "pop {r0, r1, r2, r3, r4, pc}\n");
}
