#include <stdint.h>

/* Native 0x32b9a4..0x32bb3c. Prepared whole-body candidate; product callback
 * and table/loop paths require independent native review before selection. */
extern uint32_t opencfw_em9305_init_callback_child_3246dc(uintptr_t);
extern uint32_t opencfw_em9305_init_callback_child_3246c0(uintptr_t);
extern uint32_t opencfw_em9305_associated_cleanup_3266d0(uintptr_t,uint32_t);
extern uint32_t opencfw_em9305_associated_report_30e89c(uint32_t,uint32_t,uint32_t,uint32_t,uint32_t);
extern uint32_t opencfw_em9305_associated_channel_pending_327af4(uintptr_t);
extern uint32_t opencfw_em9305_associated_channel_seed_324c98(uintptr_t,uint32_t);
extern uint32_t opencfw_em9305_associated_schedule_insert_312da4(uintptr_t,uintptr_t);
extern uint32_t opencfw_em9305_pal_random_step(void);
extern uint32_t opencfw_em9305_crc_update_304678(uint32_t,uint32_t,uintptr_t);
extern uint32_t opencfw_em9305_ll_mask_count_30c414(uint32_t,uint32_t);
extern uint32_t opencfw_em9305_associated_cycle_event_30e858(uint32_t,uint32_t,uint32_t);

static uint32_t r32(uintptr_t a){return *(volatile uint32_t *)a;}
static uint32_t r16(uintptr_t a){return *(volatile uint16_t *)a;}
static uint32_t r8(uintptr_t a){return *(volatile uint8_t *)a;}
static void w32(uintptr_t a,uint32_t v){*(volatile uint32_t *)a=v;}
static void w16(uintptr_t a,uint32_t v){*(volatile uint16_t *)a=(uint16_t)v;}
static void w8(uintptr_t a,uint32_t v){*(volatile uint8_t *)a=(uint8_t)v;}
#if defined(OPENCFW_EM9305_HOST_FIXTURE)
/* Test-only small-positive branch model, not an ARC DSP equivalence claim. */
static uint32_t native_mpywhl(uint32_t a,uint32_t b)
{return (uint32_t)(a*(uint16_t)b);}
#else
static uint32_t native_mpywhl(uint32_t a,uint32_t b)
{uint32_t out;__asm__ volatile("mpywhl %0,%1,%2":"=r"(out):"r"(a),"r"(b):"r58","r59","memory");return out;}
#endif

uint32_t opencfw_em9305_associated_cycle_callback_32b9a4(uintptr_t object)
{
    uintptr_t packet=r32(object+44u);
    uintptr_t record=r32(object+36u);
    w16(packet+224u,0u);
    /* 3246dc BL.D computes record+788 into a saved register; no memory access. */
    (void)opencfw_em9305_init_callback_child_3246dc(packet);
    if(r8(record+698u)!=0u)return opencfw_em9305_associated_cleanup_3266d0(record,3u);
    (void)opencfw_em9305_init_callback_child_3246c0(packet);
    uint32_t power=r8(packet+15u);
    if(power==0u)power=r8(0x805bedu);
    w8(packet+14u,power);
    if(r8(0x805beeu)!=0u){
        uint32_t stamp=r32(object+8u),interval_for_report=r32(record+700u);
        uint32_t count_for_report=r16(record+376u),id=r8(record+1u);
        (void)opencfw_em9305_associated_report_30e89c(id,count_for_report,0u,interval_for_report,stamp);
    }
    uint32_t count=r8(record+788u); /* 32b9fa R1 from cycle+0. */
    uint32_t scheduled=r32(record+792u);
    uint32_t interval=r32(record+700u);
    uint32_t scaled=native_mpywhl(scheduled,count);
    uint32_t remainder=interval-scaled;
    w32(object+20u,interval);
    for(;;){ /* Native failure edge 32ba8a -> 32ba20. */
        uint32_t old_index=r8(record+799u);
        uint32_t width=r8(record+788u);
        uint32_t next=(old_index+1u)&127u;
        w8(record+799u,old_index+1u); /* BRNE.D delay store. */
        uint32_t old_time;
        uint32_t next_time;
        if(next==width){
            uint32_t old_count=r16(record+376u);
            uint32_t fresh_scaled=r32(record+792u);
            old_time=r32(object+8u);
            w8(record+799u,0u);
            w16(record+376u,old_count+1u);
            next_time=remainder+fresh_scaled+old_time;
        }else{
            uint32_t fresh_scaled=r32(record+792u);
            old_time=r32(object+8u);
            next_time=fresh_scaled+old_time;
        }
        w32(record+800u,next_time);
        w32(object+8u,next_time);
        (void)opencfw_em9305_associated_channel_pending_327af4(record);
        uint32_t channel_count=r8(record+799u);
        uint32_t fresh_counter=r16(record+376u);
        uint32_t channel=opencfw_em9305_associated_channel_seed_324c98(record+720u,(uint16_t)(channel_count^fresh_counter));
        uintptr_t destination=r32(record+2812u);
        uint32_t updated_index=r8(record+799u);
        uint32_t expected=r8(destination+76u);
        w8(record+697u,channel); /* BRNE.D delay slot. */
        if((updated_index&127u)==expected)w8(destination+77u,1u);
        uint32_t inserted=opencfw_em9305_associated_schedule_insert_312da4(object,0u);
        if(inserted!=0u)break;
    }
        uint32_t selected_index=r8(record+799u)&127u;
        uintptr_t choices=r32(record+1160u);
        uint32_t selected=r8(choices+selected_index+0xf0cu);
        w8(packet+261u,0u);
        uint32_t live_result=0u;
        if(selected!=255u)live_result=r8(choices+(selected<<8u));
        if(selected==255u || live_result==0u){
            w16(record+1144u,0u);
            for(;;){
                uint32_t random=opencfw_em9305_pal_random_step();
                uint32_t crc=opencfw_em9305_crc_update_304678(random,0u,0u);
                uint32_t reference=r16(record+64u);
                w16(record+706u,crc);
                if(((reference^crc)&4095u)!=0u){live_result=crc;break;}
            }
            selected_index=r8(record+799u)&127u; /* Fallback reload 32bad4. */
        }
        if(selected_index!=0u)return live_result;
        choices=r32(record+1160u);
        uintptr_t bitmap=choices+0xf08u;
        uint32_t high=r32(bitmap),low=r32(bitmap-4u);
        uint32_t first_count=opencfw_em9305_ll_mask_count_30c414(low,high);
        uint32_t limit=r8(record+788u);
        uint32_t final_count=limit;
        if(first_count<limit){
            bitmap=r32(record+1160u)+0xf08u;
            high=r32(bitmap);low=r32(bitmap-4u);
            final_count=opencfw_em9305_ll_mask_count_30c414(low,high);
        }
        if(final_count!=0u){
            uintptr_t cursor=r32(record+1160u)+0xf0cu; /* Fresh 32bb10. */
            for(uint32_t index=0u;index<final_count;++index){
                uint32_t candidate=r8(cursor); /* LDB.AB reads old cursor. */
                cursor+=1u;
                if(candidate!=255u)return candidate;
            }
        }
        uintptr_t destination=r32(record+2812u);
        uint32_t id=r8(record+1u);
        w8(destination+78u,0u);
        w8(destination+79u,final_count);
        return opencfw_em9305_associated_cycle_event_30e858(id,0u,final_count);
}
