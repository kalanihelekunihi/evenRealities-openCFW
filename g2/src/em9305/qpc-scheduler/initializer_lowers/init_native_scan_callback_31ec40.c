#include <stdint.h>

/* Native 0x31ec40..0x31ed32: scan window scheduling callback for the scan
 * context at object+0x24. A pending stop (+149/+148) posts a 4-byte event
 * (kind 2 for the primary context 0x804fd8, else 3) to the task at
 * 0x805b18. Otherwise refresh the local address after a resolvable
 * address rotation (0x805a80), then either extend the current window
 * (+0x3c/+0x3e, 625 us units) when time remains, or move to the next
 * channel and reschedule window by window until the scheduler accepts;
 * the elapsed time is kept at +364. */
extern uintptr_t opencfw_em9305_wsf_event_allocate(uint32_t);
extern uint32_t opencfw_em9305_wsf_task_message_send(uint32_t,uintptr_t);
extern uintptr_t opencfw_em9305_radio_address_write_3045e8(uintptr_t,uint32_t,uint32_t);
extern uint32_t opencfw_em9305_init_schedule_adjust_312f88(uintptr_t,uint32_t,uint32_t);
extern uint32_t opencfw_em9305_auxiliary_elapsed_303f8c(uint32_t,uint32_t);
extern uint32_t opencfw_em9305_init_channel_next_325720(uint32_t,uint32_t);
extern uint32_t opencfw_em9305_auxiliary_insert_313220(uintptr_t);

static uint32_t r32(uintptr_t a){return *(volatile uint32_t *)a;}
static uint32_t r16(uintptr_t a){return *(volatile uint16_t *)a;}
static uint32_t r8(uintptr_t a){return *(volatile uint8_t *)a;}
static void w32(uintptr_t a,uint32_t v){*(volatile uint32_t *)a=v;}
static void w8(uintptr_t a,uint32_t v){*(volatile uint8_t *)a=(uint8_t)v;}

uint32_t opencfw_em9305_scan_callback_31ec40(uintptr_t object)
{
    uintptr_t scan=r32(object+0x24u);
    if(r8(scan+149u)!=0u||r8(scan+148u)!=0u) {
        uintptr_t message=opencfw_em9305_wsf_event_allocate(4u);
        if(message==0u) return 0u;
        w8(message+3u,3u);
        uint32_t kind=(scan!=(uintptr_t)0x804fd8u)+2u;
        uint32_t task=r8(0x805b18u);
        w8(message+2u,kind);
        return opencfw_em9305_wsf_task_message_send(task,message);
    }
    if(r8(0x805a80u)!=0u) {
        uint32_t flags=r8(scan+65u);
        if(flags&1u) {
            w8(0x805a80u,0u);
            if((flags&2u)==0u)
                (void)opencfw_em9305_radio_address_write_3045e8(scan+2u,r32(0x805a8cu),
                                                                r32(0x805a90u));
            uint32_t high=r32(0x805a90u);
            uint32_t low=r32(0x805a8cu);
            w32(scan+288u,high);
            w32(scan+284u,low);
        }
    }
    uint32_t window=r16(scan+0x3eu);
    uint32_t offset=r16(scan+0x3cu);
    w32(object+8u,r32(scan+0x38u));
    if(offset!=window) {
        uint32_t elapsed=r32(scan+364u);
        uint32_t limit=window*625u;
        if(r32(object+0xcu)+elapsed<limit&&
           opencfw_em9305_init_schedule_adjust_312f88(object,elapsed,limit)!=0u) {
            uint32_t result=opencfw_em9305_auxiliary_elapsed_303f8c(r32(object+8u),
                                                                    r32(scan+0x38u));
            w32(scan+364u,result);
            return result;
        }
    }
    uint32_t channel=r8(scan+201u);
    uint32_t mask=r8(scan+351u);
    w32(scan+364u,0u);
    uint32_t next=opencfw_em9305_init_channel_next_325720(channel,mask);
    window=r16(scan+0x3eu);
    offset=r16(scan+0x3cu);
    w8(scan+201u,next);
    if(offset==window) {
        (void)opencfw_em9305_auxiliary_insert_313220(object);
        uint32_t anchor=r32(object+8u);
        w32(scan+0x38u,anchor);
        return anchor;
    }
    uint32_t step=offset*625u;
    uint32_t limit=window*625u+step;
    uint32_t anchor=r32(object+8u);
    for(;;) {
        anchor+=step;
        w32(scan+0x38u,anchor);
        if(opencfw_em9305_init_schedule_adjust_312f88(object,step,limit)!=0u) break;
        anchor=r32(scan+0x38u);
        w32(object+8u,anchor);
    }
    uint32_t result=opencfw_em9305_auxiliary_elapsed_303f8c(r32(object+8u),r32(scan+0x38u));
    w32(scan+364u,result);
    return result;
}
