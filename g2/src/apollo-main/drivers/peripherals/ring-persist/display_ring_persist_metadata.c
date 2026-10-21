/* Native 0x47dcec and 0x47dd08 persistence startup metadata readers. */
#include <stdint.h>
extern void audio_uart_buffer_zero(void *,uint32_t,uint32_t); /* selected 0x43c0e4 */
extern uint32_t audio_uart_ring_rtc_snapshot_4d3554(void *);
extern uint32_t audio_uart_ring_parse_uint_48d874(const char *,const char **,uint32_t);
static const char product_version[]="2.2.6.10"; /* authenticated ROM 0x78c740 */
uint32_t audio_uart_ring_persist_read_clock_47dcec(void) {
    uint8_t snapshot[16];
    audio_uart_buffer_zero(snapshot,sizeof(snapshot),0u);
    (void)audio_uart_ring_rtc_snapshot_4d3554(snapshot);
    return *(const uint16_t *)(const void *)snapshot;
}
uint32_t audio_uart_ring_persist_read_version_47dd08(void) {
    const char *p=product_version;
    uint32_t parts[3]={0u,0u,0u};
    uint32_t count=0u;
    while(*p!='\0' && count<3u) {
        if((uint8_t)(*p-'0')<10u)
            parts[count++]=audio_uart_ring_parse_uint_48d874(p,&p,10u);
        else p++;
    }
    return (parts[1]<<8)|(parts[0]<<16)|parts[2];
}
