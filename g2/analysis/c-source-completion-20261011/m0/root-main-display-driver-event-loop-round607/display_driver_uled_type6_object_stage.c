/* Apollo type-6 object create/configure/start/wait providers and hardware
 * helpers 0x5398e0, 0x539a40, 0x539994, 0x539b56, 0x480058, 0x44b0b6.
 * Candidate; fixed SRAM and MMIO addresses remain integration gates.
 */
#include <stdint.h>
extern uint32_t display_driver_uled_irq_save_473940(void);
extern uint32_t display_driver_uled_delay_4807a0(uint32_t);
extern uint32_t display_driver_uled_poll_480826(uint32_t,volatile uint32_t *,
                                                  uint32_t,uint32_t,uint32_t);

uint32_t display_driver_uled_control_shutdown_480058(void) {
    uint32_t prior=display_driver_uled_irq_save_473940();
    if ((*(volatile uint32_t *)(uintptr_t)0x4002000cu & 0xffu)>=0x22u) {
        volatile uint32_t *other=(volatile uint32_t *)(uintptr_t)0x400201b0u;
        *other=*other & ~0x00200000u;
        (void)display_driver_uled_delay_4807a0(1u);
    }
    volatile uint32_t *control=(volatile uint32_t *)(uintptr_t)0x400204d8u;
    *control=*control & ~0x80000000u;
    *control=*control & ~0x40000000u;
    __asm__ volatile("msr primask, %0" :: "r"(prior) : "memory");
    (void)display_driver_uled_delay_4807a0(5u);
    return 0u;
}

void display_driver_uled_output_enable_44b0b6(uint32_t value) {
    uint32_t prior=display_driver_uled_irq_save_473940();
    volatile uint32_t *control=(volatile uint32_t *)(uintptr_t)0x40008858u;
    *control=(*control & ~0x40u)|(((uint8_t)value & 1u)<<6u);
    __asm__ volatile("msr primask, %0" :: "r"(prior) : "memory");
}

uint32_t display_driver_uled_object_create_5398e0(uint32_t slot,uint32_t *out) {
    if(slot!=0u)return 5u;
    if(out==0)return 6u;
    volatile uint32_t *object=(volatile uint32_t *)(uintptr_t)0x200740f4u;
    if((object[0]&0x01000000u)!=0u)return 7u;
    object[0]=object[0]|0x01000000u;
    object[0]=(object[0]&0xff000000u)|0x00504c30u;
    object[1]=slot;
    (void)display_driver_uled_control_shutdown_480058();
    *out=(uint32_t)(uintptr_t)object;
    return 0u;
}

uint32_t display_driver_uled_object_config_539a40(uint32_t object_addr,
                                                    const volatile void *config) {
    if(object_addr==0u)return 2u;
    volatile uint32_t *object=(volatile uint32_t *)(uintptr_t)object_addr;
    if((object[0]&~0xfe000000u)!=0x01504c30u)return 2u;
    (void)object[1];
    if((object[0]&0x02000000u)!=0u)return 7u;
    const volatile uint8_t *bytes=(const volatile uint8_t *)config;
    if(bytes[3]>=0x40u)return 6u;
    uint16_t width=*(const volatile uint16_t *)(const volatile void *)(bytes+6);
    if(bytes[2]==1u) {
        if((uint32_t)(width-4u)>=0x3bdu)return 6u;
    } else if((uint32_t)(width-10u)>=0x57u)return 6u;
    if(bytes[4]>=8u || bytes[5]>=8u || bytes[4]<bytes[5])return 6u;

    volatile uint32_t *control=(volatile uint32_t *)(uintptr_t)0x400204d8u;
    volatile uint32_t *pixels=(volatile uint32_t *)(uintptr_t)0x400204dcu;
    volatile uint32_t *timing=(volatile uint32_t *)(uintptr_t)0x400204e0u;
    *control=(*control&~0x200u)|((uint32_t)(bytes[1]&1u)<<9u);
    *control=(*control&~0x20u)|((uint32_t)(bytes[0]&1u)<<5u);
    *control=(*control&~0x8u)|((uint32_t)(bytes[2]&1u)<<3u);
    uint32_t pixel_word=*(const volatile uint32_t *)(const volatile void *)(bytes+8);
    *pixels=(*pixels&0xff000000u)|(pixel_word&0x00ffffffu);
    *timing=(*timing&~0x0fff0000u)|(((uint32_t)width&0xfffu)<<16u);
    *timing=(*timing&~0x3fu)|(uint32_t)(bytes[3]&0x3fu);
    *timing=(*timing&~0x7000u)|((uint32_t)(bytes[4]&7u)<<12u);
    *timing=(*timing&~0x700u)|((uint32_t)(bytes[5]&7u)<<8u);
    display_driver_uled_output_enable_44b0b6(bytes[0]);
    *control=*control & ~0x10u;
    *control=*control | 1u;
    *control=*control & ~2u;
    *control=*control & ~4u;
    return 0u;
}

uint32_t display_driver_uled_object_start_539994(uint32_t object_addr) {
    if(object_addr==0u)return 2u;
    volatile uint32_t *object=(volatile uint32_t *)(uintptr_t)object_addr;
    if((object[0]&~0xfe000000u)!=0x01504c30u)return 2u;
    (void)object[1];
    if((object[0]&0x02000000u)!=0u)return 0u;
    volatile uint32_t *status=(volatile uint32_t *)(uintptr_t)0x40020060u;
    if((*status&0x00080000u)==0u || (*status&0x00040000u)==0u ||
       (*status&0x00020000u)==0u || (*status&0x00010000u)==0u)return 7u;
    volatile uint32_t *control=(volatile uint32_t *)(uintptr_t)0x400204d8u;
    *control=*control|0x20000000u;
    object[0]=object[0]|0x02000000u;
    return 0u;
}

uint32_t display_driver_uled_object_wait_539b56(uint32_t object_addr) {
    if(object_addr==0u)return 2u;
    volatile uint32_t *object=(volatile uint32_t *)(uintptr_t)object_addr;
    if((object[0]&~0xfe000000u)!=0x01504c30u)return 2u;
    (void)object[1];
    volatile uint32_t *control=(volatile uint32_t *)(uintptr_t)0x400204d8u;
    uint32_t slow=(*control>>9u)&1u;
    uint32_t count=*(volatile uint32_t *)(uintptr_t)0x400204e0u & 0x3fu;
    if((*control&0x20000000u)==0u)return 7u;
    uint32_t factor=slow==1u ? 0x753u : 0x3e8u;
    uint32_t timeout=(count*factor+11u)/12u;
    return display_driver_uled_poll_480826(timeout,
        (volatile uint32_t *)(uintptr_t)0x400204e4u,1u,1u,1u);
}
