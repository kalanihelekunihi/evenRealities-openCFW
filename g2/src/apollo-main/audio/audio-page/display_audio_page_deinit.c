/* Native 0x45fb7c clear and 0x45fbae wrapper for display audio state. */
#include <stdint.h>
#include <stddef.h>
extern void *memset(void *,int,size_t);

void audio_uart_display_page_clear_45fb7c(void *object)
{
    if (object==0) return;
    uint8_t *p=(uint8_t *)object;
    p[0xc0u]=0u;
    p[0xc1u]=0u;
    p[0xc2u]=0u;
    (void)memset(p,0,0xc0u);
}

void audio_uart_display_page_deinit(void *object)
{
    if (object!=0) audio_uart_display_page_clear_45fb7c(object);
}
