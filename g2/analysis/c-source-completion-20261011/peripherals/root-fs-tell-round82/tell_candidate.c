#include <stdint.h>
/* Full native4c7018..4c7064. Cached tell reads cache+8 without a callback. */
uint32_t audio_uart_lv_fs_file_tell_4c7018(void *file,uint32_t *position)
{
    volatile uint32_t *f=file;
    if(f[1]==0u) {*position=0u;return 11u;}
    if(((volatile uint32_t *)(uintptr_t)f[1])[1]==0u &&
       ((volatile uint32_t *)(uintptr_t)f[1])[8]==0u) {*position=0u;return 9u;}
    if(((volatile uint32_t *)(uintptr_t)f[1])[1]!=0u) {
        *position=((volatile uint32_t *)(uintptr_t)f[2])[2];return 0u;
    }
    uint32_t data=f[0],driver=f[1];
    uint32_t callback=((volatile uint32_t *)(uintptr_t)f[1])[8];
    return (uint8_t)((uint32_t (*)(void *,void *,uint32_t *))(uintptr_t)callback)
        ((void *)(uintptr_t)driver,(void *)(uintptr_t)data,position);
}
