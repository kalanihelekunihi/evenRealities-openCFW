/* Native _bleSlaveRequestMtuExchange 0x46dedc and its two Cordio children
 * AttGetMtu 0x4b5204 / AttcMtuReq 0x4b57fa. */
#include <stdint.h>

extern uint8_t *audio_ble_slave_mode_context; /* live pointer cell 0x20074330 */
extern uint8_t *audio_ble_att_ccb_by_conn_id(uint8_t);
extern uint8_t *attMsgAlloc(uint16_t);
extern void *audio_ble_attc_send_message_4b5640(uint8_t,uint16_t,uint8_t,void *,uint8_t);
extern uint32_t audio_log_level(void);
extern void audio_log_extended(uint8_t,const char *,const char *,const char *,uint32_t,const char *,...);
extern uint32_t compressed_log_output(uint32_t,const char *,const char *,...);

static const char module[]="ble.Slave";
static const char source[]="D:\\01_workspace\\s200_ap510b_iar_git\\platform\\ble\\app_ble_peripheral.c";
static const char function[]="_bleSlaveRequestMtuExchange";
static const char have[]="evenBleConnInfo.SMtu = %d";
static const char have_short[]="[ble.Slave]evenBleConnInfo.SMtu = %d";
static const char want[]="MtuExchange hope to : %d";
static const char want_short[]="[ble.Slave]MtuExchange hope to : %d";

uint32_t audio_ble_att_get_mtu_body(uint8_t connection)
{
    uint8_t *ccb=audio_ble_att_ccb_by_conn_id(connection);
    return (uint32_t)ccb[0] | ((uint32_t)ccb[1]<<8);
}

/* Original AttGetMtu returns an ambient high R7 word as its second result. */
__attribute__((naked)) uint64_t audio_ble_att_get_mtu(uint8_t connection __attribute__((unused)))
{
    __asm__ volatile(
        "push {r7, lr}\n"
        "bl audio_ble_att_get_mtu_body\n"
        "mov r1, r7\n"
        "pop {r7, pc}\n");
}

void audio_ble_attc_mtu_request_body(uint32_t connection,uint32_t mtu,uint32_t *saved)
{
    uint8_t *packet=attMsgAlloc(11u);
    if (packet==0) return;
    packet[0]=3u; packet[1]=0u;
    packet[8]=2u;
    packet[9]=(uint8_t)mtu;
    packet[10]=(uint8_t)(mtu>>8);
    saved[0]=0u;
    (void)audio_ble_attc_send_message_4b5640((uint8_t)connection,0u,1u,packet,0u);
}

/* Native push {r3,r4,r5,lr} / pop {r0,r4,r5,pc}; R0 is saved R3. */
__attribute__((naked)) uint32_t audio_ble_attc_mtu_request(
    uint8_t connection __attribute__((unused)),uint16_t mtu __attribute__((unused)),
    uint32_t unused __attribute__((unused)),uint32_t inherited __attribute__((unused)))
{
    __asm__ volatile(
        "push {r3, r4, r5, lr}\n"
        "mov r2, sp\n"
        "bl audio_ble_attc_mtu_request_body\n"
        "pop {r0, r4, r5, pc}\n");
}

void audio_ble_slave_request_mtu_body(const uint8_t *event,uint32_t *saved)
{
    uint16_t connection=(uint16_t)event[0] | ((uint16_t)event[1]<<8);
    uint16_t mtu=(uint16_t)audio_ble_att_get_mtu((uint8_t)connection);
    uint8_t *row=audio_ble_slave_mode_context;
    row[0x22u]=(uint8_t)mtu;
    row[0x23u]=(uint8_t)(mtu>>8);
    if (audio_log_level()&2u) {
        saved[0]=0x130u;saved[1]=(uint32_t)(uintptr_t)have;
        audio_log_extended(4u,module,source,function,0x130u,have,mtu);
    }
    if ((audio_log_level()&1u)||(audio_log_level()&4u))
        (void)compressed_log_output(0x10400000u,have_short,have_short,mtu);
    if (audio_log_level()&2u) {
        saved[0]=0x131u;saved[1]=(uint32_t)(uintptr_t)want;
        audio_log_extended(4u,module,source,function,0x131u,want,0xf7u);
    }
    if ((audio_log_level()&1u)||(audio_log_level()&4u))
        (void)compressed_log_output(0x10400000u,want_short,want_short,0xf7u);
    (void)audio_ble_attc_mtu_request((uint8_t)connection,0xf7u,0u,0u);
}

__attribute__((naked)) uint64_t audio_ble_slave_request_mtu(
    const uint8_t *event __attribute__((unused)),...)
{
    __asm__ volatile(
        "push {r1, r2, r3, r4, r5, lr}\n"
        "mov r1, sp\n"
        "bl audio_ble_slave_request_mtu_body\n"
        "pop {r0, r1, r2, r4, r5, pc}\n");
}
