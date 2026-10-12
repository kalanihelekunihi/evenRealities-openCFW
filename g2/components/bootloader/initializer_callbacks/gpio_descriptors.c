/* Instruction-derived locked bootloader registrar430280 and required children.
 * No physical W1C, pin validity beyond stock guards, or callback ownership claim. */
#include "gpio_descriptors.h"
#define NI __attribute__((noinline))
#define R(a) (*(volatile uint32_t *)(uintptr_t)(a))
extern uint32_t opencfw_bl_critical_save(void);
extern uint32_t opencfw_bl_power_register_update(uint32_t,uint32_t);
extern uint32_t opencfw_bl_mode_register_update(uint32_t,uint32_t,uint32_t);
extern void opencfw_boot_context_nvic_enable(uint32_t);
extern const int16_t opencfw_boot_gpio_irqnums[4];
/* Stock 0x434190..0x43419b: three 32-bit product GPIO mode bases.  Native
 * registrar430280 reads each through its literal-pool pointer.  Type 2 then
 * replaces bits 6:7 with the descriptor's interrupt mode (BFI), so the
 * stored 0x93 does not force bit 7 for modes 0 and 1. */
__attribute__((section(".boot_gpio_mode_bases"), used))
const volatile uint32_t opencfw_boot_gpio_mode_bases[3] = {0x183u, 0x93u, 3u};
_Static_assert(sizeof(opencfw_boot_gpio_mode_bases) == 12u, "GPIO base size");
static void restore(uint32_t token) { __asm__ volatile("msr primask, %0" :: "r"(token) : "memory"); }
NI uint32_t opencfw_boot_gpio_mask_status(uint32_t channel,uint32_t enabled,uint32_t *mask) {
    uint32_t ch=(uint8_t)channel,en=(uint8_t)enabled;
    uint32_t token=opencfw_bl_critical_save();
    if(ch>1) { restore(token);return 6; }
    uint32_t enabled_mask[7];
    for(uint32_t i=0;i<7;i++) enabled_mask[i]=en ? R(0x40010530u+ch*0x70u+i*16u):0xffffffffu;
    for(uint32_t i=0;i<7;i++) mask[i]=R(0x40010534u+ch*0x70u+i*16u)&enabled_mask[i];
    restore(token);return 0;
}
NI uint32_t opencfw_boot_gpio_mask_clear(uint32_t channel,const uint32_t *mask) {
    if(!mask) return 6;
    uint32_t ch=(uint8_t)channel;
    if(ch<=2) {
        uint32_t token=opencfw_bl_critical_save();
        if(ch!=1) for(uint32_t i=0;i<7;i++) R(0x40010538u+i*16u)=mask[i];
        if(ch!=0) for(uint32_t i=0;i<7;i++) R(0x400105a8u+i*16u)=mask[i];
        restore(token);
    }
    (void)R(0x40010604u);return 0;
}
NI uint32_t opencfw_boot_gpio_callback_register(uint32_t channel,uint32_t pin,uint32_t callback,uint32_t argument) {
    uint32_t ch=(uint8_t)channel;
    if(ch>2)return 6;
    if(ch!=1) { R(0x20023600u+pin*4u)=callback;R(0x20023d00u+pin*4u)=argument; }
    if(ch!=0) { R(0x20023980u+pin*4u)=callback;R(0x20024080u+pin*4u)=argument; }
    return 0;
}
NI uint32_t opencfw_boot_gpio_interrupt_control(uint32_t channel,uint32_t control,const uint32_t *input) {
    uint32_t ch=(uint8_t)channel,op=(uint8_t)control;
    if(!input || op>3)return 6;
    uint32_t address=0,bit=0;
    if(op<2) {
        uint32_t pin=*input;if(pin>=224)return 5;
        address=0x40010530u+(pin>>5)*16u+(ch==1?0x70u:0);bit=1u<<(pin&31u);
    }
    uint32_t token=opencfw_bl_critical_save();
    if(op<2) {
        if(op==0) R(address)&=~bit;else R(address)|=bit;
        if(ch==2) {address+=0x70u;if(op==0)R(address)&=~bit;else R(address)|=bit;}
    } else {
        if(ch!=1) for(uint32_t i=0;i<7;i++) {uint32_t mask=((const volatile uint32_t *)input)[i];uint32_t a=0x40010530u+16u*i;if(op==2)R(a)&=~mask;else R(a)|=mask;}
        if(ch!=0) for(uint32_t i=0;i<7;i++) {uint32_t mask=((const volatile uint32_t *)input)[i];uint32_t a=0x400105a0u+16u*i;if(op==2)R(a)&=~mask;else R(a)|=mask;}
    }
    restore(token);return 0;
}
NI void opencfw_boot_gpio_priority(uint32_t interrupt,uint32_t priority) {
    uint32_t irq=interrupt&0xffffu;uint8_t value=(uint8_t)(priority<<4);
    if(!(irq&0x8000u)) *(volatile uint8_t *)(uintptr_t)(0xe000e400u+irq)=value;
    else *(volatile uint8_t *)(uintptr_t)(0xe000ed18u+(irq&15u)-4u)=value;
}
NI uint32_t opencfw_bl_descriptor_register(const opencfw_boot_gpio_descriptor *table,uint32_t count) {
    const volatile opencfw_boot_gpio_descriptor *rows=table;
    if(!table || !count)return 0xffffffffu;
    for(uint32_t i=0;i<count;i++) {
        if(rows[i].type==1) {
            (void)opencfw_bl_power_register_update(rows[i].pin,opencfw_boot_gpio_mode_bases[0]);
            (void)opencfw_bl_mode_register_update(rows[i].pin,rows[i].initial==1?1u:0u,0);
        } else if(rows[i].type==2) {
            uint32_t mode=(opencfw_boot_gpio_mode_bases[1]&~0xc0u)|
                          ((rows[i].interrupt_mode&3u)<<6);
            (void)opencfw_bl_power_register_update(rows[i].pin,mode);
            if(rows[i].interrupt_mode && rows[i].callback) {
                uint32_t pin=rows[i].pin,mask[7]={0};mask[pin>>5]=1u<<(pin&31u);
                (void)opencfw_boot_gpio_mask_status(0,1,mask);
                (void)opencfw_boot_gpio_mask_clear(0,mask);
                (void)opencfw_boot_gpio_callback_register(0,pin,rows[i].callback,0);
                (void)opencfw_boot_gpio_interrupt_control(0,1,&pin);
                uint32_t irq=(uint32_t)(int32_t)opencfw_boot_gpio_irqnums[rows[i].pin>>5];
                opencfw_boot_gpio_priority(irq,4);
                irq=(uint32_t)(int32_t)opencfw_boot_gpio_irqnums[rows[i].pin>>5];
                opencfw_boot_context_nvic_enable(irq);
            }
        } else if(rows[i].type==4) (void)opencfw_bl_power_register_update(rows[i].pin,opencfw_boot_gpio_mode_bases[2]);
    }
    return 0;
}
