/* Native SmpDbMaxAttemptReached 0x5426c0; pinned Cordio smp_db.c. */
#include <stdint.h>
extern uint8_t *smpDbGetRecord(uint8_t connection);
extern const uint8_t *audio_ble_comm_registration_slot; /* native pSmpCfg cell 0x200004b8 */
extern void smpDbStartServiceTimer(void);
extern void audio_ble_smp_db_diagnostic(const char *,uint32_t,const char *,
                                         uint8_t,uint32_t,uint32_t);
static const char function_name[]="SmpDbMaxAttemptReached";
static const char message[]="SmpDbMaxAttemptReached: connId: %d";

static uint16_t load16(const uint8_t *p)
{
    return (uint16_t)p[0]|((uint16_t)p[1]<<8u);
}
static uint32_t load32(const uint8_t *p)
{
    return (uint32_t)p[0]|((uint32_t)p[1]<<8u)|
           ((uint32_t)p[2]<<16u)|((uint32_t)p[3]<<24u);
}
static void store16(uint8_t *p,uint16_t v)
{
    p[0]=(uint8_t)v;p[1]=(uint8_t)(v>>8u);
}
static void store32(uint8_t *p,uint32_t v)
{
    p[0]=(uint8_t)v;p[1]=(uint8_t)(v>>8u);
    p[2]=(uint8_t)(v>>16u);p[3]=(uint8_t)(v>>24u);
}

uint32_t SmpDbMaxAttemptReached(uint8_t connection)
{
    uint8_t *record=smpDbGetRecord(connection);
    audio_ble_smp_db_diagnostic(function_name,0x121u,message,1u,connection,0u);
    const uint8_t *const cfg=audio_ble_comm_registration_slot;
    uint16_t multiplier=load16(record+8u);
    if (multiplier==0u) multiplier=1u;
    else multiplier=(uint16_t)(multiplier*load16(cfg+0x14u));
    const uint32_t timeout=load32(cfg)*multiplier;
    const uint32_t maximum=load32(cfg+0x0cu);
    if (timeout>maximum) store32(record+0x0cu,maximum);
    else {
        store32(record+0x0cu,timeout);
        store16(record+8u,multiplier);
    }
    store32(record+0x10u,load32(cfg+0x10u));
    smpDbStartServiceTimer();
    return load32(record+0x0cu);
}
