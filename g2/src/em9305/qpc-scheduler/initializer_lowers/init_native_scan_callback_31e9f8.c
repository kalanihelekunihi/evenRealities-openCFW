#include <stdint.h>

/* Native 0x31e9f8..0x31eac6: hand the scanner's current report (scanner =
 * object +44, report = scanner +100) to the host. Only in scanner states
 * 0, 1, 2 or 6 (+184) and while the queued-report count (0x805b01) is below
 * the configured limit ((*0x805cac)+14), and only if a replacement report
 * of the scanner's size (+150) can be allocated. The report gets the event
 * type (+152), a changed-address flag (address type +186/+187 or the
 * address pairs +168/+172 and +176/+180 differ), the 16-bit data id (+156),
 * and bytes +158/+159; it is queued on the direct (0x805000, post 0x100)
 * or the extended (0x805008, post 0x200) queue as selected by +189 and the
 * task at 0x805b18 is signalled. The new report replaces the old one. */
extern uintptr_t opencfw_em9305_wsf_event_allocate(uint32_t length);
extern uint32_t opencfw_em9305_ll_event_enqueue(uintptr_t queue,uint32_t handler,
                                                uintptr_t event);
extern uint32_t opencfw_em9305_wsf_event_post(uint32_t task,uint32_t event);
extern void opencfw_em9305_scan_counter_up_316968(void);

static inline uint32_t r8(uintptr_t a){return *(volatile uint8_t *)a;}
static inline uint32_t r32(uintptr_t a){return *(volatile uint32_t *)a;}
static inline void w8(uintptr_t a,uint32_t v){*(volatile uint8_t *)a=(uint8_t)v;}

void opencfw_em9305_scan_callback_31e9f8(uintptr_t object)
{
    uintptr_t scanner=r32(object+44u);
    uint32_t state=r8(scanner+184u);
    if(state>=7u||((0x47u>>state)&1u)==0u)return;
    uintptr_t config=r32(0x805cacu);
    if(r8(0x805b01u)>=r8(config+14u))return;
    uintptr_t replacement=opencfw_em9305_wsf_event_allocate(r8(scanner+150u));
    if(replacement==0u)return;
    w8(r32(scanner+100u)+39u,r8(scanner+152u));
    uint32_t changed=1u;
    if(r8(scanner+187u)==r8(scanner+186u)){
        uint32_t a=r32(scanner+172u),b=r32(scanner+180u);
        uint32_t c=r32(scanner+168u),d=r32(scanner+176u);
        changed=((b^a)|(d^c))!=0u;
    }
    w8(r32(scanner+100u)+40u,changed);
    w8(r32(scanner+100u)+41u,r32(scanner+156u));
    w8(r32(scanner+100u)+42u,r32(scanner+156u)>>8);
    w8(r32(scanner+100u)+43u,*(volatile uint16_t *)(scanner+158u));
    w8(r32(scanner+100u)+44u,r8(scanner+159u));
    uint32_t extended=r8(scanner+189u);
    uintptr_t report=r32(scanner+100u);
    uint32_t signal;
    if(extended!=0u){
        (void)opencfw_em9305_ll_event_enqueue(0x805000u,0u,report);
        signal=0x100u;
    }else{
        (void)opencfw_em9305_ll_event_enqueue(0x805008u,0u,report);
        signal=0x200u;
    }
    (void)opencfw_em9305_wsf_event_post(r8(0x805b18u),signal);
    opencfw_em9305_scan_counter_up_316968();
    *(volatile uint32_t *)(scanner+100u)=replacement;
}
