/* SPDX-License-Identifier: BSD-3-Clause
 * Fixed-address C reconstruction of event/state callback bodies in the locked
 * G2 image. All device accesses are volatile; delay/power-control children are
 * explicit named test interfaces, not firmware providers.
 */
#include <stdint.h>

#define R32(a) (*(volatile uint32_t *)(uintptr_t)(a))
#define R8(a)  (*(volatile uint8_t *)(uintptr_t)(a))
extern void event_child_delay(uint32_t usec);
extern uint32_t opencfw_boot_control_critical_save(void);
static uint32_t replace(uint32_t old,uint32_t value,uint32_t mask,unsigned shift);

void state_adjust_42cdf8_native(uint32_t state)
{
    uint32_t base, target, delta=0U, result;
    if(R8(0x200271a8U)==0U||((R32(0x40021108U)>>4)&3U)!=3U)return;
    if(((R32(0x40021004U)>>18)&1U)!=0U&&R8(0x200271b4U)!=0U)delta=15U;
    target=(state==0U||state==1U)?10U:0U;
    base=R32(0x20027050U);
    if((int32_t)target-(int32_t)delta<1){
        result=delta-target+base;
        if(result>=128U)result=127U;
    }else{
        uint32_t difference=target-delta;
        result=base>difference?base-difference:0U;
    }
    R32(0x4002004cU)=replace(R32(0x4002004cU),result,0x7fU,0U);
}

void state_update_critical_42cea4_native(uint32_t state)
{
    uint32_t irq=opencfw_boot_control_critical_save();
    R8(0x200271b9U)=(uint8_t)state;
    if(R8(0x200271bcU)==0U)state_adjust_42cdf8_native((uint8_t)state);
    else R8(0x200271c0U)=1U;
    __asm volatile("msr primask, %0"::"r"(irq):"memory");
}

uint32_t power_predicate_41f3f0_native(void)
{
    uint32_t mode;
    if(R8(0x200271bfU)==0U)return 0U;
    mode=R32(0x40008800U);
    if((mode&15U)==0U||(mode&0x80000000U)!=0U)return 0U;
    return ((mode>>30)&1U)==0U;
}

uint32_t state_range_update_42ced8_native(float *arg)
{
    float x=arg[0]; unsigned bucket;
    if (!(x >= -273.0f) || x >= 1000.0f) bucket=3;
    else if (x < 35.0f) bucket=0;
    else if (x < 50.0f) bucket=1;
    else bucket=2;
    if(bucket==3U){arg[1]=0.0f;arg[2]=0.0f;return 1U;}
    if(bucket==0U){if(R8(0x200271acU)==0U)R8(0x200271c0U)=0U;
        state_update_critical_42cea4_native(0U);arg[1]=-273.0f;arg[2]=35.0f;}
    else if(bucket==1U){if(R8(0x200271acU)==0U)R8(0x200271c0U)=0U;
        state_update_critical_42cea4_native(1U);arg[1]=33.0f;arg[2]=50.0f;}
    else {if(R8(0x200271acU)==0U)R8(0x200271c0U)=1U;
        state_update_critical_42cea4_native(2U);arg[1]=48.0f;arg[2]=1000.0f;}
    return 0U;
}

uint32_t state_event_zero_42cfe0_native(void)
{
    if(R8(0x200271acU)!=0U){
        if(R8(0x200271b9U)==2U)R8(0x200271c0U)=1U;
        else {
            uint32_t mode=power_predicate_41f3f0_native();
            uint32_t pwr=R32(0x40008800U)&15U;
            if(mode==0U||pwr==0U||pwr>2U){
                uint32_t mask=R32(0x40008010U);
                unsigned i;
                for(i=0;i<16U;i++){
                    uint32_t v=R32(0x40008200U+i*0x20U);
                    if((v&1U)!=0U&&((mask>>i)&1U)!=0U){
                        uint32_t kind=(v&0x1ffffU)>>8;
                        if(kind<6U||(kind>=19U&&kind<=24U)||(kind>=256U&&kind<480U)){
                            R8(0x200271c0U)=1U;return 0U;
                        }
                    }
                }
                R8(0x200271c0U)=0U;
            }else R8(0x200271c0U)=1U;
        }
    }
    return 0U;
}

