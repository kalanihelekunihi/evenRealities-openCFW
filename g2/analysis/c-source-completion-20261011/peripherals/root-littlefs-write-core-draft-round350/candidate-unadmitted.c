
/* Whole native LittleFS write core4ce308..4ce3b1,170bytes. Unadmitted draft.
 * Pinned lfs.c3657..3701; allstateoffsets/flagbits/native32bitwrap preserved. */
#include <stdint.h>
extern int32_t g2_lfs_file_flush(void *,void *);
extern int32_t g2_lfs_file_flushedwrite(void *,void *,const void *,uint32_t);
extern void g2_file_close_error(const char *,const char *,uint32_t);
static uint32_t lfs350_get(const void *p,uint32_t offset)
{return *(const volatile uint32_t *)((const uint8_t *)p+offset);}
static void lfs350_put(void *p,uint32_t offset,uint32_t value)
{*(volatile uint32_t *)((uint8_t *)p+offset)=value;}
int32_t audio_file_lfs_write_core_4ce308(void *filesystem,void *file,const void *buffer,uint32_t size)
{
 uint32_t zero_word=(uint32_t)(uintptr_t)buffer;
 if((*(const volatile uint8_t *)((const uint8_t *)file+48u)&2u)==0u)
  g2_file_close_error("(file->flags & LFS_O_WRONLY) == LFS_O_WRONLY","D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\littlefs\\lfs.c",3659u);
 if((lfs350_get(file,48u)&0x40000u)!=0u){
  int32_t error=g2_lfs_file_flush(filesystem,file);if(error!=0)return error;
 }
 if((lfs350_get(file,48u)&0x800u)!=0u&&lfs350_get(file,52u)<lfs350_get(file,44u))
  lfs350_put(file,52u,lfs350_get(file,44u));
 if(lfs350_get(filesystem,116u)<(uint32_t)(size+lfs350_get(file,52u)))return -27;
 if((lfs350_get(file,48u)&0x20000u)==0u&&lfs350_get(file,44u)<lfs350_get(file,52u)){
  uint32_t target=lfs350_get(file,52u);lfs350_put(file,52u,lfs350_get(file,44u));
  while(lfs350_get(file,52u)<target){
   *(uint8_t *)&zero_word=0u;
   int32_t error=g2_lfs_file_flushedwrite(filesystem,file,&zero_word,1u);
   if(error<0)return error;
  }
 }
 int32_t result=g2_lfs_file_flushedwrite(filesystem,file,buffer,size);
 if(result>=0)lfs350_put(file,48u,lfs350_get(file,48u)&0xfff7ffffu);
 return result;
}
