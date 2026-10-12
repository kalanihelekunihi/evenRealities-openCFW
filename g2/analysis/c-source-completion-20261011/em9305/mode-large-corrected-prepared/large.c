#include <stdint.h>

/* Native 0x31bd78..0x31c0dc, one connected callback body. The label names
 * identify native basic blocks; no interior address is exported as a fake
 * function. Three callback columns at 0x334ba4/+4/+8/+12/+16 remain genuine
 * initialized product-data contracts. */
extern uint32_t opencfw_em9305_mode_selector_31affc(uintptr_t context,
                                                     uint32_t event);
extern uint32_t opencfw_em9305_mode_guard_31a988(uintptr_t context,
                                                   uint32_t selector,
                                                   uint32_t category);
extern uint32_t opencfw_em9305_mode_reject_3233b4(uintptr_t context,
                                                    uint32_t selector);
extern uint32_t opencfw_em9305_mode_done_3234ec(uintptr_t context,
                                                  uint32_t selector);
extern uint32_t opencfw_em9305_phy_reject_32698c(uintptr_t,uint32_t,uint32_t);
extern uint32_t opencfw_em9305_phy_timer_start_32c7e4(uintptr_t);
extern uint32_t opencfw_em9305_phy_finish_32c810(uintptr_t);
extern uint32_t opencfw_em9305_phy_complete_32c818(uintptr_t);

static uint32_t read32(uintptr_t p){return *(volatile uint32_t *)p;}
static uint8_t read8(uintptr_t p){return *(volatile uint8_t *)p;}
static void write32(uintptr_t p,uint32_t v){*(volatile uint32_t *)p=v;}
static void write8(uintptr_t p,uint8_t v){*(volatile uint8_t *)p=v;}
static uint32_t bit(uint32_t word,uint32_t n)
{return n<32u?(word>>n)&1u:0u;}
static uint32_t call_column(uintptr_t context,uint32_t selector,uint32_t offset)
{
    uintptr_t location=0x334ba4u+20u*selector+offset;
    uintptr_t code=read32(location);
    return ((uint32_t (*)(uintptr_t,uintptr_t))code)(context,code);
}

