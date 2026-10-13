/* Complete native open4c8f58..4c8fd7,dir-open4c9080..4c90e1,dir-read4c9104..4c9175.
 * Pinned lv_fs_littlefs.c; native allocation84/52,info264/name8,path256 retained.
 * Unadmitted pending native/source-ABI/compiler qualification. */
#include <stdint.h>
#include <stddef.h>
extern void *audio_uart_lv_malloc(uint32_t);
extern void audio_uart_lv_heap_free(void *);
extern void audio_uart_lvgl_log(uint32_t,const char *,uint32_t,const char *,const char *,...);
extern int32_t audio_uart_lv_snprintf_483fd0(char *,uint32_t,const char *,...);
extern uint32_t audio_uart_lv_strlcpy_454778(char *,const char *,uint32_t);
extern int32_t audio_uart_lv_string_compare_4547be(const char *,const char *);
extern int32_t audio_file_lfs_open(void *,void *,const char *,uint32_t);
extern int32_t audio_file_lfs_dir_open_4cfc66(void *,void *,const char *);
extern int32_t audio_file_lfs_dir_read_4cfd02(void *,void *,void *);
struct lv344_info {uint8_t type;uint8_t reserved[3];uint32_t size;char name[256];};
_Static_assert(sizeof(struct lv344_info)==264,"native info size");
_Static_assert(offsetof(struct lv344_info,name)==8,"native info name offset");
static void *lv344_filesystem(const void *driver)
{return (void *)(uintptr_t)*(const volatile uint32_t *)((const uint8_t *)driver+48u);}
static _Noreturn void lv344_oom(uint32_t line,const char *function,const char *expression)
{
 audio_uart_lvgl_log(3u,"D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\lvgl_v9.3\\LVGL\\src\\libs\\fsdrv\\lv_fs_littlefs.c",
  line,function,"Asserted at expression: %s (%s)",expression,"Out of memory");
 for(;;)*(volatile uint32_t *)(uintptr_t)UINT32_MAX=0u;
}
void *audio_uart_lv_fs_open_4c8f58(void *driver,const char *path,uint32_t mode)
{
 uint8_t narrowed=(uint8_t)mode;uint32_t flags=0;
 if(narrowed==1u)flags=2u;else if(narrowed==2u)flags=1u;else if(narrowed==3u)flags=3u;
 void *file=audio_uart_lv_malloc(84u);
 if(file==0)lv344_oom(83u,"fs_open","lf != NULL");
 char buffer[256];(void)audio_uart_lv_snprintf_483fd0(buffer,256u,"%s",path);
 int32_t result=audio_file_lfs_open(lv344_filesystem(driver),file,buffer,flags);
 if(result!=0)return 0; /* Native open error doesnotfree thisallocation. */
 return file;
}
void *audio_uart_lv_fs_dir_open_4c9080(void *driver,const char *path)
{
 void *directory=audio_uart_lv_malloc(52u);
 if(directory==0)lv344_oom(204u,"fs_dir_open","ld != NULL");
 char buffer[256];(void)audio_uart_lv_snprintf_483fd0(buffer,256u,"%s",path);
 int32_t result=audio_file_lfs_dir_open_4cfc66(lv344_filesystem(driver),directory,buffer);
 if(result!=0){audio_uart_lv_heap_free(directory);return 0;}
 return directory;
}
uint32_t audio_uart_lv_fs_dir_read_4c9104(void *driver,void *directory,char *filename,uint32_t length)
{
 if(length==0u)return 11u;
 void *filesystem=lv344_filesystem(driver);
 *(volatile uint8_t *)filename=0u;
 struct lv344_info info;
 for(;;){
  int32_t result=audio_file_lfs_dir_read_4cfd02(filesystem,directory,&info);
  if(result<0)return 12u;
  if(result==0){*(volatile uint8_t *)filename=0u;return 0u;}
  if(*(const volatile uint8_t *)&info.type==2u)
   (void)audio_uart_lv_snprintf_483fd0(filename,length,"/%s",info.name);
  else (void)audio_uart_lv_strlcpy_454778(filename,info.name,length);
  if(audio_uart_lv_string_compare_4547be(filename,"/.")==0)continue;
  if(audio_uart_lv_string_compare_4547be(filename,"/..")==0)continue;
  return 0u;
 }
}
