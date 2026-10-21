/* Stock IOM publisher42c45a/service42c6f8 and directly required event/CQ
 * helpers. Volatile field accesses preserve callback-visible rereads. */
#include <stdint.h>
#include "context_claim.h"
#include "context_events.h"
_Static_assert(sizeof(struct opencfw_iom_descriptor)==32,"descriptor stride");
_Static_assert(sizeof(struct opencfw_iom_cq_status)==16,"status ABI");
#define W(p,o) (*(volatile uint32_t *)((uintptr_t)(p)+(o)))
#define B(p,o) (*(volatile uint8_t *)((uintptr_t)(p)+(o)))
#define NI __attribute__((noinline))
extern uint32_t opencfw_bl_critical_save(void);
extern void opencfw_boot_delay_us_math(uint32_t);
static uint32_t ring_index(uint32_t n,uint32_t size) {
    return size?n%size:n; /* UDIV0 when DIV_0_TRP is clear. */
}
NI void opencfw_boot_iom_descriptor_publish(void *h) {
    uint32_t module=W(h,4),next=W(h,0x850)+1;
    uintptr_t record=W(h,0x854)+(ring_index(next,W(h,0x848))<<5);
    uintptr_t iom=0x40050000u+(module<<12);
    W(iom,0x128)=W(record,0);W(iom,0x2c4)=W(record,4);
    W(iom,0x218)=0;W(iom,0x21c)=W(record,8);W(iom,0x220)=W(record,12);
    W(iom,0x218)=W(record,16);W(iom,0x120)=W(record,20);
}
NI uint32_t opencfw_boot_iom_error_classify(uint32_t module,uint32_t events) {
    uint32_t all=events|W(0x40050000u+(module<<12),0x204);
    if(all&0x6c) return 0x08000000u;
    if(all&0x200) return 0x08000001u;
    if(all&0x10) return 0x08000002u;
    return (all&0x4800)?1u:0u;
}
NI void opencfw_boot_iom_event_apply(void *h,uint32_t events) {
    uint32_t delay=6u*W(h,0x864),module=W(h,4);
    uintptr_t iom=0x40050000u+(module<<12);uint32_t enabled=W(iom,0x200);
    W(iom,0x200)=0;
    if(events&0x800) {
        if(W(iom,0x218)&2) {
            uint32_t remaining=W(iom,0x21c);
            while(remaining) {
                while(((W(iom,0x100)>>8)&255u)<4){}
                W(iom,0x10c)=0xdeadbeefu;
                if(remaining<5) break;
                remaining-=4;
            }
            while((W(iom,0x248)&6u)!=4u){}
        } else {
rx_busy:    if(!(W(iom,0x248)&2u)) goto idle;
rx_words:   if(((W(iom,0x100)>>16)&255u)<4) goto rx_busy;
            (void)W(iom,0x108);goto rx_words;
idle:       while((W(iom,0x248)&6u)!=4u){}
            while(((W(iom,0x100)>>16)&255u)!=0u) {
                while(((W(iom,0x100)>>16)&255u)>=4u) (void)W(iom,0x108);
            }
        }
    }
    if(events&0x210) {
        uint32_t reset=W(iom,0x388);
        while((W(iom,0x248)&6u)!=4u){}
        W(iom,0x11c)&=~0x10u;W(iom,0x110)&=~2u;
        W(iom,0x388)|=2u;opencfw_boot_delay_us_math(delay);
        W(iom,0x388)=reset;W(iom,0x110)|=2u;W(iom,0x11c)|=0x10u;
    }
    W(iom,0x208)=UINT32_MAX;W(iom,0x200)=enabled;
}
NI void opencfw_boot_iom_cq_refresh_indices(void *queue) {
    uint32_t saved=opencfw_bl_critical_save();
    uint32_t current=(W(W(W(queue,0x24),8),0)&255u)|(W(queue,0x20)&0xffffff00u);
    W(queue,0x1c)=current;
    if((int32_t)(W(queue,0x20)-W(queue,0x1c))<0) W(queue,0x1c)=W(queue,0x1c)-256u;
    W(queue,0xc)=W(W(W(queue,0x24),4),0);
    __asm__ volatile("msr primask, %0"::"r"(saved):"memory");
}
NI uint32_t opencfw_boot_iom_cq_status(void *queue,void *status) {
    if(!queue || (W(queue,0)&0x01ffffffu)!=0x01cdcdcdu) return 2;
    if(!status) return 6;
    opencfw_boot_iom_cq_refresh_indices(queue);
    W(status,0)=W(queue,0x1c);W(status,8)=W(queue,0x20);
    uint32_t unequal=W(queue,0x14)!=W(queue,0x10);
    W(status,4)=W(queue,0x20)-unequal;
    uint32_t value=W(W(W(queue,0x24),0x18),0);
    B(status,12)=(value&W(W(queue,0x24),0x1c))!=0;
    B(status,13)=(value&W(W(queue,0x24),0x24))!=0;
    B(status,14)=(value&W(W(queue,0x24),0x20))!=0;
    return 0;
}
NI uint32_t opencfw_boot_iom_cq_resume(void *queue) {
    if(!queue || (W(queue,0)&0x01ffffffu)!=0x01cdcdcdu) return 2;
    if(!(W(queue,0)&0x02000000u)) return 0;
    W(W(W(queue,0x24),0),0)&=~1u;
    uintptr_t command=W(W(W(queue,0x24),4),0);
    for(;;) {
        if((W(command,0)&~1u)==W(W(queue,0x24),8)) break;
        if(W(command,0)==W(W(queue,0x24),4)) command=W(command,4);
        else command+=8;
    }
    W(command,0)=W(W(queue,0x24),8);W(W(W(queue,0x24),4),0)=command;
    W(queue,0)&=~0x02000000u;
    return 0;
}
static void callback_slot(void *h,uint32_t slot,uint32_t status) {
    uint32_t fn=W(h,0x28+(slot<<2));
    if(fn) {
        uint32_t user=W(h,0x428+(slot<<2));fn=W(h,0x28+(slot<<2));
        ((void (*)(uint32_t,uint32_t))(uintptr_t)fn)(user,status);
        if(B(h,0x82c)!=2) W(h,0x28+(slot<<2))=0;
    }
}
NI uint32_t opencfw_boot_iom_event_service(void *h,uint32_t events) {
    if(!h || (W(h,0)&0x01ffffffu)!=0x01123456u) return 2;
    uint32_t module=W(h,4),result=0;uintptr_t iom=0x40050000u+(module<<12);
    if(B(h,0x83c)) {
        W(h,0x18)|=events;
        if((W(h,0x18)&0x801) && (!(W(iom,0x218)&1u)||(W(h,0x18)&0x4e7c))) {
            W(h,0x850)++;W(h,0x840)--;
            uintptr_t record=W(h,0x854)+(ring_index(W(h,0x850),W(h,0x848))<<5);
            if(W(record,24)) {
                uint32_t status=opencfw_boot_iom_error_classify(module,W(h,0x18));
                uint32_t user=W(record,28),fn=W(record,24);
                ((void (*)(uint32_t,uint32_t))(uintptr_t)fn)(user,status);
                W(record,24)=0;
            }
            if(W(h,0x18)&0x4a7c) {
                W(iom,0x218)&=~1u;W(iom,0x224)=0;
                opencfw_boot_iom_event_apply(h,W(h,0x18)&0x4a7c);
            }
            if(W(h,0x840)) {
                W(iom,0x224)=0;W(h,0x18)=0;
                opencfw_boot_iom_descriptor_publish(h);
            } else {
                B(h,0x83c)=0;W(iom,0x200)&=0xfffffbfeu;
                W(iom,0x238)=0x00800000u;
            }
        }
        return 0;
    }
    if(!W(h,0x24)) return 0;
    if(W(h,0x828)) {
        uint32_t status[4];result=opencfw_boot_iom_cq_status((void *)(uintptr_t)W(h,0x828),status);
        if(!result) {
            B(h,0x834)=0;
            while(W(h,0x1c)!=status[0]) {
                if(B(h,0x834)) break;
                W(h,0x1c)++;W(h,0x24)--;
                callback_slot(h,B(h,0x1c),0);
            }
            if(!B(h,0x834)&&(events&0x4a7c)) {
                W(h,0x1c)++;W(h,0x24)--;
                uint32_t slot=B(h,0x1c);
                if(W(h,0x28+(slot<<2))) {
                    uint32_t failure=opencfw_boot_iom_error_classify(module,events);
                    uint32_t user=W(h,0x428+(slot<<2)),fn=W(h,0x28+(slot<<2));
                    ((void (*)(uint32_t,uint32_t))(uintptr_t)fn)(user,failure);
                    if(B(h,0x82c)!=2) W(h,0x28+(slot<<2))=0;
                }
                W(iom,0x228)&=~1u;W(iom,0x218)&=~1u;W(iom,0x224)=0;
                opencfw_boot_iom_event_apply(h,events&0x4a7c);
                (void)opencfw_boot_iom_cq_resume((void *)(uintptr_t)W(h,0x828));
                if(W(h,0x24)) (void)opencfw_boot_iom_cq_enable(h);
            }
            if(!W(h,0x24)) (void)opencfw_boot_iom_cq_disable(h);
        }
    }
    if(!W(h,0x24)) {
        W(iom,0x200)=0;W(iom,0x208)=UINT32_MAX;W(iom,0x200)=W(h,0x14);
    }
    return result;
}
