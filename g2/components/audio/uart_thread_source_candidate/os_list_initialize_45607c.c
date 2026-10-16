/* Apollo main 0x45607c: FreeRTOS vListInitialise. */
#include <stdint.h>

void audio_os_list_initialize_45607c(uint32_t list_address) {
    volatile uint32_t *list = (volatile uint32_t *)(uintptr_t)list_address;
    uint32_t end = list_address + 8u;
    list[1] = end;
    list[2] = UINT32_MAX;
    list[3] = end;
    list[4] = end;
    list[0] = 0u;
}
