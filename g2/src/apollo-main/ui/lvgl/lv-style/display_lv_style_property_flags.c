/* Native lv_style_get_prop_flags 0x482a6a: built-in ROM flags and runtime
 * extension table with its registered length. */
#include <stdint.h>
extern const uint8_t audio_uart_lv_builtin_property_flags[]; /* ROM0x6d439c */
extern uint8_t audio_uart_display_lv_root[]; /* RAM0x2006f548 */
uint32_t audio_uart_lv_property_flags_482a6a(uint8_t property) {
    if(property==0xffu)return 0x3fu;
    if(property==0u)return 0u;
    if(property<0x8au)return audio_uart_lv_builtin_property_flags[property];
    uint32_t length;__builtin_memcpy(&length,audio_uart_display_lv_root+0x28u,4u);
    uint8_t *extended;__builtin_memcpy(&extended,audio_uart_display_lv_root+0x30u,4u);
    uint8_t index=(uint8_t)(property+0x76u);
    if(extended==0 || length<=index)return 0u;
    return extended[index];
}
