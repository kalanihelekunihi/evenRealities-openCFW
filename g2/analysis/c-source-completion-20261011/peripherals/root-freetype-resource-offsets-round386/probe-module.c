#include <stdint.h>
static uint32_t draw360_word(const void *p,uint32_t offset)
{return *(const volatile uint32_t *)((const uint8_t *)p+offset);}
static void draw360_store(void *p,uint32_t offset,uint32_t value)
{*(volatile uint32_t *)((uint8_t *)p+offset)=value;}
static void *draw360_pointer(const void *p,uint32_t offset)
{return (void *)(uintptr_t)draw360_word(p,offset);}
void audio_uart_checksum_copy(void *destination,const void *source,uint32_t length) {
    volatile uint8_t *d=destination;
    const volatile uint8_t *s=source;
    while(length && ((uintptr_t)s&3u)) { *d++=*s++; --length; }
    if(!length) return;
    if(((uintptr_t)d&3u)==0u) {
        while(length>=16u) {
            uint32_t a=*(const volatile uint32_t *)(s+0);
            uint32_t b=*(const volatile uint32_t *)(s+4);
            uint32_t c=*(const volatile uint32_t *)(s+8);
            uint32_t e=*(const volatile uint32_t *)(s+12);
            *(volatile uint32_t *)(d+0)=a;
            *(volatile uint32_t *)(d+4)=b;
            *(volatile uint32_t *)(d+8)=c;
            *(volatile uint32_t *)(d+12)=e;
            s+=16;d+=16;length-=16;
        }
        if(length&8u) {
            uint32_t a=*(const volatile uint32_t *)(s+0);
            uint32_t b=*(const volatile uint32_t *)(s+4);
            *(volatile uint32_t *)(d+0)=a;
            *(volatile uint32_t *)(d+4)=b;
            s+=8;d+=8;
        }
        if(length&4u) { *(volatile uint32_t *)d=*(const volatile uint32_t *)s;s+=4;d+=4; }
        if(length&2u) { *(volatile uint16_t *)d=*(const volatile uint16_t *)s;s+=2;d+=2; }
        if(length&1u) *d=*s;
    } else {
        while(length>=4u) {
            uint32_t a=*(const volatile uint32_t *)s;
            if(((uintptr_t)d&1u)==0u) {
                *(volatile uint16_t *)d=(uint16_t)a;
                *(volatile uint16_t *)(d+2)=(uint16_t)(a>>16);
            } else {
                d[0]=(uint8_t)a;
                *(volatile uint16_t *)(d+1)=(uint16_t)(a>>8);
                d[3]=(uint8_t)(a>>24);
            }
            s+=4;d+=4;length-=4;
        }
        while(length--) *d++=*s++;
    }
}
int32_t audio_uart_font_path_compare(const char *left,const char *right) {
    for(;;) {
        uint32_t a=(uint8_t)*left;
        uint32_t b=(uint8_t)*right;
        if(a==0u||a!=b) return (int32_t)(a-b);
        ++left;++right;
    }
}

