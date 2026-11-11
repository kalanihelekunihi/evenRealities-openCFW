/* Native 0x48297c property default arithmetic with the incoming R1 byte
 * made explicit. Stock copies only three bytes into saved R1 for two property
 * groups; the saved high byte is not initialized by this function. This is an
 * ABI model. The public entry bridge below preserves incoming R1 before any C
 * prologue can overwrite the high byte; all property logic remains C. */
#include <stdint.h>
extern const unsigned char lv_font_montserrat_14[]; /* Fix 50 */

__attribute__((used))
static uint32_t audio_uart_lv_property_default_model(uint32_t property,
                                                    uint32_t entry_r1) {
    switch((uint8_t)property) {
    case 5:case 7:return 0x1fffffffu;
    case 0x1c:return (entry_r1&0xff000000u)|0x00ffffffu;
    case 0x22:return 0xffu;
    case 0x23:case 0x31:case 0x39:case 0x3d:case 0x45:case 0x4c:
    case 0x52:case 0x58:case 0x78:return entry_r1&0xff000000u;
    case 0x24:case 0x25:case 0x29:case 0x32:case 0x3a:case 0x3e:
    case 0x44:case 0x4d:case 0x53:case 0x59:case 0x62:case 0x63:return 0xffu;
    case 0x34:return 0xfu;
    case 0x5a:return (uint32_t)(uintptr_t)lv_font_montserrat_14; /* stock 0x755610 = upstream lv_font_montserrat_14 (rom_fonts_data.c header) */
    case 0x6e:case 0x6f:case 0x76:return 0x100u;
    default:return 0u;
    }
}

uint32_t audio_uart_lv_property_default_48297c(uint32_t property) __attribute__((alias("audio_uart_lv_property_default_model")));
