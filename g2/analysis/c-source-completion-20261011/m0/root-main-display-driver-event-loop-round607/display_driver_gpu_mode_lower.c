/* Apollo Ambiq cached mode setter 0x4b06c0..0x4b072f. Candidate. */
#include <stdint.h>
extern void *audio_uart_ambiq_default_unit_4c791a(void); /* selected */
extern void display_driver_nema_mode_513924(uint32_t,int32_t,int32_t,int32_t);
void display_driver_gpu_mode_lower_4b06c0(uint32_t unit,uint32_t mode,uint32_t a,
                                          uint32_t b,uint32_t c,uint32_t force) {
    volatile uint8_t *state=unit ? (volatile uint8_t *)(uintptr_t)unit :
        (volatile uint8_t *)audio_uart_ambiq_default_unit_4c791a();
    int8_t ca=(int8_t)a,cb=(int8_t)b,cc=(int8_t)c;
    if((uint8_t)force==0u &&
       *(volatile uint32_t *)(void *)(state+0x50u)==mode &&
       (int8_t)state[0x54u]==ca &&
       (int8_t)state[0x55u]==cb &&
       (int8_t)state[0x56u]==cc) return;
    display_driver_nema_mode_513924(mode,ca,cb,cc);
    *(volatile uint32_t *)(void *)(state+0x50u)=mode;
    state[0x54u]=(uint8_t)a;
    state[0x55u]=(uint8_t)b;
    state[0x56u]=(uint8_t)c;
}
