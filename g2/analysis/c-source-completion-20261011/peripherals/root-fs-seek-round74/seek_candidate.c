#include <stdint.h>
extern uint32_t audio_uart_lv_fs_file_read_4c6f46(void *,void *,uint32_t,uint32_t *);
/* Full native4c7364..4c73c2; driver and cache reloaded after callbacks. */
uint32_t audio_uart_lv_fs_seek_cached_4c7364(void *file,uint32_t position,uint32_t whence)
{
    volatile uint32_t *f=file;
    uint32_t result=0u;
    switch((uint8_t)whence) {
    case 0: ((volatile uint32_t *)(uintptr_t)f[2])[2]=position; break;
    case 1: position+=((volatile uint32_t *)(uintptr_t)f[2])[2];
        ((volatile uint32_t *)(uintptr_t)f[2])[2]=position; break;
    case 2: {
        uint32_t data=f[0],driver=f[1];
        uint32_t callback=((volatile uint32_t *)(uintptr_t)f[1])[7];
        result=((uint32_t (*)(void *,void *,uint32_t,uint32_t))(uintptr_t)callback)
            ((void *)(uintptr_t)driver,(void *)(uintptr_t)data,position,(uint8_t)whence);
        if((uint8_t)result!=0u) break;
        uint32_t end;
        data=f[0];driver=f[1];callback=((volatile uint32_t *)(uintptr_t)f[1])[8];
        result=((uint32_t (*)(void *,void *,uint32_t *))(uintptr_t)callback)
            ((void *)(uintptr_t)driver,(void *)(uintptr_t)data,&end);
        if((uint8_t)result==0u) ((volatile uint32_t *)(uintptr_t)f[2])[2]=end;
        break;
    }
    default: break;
    }
    return (uint8_t)result;
}
/* Full native4c6fba..4c7018. Cached seek requires seek and tell callbacks. */
uint32_t audio_uart_lv_fs_file_seek_4c6fba(void *file,uint32_t position,uint32_t whence)
{
    volatile uint32_t *f=file;
    if(f[1]==0u) return 11u;
    if(((volatile uint32_t *)(uintptr_t)f[1])[1]!=0u) {
        if(((volatile uint32_t *)(uintptr_t)f[1])[7]==0u ||
           ((volatile uint32_t *)(uintptr_t)f[1])[8]==0u) return 9u;
    } else if(((volatile uint32_t *)(uintptr_t)f[1])[7]==0u) return 9u;
    uint32_t result;
    if(((volatile uint32_t *)(uintptr_t)f[1])[1]!=0u)
        result=audio_uart_lv_fs_seek_cached_4c7364(file,position,(uint8_t)whence);
    else {
        uint32_t data=f[0],driver=f[1];
        uint32_t callback=((volatile uint32_t *)(uintptr_t)f[1])[7];
        result=((uint32_t (*)(void *,void *,uint32_t,uint32_t))(uintptr_t)callback)
            ((void *)(uintptr_t)driver,(void *)(uintptr_t)data,position,(uint8_t)whence);
    }
    return (uint8_t)result;
}
/* Full native4c8d3c..4c8d8c; preserve output clear before seek. */
uint32_t audio_uart_lv_fs_read_at_4c8d3c(void *file,uint32_t position,void *buffer,uint32_t size,uint32_t *read_out)
{
    if(read_out!=0) *read_out=0u;
    uint32_t result=audio_uart_lv_fs_file_seek_4c6fba(file,position,0u);
    if((uint8_t)result!=0u) return (uint8_t)result;
    result|=audio_uart_lv_fs_file_read_4c6f46(file,buffer,size,read_out);
    return (uint8_t)result;
}