/* Whole FT_Stream_Seek5288e0..52891452bytes. Callback count0 result is failure boolean. */
uint32_t audio_uart_ft_stream_seek_5288e0(void *stream,uint32_t position)
{
 if(draw360_word(stream,20u)!=0u){
  uint32_t callback=draw360_word(stream,20u);
  uint32_t result=((uint32_t (*)(void *,uint32_t,void *,uint32_t))(uintptr_t)callback)(stream,position,0,0u);
  if(result!=0u)return 85u;
 }else if(draw360_word(stream,4u)<position)return 85u;
 draw360_store(stream,8u,position);return 0u;
}
/* Whole FT_Stream_Skip528914..52892820bytes. */
uint32_t audio_uart_ft_stream_skip_528914(void *stream,int32_t distance)
{if(distance<0)return 85u;return audio_uart_ft_stream_seek_5288e0(stream,draw360_word(stream,8u)+(uint32_t)distance);}
/* Whole FT_Stream_ReadAt528936..52899292bytes; short-read advances position. */
uint32_t audio_uart_ft_stream_read_at_528936(void *stream,uint32_t offset,void *buffer,uint32_t count)
{
 if(offset>=draw360_word(stream,4u))return 85u;
 uint32_t actual;
 if(draw360_word(stream,20u)!=0u){
  uint32_t callback=draw360_word(stream,20u);
  actual=((uint32_t (*)(void *,uint32_t,void *,uint32_t))(uintptr_t)callback)(stream,offset,buffer,count);
 }else{
  actual=draw360_word(stream,4u)-offset;
  if(count<actual)actual=count;
  uint32_t address=draw360_word(stream,0u)+offset;
  audio_uart_checksum_copy(buffer,(const void *)(uintptr_t)address,actual);
 }
 draw360_store(stream,8u,offset+actual);
 return actual<count?85u:0u;
}
/* Whole FT_Stream_Read528928..52893614bytes. */
uint32_t audio_uart_ft_stream_read_528928(void *stream,void *buffer,uint32_t count)
{return audio_uart_ft_stream_read_at_528936(stream,draw360_word(stream,8u),buffer,count);}
/* Common C representation of whole BE16/BE32 bodies; preserve all native read/order/ABI branches. */
static uint32_t ft382_read_be(void *stream,int32_t *error,uint32_t width)
{
 *error=0;
 if(draw360_word(stream,8u)+(width-1u)>=draw360_word(stream,4u)){*error=85;return 0u;}
 uint8_t local[4];const volatile uint8_t *data;
 if(draw360_word(stream,20u)!=0u){
  uint32_t offset=draw360_word(stream,8u),callback=draw360_word(stream,20u);
  uint32_t actual=((uint32_t (*)(void *,uint32_t,void *,uint32_t))(uintptr_t)callback)(stream,offset,local,width);
  if(actual!=width){*error=85;return 0u;}
  data=local;
 }else data=(const volatile uint8_t *)(uintptr_t)(draw360_word(stream,0u)+draw360_word(stream,8u));
 uint32_t value=0u;
 if(data!=0)for(uint32_t i=0;i<width;i++)value=(value<<8u)|data[i];
 draw360_store(stream,8u,draw360_word(stream,8u)+width);return value;
}
/* Whole FT_Stream_ReadUShort528b4a..528ba8 94bytes. */
uint32_t audio_uart_ft_stream_read_ushort_528b4a(void *stream,int32_t *error)
{return (uint16_t)ft382_read_be(stream,error,2u);}
/* Whole FT_Stream_ReadULong528ba8..528c14108bytes. */
uint32_t audio_uart_ft_stream_read_ulong_528ba8(void *stream,int32_t *error)
{return ft382_read_be(stream,error,4u);}
/* Whole FT_Get_Module5273b8..5273f2 58bytes. */
void *audio_uart_ft_get_module_5273b8(void *library,const char *name)
{
 if(library==0 || name==0)return 0;
 uint32_t cursor=(uint32_t)(uintptr_t)library+20u;
 uint32_t limit=cursor+draw360_word(library,16u)*4u;
 for(;cursor<limit;cursor+=4u){
  void *module=draw360_pointer((void *)(uintptr_t)cursor,0u);
  const char *module_name=draw360_pointer(draw360_pointer(module,0u),8u);
  if(audio_uart_font_path_compare(module_name,name)==0)return draw360_pointer((void *)(uintptr_t)cursor,0u);
 }
 return 0;
}

static uint32_t word(const void *p,uint32_t o) {
    return *(const uint32_t *)(const void *)((const uint8_t *)p+o);
}

