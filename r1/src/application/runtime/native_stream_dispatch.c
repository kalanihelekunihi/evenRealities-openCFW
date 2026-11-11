/* Stock R1 0x8a1e0: the timer record, not the stream owner, is argument zero. */
#include <stdint.h>
#include "../board/native_watchdog.h"
extern uint32_t r1_stream_sample_rate_copy(const void *,uint32_t,uint32_t,void *,uint32_t,uint32_t);
extern uint32_t r1_stream_deferred_cleanup(void *);
static inline uint32_t word(uint32_t p,uint32_t offset)
{return *(volatile uint32_t *)(uintptr_t)(p+offset);}
static inline uint32_t half(uint32_t p,uint32_t offset)
{return *(volatile uint16_t *)(uintptr_t)(p+offset);}
static inline uint32_t byte(uint32_t p,uint32_t offset)
{return *(volatile uint8_t *)(uintptr_t)(p+offset);}
static inline void put_word(uint32_t p,uint32_t offset,uint32_t value)
{*(volatile uint32_t *)(uintptr_t)(p+offset)=value;}
static inline void put_half(uint32_t p,uint32_t offset,uint32_t value)
{*(volatile uint16_t *)(uintptr_t)(p+offset)=(uint16_t)value;}
static inline void put_byte(uint32_t p,uint32_t offset,uint32_t value)
{*(volatile uint8_t *)(uintptr_t)(p+offset)=(uint8_t)value;}
void r1_stream_timer_dispatch(void *timer)
{
    uint32_t object=word((uint32_t)(uintptr_t)timer,12);
    if(!object)return;
    uint32_t ops=word(object,12);
    if(!ops || !word(ops,8) || !word(object,20))return;
    uint32_t rate=byte(object,16);
    if(!rate)return;
    uint32_t width=half(object,28);
    if(!width)return;
    uint32_t chunk=rate*width;
    if(!chunk)return;
    if(word(object,24)>=chunk)put_word(object,24,0);
    ops=word(object,12);
    uint32_t buffer=word(object,20),cursor=word(object,24);
    uint32_t read_callback=word(ops,8);
    uint32_t requested=half(object,28);
    uint32_t context=word(object,36);
    uint32_t got=((uint32_t (*)(uint32_t,uint32_t,uint32_t))(uintptr_t)read_callback)(buffer+cursor,requested,context);
    width=half(object,28);
    if(width!=got)return;
    uint32_t end=width+cursor;
    uint32_t wrapped=(end==chunk);
    put_word(object,24,wrapped?0:end);
    struct r1_native_list *list=(struct r1_native_list *)(uintptr_t)(object+44);
    uint32_t base=wrapped?chunk-width:word(object,24)-width;
    uint32_t sample=word(object,20)+base;
    put_byte(object,40,byte(object,40)|2u);
    void *node=r1_native_list_head(list);
    while(node){
        uint32_t listener=(uint32_t)(uintptr_t)node;
        uint32_t flags=half(listener,20);
        if(!(flags&1u)){
            uint32_t callback=word(listener,16);
            if(callback){
                uint32_t mode=byte(listener,14);
                uint32_t fire=0,data=sample,length=0;
                if(mode==1){
                    uint32_t listener_rate=byte(listener,13);
                    uint32_t current_rate=byte(object,16);
                    if(listener_rate==current_rate)fire=1;
                    else{
                        /* BFI preserves bit zero and truncates the accumulator. */
                        listener_rate=byte(listener,13);
                        current_rate=byte(object,16);
                        if(listener_rate!=current_rate){
                            flags=(flags&1u)|(((listener_rate+(flags>>1))&0x7fffu)<<1);
                            put_half(listener,20,flags);
                            current_rate=byte(object,16);
                            if(current_rate<=(flags>>1)){
                                flags=(flags&1u)|((((flags>>1)-current_rate)&0x7fffu)<<1);
                                put_half(listener,20,flags);fire=1;
                            }
                        }
                    }
                    if(fire)length=half(object,28);
                }else if(mode==0 && wrapped){
                    uint32_t current_rate=byte(object,16);
                    uint32_t listener_rate=byte(listener,13);
                    if(current_rate==listener_rate){data=word(object,20);length=(uint16_t)chunk;}
                    else{
                        buffer=word(object,20);width=half(object,28);data=buffer+chunk;
                        length=(uint16_t)r1_stream_sample_rate_copy((const void *)(uintptr_t)buffer,current_rate,chunk,(void *)(uintptr_t)data,listener_rate,width);
                        callback=word(listener,16);
                    }
                    fire=1;
                }
                if(fire)((void (*)(void *,uint32_t,uint32_t))(uintptr_t)callback)(node,data,length);
            }
        }
        node=r1_native_list_next(list,node);
    }
    uint32_t flags=byte(object,40)&~2u;
    put_byte(object,40,flags);
    if(flags&4u)(void)r1_stream_deferred_cleanup((void *)(uintptr_t)object);
}
