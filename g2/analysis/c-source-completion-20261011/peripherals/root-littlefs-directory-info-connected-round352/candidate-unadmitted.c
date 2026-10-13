
/* Entire lfs_dir_getinfo4cbf38..4cbfdd166bytes; pinned lfs.c1415..1447. Draft. */
int32_t audio_file_lfs_dir_getinfo_4cbf38(void *filesystem,void *directory,uint32_t identifier,void *information)
{
 uint8_t *info=information;uint32_t id=(uint16_t)identifier;
 if(id==0x3ffu){lfs351_dotcopy((char *)info+8u,"/");*(volatile uint8_t *)info=2u;return 0;}
 int32_t tag=audio_file_lfs_dir_get(filesystem,directory,0x780ffc00u,
  (lfs351_word(filesystem,112u)+1u)|(id<<10u),info+8u);
 if(tag<0)return tag;
 *(volatile uint8_t *)info=(uint8_t)(((uint32_t)tag>>20u)&0x7ffu);
 uint32_t pair[2]={identifier,(uint32_t)(uintptr_t)information};
 tag=audio_file_lfs_dir_get(filesystem,directory,0x700ffc00u,0x20000008u|(id<<10u),pair);
 if(tag<0)return tag;
 audio_file_lfs_ctz_fromle32(pair);
 uint32_t type=((uint32_t)tag>>20u)&0x7ffu;
 if(type==0x202u)lfs351_store(information,4u,pair[1]);
 else if(type==0x201u)lfs351_store(information,4u,(uint32_t)tag&0x3ffu);
 return 0;
}
