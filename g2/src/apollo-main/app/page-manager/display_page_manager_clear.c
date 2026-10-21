/* Native page-manager initializer 0x45fba2 and its conditional clear 0x45fb7c. */
#include <stdint.h>
extern void audio_uart_buffer_zero(void *,uint32_t,uint32_t); /* selected 0x43c0e4 */
void audio_uart_page_45fb7c(void *page) {
    if(!page)return;
    uint8_t *p=(uint8_t *)page;
    p[0xc0u]=0u;p[0xc1u]=0u;p[0xc2u]=0u;
    audio_uart_buffer_zero(page,0xc0u,0u);
}
void audio_uart_page_45fba2(void *page) {
    if(page)audio_uart_page_45fb7c(page);
}
