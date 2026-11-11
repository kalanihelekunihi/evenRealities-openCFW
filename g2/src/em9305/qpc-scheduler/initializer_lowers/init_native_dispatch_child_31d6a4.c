#include <stdint.h>

/* Native 0x31d6a4..0x31db9c: deliver the packets received in a group
 * event (group +0x18 subevents, +52 links at +0x38[i], +6 timing) to the
 * links. For each link and subevent j the received buffer (3174d8) is
 * checked by the MIC hook (0x8051dc; on failure the buffer is released,
 * event 6 is sent and the group closed). The 64-bit event counter
 * (counter * subevents + j) is published at link +232. Links whose
 * configuration (+4)->+0x1e is set take the buffer through 316f70
 * (counting deliveries per link) or, in the framed/ISO-test mode (+44 ==
 * 1), drain the completed SDUs (317624) to the host data hook 0x802804
 * (credits at 0x805add). Other links decode the PDU header (317a98),
 * build an SDU descriptor (status by mode +252 and the LLID), queue it
 * (31b9ac, 302664, 3250f4) and, on the last subevent of a missed link,
 * insert an empty/lost SDU when enabled (0x805a86 bit 1, 0x802a24[i]).
 * Completed SDUs from the link queue (+0x20) go to the HCI queue (+48)
 * or are reassembled (31ba78/31ba54) and passed to the host hook. Each
 * subevent ends with 31db9c. Links with deliveries are reported to the
 * hook 0x805b3c (count, handles, counts). Returns the stock r0. */
extern uintptr_t opencfw_em9305_dispatch_child_3174d8(uintptr_t object,
                                                     uint32_t tag);
extern uint32_t opencfw_em9305_dispatch_child_316f70(uintptr_t output,
    uintptr_t queue,uint32_t handle,uintptr_t buffer,uint32_t llid,
    uint32_t anchor,uint32_t timing);
extern uint32_t opencfw_em9305_ll_receive_buffer_release_31761c(uintptr_t buffer);
extern void opencfw_em9305_dispatch_child_31db9c(uintptr_t group,
                                                uint32_t event_counter);
extern uint32_t opencfw_em9305_dispatch_child_317a98(uintptr_t out,uintptr_t in);
extern uint32_t opencfw_em9305_dispatch_child_3250f4(uintptr_t context,
                                                    uintptr_t pdu);
extern uintptr_t opencfw_em9305_wsf_event_remove(uintptr_t queue,
                                                 uintptr_t out_u8);
extern uint32_t opencfw_em9305_ll_event_enqueue(uintptr_t queue,uint32_t handler,
                                                uintptr_t event);
extern uint32_t opencfw_em9305_wsf_critical_enter(void);
extern uint32_t opencfw_em9305_wsf_critical_exit(void);
extern uint32_t opencfw_em9305_dispatch_child_31ba78(uintptr_t reassembly,
    uint32_t handle,uint32_t counter,uintptr_t event);
extern uintptr_t opencfw_em9305_dispatch_child_31ba54(uintptr_t reassembly);
extern uint32_t opencfw_em9305_ll_received_decode_31bc7c(uintptr_t output,
                                                         uintptr_t input);
extern uint32_t opencfw_em9305_pal_hook_three(uint32_t value);
extern uint32_t opencfw_em9305_pal_hook_two(uint32_t value);
extern uint32_t opencfw_em9305_wsf_event_release(uintptr_t event);
extern uintptr_t opencfw_em9305_dispatch_child_317624(uintptr_t record);
extern uint32_t opencfw_em9305_dispatch_child_31b9ac(uintptr_t out,uintptr_t in);
extern uint32_t opencfw_em9305_dispatch_child_302664(uintptr_t output,
    uintptr_t input,uint32_t length);
extern uintptr_t opencfw_em9305_ll_receive_buffer_allocate_3175f0(void);
extern uint32_t opencfw_em9305_dispatch_event_send_31d128(uintptr_t record,
                                                          uint32_t status);

typedef uint32_t (*opencfw_em9305_mic_hook_31d6a4)(uintptr_t,uintptr_t);
typedef uint32_t (*opencfw_em9305_data_hook_31d6a4)(uint32_t,uint32_t,uint32_t,
                                                   uint32_t);
typedef uint32_t (*opencfw_em9305_report_hook_31d6a4)(uint32_t,uintptr_t,
                                                     uintptr_t);

/* SDU descriptor for 31b9ac, and the decoded SDU from 31bc7c (24 bytes). */
struct opencfw_em9305_sdu_31d6a4 {
    uint16_t handle;
    uint8_t status,flags;
    uint16_t length,reserved6;
    uint32_t anchor;
    uint16_t counter,sdu_length;
    uint8_t kind,reserved17[3];
    uint32_t data;
};

