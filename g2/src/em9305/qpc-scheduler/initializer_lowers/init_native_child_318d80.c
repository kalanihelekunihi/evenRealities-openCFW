#include <stdint.h>

/* Native 0x318d80..0x318eda: path-loss / power-control monitor for the
 * connection record. Runs only when monitoring is enabled for the link
 * (bit 1 of +548) and globally (bit 7 of 0x805a85); otherwise the zone
 * byte +770 is cleared. Pending averages (+780 samples summing to +784)
 * are flushed into the sample filter (325284 on +788). After at least
 * four samples (+793) the filtered RSSI (3252a0) is checked against the
 * window +778..+779 (state +776, hits +777); the power step proposed by
 * 31b32c for the current PHY entry (+557 + PHY index, adjusted for coded
 * S2) is limited to the entry's maximum (+561), and a non-zero step is
 * reported to the LL task (message 0x2801 with handle, step and PHY)
 * unless a procedure (state 0x1c at +635 or bit 4 of +647) is running.
 * The sample count is then reset. */
extern void opencfw_em9305_child_325284(uintptr_t filter,uint32_t value);
extern int32_t opencfw_em9305_child_3252a0(uintptr_t samples);
extern int32_t opencfw_em9305_child_31b32c(uintptr_t range,int32_t target,
                                           uint32_t allow_up,uint32_t force);
extern uintptr_t opencfw_em9305_wsf_event_allocate(uint32_t length);
extern uint32_t opencfw_em9305_wsf_task_message_send(uint32_t task,
                                                     uintptr_t message);

static inline uint32_t r8(uintptr_t a){return *(volatile uint8_t *)a;}
static inline int32_t s8(uintptr_t a){return *(volatile int8_t *)a;}
static inline void w8(uintptr_t a,uint32_t v){*(volatile uint8_t *)a=(uint8_t)v;}

void opencfw_em9305_child_318d80(uintptr_t record)
{
    uintptr_t filter=record+788u;
    if((r8(record+548u)&2u)==0u||(r8(0x805a85u)&0x80u)==0u){
        w8(record+770u,0u);
        return;
    }
    uint32_t phy=r8(record+77u);
    uint32_t coded=0u;
    if(phy==3u)coded=r8(record+78u)==1u;
    uint32_t samples=*(volatile uint16_t *)(record+780u);
    if(samples!=0u){
        int32_t average=*(volatile int32_t *)(record+784u)/(int32_t)samples;
        opencfw_em9305_child_325284(filter,(uint32_t)(int32_t)(int8_t)average);
        *(volatile uint16_t *)(record+780u)=0u;
        *(volatile uint32_t *)(record+784u)=0u;
    }
    if(r8(record+793u)<4u)return;
    int32_t rssi=opencfw_em9305_child_3252a0(record+788u);
    if(r8(record+776u)==0u){
        if(!(s8(record+778u)<rssi)&&rssi>=s8(record+779u))return;
        w8(record+776u,1u);
    }
    uint32_t entry_index=coded+phy;
    uintptr_t entry=record+(uint8_t)entry_index+557u;
    uint32_t caps=r8(entry);
    int32_t step=opencfw_em9305_child_31b32c(record+776u,rssi,(caps&2u)==0u,
                                             (caps&1u)==0u);
    uint32_t limit=r8(entry+4u);
    if(limit!=255u&&-step>(int32_t)limit)step=-(int32_t)limit;
    int32_t low=s8(record+778u);
    if(low<rssi||rssi<s8(record+779u)){
        uint32_t hits=r8(record+777u);
        w8(record+777u,hits+1u);
    }
    uint32_t clear=1u;
    if((caps&3u)==3u||(uint8_t)step!=0u){
        int32_t span=(low-s8(record+779u))/4;
        if(r8(record+777u)<(uint8_t)span)clear=0u;
    }
    if(clear)*(volatile uint16_t *)(record+776u)=0u;
    if((uint8_t)step==0u)return;
    if(r8(record+635u)==0x1cu)return;
    if((r8(record+647u)&0x10u)!=0u)return;
    uintptr_t message=opencfw_em9305_wsf_event_allocate(6u);
    if(message!=0u){
        *(volatile uint16_t *)(message+2u)=0x2801u;
        uintptr_t base=*(volatile uint32_t *)0x805c70u;
        w8(message+5u,entry_index);
        w8(message+4u,(uint32_t)step);
        int32_t handle=(int32_t)(record-base)/912;
        uint32_t task=r8(0x805b18u);
        *(volatile uint16_t *)message=(uint8_t)handle;
        (void)opencfw_em9305_wsf_task_message_send(task,message);
    }
    w8(record+793u,0u);
}
