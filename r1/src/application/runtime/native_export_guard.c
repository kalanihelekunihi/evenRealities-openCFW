#include <stdint.h>
#include <stddef.h>
/* Narrow RW cells alongside the existing status-ring read/write/drop owners. */
volatile uint8_t r1_ep_active __attribute__((section(".r1.ep.active")))=0;
volatile uint8_t r1_ep_export_paused __attribute__((section(".r1.ep.export.paused")))=0;
void *volatile r1_ep_mutex __attribute__((section(".r1.ep.mutex"),aligned(4)))=0;
volatile uint32_t r1_ep_export_pause_tick __attribute__((section(".r1.ep.export.pause.tick"),aligned(4)))=0;
extern uint32_t xTaskGetTickCount(void);
extern volatile uint8_t r1_structured_log_export_state;
extern uint32_t r1_event_publish(uint32_t,const void *,uint32_t);
extern int32_t xQueueSemaphoreTake(void *,uint32_t),xQueueGenericSend(void *,const void *,uint32_t,int32_t);
extern void r1_ep_plan_initialization(void),r1_ep_export_ring_flush(void);
extern uint32_t r1_structured_log_mode_get(void),r1_structured_log_format(uint32_t,const char *,const char *,...);
extern void nrf_log_frontend_std_0(uint32_t,const char *);
void r1_ep_export_guard(uint32_t force)
{
    if (!force && r1_ep_export_paused) {
        uint32_t now=xTaskGetTickCount();
        uint32_t elapsed=now-r1_ep_export_pause_tick;
        if (elapsed<307200) return;
        const char *ring="[RING][ep] export guard timeout, force resume flush";
        if ((r1_structured_log_mode_get()&1u)||(r1_structured_log_mode_get()&4u))
            (void)r1_structured_log_format(0x08000000,ring,ring);
        if (r1_structured_log_mode_get()&2u)
            nrf_log_frontend_std_0(0x001c0002,"[ep] export guard timeout, force resume flush");
        r1_ep_export_paused=0;
    }
    if (!r1_ep_active) {
        r1_ep_plan_initialization();
        if (!r1_ep_active) return;
    }
    void *mutex=r1_ep_mutex;
    if (!mutex || xQueueSemaphoreTake(mutex,1024)!=1) return;
    r1_ep_export_ring_flush();
    (void)xQueueGenericSend(r1_ep_mutex,0,0,0);
}
void r1_event_service_0005e0de(void){r1_ep_export_guard(0);}
void r1_ep_export_force_flush(void){r1_ep_export_guard(1);}

/* Stock 0x5dfcc is shared by both export preparation and the start callback. */
uint32_t r1_ep_export_pause_begin(void)
{
    r1_ep_export_pause_tick=xTaskGetTickCount();
    r1_ep_export_paused=1;
    return 1;
}

/* Stock 0x58d64 calls 0x5dfcc after logging. The structured-log guard must
 * be raised only after the start message has been admitted. */
uint32_t r1_log_export_snapshot_start(void)
{
    const char *ring="[RING]log export start";
    if ((r1_structured_log_mode_get()&1u)||(r1_structured_log_mode_get()&4u))
        (void)r1_structured_log_format(0x0c000000u,ring,ring);
    if (r1_structured_log_mode_get()&2u)
        nrf_log_frontend_std_0(0x001c0003u,"log export start");
    r1_structured_log_export_state=1;
    return r1_ep_export_pause_begin();
}

/* Stock 0x58d54 clears the log gate and tail-calls 0x5dfe0, which resumes
 * EP persistence and publishes the zero-length 0x2003 event. */
uint32_t r1_log_export_snapshot_finish(void)
{
    r1_structured_log_export_state=0;
    r1_ep_export_paused=0;
    return r1_event_publish(0x2003u,NULL,0);
}
