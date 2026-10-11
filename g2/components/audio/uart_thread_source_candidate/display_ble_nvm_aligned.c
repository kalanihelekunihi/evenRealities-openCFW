/* Native aligned flash program wrapper 0x4d09d8 with IRQ save/restore. */
#include <stdint.h>
extern uint32_t audio_ble_flash_enter_program_mode(void); /* 0x47f3c6 */
extern uint32_t audio_ble_flash_leave_program_mode(void); /* 0x47f418 */
extern uint32_t audio_ble_flash_execute(uint32_t,uint32_t,const uint8_t *,uint32_t,uint32_t); /* 0x541b7c */
uint32_t audio_ble_nvm_write_aligned(uint32_t key,const uint8_t *source_bytes,
                                     uint8_t *destination,uint32_t words) {
    if(((uintptr_t)destination&3u)!=0u) return 0x08000140u;
    uint32_t irq_mask;
    __asm__ volatile("mrs %0, PRIMASK\n\tcpsid i" : "=r"(irq_mask) :: "memory");
    (void)audio_ble_flash_enter_program_mode();
    uint32_t result=audio_ble_flash_execute(key,1u,source_bytes,
                                             ((uint32_t)(uintptr_t)destination-0x400000u)>>2,
                                             words);
    (void)audio_ble_flash_leave_program_mode();
    __asm__ volatile("msr PRIMASK, %0" :: "r"(irq_mask) : "memory");
    return result==0u?0u:result|0x08000100u;
}
