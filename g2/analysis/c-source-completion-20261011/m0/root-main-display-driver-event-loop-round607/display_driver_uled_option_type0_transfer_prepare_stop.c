/* Apollo S200 transfer stop snapshot at 0x538d18. */
#include <stdint.h>

extern uint32_t display_driver_uled_irq_save_473940(void);

void display_driver_uled_transfer_prepare_stop_538d18(uint32_t *transfer) {
    uint32_t mask=display_driver_uled_irq_save_473940();
    uint32_t table=transfer[9];
    uint32_t counter=*(volatile const uint32_t *)(uintptr_t)
        (*(volatile const uint32_t *)(uintptr_t)(table+8u));
    uint32_t next=(transfer[8]&0xffffff00u)|(counter&255u);
    transfer[7]=next;
    if ((int32_t)(transfer[8]-next)<0) transfer[7]=next-256u;
    transfer[3]=*(volatile const uint32_t *)(uintptr_t)
        (*(volatile const uint32_t *)(uintptr_t)(table+4u));
    __asm__ volatile("msr PRIMASK, %0" :: "r"(mask) : "memory");
}
