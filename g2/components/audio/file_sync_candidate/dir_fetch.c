/* Stock 0x4cbedc specialized pinned LittleFS lfs_dir_fetchmatch(-1,-1,NULL,NULL,NULL).
 * Layout and disk effects follow pinned upstream LittleFS lfs.c lines 1110-1394. */
#include <stdint.h>
#include <stddef.h>
extern int32_t g2_lfs_bd_read(void *,const void *,void *,uint32_t,uint32_t,
                               uint32_t,void *,uint32_t);
extern int32_t g2_log_transport_queue_failure(const char *,...);
extern int32_t g2_lfs_gstate_hasmovehere(void *state,const void *pair);
typedef struct {
    uint32_t pair[2],rev,off,etag;
    uint16_t count;
    uint8_t erased,split;
    uint32_t tail[2];
} g2_mdir;
_Static_assert(sizeof(g2_mdir)==32,"stock LittleFS metadata layout");
static uint32_t rd32(const void *p,uint32_t off) {return *(const uint32_t *)((const uint8_t *)p+off);}
static void wr32(void *p,uint32_t off,uint32_t v) {*(uint32_t *)((uint8_t *)p+off)=v;}
static uint32_t *word(void *p,uint32_t off) {return (uint32_t *)((uint8_t *)p+off);}
static uint32_t tag_size(uint32_t t) {return t&0x3ffu;}
static uint32_t tag_id(uint32_t t) {return (t>>10u)&0x3ffu;}
static uint32_t tag_type1(uint32_t t) {return (t>>20u)&0x700u;}
static uint32_t tag_type2(uint32_t t) {return (t>>20u)&0x780u;}
static uint32_t tag_type3(uint32_t t) {return (t>>20u)&0x7ffu;}
static uint32_t tag_chunk(uint32_t t) {return (t>>20u)&0xffu;}
static uint32_t tag_dsize(uint32_t t) {return 4u+tag_size(t+(tag_size(t)==0x3ffu));}
static uint32_t crc32(uint32_t crc,const void *buffer,uint32_t size) {
    static const uint32_t tab[16]={0,0x1db71064,0x3b6e20c8,0x26d930ac,
        0x76dc4190,0x6b6b51f4,0x4db26158,0x5005713c,
        0xedb88320,0xf00f9344,0xd6d6a3e8,0xcb61b38c,
        0x9b64c2b0,0x86d3d2d4,0xa00ae278,0xbdbdf21c};
    const uint8_t *p=(const uint8_t *)buffer;
    for(uint32_t i=0;i<size;i++) {
        crc=(crc>>4u)^tab[(crc^p[i])&15u];
        crc=(crc>>4u)^tab[(crc^(p[i]>>4u))&15u];
    }
    return crc;
}
static int32_t bd_crc(void *fs,uint32_t block,uint32_t off,
                      uint32_t size,uint32_t *crc) {
    uint32_t block_size=rd32((const void *)(uintptr_t)rd32(fs,0x68u),0x1cu);
    for(uint32_t i=0;i<size;) {
        uint8_t bytes[8];uint32_t diff=size-i;
        if(diff>8u) diff=8u;
        int32_t err=g2_lfs_bd_read(fs,NULL,fs,block_size-i,block,off+i,bytes,diff);
        if(err) return err;
        *crc=crc32(*crc,bytes,diff);i+=diff;
    }
    return 0;
}
static const char bad_pair_format[]="%s:%d:error: Corrupted dir pair at {0x%x, 0x%x}%s\n";
static const char source_path[]="D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\littlefs\\lfs.c";
typedef int32_t (*g2_lfs_match)(void *,uint32_t,const void *);
int32_t g2_lfs_dir_fetchmatch(void *filesystem,void *directory,
                              const uint32_t *pair,uint32_t mask,
                              uint32_t wanted,uint16_t *id,
                              g2_lfs_match match,void *data) {
    uint8_t *fs=(uint8_t *)filesystem;
    g2_mdir *dir=(g2_mdir *)directory;
    uint32_t block_count=rd32(fs,0x6cu);
    if(block_count && (pair[0]>=block_count || pair[1]>=block_count)) return -84;
    uint32_t besttag=UINT32_MAX;
    uint32_t revs[2]={0u,0u};uint32_t r=0u;
    for(uint32_t i=0;i<2u;i++) {
        int32_t err=g2_lfs_bd_read(fs,NULL,fs,4u,pair[i],0u,&revs[i],4u);
        if(err && err!=-84) return err;
        if(err!=-84 && (int32_t)(revs[i]-revs[(i+1u)&1u])>0) r=i;
    }
    dir->pair[0]=pair[r];dir->pair[1]=pair[(r+1u)&1u];
    dir->rev=revs[r];dir->off=0u;
    for(uint32_t attempt=0;attempt<2u;attempt++) {
        uint32_t off=0u,ptag=UINT32_MAX,crc=crc32(UINT32_MAX,&dir->rev,4u);
        uint32_t temp_count=0u,temp_tail[2]={UINT32_MAX,UINT32_MAX};
        uint32_t tempbesttag=besttag;
        uint32_t maybe_erased=0u,has_fcrc=0u,fcrc[2]={0u,0u};
        uint8_t temp_split=0u;
        uint32_t block_size=rd32((const void *)(uintptr_t)rd32(fs,0x68u),0x1cu);
        for(;;) {
            uint32_t raw_tag;
            off+=tag_dsize(ptag);
            int32_t err=g2_lfs_bd_read(fs,NULL,fs,block_size,dir->pair[0],off,&raw_tag,4u);
            if(err) {if(err==-84) break;return err;}
            crc=crc32(crc,&raw_tag,4u);
            uint32_t tag=__builtin_bswap32(raw_tag)^ptag;
            if(tag&0x80000000u) {
                maybe_erased=tag_type2(ptag)==0x500u;
                break;
            }
            if(off+tag_dsize(tag)>block_size) break;
            ptag=tag;
            if(tag_type2(tag)==0x500u) {
                uint32_t dcrc;
                err=g2_lfs_bd_read(fs,NULL,fs,block_size,dir->pair[0],off+4u,&dcrc,4u);
                if(err) {if(err==-84) break;return err;}
                if(crc!=dcrc) break;
                ptag^=(tag_chunk(tag)&1u)<<31u;
                uint32_t seed=rd32(fs,0x2cu);
                wr32(fs,0x2cu,crc32(seed,&crc,4u));
                besttag=tempbesttag;
                dir->off=off+tag_dsize(tag);dir->etag=ptag;
                dir->count=(uint16_t)temp_count;
                dir->tail[0]=temp_tail[0];dir->tail[1]=temp_tail[1];
                dir->split=temp_split;crc=UINT32_MAX;
                continue;
            }
            err=bd_crc(fs,dir->pair[0],off+4u,tag_dsize(tag)-4u,&crc);
            if(err) {if(err==-84) break;return err;}
            if(tag_type1(tag)==0u) {
                if(tag_id(tag)>=temp_count) temp_count=tag_id(tag)+1u;
            } else if(tag_type1(tag)==0x400u) {
                temp_count+=(uint32_t)(int32_t)(int8_t)tag_chunk(tag);
                if(tag==(0x4ff00000u|(tempbesttag&0xffc00u)))
                    tempbesttag|=0x80000000u;
                else if(tempbesttag!=UINT32_MAX &&
                        tag_id(tag)<=tag_id(tempbesttag))
                    tempbesttag+=(uint32_t)((int32_t)(int8_t)tag_chunk(tag)*1024);
            } else if(tag_type1(tag)==0x600u) {
                temp_split=(uint8_t)(tag_chunk(tag)&1u);
                err=g2_lfs_bd_read(fs,NULL,fs,block_size,dir->pair[0],off+4u,temp_tail,8u);
                if(err) {if(err==-84) break;return err;}
            } else if(tag_type3(tag)==0x5ffu) {
                err=g2_lfs_bd_read(fs,NULL,fs,block_size,dir->pair[0],off+4u,fcrc,8u);
                if(err && err!=-84) return err;
                has_fcrc=1u;
            }
            if((mask&tag)==(mask&wanted)) {
                uint32_t disk[2]={dir->pair[0],off+4u};
                int32_t result=match(data,tag,disk);
                if(result<0) {if(result==-84) break;return result;}
                if(result==0) tempbesttag=tag;
                else if((tag&0x7ffffc00u)==(tempbesttag&0x7ffffc00u))
                    tempbesttag=UINT32_MAX;
                else if(result==2 && tag_id(tag)<=tag_id(tempbesttag))
                    tempbesttag=tag|0x80000000u;
            }
        }
        if(dir->off==0u) {
            uint32_t t=dir->pair[0];dir->pair[0]=dir->pair[1];dir->pair[1]=t;
            dir->rev=revs[(r+1u)&1u];continue;
        }
        dir->erased=0u;
        uint32_t prog_size=rd32((const void *)(uintptr_t)rd32(fs,0x68u),0x18u);
        if(maybe_erased && dir->off%prog_size==0u && has_fcrc) {
            uint32_t fcrc_actual=UINT32_MAX;
            int32_t err=bd_crc(fs,dir->pair[0],dir->off,fcrc[0],&fcrc_actual);
            if(err && err!=-84) return err;
            dir->erased=(uint8_t)(fcrc_actual==fcrc[1]);
        }
        uint32_t *gdisk=word(fs,0x3cu);
        if(g2_lfs_gstate_hasmovehere(gdisk,dir->pair)) {
            if(tag_id(gdisk[0])==tag_id(besttag)) besttag|=0x80000000u;
            else if(besttag!=UINT32_MAX && tag_id(gdisk[0])<tag_id(besttag))
                besttag-=0x400u;
        }
        if(id) *id=(uint16_t)(tag_id(besttag)<dir->count ? tag_id(besttag) : dir->count);
        if((besttag&0x80000000u)==0u) return (int32_t)besttag;
        if(tag_id(besttag)<dir->count) return -2;
        return 0;
    }
    g2_log_transport_queue_failure(bad_pair_format,source_path,1385,
                                    dir->pair[0],dir->pair[1],"");
    return -84;
}
int32_t g2_lfs_dir_fetch(void *filesystem,void *directory,const uint32_t *pair) {
    return g2_lfs_dir_fetchmatch(filesystem,directory,pair,UINT32_MAX,
                                  UINT32_MAX,NULL,NULL,NULL);
}