void audio_uart_font_mem_free(void *memory,void *block) { /* 0x529256 */
    if(block!=0) {
        uint32_t callback=word(memory,8u);
        ((void (*)(void *,void *))(uintptr_t)callback)(memory,block);
    }
}
void audio_uart_buffer_zero(void *destination,uint32_t length,uint32_t fill)
{
    volatile uint8_t *p=(volatile uint8_t *)destination;
    for (uint32_t i=0;i<length;i++) p[i]=(uint8_t)fill;
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
extern void *audio_uart_font_mem_realloc_items(void *,int32_t,int32_t,int32_t,void *,int32_t *);
extern void audio_uart_ft_sort_core_56798c(void *,uint32_t,uint32_t,uint32_t,int32_t (*)(const void *,const void *));
/* Whole callback528272..52829838bytes, authenticated pointer word528710. */
int32_t audio_uart_ft_resource_ref_compare_528272(const void *left,const void *right)
{
 int32_t a=*(const volatile int16_t *)left,b=*(const volatile int16_t *)right;
 if(a<b)return -1;
 b=*(const volatile int16_t *)right;a=*(const volatile int16_t *)left;
 return b<a?1:0;
}
/* Whole qsort wrapper567c4c..567c6424bytes. Void contract; native scratch R0/R1 not API output. */
void audio_uart_ft_qsort_567c4c(void *base,uint32_t count,uint32_t width,int32_t (*compare)(const void *,const void *))
{if(base!=0 && compare!=0)audio_uart_ft_sort_core_56798c(base,count,count,width,compare);}
/* Whole FT_Raccess_Get_DataOffsets528298..528470472bytes. */
uint32_t audio_uart_ft_raccess_offsets_528298(void *library,void *stream,uint32_t map,uint32_t data,uint32_t tag,uint32_t sort,void **offsets_out,int32_t *count_out)
{
 void *memory=draw360_pointer(library,0u);int32_t error=(int32_t)audio_uart_ft_stream_seek_5288e0(stream,map);
 if(error!=0)return (uint32_t)error;
 int32_t types=(int16_t)audio_uart_ft_stream_read_ushort_528b4a(stream,&error);
 if(error!=0)return (uint32_t)error;
 types++;
 if(types>=4080)return 8u;
 volatile int32_t *count=count_out;
 for(int32_t i=0;i<types;i++){
  uint32_t current_tag=audio_uart_ft_stream_read_ulong_528ba8(stream,&error);
  if(error!=0)return (uint32_t)error;
  int32_t subcount=(int16_t)audio_uart_ft_stream_read_ushort_528b4a(stream,&error);
  if(error!=0)return (uint32_t)error;
  int32_t relative=(int16_t)audio_uart_ft_stream_read_ushort_528b4a(stream,&error);
  if(error!=0)return (uint32_t)error;
  if(current_tag!=tag)continue;
  *count=subcount+1;
  if((uint32_t)*count-1u>2726u)return 8u;
  error=(int32_t)audio_uart_ft_stream_seek_5288e0(stream,map+(uint32_t)relative);
  if(error!=0)return (uint32_t)error;
  uint8_t *references=audio_uart_font_mem_realloc_items(memory,8,0,*count,0,&error);
  if(error!=0)return (uint32_t)error;
  for(int32_t j=0;j<*count;j++){
   uint16_t id=(uint16_t)audio_uart_ft_stream_read_ushort_528b4a(stream,&error);
   *(volatile uint16_t *)(references+(uint32_t)j*8u)=id;
   if(error!=0)goto cleanup;
   error=(int32_t)audio_uart_ft_stream_skip_528914(stream,2);
   if(error!=0)goto cleanup;
   uint32_t attributes=audio_uart_ft_stream_read_ulong_528ba8(stream,&error);
   if(error!=0)goto cleanup;
   error=(int32_t)audio_uart_ft_stream_skip_528914(stream,4);
   if(error!=0)goto cleanup;
   if((int32_t)attributes<0){error=8;goto cleanup;}
   draw360_store(references+(uint32_t)j*8u,4u,attributes&0x00ffffffu);
  }
  if((uint8_t)sort!=0u){
   audio_uart_ft_qsort_567c4c(references,(uint32_t)*count,8u,audio_uart_ft_resource_ref_compare_528272);
   /* Native trace-disabled loop still rereads caller-owned count. */
   for(int32_t j=0;j<*count;j++){}
  }
  uint32_t *offsets=audio_uart_font_mem_realloc_items(memory,4,0,*count,0,&error);
  if(error==0){
   for(int32_t j=0;j<*count;j++)offsets[j]=draw360_word(references+(uint32_t)j*8u,4u)+data;
   *offsets_out=offsets;error=0;
  }
 cleanup:
  audio_uart_font_mem_free(memory,references);return (uint32_t)error;
 }
 return 1u;
}
