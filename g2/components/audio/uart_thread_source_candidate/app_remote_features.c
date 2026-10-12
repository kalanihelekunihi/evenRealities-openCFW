/* Native DmReadRemoteFeatures 0x4b6cb0, called for APP event 2.
 * The DM CCB and registration callback table remain live product RAM. */
#include <stdint.h>
extern uint8_t *dmConnCcbById(uint8_t);
extern void HciLeReadRemoteFeatCmd(uint16_t); /* native 0x52b352 */
extern uint8_t audio_dm_connection_records[]; /* stock 0x200712a4 */
extern void audio_uart_buffer_zero(void *,uint32_t,uint32_t);
static uint16_t rd16(const uint8_t *p){return (uint16_t)p[0]|((uint16_t)p[1]<<8);}
static uint32_t rd32(const uint8_t *p){return (uint32_t)p[0]|((uint32_t)p[1]<<8)|((uint32_t)p[2]<<16)|((uint32_t)p[3]<<24);}

__attribute__((used,noinline))
uint32_t audio_ble_dm_read_remote_features_body(uint32_t connection){
    uint8_t *ccb=dmConnCcbById((uint8_t)connection);
    if(ccb==0)return connection;
    if(ccb[0x2cu]==0u){HciLeReadRemoteFeatCmd(rd16(ccb+0x0cu));return connection;}
    uint8_t event[16];
    audio_uart_buffer_zero(event,16u,0u);
    event[0]=ccb[0x10u];event[1]=0u;event[2]=0x57u;
    event[6]=ccb[0x0cu];event[7]=ccb[0x0du];
    uint32_t feature=rd32(ccb+0x28u);
    for(uint32_t i=0u;i<4u;i++)event[8u+i]=(uint8_t)(feature>>(8u*i));
    uint32_t callback=rd32(audio_dm_connection_records+0x9cu);
    ((void (*)(const uint8_t *))(uintptr_t)callback)(event);
    /* Native packet occupies saved R0-R3 stack slots, so its first word
     * becomes the return value, including mutations by the callback. */
    return rd32(event);
}

__attribute__((naked))
uint32_t DmReadRemoteFeatures(uint8_t connection __attribute__((unused))){
    __asm__ volatile(
        "push {r0, r1, r2, r3, r4, r5, r6, lr}\n"
        "bl audio_ble_dm_read_remote_features_body\n"
        "str r0, [sp]\n"
        "pop {r0, r1, r2, r3, r4, r5, r6, pc}\n");
}