static uint32_t replace(uint32_t old,uint32_t value,uint32_t mask,unsigned shift)
{return (old&~(mask<<shift))|((value&mask)<<shift);}
static uint32_t replace_masked(uint32_t old,uint32_t keep,uint32_t value)
{return (old&keep)|value;}

uint32_t state_event_one_value_42d104_native(uint32_t value)
{
    volatile uint32_t *state=(volatile uint32_t *)(uintptr_t)0x40020080U;
    uint32_t mode=(R32(0x40021108U)&0x3fU)>>4;
    uint32_t n;
    if(mode==3U){
        if(R8(0x200271b4U)!=0U){R32(0x2002709cU)=(R32(0x40020080U)&0x3fffU)>>10;*state=(*state&0xffffc3ffU)|0x400U;}
        n=(((*state&0x3ffU)+12U)<0x400U)?12U:0x3ffU-(*state&0x3ffU);
        *state=(*state&0xfffffc00U)|((*state+n)&0x3ffU);
        R32(0x40020088U)=replace(R32(0x40020088U),5U,0x3fU,0U);event_child_delay(5U);
        if(R8(0x200271b4U)!=0U)R32(0x4002004cU)=replace(R32(0x4002004cU),(((R32(0x4002004cU)&0x7fU)+15U<128U)?(R32(0x4002004cU)&0x7fU)+15U:127U),0x7fU,0U);
        R32(0x40020380U)|=0x20000000U;R32(0x40020380U)|=0x10000000U;R32(0x40020380U)|=0x80000000U;R32(0x40020380U)|=0x40000000U;event_child_delay(10U);
        if(R8(0x200271b4U)!=0U){R32(0x40020044U)=replace(R32(0x40020044U),(((R32(0x40020044U)&0x7fU)+9U<128U)?(R32(0x40020044U)&0x7fU)+9U:127U),0x7fU,0U);R32(0x400201b0U)|=0x100U;}
        if(R8(0x200271b4U)==0U){R32(0x40020344U)=replace_masked(R32(0x40020344U),0xc1ffffffU,0x0c000000U);R32(0x40020344U)=replace_masked(R32(0x40020344U),0xffff07ffU,0x3000U);R32(0x4002034cU)=replace_masked(R32(0x4002034cU),0xc1ffffffU,0x0a000000U);R32(0x4002034cU)=replace_masked(R32(0x4002034cU),0xffff07ffU,0x2800U);R32(0x40020358U)=replace(R32(0x40020358U),value==1U?9U:13U,0x1fU,8U);R32(0x40020354U)=replace(R32(0x40020354U),value==1U?13U:19U,0x1fU,17U);}
        else {R32(0x40020344U)=replace_masked(R32(0x40020344U),0xc1ffffffU,0x14000000U);R32(0x40020344U)=replace_masked(R32(0x40020344U),0xffff07ffU,0x5000U);R32(0x4002034cU)=replace_masked(R32(0x4002034cU),0xc1ffffffU,0x10000000U);R32(0x4002034cU)=replace_masked(R32(0x4002034cU),0xffff07ffU,0x4000U);R32(0x40020358U)=replace(R32(0x40020358U),value==1U?16U:20U,0x1fU,8U);R32(0x40020354U)=replace(R32(0x40020354U),value==1U?20U:22U,0x1fU,17U);}
        R32(0x40020380U)&=~0x20000000U;R32(0x40020380U)&=~0x10000000U;R32(0x40020380U)&=~0x80000000U;R32(0x40020380U)&=~0x40000000U;
        *state=(*state&0xfffffc00U)|((*state-n)&0x3ffU);R32(0x40020088U)=replace(R32(0x40020088U),R8(0x200271b3U)==0U?1U:0U,0x3fU,0U);
    }else{
        R32(0x20027098U)=(*state&0x3fffU)>>10;*state=(*state&0xffffc3ffU)|0x800U;
        R32(0x200270a0U)=R32(0x40020088U)&0x3fU;n=(R32(0x40020088U)&0x3fU)+5U;if(n>63U)n=63U;R32(0x40020088U)=replace(R32(0x40020088U),n,0x3fU,0U);event_child_delay(15U);
    }
    return 0U;
}

