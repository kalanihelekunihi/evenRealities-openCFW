/* Native 0x45fbae wrapper for display audio state. Its conditional clear
 * 0x45fb7c is audio_uart_page_45fb7c (app/page-manager). */
#include <stdint.h>
extern void audio_uart_page_45fb7c(void *page); /* 0x45fb7c */

/* Stock 0x0045FBAE (page clear wrapper) */
void audio_uart_display_page_deinit(void *object)
{
    if (object!=0) audio_uart_page_45fb7c(object);
}
