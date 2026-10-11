/* Native flash execute shim 0x541b7c into the resident ROM callback table. */
#include <stdint.h>
typedef uint32_t (*audio_ble_flash_execute_fn)(uint32_t,uint32_t,
                                                const uint8_t *,uint32_t,uint32_t);
uint32_t audio_ble_flash_execute(uint32_t key,uint32_t mode,
                                 const uint8_t *source,uint32_t offset,
                                 uint32_t words) {
    audio_ble_flash_execute_fn callback =
        *(audio_ble_flash_execute_fn const volatile *)(0x75d630u+4u);
    uint32_t result=callback(key,mode,source,offset,words);
    *(volatile uint32_t *)0x40014008u=0xc3u;
    *(volatile uint32_t *)0x40014024u=0u;
    *(volatile uint32_t *)0x40014008u=0u;
    return result;
}