uint32_t state_register_initialize_42d3bc_native(void)
{
    volatile uint32_t *state=(volatile uint32_t *)(uintptr_t)0x40020080U;uint32_t n;
    if(((R32(0x40021108U)&0x3fU)>>4)==3U){
        n=(((*state&0x3ffU)+12U)<0x400U)?12U:0x3ffU-(*state&0x3ffU);*state=(*state&0xfffffc00U)|((*state+n)&0x3ffU);
        R32(0x40020088U)=replace(R32(0x40020088U),5U,0x3fU,0U);event_child_delay(5U);
        R32(0x40020380U)|=0x20000000U;R32(0x40020380U)|=0x10000000U;R32(0x40020380U)|=0x80000000U;R32(0x40020380U)|=0x40000000U;event_child_delay(10U);
        R32(0x40020344U)=replace_masked(R32(0x40020344U),0xc1ffffffU,0x0c000000U);R32(0x40020344U)=replace_masked(R32(0x40020344U),0xffff07ffU,0x3000U);R32(0x4002034cU)=replace_masked(R32(0x4002034cU),0xc1ffffffU,0x0a000000U);R32(0x4002034cU)=replace_masked(R32(0x4002034cU),0xffff07ffU,0x2800U);R32(0x40020358U)=replace(R32(0x40020358U),7U,0x1fU,8U);R32(0x40020354U)=replace(R32(0x40020354U),10U,0x1fU,17U);
        if(R8(0x200271b4U)!=0U){uint32_t v=R32(0x4002004cU)&0x7fU;R32(0x4002004cU)=replace(R32(0x4002004cU),v<16U?0U:v-15U,0x7fU,0U);v=R32(0x40020044U)&0x7fU;R32(0x40020044U)=replace(R32(0x40020044U),v<10U?0U:v-9U,0x7fU,0U);*state=(*state&0xffffc3ffU)|((R32(0x2002709cU)&0xfU)<<10);R32(0x400201b0U)&=~0x100U;}
        *state=(*state&0xfffffc00U)|((*state-n)&0x3ffU);R32(0x40020088U)=replace(R32(0x40020088U),R8(0x200271b3U)==0U?1U:0U,0x3fU,0U);
        R32(0x40020380U)&=~0x20000000U;R32(0x40020380U)&=~0x10000000U;R32(0x40020380U)&=~0x80000000U;R32(0x40020380U)&=~0x40000000U;
    }else {R32(0x40020088U)=replace(R32(0x40020088U),R32(0x200270a0U)&0x3fU,0x3fU,0U);*state=(*state&0xffffc3ffU)|((R32(0x20027098U)&0xfU)<<10);}
    return 0U;
}

uint32_t state_event_dispatch_42d562_native(uint32_t selector,uint32_t unused,uint8_t *state)
{
    uint32_t result=0U;(void)unused;selector=(uint8_t)selector;
    if(selector==0U){if(state&&state[0]==2U)(void)state_event_zero_42cfe0_native();}
    else if(selector==2U)result=state_range_update_42ced8_native((float *)(void *)state);
    else if(selector==1U){if(state[0]==0U)result=state_register_initialize_42d3bc_native();else result=state_event_one_value_42d104_native(state[0]);}
    return result;
}

uint32_t state_event_flag_set_42d5c2_native(void){R8(0x200271b6U)=1U;return 0U;}
uint32_t state_event_finalize_42d5cc_native(void){uint32_t irq=opencfw_boot_control_critical_save();if(R8(0x200271b7U)!=0U){state_adjust_42cdf8_native(R8(0x200271b9U));R8(0x200271b7U)=0U;}R8(0x200271b6U)=0U;__asm volatile("msr primask, %0"::"r"(irq):"memory");return 0U;}

uint32_t autosw_initialize_42d63a_native(void){volatile uint32_t *p=(volatile uint32_t *)(uintptr_t)0x400211a0U;*p&=~0x1f00U;*p=(*p&~0xffff0000U)|(1000U<<16);R32(0x400211a8U)=0U;R32(0x400211a4U)=800U;R32(0x400211acU)=450U;R32(0x400211b4U)=600U;R32(0x400211bcU)=250U;*p&=~2U;*p=(*p>>1)<<1;return 0U;}
