/* Native FreeType memory-reallocate array helpers 0x52919c/0x5291e4.
 * The library-owned allocator vtable remains the actual runtime contract. */
#include <stdint.h>
extern void audio_uart_font_mem_free(void *,void *); /* selected 0x529256 */
extern void audio_uart_buffer_zero(void *,uint32_t,uint32_t); /* selected 0x43c0e4 */
static uint32_t word(const void *p,uint32_t o) {
    return *(const uint32_t *)(const void *)((const uint8_t *)p+o);
}
static void *realloc_base(void *memory,int32_t item_size,int32_t old_count,
                          int32_t new_count,void *old_block,int32_t *error) { /* 0x5291e4 */
    int32_t status=0;
    void *result=old_block;
    if(old_count<0||new_count<0||item_size<0) status=6;
    else if(new_count==0||item_size==0) {
        audio_uart_font_mem_free(memory,old_block);
        result=0;
    } else if(new_count>INT32_MAX/item_size) status=10;
    else if(old_count==0) {
        uint32_t callback=word(memory,4u);
        result=((void *(*)(void *,int32_t))(uintptr_t)callback)(memory,item_size*new_count);
        if(result==0) status=64;
    } else {
        uint32_t callback=word(memory,12u);
        void *new_block=((void *(*)(void *,int32_t,int32_t,void *))(uintptr_t)callback)
            (memory,item_size*old_count,item_size*new_count,old_block);
        if(new_block==0) status=64;
        else result=new_block;
    }
    *error=status;
    return result;
}
void *audio_uart_font_mem_realloc_raw(void *memory,int32_t item_size,
                                      int32_t old_count,int32_t new_count,
                                      void *old_block,int32_t *error) { /* 0x5291e4 */
    return realloc_base(memory,item_size,old_count,new_count,old_block,error);
}
void *audio_uart_font_mem_realloc_items(void *memory,int32_t item_size,
                                        int32_t old_count,int32_t new_count,
                                        void *old_block,int32_t *error) { /* 0x52919c */
    int32_t status=0;
    void *result=realloc_base(memory,item_size,old_count,new_count,old_block,&status);
    if(status==0&&old_count<new_count) {
        uint32_t offset=(uint32_t)(item_size*old_count);
        uint32_t length=(uint32_t)(item_size*(new_count-old_count));
        audio_uart_buffer_zero((uint8_t *)result+offset,length,0u);
    }
    *error=status;
    return result;
}
