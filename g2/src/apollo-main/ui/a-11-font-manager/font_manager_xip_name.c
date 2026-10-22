/* Font manager accessor, stock D:\01_workspace\s200_ap510b_iar_git\app\gui\common\lvgl_font_manager.c
 * (module 0x46cae0..0x46d588). Native 0x46d584..0x46d588, literal 0x46d630.
 * Returns the 16-byte name of the XIP font loaded by _xip_font_configure (0x46d29a). */
#include <stdint.h>

extern uint8_t audio_uart_ring_config_name[16]; /* RAM 0x20073e94 */

uint8_t *font_manager_xip_font_name_46d584(void)
{
    return audio_uart_ring_config_name;
}