static inline uint32_t r8(uintptr_t a){return *(volatile uint8_t *)a;}
static inline uint32_t r16(uintptr_t a){return *(volatile uint16_t *)a;}
static inline uint32_t r32(uintptr_t a){return *(volatile uint32_t *)a;}
static inline void w8(uintptr_t a,uint32_t v){*(volatile uint8_t *)a=(uint8_t)v;}
static inline void w16(uintptr_t a,uint32_t v){*(volatile uint16_t *)a=(uint16_t)v;}
static inline void w32(uintptr_t a,uint32_t v){*(volatile uint32_t *)a=v;}

static void credit_add(int32_t delta)
{
    (void)opencfw_em9305_wsf_critical_enter();
    w8(0x805addu,r8(0x805addu)+(uint32_t)delta);
    (void)opencfw_em9305_wsf_critical_exit();
}

/* Pass one decoded SDU (event) to the host data hook and free it. */
static void deliver(uintptr_t handle_field,uintptr_t event,uint32_t anchor,
                    struct opencfw_em9305_sdu_31d6a4 *sdu)
{
    (void)opencfw_em9305_ll_received_decode_31bc7c((uintptr_t)sdu,event);
    uint32_t length=sdu->sdu_length;
    if(length==0u){
        (void)opencfw_em9305_pal_hook_three(0x16u);
        length=sdu->sdu_length;
    }
    uint32_t handle=r16(handle_field);
    ((opencfw_em9305_data_hook_31d6a4)(uintptr_t)r32(0x802804u))(handle,sdu->data,
                                                                length,anchor);
    (void)opencfw_em9305_pal_hook_two(0x16u);
    (void)opencfw_em9305_wsf_event_release(event);
    credit_add(1);
}

/* Route one completed SDU: to the HCI queue (+48) when +108, else through
 * the reassembly (+0x2c) to the host; counts complete-but-empty SDUs. */
static void route(uintptr_t link,uintptr_t event,uint32_t counter,
                  uint32_t anchor,uint16_t *count,
                  struct opencfw_em9305_sdu_31d6a4 *sdu)
{
    uintptr_t reassembly=link+0x2cu;
    uint32_t handle=r16(link+2u);
    if(r8(link+108u)!=0u){
        (void)opencfw_em9305_ll_event_enqueue(link+0x30u,(uint8_t)handle,event);
        w8(link+56u,r8(link+56u)+1u);
        credit_add(-1);
        return;
    }
    if(opencfw_em9305_dispatch_child_31ba78(reassembly,handle,counter,event)==0u){
        (void)opencfw_em9305_wsf_event_release(event);
        return;
    }
    uint32_t state=r8(reassembly);
    if(state==1u){
        uintptr_t done;
        while((done=opencfw_em9305_dispatch_child_31ba54(reassembly))!=0u)
            deliver(link+0x3au,done,anchor,sdu);
    }else if(state==0u){
        (*count)++;
    }
}

/* Drain the link's SDU queue (+0x20) through route(). */
static void drain(uintptr_t link,uint32_t counter,uint32_t anchor,
                  uint16_t *count,struct opencfw_em9305_sdu_31d6a4 *sdu,
                  uint8_t *handler)
{
    uintptr_t event;
    while((event=opencfw_em9305_wsf_event_remove(link+0x20u,
                                                 (uintptr_t)handler))!=0u)
        route(link,event,counter,anchor,count,sdu);
}

