/* Dashboard layout text getters, stock
 * D:\01_workspace\s200_ap510b_iar_git\app\gui\dashboard\dashboard_ext.c.
 * Native 0x5020f0..0x502119; empty-string literal 0x502130, pointer cells
 * 0x50215c (ready byte), 0x502660 and 0x50267c (decoded text fields).
 *
 * Both read the layout protobuf decoded by the loader at 0x501d5c. Until it
 * has been loaded they return the empty string. The APP_REQUEST_PB_FILE_INFO
 * reply (0x500a16) copies the first into a 16-byte field and the second into
 * a 32-byte field. */
#include <stdint.h>

extern volatile uint8_t audio_uart_dashboard_ready;    /* RAM 0x20074fa5 */
extern uint8_t audio_uart_dashboard_decoded[188];      /* RAM 0x2037cc68 */

static const char empty_text[] = ""; /* ROM 0x502130 */

/* Decoded text field at +0x00 (16 bytes). */
const char *dashboard_ext_layout_text0_get_5020f0(void)
{
    if (audio_uart_dashboard_ready == 0u)
        return empty_text;
    return (const char *)&audio_uart_dashboard_decoded[0x00];
}

/* Decoded text field at +0x10 (32 bytes). */
const char *dashboard_ext_layout_text1_get_502108(void)
{
    if (audio_uart_dashboard_ready == 0u)
        return empty_text;
    return (const char *)&audio_uart_dashboard_decoded[0x10];
}
