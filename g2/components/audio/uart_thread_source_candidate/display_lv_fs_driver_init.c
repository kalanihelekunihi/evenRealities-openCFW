/* Native LV filesystem driver descriptor construction 0x4c8f0a.
 * Descriptor is source-initialized RAM within selected LV root at +0x18c. */
#include <stdint.h>
typedef void * (*lv345_open_cb)(void *,const char *,uint32_t);
typedef void * (*lv345_dir_open_cb)(void *,const char *);
typedef uint32_t (*lv345_dir_read_cb)(void *,void *,char *,uint32_t);
typedef uint32_t (*lv342_close_cb)(void *,void *);
typedef uint32_t (*lv342_read_cb)(void *,void *,void *,uint32_t,uint32_t *);
typedef uint32_t (*lv342_write_cb)(void *,void *,const void *,uint32_t,uint32_t *);
typedef uint32_t (*lv342_seek_cb)(void *,void *,uint32_t,uint32_t);
typedef uint32_t (*lv342_tell_cb)(void *,void *,uint32_t *);
extern uint8_t audio_uart_display_lv_root[];
extern void audio_uart_lv_fs_driver_construct_4c7064(void *);
extern void audio_uart_lv_fs_driver_register_4c706e(void *);
extern void * audio_uart_lv_fs_open_4c8f58(void *,const char *,uint32_t);
extern uint32_t audio_uart_lv_fs_close_4c8fd8(void *,void *);
extern uint32_t audio_uart_lv_fs_read_4c8ff0(void *,void *,void *,uint32_t,uint32_t *);
extern uint32_t audio_uart_lv_fs_write_4c900c(void *,void *,const void *,uint32_t,uint32_t *);
extern uint32_t audio_uart_lv_fs_seek_4c9028(void *,void *,uint32_t,uint32_t);
extern uint32_t audio_uart_lv_fs_tell_4c9064(void *,void *,uint32_t *);
extern void * audio_uart_lv_fs_dir_open_4c9080(void *,const char *);
extern uint32_t audio_uart_lv_fs_dir_close_4c90e4(void *,void *);
extern uint32_t audio_uart_lv_fs_dir_read_4c9104(void *,void *,char *,uint32_t);

void audio_uart_lv_init_misc_4c8f0a(void)
{
    uint8_t *driver=audio_uart_display_lv_root+0x18cu;
    audio_uart_lv_fs_driver_construct_4c7064(driver);
    driver[0]=0x4cu;
    *(lv345_open_cb *)(void *)(driver+0x0cu)=audio_uart_lv_fs_open_4c8f58;
    *(lv342_close_cb *)(void *)(driver+0x10u)=audio_uart_lv_fs_close_4c8fd8;
    *(lv342_read_cb *)(void *)(driver+0x14u)=audio_uart_lv_fs_read_4c8ff0;
    *(lv342_write_cb *)(void *)(driver+0x18u)=audio_uart_lv_fs_write_4c900c;
    *(lv342_seek_cb *)(void *)(driver+0x1cu)=audio_uart_lv_fs_seek_4c9028;
    *(lv342_tell_cb *)(void *)(driver+0x20u)=audio_uart_lv_fs_tell_4c9064;
    *(lv345_dir_open_cb *)(void *)(driver+0x24u)=audio_uart_lv_fs_dir_open_4c9080;
    *(lv342_close_cb *)(void *)(driver+0x2cu)=audio_uart_lv_fs_dir_close_4c90e4;
    *(lv345_dir_read_cb *)(void *)(driver+0x28u)=audio_uart_lv_fs_dir_read_4c9104;
    audio_uart_lv_fs_driver_register_4c706e(driver);
}
