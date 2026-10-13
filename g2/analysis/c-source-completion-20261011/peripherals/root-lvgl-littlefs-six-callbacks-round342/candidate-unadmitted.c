/* Six complete native LittleFS LVGL callbacks, source-backed lv_fs_littlefs.c.
 * drv userdata48; output store/reread; whence UXTB; status0/12 andcleanup ordering.
 * Underlying native LittleFS entrypoints remain explicit providers. */
#include <stdint.h>
extern int32_t audio_file_lfs_read(void *,void *,void *,uint32_t);
extern int32_t audio_file_lfs_seek(void *,void *,int32_t,uint32_t);
extern int32_t audio_file_lfs_tell(void *,void *);
extern int32_t audio_file_lfs_close_4cfad0(void *,void *);
extern int32_t audio_file_lfs_write_4cfb7c(void *,void *,const void *,uint32_t);
extern int32_t audio_file_lfs_dir_close_4cfcf8(void *,void *);
extern void audio_uart_lv_heap_free(void *);
static void *lv342_filesystem(const void *driver)
{return (void *)(uintptr_t)*(const volatile uint32_t *)((const uint8_t *)driver+48u);}
uint32_t audio_uart_lv_fs_read_4c8ff0(void *driver,void *file,void *buffer,uint32_t count,uint32_t *output)
{
 int32_t result=audio_file_lfs_read(lv342_filesystem(driver),file,buffer,count);
 volatile uint32_t *p=output;*p=(uint32_t)result;
 return (int32_t)*p<0?12u:0u;
}
uint32_t audio_uart_lv_fs_write_4c900c(void *driver,void *file,const void *buffer,uint32_t count,uint32_t *output)
{
 int32_t result=audio_file_lfs_write_4cfb7c(lv342_filesystem(driver),file,buffer,count);
 volatile uint32_t *p=output;*p=(uint32_t)result;
 return (int32_t)*p<0?12u:0u;
}
uint32_t audio_uart_lv_fs_seek_4c9028(void *driver,void *file,uint32_t position,uint32_t whence)
{
 uint8_t narrowed=(uint8_t)whence;uint32_t mode=0u;
 if(narrowed==1u)mode=1u;else if(narrowed==2u)mode=2u;
 int32_t result=audio_file_lfs_seek(lv342_filesystem(driver),file,(int32_t)position,mode);
 return result<0?12u:0u;
}
uint32_t audio_uart_lv_fs_tell_4c9064(void *driver,void *file,uint32_t *output)
{
 int32_t result=audio_file_lfs_tell(lv342_filesystem(driver),file);
 volatile uint32_t *p=output;*p=(uint32_t)result;
 return (int32_t)*p<0?12u:0u;
}
uint32_t audio_uart_lv_fs_close_4c8fd8(void *driver,void *file)
{
 (void)audio_file_lfs_close_4cfad0(lv342_filesystem(driver),file);
 audio_uart_lv_heap_free(file);return 0u;
}
uint32_t audio_uart_lv_fs_dir_close_4c90e4(void *driver,void *directory)
{
 int32_t result=audio_file_lfs_dir_close_4cfcf8(lv342_filesystem(driver),directory);
 if(result<0)return 12u;
 audio_uart_lv_heap_free(directory);return 0u;
}
