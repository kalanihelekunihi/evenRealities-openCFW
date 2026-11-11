/* Stock R1 sleep-sync packet constructor at application 0x8da24. */
#include <stdint.h>
#include <stddef.h>
#include "native_health_event_post.h"
#include "../board/native_battery_memory.h"

extern void *pvPortMalloc(size_t);
extern void vPortFree(void *);
extern void __aeabi_memclr(void *,size_t);
extern int32_t r1_time_utc_offset_get(void);
struct r1_sleep_sync_ack_context;
extern void r1_sleep_sync_ack_plan(struct r1_sleep_sync_ack_context *);
extern uint32_t r1_structured_log_mode_get(void);
extern uint32_t r1_structured_log_format(uint32_t,const char *,const char *,...);
extern void nrf_log_frontend_std_0(uint32_t,const char *);
extern void nrf_log_frontend_std_2(uint32_t,const char *,uint32_t,uint32_t);

static const char alloc_ring[]="[RING]sleep sync alloc ack ctx fail";
static const char alloc_sdk[]="sleep sync alloc ack ctx fail";
static const char send_ring[]="[RING]sleep sync send failed: %d-%d";
static const char send_sdk[]="sleep sync send failed: %d-%d";

static void log_alloc_failure(void)
{
    if ((r1_structured_log_mode_get()&1u)||
        (r1_structured_log_mode_get()&4u))
        (void)r1_structured_log_format(0x04000000,alloc_ring,alloc_ring);
    if (r1_structured_log_mode_get()&2u)
        nrf_log_frontend_std_0(0x001c0001,alloc_sdk);
}

static void log_send_failure(const volatile uint8_t *report)
{
    if ((r1_structured_log_mode_get()&1u)||
        (r1_structured_log_mode_get()&4u))
        (void)r1_structured_log_format(0x04800000,send_ring,send_ring,
                                       read32(report+12),read32(report+16));
    if (r1_structured_log_mode_get()&2u)
        nrf_log_frontend_std_2(0x001c0001,send_sdk,
                               read32(report+12),read32(report+16));
}

void r1_sleep_sync_packet_builder(const void *report_buffer,
                                  uint32_t request_kind,uint32_t request_count,
                                  const void *source_buffer)
{
    const volatile uint8_t *report=report_buffer;
    const volatile uint8_t *source=source_buffer;
    uint32_t stages=report[30];
    uint32_t allocation=32u+3u*stages;
    volatile uint8_t *packet=pvPortMalloc(allocation);
    if (!packet) return;
    __aeabi_memclr((void *)(uintptr_t)packet,allocation);

    packet[0]=report[0];packet[1]=report[1];packet[2]=report[2];
    packet[4]=report[4];packet[5]=report[5];packet[6]=report[6];packet[7]=report[7];
    write32(packet+12,read32(report+12));
    write32(packet+16,read32(report+16));
    for (uint32_t offset=20;offset<=28;offset+=2)
        write16(packet+offset,read16(report+offset));
    write16(packet+8,read16(report+8));
    uint32_t start=read32(report+12);
    write16(packet+10,start<UINT32_C(0x38640900) ?
            0u:(uint16_t)r1_time_utc_offset_get());

    uint32_t run=0;
    for (uint32_t index=0;index<stages;++index) {
        uint8_t encoded=report[32+index];
        uint8_t kind=encoded&3u;
        uint8_t new_run=!index || packet[32+3u*run]!=kind;
        if (index && new_run) ++run;
        if (new_run) {
            packet[32+3u*run]=kind;
            write16(packet+33+3u*run,encoded>>2);
        } else {
            write16(packet+33+3u*run,
                    (uint16_t)(read16(packet+33+3u*run)+(encoded>>2)));
        }
    }
    uint32_t runs=stages?run+1u:0u;
    write16(packet+30,runs);
    if (!runs) {vPortFree((void *)(uintptr_t)packet);return;}

    uint32_t length=32u+3u*runs;
    uint32_t block=r1_sync_block_field_get();
    start=read32(packet+12);
    uint32_t end=read32(packet+16);
    if (start<UINT32_C(0x38640900) && block && block>=start && end>block)
        write32(packet+16,block);

    uint32_t sent=0;
    if (source && source[0]==0) {
        volatile uint8_t *context=pvPortMalloc(12);
        if (!context) {
            log_alloc_failure();
            goto done;
        }
        write32(context,read32(source+4));
        write32(context+4,read32(report+12));
        write32(context+8,read32(report+16));
        sent=r1_event_post_module6(packet,length,block,request_count,
                                   (uint32_t)(uintptr_t)r1_sleep_sync_ack_plan,
                                   context);
    } else {
        sent=r1_event_post_0x601(packet,length,block,request_kind,request_count);
    }
    if (!sent) log_send_failure(report);
done:
    vPortFree((void *)(uintptr_t)packet);
}
