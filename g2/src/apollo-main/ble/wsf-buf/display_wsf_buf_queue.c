/* Native Cordio WsfBufAlloc 0x530446, WsfQueueEnq/Deq 0x538c24/0x538c4a. */
#include <stdint.h>
struct wsf_pool_desc {uint16_t size;uint16_t pad;uint32_t reserved;void *free_head;};
_Static_assert(sizeof(struct wsf_pool_desc)==12u,"WSF pool ABI");
struct wsf_queue {void *head;void *tail;};
extern struct wsf_pool_desc *audio_wsf_pool_list; /* pointer cell RAM 0x20074eec */
extern volatile uint8_t audio_wsf_pool_count; /* RAM 0x20075044 */
extern void audio_wsf_cs_enter(void); /* native 0x52b8a4 */
extern void audio_wsf_cs_exit(void); /* native 0x52b8b6 */
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint8_t,const char *,const char *,const char *,uint32_t,const char *,...);
extern uint32_t compressed_log_output(uint32_t,const char *,const char *,...);
static const char module[]="wsf.buf";
static const char path[]="D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\cordio\\wsf\\sources\\port\\freertos\\wsf_buf.c";
static const char function[]="WsfBufAlloc";
static const char fail[]="WsfBufAlloc failed len:%u";
static const char fail_short[]="[wsf.buf]WsfBufAlloc failed len:%u";
void *audio_wsf_buffer_alloc(uint16_t size) {
    struct wsf_pool_desc *pool=audio_wsf_pool_list;
    uint8_t count=audio_wsf_pool_count;
    while(count!=0u) {
        if(size<=pool->size) {
            audio_wsf_cs_enter();
            uint32_t *block=(uint32_t *)pool->free_head;
            if(block!=0) {
                pool->free_head=(void *)(uintptr_t)block[0];
                block[1]=0u;
                audio_wsf_cs_exit();
                return block;
            }
            audio_wsf_cs_exit();
        }
        pool++;count--;
    }
    if((audio_log_flags()&2u)!=0u)
        audio_log_extended(1u,module,path,function,321u,fail,size);
    if((audio_log_flags()&1u)!=0u||(audio_log_flags()&4u)!=0u)
        (void)compressed_log_output(0x04400000u,fail_short,fail_short,size);
    return 0;
}
