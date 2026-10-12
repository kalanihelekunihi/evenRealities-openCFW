/* Native 0x52e5ce and 0x52e5f2 copy accepted product configuration into
 * authenticated live RAM cells. They do not initialize those source inputs. */
#include <stdint.h>
#define W(a) (*(volatile uint32_t *)(uintptr_t)(a))
#define B(a) (*(volatile uint8_t *)(uintptr_t)(a))
uint32_t audio_ble_radio_configure_52e5ce(void *context,uint32_t mode,uint32_t value) {
    if(context==0) return 0u;
    W(0x2007422cu)=(uint32_t)(uintptr_t)context;
    B(0x20074f50u)=(uint8_t)mode;
    W(0x20074230u)=value;
    return 1u;
}
uint32_t audio_ble_radio_tune_52e5f2(uint32_t context,uint32_t mode) {
    if(context==0u) return 0u;
    W(0x20074234u)=context;
    W(0x20074238u)=(uint8_t)mode;
    return 1u;
}
