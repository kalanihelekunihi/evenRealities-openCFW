/* Complete native4c713c..4c7326; reconstructed from pinned lv_fs.c and
 * native field offsets, 16-bit partial-copy length and fresh owner reloads.
 * Unselected pending compiled/native comparison. */
#include <stdint.h>
extern void *audio_uart_lv_grid_copy_454738(void *,const void *,uint32_t);
extern void *audio_uart_lv_malloc(uint32_t);
extern void audio_uart_lvgl_log(uint32_t,const char *,uint32_t,const char *,...);
#define CACHE ((volatile uint32_t *)(uintptr_t)f[2])
#define DRIVER ((volatile uint32_t *)(uintptr_t)f[1])
#define SEEK(pos) ((uint32_t (*)(void *,void *,uint32_t,uint32_t))(uintptr_t)DRIVER[7])((void *)(uintptr_t)f[1],(void *)(uintptr_t)f[0],(pos),0u)
#define READ(buf,len,count) ((uint32_t (*)(void *,void *,void *,uint32_t,uint32_t *))(uintptr_t)DRIVER[5])((void *)(uintptr_t)f[1],(void *)(uintptr_t)f[0],(buf),(len),(count))
uint32_t audio_uart_lv_fs_read_cached_4c713c(void *file,void *out,uint32_t request,uint32_t *read_out)
{
    volatile uint32_t *f=file;
    uint32_t result=0u,position=CACHE[2],start=CACHE[0],end=CACHE[1];
    uint8_t *buffer=(void *)(uintptr_t)CACHE[3];
    uint32_t buffer_size=DRIVER[1];
    if(position>=start && position<=end) {
        uint32_t remaining=end-position+1u;
        uint32_t offset=(end-start)-remaining+1u;
        if(DRIVER[1]==UINT32_MAX && request>remaining) request=remaining-1u;
        if(request<=remaining) {
            audio_uart_lv_grid_copy_454738(out,buffer+offset,request);
            *read_out=request;
        } else {
            audio_uart_lv_grid_copy_454738(out,buffer+offset,remaining);
            (void)SEEK(CACHE[1]+1u);
            uint32_t count=0u;
            if(request-remaining>buffer_size) {
                result=READ((uint8_t *)out+remaining,request-remaining,&count);
            } else {
                result=READ(buffer,buffer_size,&count);
                CACHE[0]=CACHE[1]+1u;
                CACHE[1]=CACHE[0]+count-1u;
                uint32_t chunk=request-remaining;
                if(chunk>=count) chunk=count;
                audio_uart_lv_grid_copy_454738((uint8_t *)out+remaining,buffer,(uint16_t)chunk);
            }
            uint32_t total=remaining+count;
            *read_out=total<request?total:request;
        }
    } else {
        (void)SEEK(CACHE[2]);
        if(request>buffer_size) {
            result=READ(out,request,read_out);
        } else {
            if(buffer==0) {
                CACHE[3]=(uint32_t)(uintptr_t)audio_uart_lv_malloc(buffer_size);
                if(CACHE[3]==0u) {
                    audio_uart_lvgl_log(3u,"D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\lvgl_v9.3\\LVGL\\src\\misc\\lv_fs.c",600u,"lv_fs_read_cached","Asserted at expression: %s (%s)","file_p->cache->buffer != NULL","Out of memory");
                    for(;;) *(volatile uint32_t *)(uintptr_t)UINT32_MAX=0u;
                }
                buffer=(void *)(uintptr_t)CACHE[3];
            }
            uint32_t count=0u;
            result=READ(buffer,buffer_size,&count);
            CACHE[0]=position;
            CACHE[1]=CACHE[0]+count-1u;
            *read_out=request<count?request:count;
            audio_uart_lv_grid_copy_454738(out,buffer,*read_out);
        }
    }
    if((uint8_t)result==0u) CACHE[2]=CACHE[2]+*read_out;
    return (uint8_t)result;
}
#undef READ
#undef SEEK
#undef DRIVER
#undef CACHE
