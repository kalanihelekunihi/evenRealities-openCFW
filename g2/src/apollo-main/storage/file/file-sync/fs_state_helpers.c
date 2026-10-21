/* Pinned LittleFS state helpers, stock 0x4cf5ec/0x4cf570/0x4cbefc. */
#include <stdint.h>
extern int32_t g2_lfs_dir_getslice(void *,void *,uint32_t,uint32_t,
                                    uint32_t,void *,uint32_t);
extern void g2_file_close_error(const char *,const char *,uint32_t);
static uint32_t *word(void *p,uint32_t off) {return (uint32_t *)((uint8_t *)p+off);}
static const char path[]="D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\littlefs\\lfs.c";
static const char low_assert[]="lfs_tag_size(lfs->gstate.tag) > 0x000 || orphans >= 0";
static const char high_assert[]="lfs_tag_size(lfs->gstate.tag) < 0x1ff || orphans <= 0";
void g2_lfs_fs_prepmove(void *filesystem,uint32_t id,const uint32_t *pair) {
    uint32_t *state=word(filesystem,0x30u);
    uint32_t move=id==0x3ffu ? 0u : (0x4ff00000u|(id<<10u));
    state[0]=(state[0]&0x800003ffu)|move;
    state[1]=id==0x3ffu ? 0u : pair[0];
    state[2]=id==0x3ffu ? 0u : pair[1];
}
int32_t g2_lfs_fs_preporphans(void *filesystem,int8_t orphans) {
    uint32_t *state=word(filesystem,0x30u);
    uint32_t count=state[0]&0x3ffu;
    if(count==0u && orphans<0) g2_file_close_error(low_assert,path,4892u);
    if(count>0x1feu && orphans>0) g2_file_close_error(high_assert,path,4893u);
    state[0]=(state[0]+(int32_t)orphans);
    state[0]=(state[0]&0x7fffffffu)|((state[0]&0x3ffu)!=0u ? 0x80000000u : 0u);
    return 0;
}
int32_t g2_lfs_dir_getgstate(void *filesystem,void *directory,void *gstate) {
    uint32_t temp[3];
    int32_t tag=g2_lfs_dir_getslice(filesystem,directory,0x7ff00000u,
                                     0x7ff0000cu,0u,temp,12u);
    if(tag<0 && tag!=-2) return tag;
    if(tag!=-2) {
        uint32_t *out=(uint32_t *)gstate;
        for(uint32_t i=0;i<3u;i++) out[i]^=temp[i];
    }
    return 0;
}
