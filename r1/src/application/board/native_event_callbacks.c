#include <stdint.h>
#include "native_battery_memory.h"
#include "../runtime/native_subscriber.h"
extern uint32_t r1_authenticated_phone_connection_gate(void);
extern void r1_event_service_000838e0(void),r1_event_service_0008d380(void);
extern void r1_event_service_0008e274(void),r1_event_service_0008e55c(void),r1_event_service_0008e552(void);
extern void r1_event_service_0008b378(const void *),r1_event_service_0008b8e8(const void *);
extern void r1_event_service_0008a80a(uint32_t,uint32_t),r1_event_service_0008a83e(uint32_t,uint32_t);
extern void r1_event_service_0008a8ae(uint32_t,uint32_t),r1_event_service_0008a8fc(uint32_t,uint32_t);
extern void r1_event_service_0008a7f4(uint32_t,uint32_t),r1_event_service_0008a8d8(uint32_t,uint32_t);
extern void r1_event_service_0008dd90(const volatile uint8_t *),r1_event_service_0008dd88(void);
extern void r1_event_service_0008dc94(const volatile uint8_t *);
extern void r1_event_service_0008e154(uint32_t),r1_event_service_0008e1e0(const void *,uint32_t);
extern uint32_t r1_event_service_0008aeb0(uint32_t,int32_t),r1_event_service_0008aea4(void);
extern uint32_t r1_time_backend_timestamp(void);
extern void r1_event_service_0006b724(const void *,uint32_t);
extern void nrf_log_frontend_std_2(uint32_t,const char *,uint32_t,uint32_t);
extern void nrf_log_frontend_std_4(uint32_t,const char *,uint32_t,uint32_t,uint32_t,uint32_t);
extern void nrf_log_frontend_std_5(uint32_t,const char *,uint32_t,uint32_t,uint32_t,uint32_t,uint32_t);

extern void r1_event_service_0004c4b8(uint32_t);
/* Branch-only event adapters are ordinary C; byte/relocation replay guards
 * the complete incoming register state at the unresolved service boundary. */
