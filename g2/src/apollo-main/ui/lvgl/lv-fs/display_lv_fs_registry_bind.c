/* Native LV filesystem driver lookup0x4c70b4 and bind0x4c8efc.
 * Registry is array/list at fixed LV root offset0x180. */
#include <stdint.h>
extern uint8_t audio_uart_display_lv_root[];
extern void *audio_uart_lv_list_first(void *); /* selected native0x482cd8 */
extern void *audio_uart_lv_list_next(void *,void *); /* selected native0x482cf0 */

/* Retired: stock 0x4c70b4 is upstream lv_fs_get_drv (lvgl/src/misc/lv_fs.c); this name is a link alias. */
void *audio_uart_lv_fs_driver_find_4c70b4(uint32_t letter);

void audio_uart_lv_init_global_bind_4c8efc(void *filesystem)
{
    uint8_t *driver=audio_uart_lv_fs_driver_find_4c70b4(0x4cu);
    *(void **)(void *)(driver+0x30u)=filesystem;
}