uint32_t opencfw_em9305_mode_event_31bd78(uintptr_t context,uint32_t event)
{
    uint32_t category=0u,selector=0u,delta=event-12u;
    uintptr_t mode=context+628u;
    if(delta<24u) {
        if(bit(0x00e98c00u,delta)!=0u) goto select_mode;
        if(delta==0u) goto event_twelve;
        if(delta==1u){category=4u;goto select_mode;}
    }
    delta=event-102u;
    if(delta>=11u) return 0u;
    if(bit(0x77u,delta)!=0u){category=1u;goto select_mode;}
    if(delta==8u){category=6u;goto select_mode;}
    if(delta!=10u) return 0u;
    uint32_t first=read32(context+656u);
    uint32_t second=read32(context+652u);
    category=(first|second)==0u?1u:2u;
    goto select_mode;

event_twelve:
    {
        uint32_t code=read8(0x802818u)-1u;
        if(code>41u) return 0u;
        category=4u;
        switch(code) {
        case 0:case 7:case 13:case 19:case 28:
            goto select_mode;
        case 1:case 11:case 24:case 27:case 39:case 40:case 41:
            category=3u;goto select_mode;
        case 6:case 12:case 16:
            category=7u;goto select_mode;
        case 8:case 20:case 29:
            category=5u;goto select_mode;
        default:return 0u;
        }
    }

select_mode:
    selector=opencfw_em9305_mode_selector_31affc(context,event);
    if(selector>=10u) return 0u;
    mode=context+628u;
    uint32_t state=read8(mode-8u);
    if(state==1u) goto mode_active;
    if(state!=0u) goto finish_one;
    if((uint32_t)(category-2u)>=3u) goto mode_inactive;
    if(opencfw_em9305_mode_guard_31a988(context,selector,category)==0u)
        goto phy_reject_and_finish;
    if(category!=2u) (void)call_column(context,selector,8u);
    if(selector>=2u) {
        (void)call_column(context,selector,12u);
        (void)opencfw_em9305_phy_finish_32c810(context);
        return 1u;
    }
    write8(mode-8u,1u);
    write8(mode,0u);
    write8(mode+7u,(uint8_t)selector);
    write8(mode-2u,1u);
    goto finish_one;

mode_active:
    if(category>7u) goto finish_one;
    switch(category) {
    case 0:case 1:goto active_start;
    case 2:goto finish_one;
    case 3:goto active_three;
    case 4:goto active_four;
    case 5:goto active_five;
    case 6:goto active_six;
    case 7:goto active_seven;
    }
    goto finish_one;

active_start:
    if(opencfw_em9305_mode_guard_31a988(context,selector,category)==0u)
        goto reject_and_finish;
    if(category==0u) {
        uint32_t flags=read32(context+636u);
        write32(context+636u,flags|(1u<<selector));
    }
    if(read8(mode+7u)!=selector) {
        uint32_t flags=read32(context+644u);
        write32(context+644u,flags|(1u<<selector));
    }
    if(category==0u && bit(780u,selector)==0u)
        (void)call_column(context,selector,0u);
    if(selector!=0u) return 1u;
    {
        uint32_t flags=read32(context+652u);
        uint32_t pending=read32(context+644u);
        uintptr_t callback=read32(0x334ba8u); /* native load before writes */
        write32(context+652u,flags|1u);
        write32(context+648u,0u);
        write32(context+644u,pending&~1u);
        (void)((uint32_t (*)(uintptr_t,uintptr_t))callback)(context,callback);
    }
    goto finish_one;

mode_inactive:
    if(category!=0u && category!=1u) goto finish_one;
    if(category==0u) {
        uint32_t flags=read32(context+636u);
        write32(context+636u,flags|(1u<<selector));
        if(bit(780u,selector)==0u)(void)call_column(context,selector,0u);
    }
    if(opencfw_em9305_mode_guard_31a988(context,selector,category)==0u)
        goto reject_and_finish;
    (void)call_column(context,selector,4u);
    (void)opencfw_em9305_phy_timer_start_32c7e4(context);
    write8(mode-2u,1u);
    write8(mode+7u,(uint8_t)selector);
    write8(mode-8u,1u);
    goto finish_one;

active_three:
    if(read8(mode+7u)==selector) goto active_shared;
    if(opencfw_em9305_mode_guard_31a988(context,selector,3u)==0u)
        goto finish_one;
    (void)call_column(context,selector,8u);
    goto mark_complete_bit;

active_four:
    (void)call_column(context,selector,8u);
    if(read8(mode+7u)==19u) goto mark_complete_bit;
    if(selector>=2u) {
        if(opencfw_em9305_mode_guard_31a988(context,selector,4u)==0u) {
            (void)opencfw_em9305_phy_reject_32698c(context,26u,0u);
        } else {
            (void)call_column(context,selector,12u);
        }
        return 1u;
    }
    goto mark_complete_bit;

active_five:
    if(read8(mode+7u)!=selector) goto active_clear_pending;
active_shared:
    if(bit(867u,selector)==0u)(void)call_column(context,selector,16u);
active_six:
    (void)opencfw_em9305_mode_done_3234ec(context,selector);
    goto active_finalize;
active_seven:
    (void)opencfw_em9305_mode_reject_3233b4(context,selector);
active_finalize:
    (void)opencfw_em9305_phy_complete_32c818(context);
    write8(mode-2u,0u);
    write8(mode+7u,255u);
    write8(mode-8u,0u);
    (void)opencfw_em9305_phy_finish_32c810(context);
    goto finish_one;

active_clear_pending:
    {
        uint32_t pending=read32(context+644u);
        if(bit(pending,selector)==0u) goto finish_one;
        uint8_t delayed=read8(mode+3u);
        write32(context+648u,0u);
        write32(context+644u,pending&~(1u<<selector));
        if(delayed!=0u) write8(mode+3u,0u);
        if(bit(867u,selector)==0u)(void)call_column(context,selector,16u);
        (void)opencfw_em9305_mode_done_3234ec(context,selector);
    }
    goto finish_one;

mark_complete_bit:
    write32(context+652u,read32(context+652u)|(1u<<selector));
    goto finish_one;
reject_and_finish:
    (void)opencfw_em9305_mode_reject_3233b4(context,selector);
    goto finish_one;
phy_reject_and_finish:
    (void)opencfw_em9305_phy_reject_32698c(context,26u,0u);
    goto finish_one;
finish_one:
    if(selector==0u) {
        uint32_t previous=read8(mode+7u);
        if(previous==0u || bit(read8(mode+24u),0u)!=0u)
            write8(context+1u,3u);
    }
    return 1u;
}
