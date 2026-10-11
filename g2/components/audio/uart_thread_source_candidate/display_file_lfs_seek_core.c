/* LittleFS lfs_file_seek native 0x4ce3bc; pinned lfs.c semantics and
 * native cache-offset fast path are retained. */
#include <stdint.h>
int32_t audio_file_lfs_size_core(void *,void *); /* 0x4ce472 */
extern uint32_t g2_lfs_ctz_index(void *,uint32_t *); /* selected 0x4cd6e4 */
extern int32_t g2_lfs_file_flush(void *,void *); /* selected 0x4cde54 */
static uint32_t word(const void *p,uint32_t offset) {
    return *(const uint32_t *)(const void *)((const uint8_t *)p+offset);
}
static void setword(void *p,uint32_t offset,uint32_t value) {
    *(uint32_t *)(void *)((uint8_t *)p+offset)=value;
}
int32_t audio_file_lfs_seek_core(void *filesystem,void *file,int32_t offset,uint32_t whence) {
    uint32_t old=word(file,0x34u);
    uint32_t target=old;
    if(whence==0u) target=(uint32_t)offset;
    else if(whence==1u) target=(uint32_t)offset+old;
    else if(whence==2u) target=(uint32_t)offset+(uint32_t)audio_file_lfs_size_core(filesystem,file);
    if(word(filesystem,0x74u)<target) return -22;
    if(old==target) return (int32_t)target;
    if((word(file,0x30u)&0x40000u)!=0u &&
       word(file,0x3cu)!=word((void *)(uintptr_t)word(filesystem,0x68u),0x1cu)) {
        uint32_t previous=old;
        uint32_t old_block=g2_lfs_ctz_index(filesystem,&previous);
        uint32_t next=target;
        uint32_t new_block=g2_lfs_ctz_index(filesystem,&next);
        if(old_block==new_block && next>=word(file,0x44u) &&
           next<word(file,0x48u)+word(file,0x44u)) {
            setword(file,0x34u,target);
            setword(file,0x3cu,next);
            return (int32_t)target;
        }
    }
    int32_t err=g2_lfs_file_flush(filesystem,file);
    if(err!=0) return err;
    setword(file,0x34u,target);
    return (int32_t)target;
}
int32_t audio_file_lfs_size_core(void *filesystem,void *file) { /* 0x4ce472 */
    (void)filesystem;
    uint32_t size=word(file,0x2cu);
    if((word(file,0x30u)&0x20000u)!=0u) {
        uint32_t position=word(file,0x34u);
        return (int32_t)(position>size?position:size);
    }
    return (int32_t)size;
}
