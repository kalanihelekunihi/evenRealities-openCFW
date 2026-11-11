#include <stdint.h>
/* Native health-settings change detection and cached persistence. */
#include "native_gomore_authorization.h"
extern uint32_t r1_structured_log_mode_get(void);
extern uint32_t r1_structured_log_format(uint32_t,const char *,const char *,...);
extern void nrf_log_frontend_std_0(uint32_t,const char *);
extern void r1_record12_reinitialize(void);
const char r1_health_change_ring_text[56]
 __attribute__((section(".r1.health.change.ring")))=
 "[RING]gm user info significant change, reinit algorithm";
const char r1_health_change_sdk_text[50]
 __attribute__((section(".r1.health.change.sdk")))=
 "gm user info significant change, reinit algorithm";
/* Native 0x6c53c: unsigned deltas preserve the inclusive +/-2 and +/-9
 * windows. Read every updated byte before its corresponding previous byte,
 * even once a change is known. Only bit zero of the status gates reinit. */
void r1_record12_apply(const volatile uint8_t *previous,
                       const volatile uint8_t *updated)
{
    if (!previous || !updated) return;
    uint32_t next=updated[0];
    uint32_t before=previous[0];
    uint32_t changed=(next-before+2u)>4u;
    next=updated[1];
    before=previous[1];
    if (next!=before) changed=1;
    next=updated[2];
    before=previous[2];
    if ((next-before+9u)>18u) changed=1;
    next=updated[3];
    before=previous[3];
    if ((next-before+9u)>18u) changed=1;
    if (!(changed&r1_device_id_once_status)) return;
    if ((r1_structured_log_mode_get()&1u)||
        (r1_structured_log_mode_get()&4u))
        (void)r1_structured_log_format(0x0c000000u,r1_health_change_ring_text,
                                     r1_health_change_ring_text);
    if (r1_structured_log_mode_get()&2u)
        nrf_log_frontend_std_0(0x001c0003u,r1_health_change_sdk_text);
    r1_record12_reinitialize();
}
extern void *volatile r1_health_settings_kv_handle;
extern uint32_t r1_kv_class_read(void *,void *,uint32_t);
extern uint32_t r1_kv_class_write(void *,const void *,uint32_t);
struct __attribute__((packed,may_alias)) r1_health_unaligned_word { uint32_t value; };
/* Stock 0x73604 uses a 12-byte local view. Refresh the live handle
 * before writing and keep ordered unaligned load/store pairs. */
__attribute__((noinline,used)) uint32_t
r1_record12_persist_body(const volatile uint8_t *record,volatile uint32_t *frame)
{
    if (!record) return 0;
    (void)r1_kv_class_read(r1_health_settings_kv_handle,(void *)frame,12);
    for (uint32_t i=0;i<3;i++)
        frame[i]=((const volatile struct r1_health_unaligned_word *)
                  (const volatile void *)(record+4*i))->value;
    return r1_kv_class_write(r1_health_settings_kv_handle,(const void *)frame,12);
}
void r1_record12_persist(const void *record)
{
    volatile uint32_t frame[3];
    r1_record12_persist_body(record,frame);
}
