/* Complete native public LittleFS entries anddir-close core.
 * Unadmitted; native/source/compiler/runtime qualification remains.
 * Pinned lfs.c6155/6207/6318 etc; native mlist offset40 retained. */
#include <stdint.h>
extern int32_t g2_lfs_mlist_isopen(void *,void *);
extern void g2_file_close_error(const char *,const char *,uint32_t);
extern int32_t g2_lfs_file_close(void *,void *);
extern int32_t audio_file_lfs_write_core_4ce308(void *,void *,const void *,uint32_t);
extern int32_t audio_file_lfs_dir_open_core_4cd558(void *,void *,const char *);
extern int32_t audio_file_lfs_dir_read_core_4cd60e(void *,void *,void *);
extern void g2_lfs_mlist_remove(void *,void *);
static void *lfs347_list(const void *filesystem)
{return (void *)(uintptr_t)*(const volatile uint32_t *)((const uint8_t *)filesystem+40u);}
static const char lfs347_source[]="D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\littlefs\\lfs.c";
static const char lfs347_open[]="lfs_mlist_isopen(lfs->mlist, (struct lfs_mlist*)file)";
static const char lfs347_closed_dir[]="!lfs_mlist_isopen(lfs->mlist, (struct lfs_mlist*)dir)";
int32_t audio_file_lfs_close_4cfad0(void *filesystem,void *file)
{
 if(g2_lfs_mlist_isopen(lfs347_list(filesystem),file)==0)
  g2_file_close_error(lfs347_open,lfs347_source,6155u);
 return g2_lfs_file_close(filesystem,file);
}
int32_t audio_file_lfs_write_4cfb7c(void *filesystem,void *file,const void *buffer,uint32_t size)
{
 if(g2_lfs_mlist_isopen(lfs347_list(filesystem),file)==0)
  g2_file_close_error(lfs347_open,lfs347_source,6207u);
 return audio_file_lfs_write_core_4ce308(filesystem,file,buffer,size);
}
int32_t audio_file_lfs_dir_open_4cfc66(void *filesystem,void *directory,const char *path)
{
 if(g2_lfs_mlist_isopen(lfs347_list(filesystem),directory)!=0)
  g2_file_close_error(lfs347_closed_dir,lfs347_source,6318u);
 return audio_file_lfs_dir_open_core_4cd558(filesystem,directory,path);
}
int32_t audio_file_lfs_dir_close_core_4cd604(void *filesystem,void *directory)
{
 g2_lfs_mlist_remove(filesystem,directory);return 0;
}
int32_t audio_file_lfs_dir_close_4cfcf8(void *filesystem,void *directory)
{return audio_file_lfs_dir_close_core_4cd604(filesystem,directory);}
int32_t audio_file_lfs_dir_read_4cfd02(void *filesystem,void *directory,void *info)
{return audio_file_lfs_dir_read_core_4cd60e(filesystem,directory,info);}