uint32_t opencfw_em9305_dispatch_child_31d6a4(uintptr_t group,uint32_t counter,
                                              uint32_t anchor)
{
    struct opencfw_em9305_sdu_31d6a4 sdu,decoded;
    volatile uint32_t event_counter[2];
    struct { uint16_t counts[4],handles[4]; } report;
    uint8_t header[4];
    uint8_t handler;
    uint32_t count=r8(group+0x18u);
    uint32_t base=counter*count;
    uint32_t reported=0u;
    for(uint32_t k=0u;k<4u;k++){
        report.counts[k]=0u;
        report.handles[k]=0u;
    }
    for(uint32_t i=0u;i<r8(group+52u);i++){
        uintptr_t link=r32(group+4u*i+0x38u);
        uint32_t slot=(uint8_t)reported;
        if(link==0u)continue;
        uint16_t *delivered=&report.counts[slot];
        for(uint32_t j=0u;j<count;j++){
            uintptr_t buffer=opencfw_em9305_dispatch_child_3174d8(link,(uint8_t)j);
            uint32_t low=j+base;
            w32(link+232u,(uintptr_t)event_counter);
            event_counter[0]=low;
            event_counter[1]=low<j;
            if(buffer!=0u){
                uintptr_t hook=r32(0x8051dcu);
                if(hook!=0u&&((opencfw_em9305_mic_hook_31d6a4)hook)(link+196u,
                                                                  buffer)==0u){
                    (void)opencfw_em9305_ll_receive_buffer_release_31761c(buffer);
                    (void)opencfw_em9305_dispatch_event_send_31d128(group,6u);
                    opencfw_em9305_dispatch_child_31db9c(group,counter);
                    return 0u;
                }
            }
            if(r8(r32(link+4u)+0x1eu)!=0u){
                if(buffer!=0u){
                    uint32_t mode=r8(link+44u);
                    if(mode==1u){
                        (void)opencfw_em9305_dispatch_child_316f70(link+0x10u,
                            link+0x30u,r16(link+2u),buffer,r8(buffer+1u),anchor,
                            r16(group+6u));
                        uintptr_t event;
                        while((event=opencfw_em9305_dispatch_child_317624(link))!=0u)
                            deliver(link+2u,event,anchor,&sdu);
                    }else if(mode==0u||r8(link+108u)!=0u){
                        *delivered=(uint16_t)(*delivered+
                            opencfw_em9305_dispatch_child_316f70(link+0x10u,
                                link+0x30u,r16(link+2u),buffer,r8(buffer+1u),
                                anchor,r16(group+6u)));
                    }
                    (void)opencfw_em9305_ll_receive_buffer_release_31761c(buffer);
                }
                opencfw_em9305_dispatch_child_31db9c(group,counter);
            }else if(buffer!=0u){
                w8(link+112u,j);
                (void)opencfw_em9305_dispatch_child_317a98((uintptr_t)header,buffer);
                uint32_t length=header[3];
                uint32_t mode=r8(link+252u);
                uintptr_t event=buffer-10u;
                sdu.anchor=anchor;
                sdu.status=0u;
                sdu.flags=0u;
                sdu.data=0u;
                sdu.kind=0u;
                sdu.length=(uint16_t)length;
                sdu.sdu_length=(uint16_t)length;
                sdu.counter=(uint16_t)event_counter[0];
                sdu.handle=(uint16_t)r16(link+2u);
                uint32_t llid=header[0];
                if(mode==1u){
                    sdu.status=llid==1u?1u:3u;
                }else if(mode==0u){
                    if(llid==1u){
                        sdu.flags=1u;
                    }else{
                        sdu.status=2u;
                        sdu.flags=1u;
                    }
                }else{
                    (void)opencfw_em9305_wsf_event_release(event);
                    count=r8(group+0x18u);
                    continue;
                }
                w8(link+252u,llid);
                uint32_t used=opencfw_em9305_dispatch_child_31b9ac(event,(uintptr_t)&sdu);
                (void)opencfw_em9305_dispatch_child_302664(used+event,buffer+2u,
                                                           sdu.sdu_length);
                if(opencfw_em9305_dispatch_child_3250f4(link+0x10u,event)!=0u)
                    drain(link,event_counter[0],anchor,delivered,&decoded,&handler);
                else{
                    count=r8(group+0x18u);
                    continue;
                }
                opencfw_em9305_dispatch_child_31db9c(group,counter);
            }else{
                w8(link+42u,1u);
                if(j+1u==r8(group+0x18u)){
                    if(opencfw_em9305_dispatch_child_3250f4(link+0x10u,0u)!=0u){
                        drain(link,event_counter[0],anchor,delivered,&sdu,
                              (uint8_t *)&decoded);
                    }else if((r8(0x805a86u)&2u)!=0u&&r8(0x802a24u+i)==0u){
                        uintptr_t lost=opencfw_em9305_ll_receive_buffer_allocate_3175f0();
                        if(lost!=0u){
                            sdu.anchor=anchor;
                            sdu.kind=2u;
                            sdu.length=0u;
                            sdu.status=2u;
                            sdu.flags=1u;
                            sdu.data=0u;
                            sdu.sdu_length=0u;
                            sdu.counter=(uint16_t)event_counter[0];
                            sdu.handle=(uint16_t)r16(link+2u);
                            lost-=10u;
                            (void)opencfw_em9305_dispatch_child_31b9ac(lost,
                                                                       (uintptr_t)&sdu);
                            route(link,lost,event_counter[0],anchor,delivered,
                                  &decoded);
                        }
                    }
                }
                opencfw_em9305_dispatch_child_31db9c(group,counter);
            }
            count=r8(group+0x18u);
        }
        if(*delivered!=0u){
            if(r8(link+108u)==0u&&r8(link+44u)!=1u){
                report.handles[slot]=(uint16_t)r16(link+2u);
                reported++;
            }else{
                *delivered=0u;
            }
        }
    }
    uintptr_t hook=r32(0x805b3cu);
    if(hook==0u)return count;
    if((uint8_t)reported==0u)return 0u;
    return ((opencfw_em9305_report_hook_31d6a4)hook)((uint8_t)reported,
        (uintptr_t)report.handles,(uintptr_t)report.counts);
}
