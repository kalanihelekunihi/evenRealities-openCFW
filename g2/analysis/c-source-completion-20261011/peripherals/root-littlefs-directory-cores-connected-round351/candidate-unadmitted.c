
/* Whole directory cores:open4cd558..4cd5fd/read4cd60e..4cd6b9. Draft.
 * Pinned lfs.c2722..2821, nativeoffsetsandtagconstants preserved. */
extern int32_t audio_file_lfs_dir_find(void *,void *,const char **,uint16_t *);
extern int32_t audio_file_lfs_dir_get(void *,void *,uint32_t,uint32_t,void *);
extern void audio_file_lfs_ctz_fromle32(void *);
extern int32_t g2_lfs_dir_fetch(void *,void *,const uint32_t *);
extern void audio_file_lfs_mlist_append(void *,void *);
extern void *g2_lfs_cache_fill(void *,uint32_t,uint32_t);
extern int32_t audio_file_lfs_dir_getinfo_4cbf38(void *,void *,uint32_t,void *);
static uint32_t lfs351_word(const void *p,uint32_t offset)
{return *(const volatile uint32_t *)((const uint8_t *)p+offset);}
static void lfs351_store(void *p,uint32_t offset,uint32_t value)
{*(volatile uint32_t *)((uint8_t *)p+offset)=value;}
static uint16_t lfs351_half(const void *p,uint32_t offset)
{return *(const volatile uint16_t *)((const uint8_t *)p+offset);}
static void lfs351_storehalf(void *p,uint32_t offset,uint16_t value)
{*(volatile uint16_t *)((uint8_t *)p+offset)=value;}
int32_t audio_file_lfs_dir_open_core_4cd558(void *filesystem,void *directory,const char *path)
{
 uint8_t *d=directory;
 int32_t tag=audio_file_lfs_dir_find(filesystem,d+8u,&path,0);
 if(tag<0)return tag;
 if(((uint32_t)tag>>20u&0x7ffu)!=2u)return -20;
 uint32_t pair[2];uint32_t id=((uint32_t)tag>>10u)&0x3ffu;
 if(id==0x3ffu){pair[0]=lfs351_word(filesystem,32u);pair[1]=lfs351_word(filesystem,36u);}
 else {
  int32_t result=audio_file_lfs_dir_get(filesystem,d+8u,0x700ffc00u,0x20000008u|(id<<10u),pair);
  if(result<0)return result;
  audio_file_lfs_ctz_fromle32(pair);
 }
 int32_t result=g2_lfs_dir_fetch(filesystem,d+8u,pair);
 if(result!=0)return result;
 lfs351_store(directory,44u,lfs351_word(directory,8u));
 lfs351_store(directory,48u,lfs351_word(directory,12u));
 lfs351_storehalf(directory,4u,0u);lfs351_store(directory,40u,0u);
 *(volatile uint8_t *)(d+6u)=2u;audio_file_lfs_mlist_append(filesystem,directory);return 0;
}
static void lfs351_dotcopy(char *destination,const char *source)
{for(;;){uint8_t byte=*(const volatile uint8_t *)source++;*(volatile uint8_t *)destination++=byte;if(byte==0u)return;}}
int32_t audio_file_lfs_dir_read_core_4cd60e(void *filesystem,void *directory,void *information)
{
 uint8_t *d=directory,*info=information;
 (void)g2_lfs_cache_fill(info,264u,0u);
 if(lfs351_word(directory,40u)==0u){
  *(volatile uint8_t *)info=2u;lfs351_dotcopy((char *)info+8u,".");
  lfs351_store(directory,40u,lfs351_word(directory,40u)+1u);return 1;
 }else if(lfs351_word(directory,40u)==1u){
  *(volatile uint8_t *)info=2u;lfs351_dotcopy((char *)info+8u,"..");
  lfs351_store(directory,40u,lfs351_word(directory,40u)+1u);return 1;
 }
 for(;;){
  if(lfs351_half(directory,4u)==lfs351_half(directory,28u)){
   if(*(const volatile uint8_t *)(d+31u)==0u)return 0;
   int32_t result=g2_lfs_dir_fetch(filesystem,d+8u,(const uint32_t *)(d+32u));
   if(result!=0)return result;
   lfs351_storehalf(directory,4u,0u);
  }
  int32_t result=audio_file_lfs_dir_getinfo_4cbf38(filesystem,d+8u,lfs351_half(directory,4u),information);
  if(result!=0&&result!=-2)return result;
  lfs351_storehalf(directory,4u,(uint16_t)(lfs351_half(directory,4u)+1u));
  if(result!=-2)break;
 }
 lfs351_store(directory,40u,lfs351_word(directory,40u)+1u);return 1;
}