extern void r1_event_service_00049068(uint32_t,uint32_t);
extern void r1_event_service_0004a5bc(uint32_t,uint32_t);
extern void r1_event_service_0004a4b4(uint32_t,uint32_t);
extern uint32_t r1_event_service_0007c52c(uint32_t,uint32_t);
#include "../runtime/native_health_enable.h"
/* Authenticated native callback contracts; opcode arrays and guessed provider bodies are not used. */
const char r1_event_text_42180[29] __attribute__((section(".r1.event.s42180")))="[RING]hr measure control: %d";
const char r1_event_text_421a8[23] __attribute__((section(".r1.event.s421a8")))="hr measure control: %d";
const char r1_event_text_42214[22] __attribute__((section(".r1.event.s42214")))="[RING]set hr mode: %d";
const char r1_event_text_42234[16] __attribute__((section(".r1.event.s42234")))="set hr mode: %d";
const char r1_event_text_42294[24] __attribute__((section(".r1.event.s42294")))="[RING]set spo2 mode: %d";
const char r1_event_text_422b4[18] __attribute__((section(".r1.event.s422b4")))="set spo2 mode: %d";
const char r1_event_text_42318[26] __attribute__((section(".r1.event.s42318")))="[RING]set stress mode: %d";
const char r1_event_text_4233c[20] __attribute__((section(".r1.event.s4233c")))="set stress mode: %d";
const char r1_event_text_423a0[24] __attribute__((section(".r1.event.s423a0")))="[RING]set temp mode: %d";
const char r1_event_text_423c0[18] __attribute__((section(".r1.event.s423c0")))="set temp mode: %d";
const char r1_event_text_42430[31] __attribute__((section(".r1.event.s42430")))="[RING]spo2 measure control: %d";
const char r1_event_text_42458[25] __attribute__((section(".r1.event.s42458")))="spo2 measure control: %d";
const char r1_event_text_424cc[33] __attribute__((section(".r1.event.s424cc")))="[RING]stress measure control: %d";
const char r1_event_text_424f8[27] __attribute__((section(".r1.event.s424f8")))="stress measure control: %d";
const char r1_event_text_4256c[31] __attribute__((section(".r1.event.s4256c")))="[RING]temp measure control: %d";
const char r1_event_text_42594[25] __attribute__((section(".r1.event.s42594")))="temp measure control: %d";
const char r1_event_text_42710[29] __attribute__((section(".r1.event.s42710")))="[RING]usinfo old:%d,%d,%d,%d";
const char r1_event_text_42738[23] __attribute__((section(".r1.event.s42738")))="usinfo old:%d,%d,%d,%d";
const char r1_event_text_42750[15] __attribute__((section(".r1.event.s42750")))="[RING]%d,%d,%d";
const char r1_event_text_42760[22] __attribute__((section(".r1.event.s42760")))="[RING]new:%d,%d,%d,%d";
const char r1_event_text_42778[16] __attribute__((section(".r1.event.s42778")))="new:%d,%d,%d,%d";
const char r1_event_text_427f4[35] __attribute__((section(".r1.event.s427f4")))="[RING]activity data:%d,%d,%d,%d,%d";
const char r1_event_text_42820[29] __attribute__((section(".r1.event.s42820")))="activity data:%d,%d,%d,%d,%d";
const char r1_event_text_42920[29] __attribute__((section(".r1.event.s42920")))="[RING]one the hour:%d, ts:%d";
const char r1_event_text_42948[23] __attribute__((section(".r1.event.s42948")))="one the hour:%d, ts:%d";
const char r1_event_text_429cc[31] __attribute__((section(".r1.event.s429cc")))="[RING]service stress point: %d";
const char r1_event_text_429f4[25] __attribute__((section(".r1.event.s429f4")))="service stress point: %d";
const char r1_event_text_42ab4[52] __attribute__((section(".r1.event.s42ab4")))="[RING]update ts: %d, tz: %d, old_ts: %d, old_tz: %d";
const char r1_event_text_42af0[46] __attribute__((section(".r1.event.s42af0")))="update ts: %d, tz: %d, old_ts: %d, old_tz: %d";
const char r1_event_text_42b74[27] __attribute__((section(".r1.event.s42b74")))="[RING]storage gm l:%d,k:%s";
const char r1_event_text_42b98[21] __attribute__((section(".r1.event.s42b98")))="storage gm l:%d,k:%s";
void r1_event_callback_00042108(uint32_t payload,uint32_t length)
{ r1_event_service_00049068(payload,length); }
void r1_event_callback_0004210c(uint32_t payload,uint32_t length)
{ if (length == 1) r1_event_service_0004c4b8((uint8_t)payload); }
void r1_event_callback_00042118(uint32_t payload,uint32_t length)
{
    (void)length; if (payload) (void)r1_event_service_0008b0fc((volatile uint8_t *)(uintptr_t)payload);
}
void r1_event_callback_00042122(uint32_t payload,uint32_t length)
{ (void)r1_event_service_000496fc((uint8_t)payload,length); }
extern void r1_event_service_000497cc(uint32_t,uint32_t);
extern uint32_t r1_structured_log_mode_get(void);
extern uint32_t r1_structured_log_format(uint32_t,const char *,const char *,...);
extern void nrf_log_frontend_std_1(uint32_t,const char *,uint32_t);
void r1_event_callback_00042128(uint32_t payload,uint32_t length)
{
    if (length!=1) return;
    uint32_t enabled=payload!=0;
    if ((r1_structured_log_mode_get()&1u)||(r1_structured_log_mode_get()&4u))
        (void)r1_structured_log_format(0x0c400000,r1_event_text_42180,r1_event_text_42180,enabled);
    if (r1_structured_log_mode_get()&2u)
        nrf_log_frontend_std_1(0x001c0003,r1_event_text_421a8,enabled);
    r1_event_service_000497cc(enabled,0);
}
void r1_event_callback_000421c0(uint32_t payload,uint32_t length)
{ r1_event_service_0004a5bc(payload,length); }
extern void r1_event_service_000499c4(uint32_t,uint32_t);
extern uint32_t r1_structured_log_mode_get(void);
extern uint32_t r1_structured_log_format(uint32_t,const char *,const char *,...);
extern void nrf_log_frontend_std_1(uint32_t,const char *,uint32_t);
void r1_event_callback_000421c4(uint32_t payload,uint32_t length)
{
    if (length!=1) return;
    uint32_t mode=(uint8_t)payload;
    if ((r1_structured_log_mode_get()&1u)||(r1_structured_log_mode_get()&4u))
        (void)r1_structured_log_format(0x0c400000,r1_event_text_42214,r1_event_text_42214,mode);
    if (r1_structured_log_mode_get()&2u)
        nrf_log_frontend_std_1(0x001c0003,r1_event_text_42234,mode);
    r1_event_service_000499c4(mode,0);
}
extern void r1_event_service_0004ad7c(uint32_t,uint32_t);
extern uint32_t r1_structured_log_mode_get(void);
extern uint32_t r1_structured_log_format(uint32_t,const char *,const char *,...);
extern void nrf_log_frontend_std_1(uint32_t,const char *,uint32_t);
void r1_event_callback_00042244(uint32_t payload,uint32_t length)
{
    if (length!=1) return;
    uint32_t mode=(uint8_t)payload;
    if ((r1_structured_log_mode_get()&1u)||(r1_structured_log_mode_get()&4u))
        (void)r1_structured_log_format(0x0c400000,r1_event_text_42294,r1_event_text_42294,mode);
    if (r1_structured_log_mode_get()&2u)
        nrf_log_frontend_std_1(0x001c0003,r1_event_text_422b4,mode);
    r1_event_service_0004ad7c(mode,0);
}
extern void r1_event_service_0004b48c(uint32_t,uint32_t);
extern uint32_t r1_structured_log_mode_get(void);
extern uint32_t r1_structured_log_format(uint32_t,const char *,const char *,...);
extern void nrf_log_frontend_std_1(uint32_t,const char *,uint32_t);
void r1_event_callback_000422c8(uint32_t payload,uint32_t length)
{
    if (length!=1) return;
    uint32_t mode=(uint8_t)payload;
    if ((r1_structured_log_mode_get()&1u)||(r1_structured_log_mode_get()&4u))
        (void)r1_structured_log_format(0x0c400000,r1_event_text_42318,r1_event_text_42318,mode);
    if (r1_structured_log_mode_get()&2u)
        nrf_log_frontend_std_1(0x001c0003,r1_event_text_4233c,mode);
    (void)r1_event_service_0004b48c(mode,0);
}
extern void r1_event_service_0004bab4(uint32_t);
void r1_event_callback_00042350(uint32_t payload,uint32_t length)
{
    if (length!=1) return;
    uint32_t mode=(uint8_t)payload;
    if ((r1_structured_log_mode_get()&1u)||(r1_structured_log_mode_get()&4u))
        (void)r1_structured_log_format(0x0c400000,r1_event_text_423a0,r1_event_text_423a0,mode);
    if (r1_structured_log_mode_get()&2u)
        nrf_log_frontend_std_1(0x001c0003,r1_event_text_423c0,mode);
    r1_event_service_0004bab4(mode);
}
void r1_event_callback_000423d4(uint32_t payload,uint32_t length)
{ r1_event_service_0004a4b4(payload,length); }
extern void r1_event_service_0004aaf8(uint32_t,uint32_t);
extern uint32_t r1_structured_log_mode_get(void);
extern uint32_t r1_structured_log_format(uint32_t,const char *,const char *,...);
extern void nrf_log_frontend_std_1(uint32_t,const char *,uint32_t);
void r1_event_callback_000423d8(uint32_t payload,uint32_t length)
{
    if (length!=1) return;
    uint32_t enabled=payload!=0;
    if ((r1_structured_log_mode_get()&1u)||(r1_structured_log_mode_get()&4u))
        (void)r1_structured_log_format(0x0c400000,r1_event_text_42430,r1_event_text_42430,enabled);
    if (r1_structured_log_mode_get()&2u)
        nrf_log_frontend_std_1(0x001c0003,r1_event_text_42458,enabled);
    r1_event_service_0004aaf8(enabled,0);
}
extern uint32_t r1_event_service_0004b33e(uint32_t,uint32_t);
extern uint32_t r1_structured_log_mode_get(void);
extern uint32_t r1_structured_log_format(uint32_t,const char *,const char *,...);
extern void nrf_log_frontend_std_1(uint32_t,const char *,uint32_t);
void r1_event_callback_00042474(uint32_t payload,uint32_t length)
{
    if (length!=1) return;
    uint32_t enabled=payload!=0;
    if ((r1_structured_log_mode_get()&1u)||(r1_structured_log_mode_get()&4u))
        (void)r1_structured_log_format(0x0c400000,r1_event_text_424cc,r1_event_text_424cc,enabled);
    if (r1_structured_log_mode_get()&2u)
        nrf_log_frontend_std_1(0x001c0003,r1_event_text_424f8,enabled);
    (void)r1_event_service_0004b33e(enabled,0);
}
/* Stock 0x42514: one-byte event, full-word boolean conversion. */
extern void r1_event_service_0004b6c0(uint32_t);
extern uint32_t r1_structured_log_mode_get(void);
extern uint32_t r1_structured_log_format(uint32_t,const char *,const char *,...);
extern void nrf_log_frontend_std_1(uint32_t,const char *,uint32_t);
void r1_event_callback_00042514(uint32_t payload,uint32_t length)
{
    if (length!=1) return;
    uint32_t enabled=payload!=0;
    if ((r1_structured_log_mode_get()&1u)||(r1_structured_log_mode_get()&4u))
        (void)r1_structured_log_format(0x0c400000,r1_event_text_4256c,r1_event_text_4256c,enabled);
    if (r1_structured_log_mode_get()&2u)
        nrf_log_frontend_std_1(0x001c0003,r1_event_text_42594,enabled);
    r1_event_service_0004b6c0(enabled);
}
/* Incoming R2/R3 are fallback words used by the stock getter. The event
 * table calls this ARM entry with two declared arguments; these additional
 * parameters name its observed ambient register words for the C body. */
