/* Native LV filesystem driver descriptor construction 0x4c8f0a.
 * Descriptor is source-initialized RAM within selected LV root at +0x18c. */
#include <stdint.h>
extern uint8_t audio_uart_display_lv_root[];
extern void audio_uart_lv_fs_driver_construct_4c7064(void *);
extern void audio_uart_lv_fs_driver_register_4c706e(void *);
extern void audio_uart_lv_fs_open_4c8f58(void);
extern void audio_uart_lv_fs_close_4c8fd8(void);
extern void audio_uart_lv_fs_read_4c8ff0(void);
extern void audio_uart_lv_fs_write_4c900c(void);
extern void audio_uart_lv_fs_seek_4c9028(void);
extern void audio_uart_lv_fs_tell_4c9064(void);
extern void audio_uart_lv_fs_dir_open_4c9080(void);
extern void audio_uart_lv_fs_dir_close_4c90e4(void);
extern void audio_uart_lv_fs_dir_read_4c9104(void);

void audio_uart_lv_init_misc_4c8f0a(void)
{
    uint8_t *driver=audio_uart_display_lv_root+0x18cu;
    audio_uart_lv_fs_driver_construct_4c7064(driver);
    driver[0]=0x4cu;
    *(void (**)(void))(void *)(driver+0x0cu)=audio_uart_lv_fs_open_4c8f58;
    *(void (**)(void))(void *)(driver+0x10u)=audio_uart_lv_fs_close_4c8fd8;
    *(void (**)(void))(void *)(driver+0x14u)=audio_uart_lv_fs_read_4c8ff0;
    *(void (**)(void))(void *)(driver+0x18u)=audio_uart_lv_fs_write_4c900c;
    *(void (**)(void))(void *)(driver+0x1cu)=audio_uart_lv_fs_seek_4c9028;
    *(void (**)(void))(void *)(driver+0x20u)=audio_uart_lv_fs_tell_4c9064;
    *(void (**)(void))(void *)(driver+0x24u)=audio_uart_lv_fs_dir_open_4c9080;
    *(void (**)(void))(void *)(driver+0x2cu)=audio_uart_lv_fs_dir_close_4c90e4;
    *(void (**)(void))(void *)(driver+0x28u)=audio_uart_lv_fs_dir_read_4c9104;
    audio_uart_lv_fs_driver_register_4c706e(driver);
}
