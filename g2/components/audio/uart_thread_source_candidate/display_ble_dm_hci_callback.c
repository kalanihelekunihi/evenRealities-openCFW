/* Native dmHciEvtCback 0x4d299c. Event-class map at original 0x6e006c is
 * immutable product ROM data; selected source must provide its typed table. */
#include <stdint.h>
extern const uint8_t audio_ble_dm_hci_event_class_map_6e006c[];
static uint32_t read32(const volatile uint8_t *p) {
    return (uint32_t)p[0]|((uint32_t)p[1]<<8u)|((uint32_t)p[2]<<16u)|((uint32_t)p[3]<<24u);
}
void audio_ble_dm_handler_4d299c(void *event) {
    const uint8_t *message=(const uint8_t *)event;
    volatile uint8_t *const dm=(volatile uint8_t *)(uintptr_t)0x20073b78u;
    if(dm[0x10u]!=0u && message[2u]!=0u)return;
    uint8_t slot=audio_ble_dm_hci_event_class_map_6e006c[message[2u]];
    volatile uint8_t *const registry=(volatile uint8_t *)(uintptr_t)0x20000694u;
    uint32_t handler=read32(registry+(uint32_t)slot*4u);
    uint32_t callback=read32((volatile uint8_t *)(uintptr_t)(handler+4u));
    ((void (*)(void *))(uintptr_t)callback)(event);
}
void audio_ble_handler_4d2a5c(uint32_t ignored,void *event) { /* DmHandler */
    (void)ignored;
    if(event==0)return;
    const uint8_t *message=(const uint8_t *)event;
    volatile uint8_t *const dm=(volatile uint8_t *)(uintptr_t)0x20073b78u;
    if(dm[0x10u]!=0u)return;
    volatile uint8_t *const registry=(volatile uint8_t *)(uintptr_t)0x20000694u;
    uint32_t handler=read32(registry+((uint32_t)message[2u]>>3u)*4u);
    uint32_t callback=read32((volatile uint8_t *)(uintptr_t)(handler+8u));
    ((void (*)(void *))(uintptr_t)callback)(event);
}