extern void r1_event_profile_update_body(uint32_t,uint32_t,uint32_t,uint32_t);
void r1_event_callback_000425b0(
    uint32_t payload,uint32_t length,uint32_t fallback2,uint32_t fallback3)
{
    __attribute__((musttail)) return r1_event_profile_update_body(
        payload,length,fallback2,fallback3);
}
void r1_event_callback_00042788(uint32_t payload,uint32_t length)
{
    if (!payload || length!=12) return;
    const volatile uint8_t *p=(const volatile uint8_t *)(uintptr_t)payload;
    if ((r1_structured_log_mode_get()&1u)||(r1_structured_log_mode_get()&4u)) {
        uint32_t b=read16(p+2),d=read16(p+6),c=read16(p+4),e=read32(p+8),a=read16(p);
        (void)r1_structured_log_format(0x0d400000,r1_event_text_427f4,r1_event_text_427f4,a,b,c,d,e);
    }
    if (r1_structured_log_mode_get()&2u) {
        uint32_t c=read16(p+4),d=read16(p+6),e=read32(p+8),b=read16(p+2),a=read16(p);
        nrf_log_frontend_std_5(0x001c0003,r1_event_text_42820,a,b,c,d,e);
    }
    r1_event_service_0008a7f4(payload,length);
}
void r1_event_callback_00042840(uint32_t payload,uint32_t length)
{
    (void)payload;(void)length; r1_event_service_0008d380(); r1_event_service_0008e274(); r1_event_service_0008e55c(); r1_event_service_0008e552();
}
void r1_event_callback_00042856(uint32_t payload,uint32_t length)
{
    (void)length; if (payload) (void)r1_event_service_0008b0fc((volatile uint8_t *)(uintptr_t)payload);
}
void r1_event_callback_00042860(uint32_t payload,uint32_t length)
{
    if (payload && length==9) r1_event_service_0008b378((const void *)(uintptr_t)payload);
}
void r1_event_callback_0004286e(uint32_t payload,uint32_t length)
{
    if (payload && length==8) r1_event_service_0008b8e8((const void *)(uintptr_t)payload);
}
void r1_event_callback_0004287c(uint32_t payload,uint32_t length)
{
    (void)length; uint32_t command=(uint8_t)payload; uint32_t allowed=r1_authenticated_phone_connection_gate(); if (allowed && command==1) r1_event_service_000838e0();
}
void r1_event_callback_00042896(uint32_t payload,uint32_t length)
{
    if (payload && length==8) r1_event_service_0008a80a(payload,length);
}
void r1_event_callback_000428a4(uint32_t payload,uint32_t length)
{
    if (payload && length==8) r1_event_service_0008a83e(payload,length);
}
void r1_event_callback_000428b2(uint32_t payload,uint32_t length)
{ (void)payload;(void)length; }
void r1_event_callback_000428b4(uint32_t payload,uint32_t length)
{
    (void)length;
    uint32_t value=(uint8_t)payload;
    if ((r1_structured_log_mode_get()&1u)||(r1_structured_log_mode_get()&4u)) {
        uint32_t timestamp=r1_time_backend_timestamp();
        (void)r1_structured_log_format(0x0c800000,r1_event_text_42920,r1_event_text_42920,value,timestamp);
    }
    if (r1_structured_log_mode_get()&2u) {
        uint32_t timestamp=r1_time_backend_timestamp();
        nrf_log_frontend_std_2(0x001c0003,r1_event_text_42948,value,timestamp);
    }
    (void)r1_event_service_0008b028(1,(const void *)(uintptr_t)value,1);
    if (!value) (void)r1_event_service_0008b028(2,0,0);
}
void r1_event_callback_00042960(uint32_t payload,uint32_t length)
{
    (void)length; r1_event_service_0008dd90((const volatile uint8_t *)(uintptr_t)payload);
}
void r1_event_callback_00042964(uint32_t payload,uint32_t length)
{
    (void)length; r1_event_service_0008e154((uint8_t)payload);
}
void r1_event_callback_0004296a(uint32_t payload,uint32_t length)
{
    if (payload && length==8) r1_event_service_0008a8ae(payload,length);
}
void r1_event_callback_00042978(uint32_t payload,uint32_t length)
{
    if (!payload || length!=8) return;
    const volatile uint8_t *p=(const volatile uint8_t *)(uintptr_t)payload;
    if ((r1_structured_log_mode_get()&1u)||(r1_structured_log_mode_get()&4u)) {
        uint32_t value=p[0];
        (void)r1_structured_log_format(0x0c400000,r1_event_text_429cc,r1_event_text_429cc,value);
    }
    if (r1_structured_log_mode_get()&2u) nrf_log_frontend_std_1(0x001c0003,r1_event_text_429f4,p[0]);
    r1_event_service_0008a8d8(payload,length);
}
void r1_event_callback_00042a10(uint32_t payload,uint32_t length)
{
    if (payload && length==8) r1_event_service_0008a8fc(payload,length);
}
void r1_event_callback_00042a20(uint32_t payload,uint32_t length)
{
    if (!payload || length!=12) return;
    const volatile uint8_t *p=(const volatile uint8_t *)(uintptr_t)payload;
    uint32_t timezone=read16(p+2),timestamp=read32(p+8);
    if (r1_event_service_0008aeb0(timestamp,(int32_t)timezone)) (void)r1_event_service_0008aea4();
    if ((r1_structured_log_mode_get()&1u)||(r1_structured_log_mode_get()&4u)) {
        uint32_t ntz=read16(p+2),otz=read16(p),ots=read32(p+4),nts=read32(p+8);
        (void)r1_structured_log_format(0x0d000000,r1_event_text_42ab4,r1_event_text_42ab4,nts,ntz,ots,otz);
    }
    if (r1_structured_log_mode_get()&2u) {
        uint32_t otz=read16(p),ots=read32(p+4),ntz=read16(p+2),nts=read32(p+8);
        nrf_log_frontend_std_4(0x001c0003,r1_event_text_42af0,nts,ntz,ots,otz);
    }
    uint32_t ntz=read16(p+2),otz=read16(p);
    if (ntz!=otz) { (void)r1_event_service_0008b028(0,(const void *)(uintptr_t)payload,12); return; }
    uint32_t old=read32(p+4),now=read32(p+8);
    uint32_t difference=now>old ? now-old : old-now;
    if (difference>30) (void)r1_event_service_0008b028(0,(const void *)(uintptr_t)payload,12);
}
void r1_event_callback_00042b20(uint32_t payload,uint32_t length)
{
    (void)length;
    const volatile uint8_t *p=(const volatile uint8_t *)(uintptr_t)payload;
    const void *key=(const void *)(uintptr_t)(payload+1u);
    if ((r1_structured_log_mode_get()&1u)||(r1_structured_log_mode_get()&4u)) {
        uint32_t size=p[0];
        (void)r1_structured_log_format(0x0c800000,r1_event_text_42b74,r1_event_text_42b74,size,key);
    }
    if (r1_structured_log_mode_get()&2u) nrf_log_frontend_std_2(0x001c0003,r1_event_text_42b98,p[0],(uint32_t)(uintptr_t)key);
    r1_event_service_0006b724(key,p[0]);
}
extern void r1_event_service_000914a0(void),r1_event_service_0005e0de(void);
void r1_event_callback_00042bb0(uint32_t payload,uint32_t length)
{
    (void)payload;(void)length;
    r1_event_service_000914a0();
    r1_event_service_0005e0de();
}
void r1_event_callback_00042bbe(uint32_t payload,uint32_t length)
{ r1_event_service_0007c52c(payload,length); }
void r1_event_callback_00042bc2(uint32_t payload,uint32_t length)
{
    (void)payload;(void)length; r1_event_service_0008dd88();
}
void r1_event_callback_00042bc6(uint32_t payload,uint32_t length)
{
    (void)length; r1_event_service_0008dc94((const volatile uint8_t *)(uintptr_t)payload);
}
void r1_event_callback_00042bca(uint32_t payload,uint32_t length)
{
    r1_event_service_0008e1e0((const void *)(uintptr_t)payload,length);
}
