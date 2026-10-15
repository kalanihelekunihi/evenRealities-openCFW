/* Apollo type-6 object and control helpers 0x539a10, 0x539944,
 * 0x4800e4 and 0x48009e. Candidate with fixed peripheral addresses.
 */
#include <stdint.h>
extern uint32_t display_driver_uled_irq_save_473940(void);
extern uint32_t display_driver_uled_delay_4807a0(uint32_t);

uint32_t display_driver_uled_status_flag_4800e4(uint8_t *out) {
    uint32_t control=*(volatile uint32_t *)(uintptr_t)0x400204d8u;
    *out=(uint8_t)(((control>>31u)^1u)&1u);
    return 0u;
}

uint32_t display_driver_uled_control_start_48009e(void) {
    uint32_t prior=display_driver_uled_irq_save_473940();
    volatile uint32_t *control=(volatile uint32_t *)(uintptr_t)0x400204d8u;
    *control=*control|0x80000000u;
    *control=*control|0x40000000u;
    if ((*(volatile uint32_t *)(uintptr_t)0x4002000cu & 0xffu)>=0x22u) {
        (void)display_driver_uled_delay_4807a0(1u);
        volatile uint32_t *other=(volatile uint32_t *)(uintptr_t)0x400201b0u;
        *other=*other|0x00200000u;
    }
    __asm__ volatile("msr primask, %0" :: "r"(prior) : "memory");
    return 0u;
}

uint32_t display_driver_uled_object_stop_539a10(uint32_t object_addr) {
    if(object_addr==0u)return 2u;
    volatile uint32_t *object=(volatile uint32_t *)(uintptr_t)object_addr;
    if ((object[0]&~0xfe000000u)!=0x01504c30u)return 2u;
    (void)object[1];
    volatile uint32_t *control=(volatile uint32_t *)(uintptr_t)0x400204d8u;
    *control=*control & ~0x20000000u;
    object[0]=object[0] & ~0x02000000u;
    return 0u;
}

uint32_t display_driver_uled_object_release_539944(uint32_t object_addr) {
    if(object_addr==0u)return 2u;
    volatile uint32_t *object=(volatile uint32_t *)(uintptr_t)object_addr;
    if ((object[0]&~0xfe000000u)!=0x01504c30u)return 2u;
    uint32_t result=0u;
    if ((object[0]&0x02000000u)!=0u)
        result=display_driver_uled_object_stop_539a10(object_addr);
    uint8_t flag=0u;
    (void)display_driver_uled_status_flag_4800e4(&flag);
    if (flag!=0u)(void)display_driver_uled_control_start_48009e();
    object[0]=object[0]&~0x01000000u;
    return result;
}
