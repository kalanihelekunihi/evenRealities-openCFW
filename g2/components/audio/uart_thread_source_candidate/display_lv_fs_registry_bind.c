/* Native LV filesystem driver lookup0x4c70b4 and bind0x4c8efc.
 * Registry is array/list at fixed LV root offset0x180. */
#include <stdint.h>
extern uint8_t audio_uart_display_lv_root[];
extern void *audio_uart_lv_list_first(void *); /* selected native0x482cd8 */
extern void *audio_uart_lv_list_next(void *,void *); /* selected native0x482cf0 */

void *audio_uart_lv_fs_driver_find_4c70b4(uint32_t letter)
{
    uint8_t *registry=audio_uart_display_lv_root+0x180u;
    for (uint8_t *slot=audio_uart_lv_list_first(registry);
         slot!=0;
         slot=audio_uart_lv_list_next(registry,slot)) {
        uint8_t *driver=*(uint8_t **)(void *)slot;
        if (driver[0]==(uint8_t)letter) return driver;
    }
    return 0;
}

void audio_uart_lv_init_global_bind_4c8efc(void *filesystem)
{
    uint8_t *driver=audio_uart_lv_fs_driver_find_4c70b4(0x4cu);
    *(void **)(void *)(driver+0x30u)=filesystem;
}
