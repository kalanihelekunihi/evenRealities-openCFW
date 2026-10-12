/* Native AttHandler 0x4b5146: dispatch by event byte through live ATT class
 * vtables. The function pointer and class instances are runtime RAM inputs. */
#include <stdint.h>
static uint32_t read32(const volatile uint8_t *p) {
    return (uint32_t)p[0]|((uint32_t)p[1]<<8u)|((uint32_t)p[2]<<16u)|((uint32_t)p[3]<<24u);
}
void audio_ble_handler_4b5146(uint32_t ignored,void *message) {
    (void)ignored;
    if(message==0)return;
    uint8_t event=((const uint8_t *)message)[2u];
    volatile uint8_t *const table=(volatile uint8_t *)(uintptr_t)0x200610acu;
    uint32_t target;
    if(event>=0x80u) {
        target=read32(table+0x4cu);
        if(target==0u)return;
    } else {
        uint32_t slot=event<0x20u?0x3cu:event<0x40u?0x40u:
                      event<0x60u?0x48u:0x44u;
        uint32_t object=read32(table+slot);
        target=read32((volatile uint8_t *)(uintptr_t)(object+8u));
    }
    ((void (*)(void *))(uintptr_t)target)(message);
}
