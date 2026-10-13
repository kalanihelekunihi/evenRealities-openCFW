#include <stdint.h>
extern uint32_t audio_uart_power_peripheral_descriptor_47ef18(uint32_t *,uint32_t);
/* Native47f90c..47f942: output clear precedes descriptor lookup. */
uint32_t audio_uart_nema_power_status_47f90c(uint32_t peripheral,uint8_t *powered) {
    if(!powered) return 6u;
    *powered=0u;
    uint32_t descriptor[4];
    uint32_t result=audio_uart_power_peripheral_descriptor_47ef18(descriptor,(uint8_t)peripheral);
    if(result) return result;
    uint32_t status=*(volatile uint32_t *)(uintptr_t)descriptor[2];
    *powered=(uint8_t)((status&descriptor[3])!=0u);
    return 0u;
}
