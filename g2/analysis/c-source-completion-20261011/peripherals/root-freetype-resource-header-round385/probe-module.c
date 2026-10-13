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

static uint32_t ft385_be32(const uint8_t *p)
{return ((uint32_t)p[0]<<24u)|((uint32_t)p[1]<<16u)|((uint32_t)p[2]<<8u)|p[3];}
/* Whole FT_Raccess_Get_HeaderInfo528064..528272526bytes. Output writes persist on later failure. */
uint32_t audio_uart_ft_raccess_header_528064(void *library,void *stream,uint32_t resource,uint32_t *map_out,uint32_t *data_out)
{
 (void)library;uint8_t h[32];int32_t error=(int32_t)audio_uart_ft_stream_seek_5288e0(stream,resource);
 if(error!=0)return (uint32_t)error;
 error=(int32_t)audio_uart_ft_stream_read_528928(stream,h,16u);
 if(error!=0)return (uint32_t)error;
 if(h[0]>=128u || h[4]>=128u || h[8]>=128u || h[12]>=128u)return 2u;
 volatile uint32_t *data=data_out;
 *data=ft385_be32(h);
 uint32_t map=ft385_be32(h+4u),data_length=ft385_be32(h+8u),map_length=ft385_be32(h+12u);
 if(map==0u)return 2u;
 if((int32_t)*data<(int32_t)map){if((int32_t)(map-data_length)<(int32_t)*data)return 2u;}
 else if((int32_t)(*data-map_length)<(int32_t)map)return 2u;
 if((int32_t)(0x7fffffffu-data_length)<(int32_t)*data || (int32_t)(0x7fffffffu-map_length)<(int32_t)map || (int32_t)(0x7fffffffu-*data-data_length)<(int32_t)resource || (int32_t)(0x7fffffffu-map-map_length)<(int32_t)resource || draw360_word(stream,4u)<data_length+*data+resource || draw360_word(stream,4u)<map_length+map+resource)return 2u;
 *data=resource+*data;map+=resource;
 error=(int32_t)audio_uart_ft_stream_seek_5288e0(stream,map);
 if(error!=0)return (uint32_t)error;
 h[31]=(uint8_t)(h[15]+1u);
 error=(int32_t)audio_uart_ft_stream_read_528928(stream,h+16u,16u);
 if(error!=0)return (uint32_t)error;
 uint32_t all_zero=1u,all_equal=1u;
 for(uint32_t i=0;i<16u;i++){if(h[i+16u]!=0u)all_zero=0u;if(h[i+16u]!=h[i])all_equal=0u;}
 if(all_zero==0u && all_equal==0u)return 2u;
 /* Native BE reader overwrites the skip status through its error output. */
 (void)audio_uart_ft_stream_skip_528914(stream,8);
 int32_t type_offset=(int16_t)audio_uart_ft_stream_read_ushort_528b4a(stream,&error);
 if(error!=0)return (uint32_t)error;
 if(type_offset<0)return 2u;
 uint32_t type_position=map+(uint32_t)type_offset;
 error=(int32_t)audio_uart_ft_stream_seek_5288e0(stream,type_position);
 if(error==0)*map_out=type_position;
 return (uint32_t)error;
}
