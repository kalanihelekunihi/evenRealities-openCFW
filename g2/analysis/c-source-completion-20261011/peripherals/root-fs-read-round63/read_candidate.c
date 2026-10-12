/* Full native4c6f46..4c6fba. Driver offsets cache_size4/read20/seek28.
 * Cached read is a genuine child provider, not an uncached substitute. */
#include <stdint.h>
extern uint32_t audio_uart_lv_fs_read_cached_4c713c(void *,void *,uint32_t,uint32_t *);
uint32_t audio_uart_lv_fs_file_read_4c6f46(void *file,void *buffer,uint32_t size,uint32_t *read_out)
{
    volatile uint32_t *f=file;
    if(read_out != 0) *read_out=0u;
    if(f[1]==0u) return 11u;
    if(((volatile uint32_t *)(uintptr_t)f[1])[1]!=0u) {
        if(((volatile uint32_t *)(uintptr_t)f[1])[5]==0u ||
           ((volatile uint32_t *)(uintptr_t)f[1])[7]==0u) return 9u;
    } else if(((volatile uint32_t *)(uintptr_t)f[1])[5]==0u) return 9u;
    uint32_t count=0u,result;
    if(((volatile uint32_t *)(uintptr_t)f[1])[1]!=0u) {
        result=audio_uart_lv_fs_read_cached_4c713c(file,buffer,size,&count);
    } else {
        uint32_t data=f[0],driver=f[1];
        uint32_t callback=((volatile uint32_t *)(uintptr_t)f[1])[5];
        result=((uint32_t (*)(void *,void *,void *,uint32_t,uint32_t *))(uintptr_t)callback)
            ((void *)(uintptr_t)driver,(void *)(uintptr_t)data,buffer,size,&count);
    }
    if(read_out != 0) *read_out=count;
    return (uint8_t)result;
}
