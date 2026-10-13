#include <stdint.h>
extern void *audio_uart_lv_fs_driver_find_4c70b4(uint32_t);
extern void *audio_uart_lv_heap_alloc(uint32_t);
extern void audio_uart_lvgl_log(uint32_t,const char *,uint32_t,const char *,...);
static const char fs_open_null[]="Can't open file: path is NULL";
static const char fs_open_function[]="lv_fs_open";
static const char fs_open_path[]="D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\lvgl_v9.3\\LVGL\\src\\misc\\lv_fs.c";
static const char fs_open_unknown[]="Can't open file (%s): unknown driver letter";
static const char fs_open_ready[]="Can't open file (%s): driver not ready";
static const char fs_open_missing[]="Can't open file (%s): open function not exists";
static const char fs_open_reason[]="Out of memory";
static const char fs_open_expression[]="file_p->cache != NULL";
static const char fs_open_format[]="Asserted at expression: %s (%s)";
/* Native4c6d9a..4c6ee0. Driver cache UINT32_MAX denotes memory-backed file. */
uint32_t audio_uart_lv_fs_file_open_4c6d9a(void *file,const char *path,uint32_t mode) {
    volatile uint32_t *f=file;
    if(path==0) {audio_uart_lvgl_log(2u,fs_open_path,79u,fs_open_function,fs_open_null);return 11u;}
    const volatile uint8_t *p=(const volatile uint8_t *)path;
    uint8_t letter=p[0];const char *relative=path;
    if(p[0]!=0u) {relative=path+1;if(*(const volatile uint8_t *)relative==':')++relative;}
    volatile uint32_t *driver=audio_uart_lv_fs_driver_find_4c70b4(letter);
    if(driver==0) {audio_uart_lvgl_log(2u,fs_open_path,88u,fs_open_function,fs_open_unknown,path);return 3u;}
    if(driver[2]!=0u) {
        uint32_t cb=driver[2];
        if(((uint32_t (*)(void *))(uintptr_t)cb)((void *)driver)==0u) {
            audio_uart_lvgl_log(2u,fs_open_path,94u,fs_open_function,fs_open_ready,path);return 1u;
        }
    }
    if(driver[3]==0u) {audio_uart_lvgl_log(2u,fs_open_path,100u,fs_open_function,fs_open_missing,path);return 9u;}
    f[1]=(uint32_t)(uintptr_t)driver;
    if(driver[1]==UINT32_MAX) f[0]=(uint32_t)(uintptr_t)file;
    else {
        uint32_t cb=driver[3];
        void *handle=((void *(*)(void *,const char *,uint8_t))(uintptr_t)cb)((void *)driver,relative,(uint8_t)mode);
        if(handle==0||(uintptr_t)handle==UINT32_MAX)return 12u;
        f[0]=(uint32_t)(uintptr_t)handle;
    }
    if(driver[1]!=0u) {
        f[2]=(uint32_t)(uintptr_t)audio_uart_lv_heap_alloc(16u);
        if(f[2]==0u) {
            audio_uart_lvgl_log(3u,fs_open_path,123u,fs_open_function,fs_open_format,fs_open_expression,fs_open_reason);
            for(;;)*(volatile uint32_t *)(uintptr_t)UINT32_MAX=0u;
        }
        if(driver[1]==UINT32_MAX) {
            uint32_t buffer=*(const volatile uint32_t *)((const uint8_t *)path+4u);
            ((volatile uint32_t *)(uintptr_t)f[2])[3]=buffer;
            ((volatile uint32_t *)(uintptr_t)f[2])[0]=0u;
            ((volatile uint32_t *)(uintptr_t)f[2])[2]=0u;
            uint32_t end=*(const volatile uint32_t *)((const uint8_t *)path+8u);
            ((volatile uint32_t *)(uintptr_t)f[2])[1]=end;
        } else {
            ((volatile uint32_t *)(uintptr_t)f[2])[0]=UINT32_MAX;
            ((volatile uint32_t *)(uintptr_t)f[2])[1]=UINT32_MAX-1u;
        }
    }
    return 0u;
}
