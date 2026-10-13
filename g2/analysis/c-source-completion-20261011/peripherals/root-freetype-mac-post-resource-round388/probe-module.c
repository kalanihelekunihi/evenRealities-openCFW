#include <stdint.h>
static uint32_t draw360_word(const void *p,uint32_t offset)
{return *(const volatile uint32_t *)((const uint8_t *)p+offset);}
static void draw360_store(void *p,uint32_t offset,uint32_t value)
{*(volatile uint32_t *)((uint8_t *)p+offset)=value;}
static void *draw360_pointer(const void *p,uint32_t offset)
{return (void *)(uintptr_t)draw360_word(p,offset);}

extern void *audio_uart_font_mem_alloc(void *,int32_t,int32_t *);
extern void audio_uart_font_mem_free(void *,void *);
extern uint32_t audio_uart_ft_stream_seek_5288e0(void *,uint32_t);
extern uint32_t audio_uart_ft_open_face_internal_5264a6(void *,const void *,int32_t,void **,uint32_t);
void audio_uart_ft_stream_open_memory_5288b8(void *stream,const void *base,uint32_t size)
{
 draw360_store(stream,0u,(uint32_t)(uintptr_t)base);draw360_store(stream,4u,size);
 draw360_store(stream,8u,0u);draw360_store(stream,32u,0u);
 draw360_store(stream,20u,0u);draw360_store(stream,24u,0u);
}
void audio_uart_ft_stream_close_5288ce(void *stream)
{
 if(stream!=0 && draw360_word(stream,24u)!=0u){uint32_t callback=draw360_word(stream,24u);((void (*)(void *))(uintptr_t)callback)(stream);}
}

/* Whole ft_lookup_PS_in_sfnt_stream525c08..525d32 298bytes. */
extern uint32_t audio_uart_ft_stream_read_ulong_528ba8(void *,int32_t *);
extern uint32_t audio_uart_ft_stream_read_ushort_528b4a(void *,int32_t *);
extern uint32_t audio_uart_ft_stream_skip_528914(void *,int32_t);
uint32_t audio_uart_ft_lookup_ps_sfnt_525c08(void *stream,int32_t index,uint32_t *offset,uint32_t *length,uint8_t *cid)
{
 *offset=0u;*length=0u;*cid=0u;
 int32_t error=index;
 uint32_t tag=audio_uart_ft_stream_read_ulong_528ba8(stream,&error);
 if(error!=0)return (uint32_t)error;
 if(tag!=0x74797031u)return 2u;
 uint32_t count=(uint16_t)audio_uart_ft_stream_read_ushort_528b4a(stream,&error);
 if(error!=0)return (uint32_t)error;
 error=(int32_t)audio_uart_ft_stream_skip_528914(stream,6);
 if(error!=0)return (uint32_t)error;
 int32_t found=-1;*cid=0u;
 for(uint32_t i=0;i<count;i++){
  uint32_t table=audio_uart_ft_stream_read_ulong_528ba8(stream,&error);
  if(error!=0)return (uint32_t)error;
  error=(int32_t)audio_uart_ft_stream_skip_528914(stream,4);
  if(error!=0)return (uint32_t)error;
  uint32_t value=audio_uart_ft_stream_read_ulong_528ba8(stream,&error);*offset=value;
  if(error!=0)return (uint32_t)error;
  value=audio_uart_ft_stream_read_ulong_528ba8(stream,&error);*length=value;
  if(error!=0)return (uint32_t)error;
  if(table==0x43494420u){found=(int32_t)((uint32_t)found+1u);*offset+=22u;*length-=22u;*cid=1u;if(index<0)return 0u;}
  else if(table==0x54595031u){found=(int32_t)((uint32_t)found+1u);*offset+=24u;*length-=24u;*cid=0u;if(index<0)return 0u;}
  if(index>=0 && found==index)return 0u;
 }
 return 142u;
}
/* Whole open_face_from_buffer525b6e..525c08 154bytes, typed stream ownership. */
extern void audio_uart_ft_memory_stream_close_525b02(void *);
extern uint32_t audio_uart_ft_new_memory_stream_525b20(void *,void *,uint32_t,void (*)(void *),void **);
extern void *audio_uart_ft_get_module_5273b8(void *,const char *);
uint32_t audio_uart_ft_open_face_from_buffer_525b6e(void *library,void *buffer,uint32_t size,int32_t index,const char *driver_name,void **out)
{
 void *stream=0,*memory=draw360_pointer(library,0u);
 uint32_t error=audio_uart_ft_new_memory_stream_525b20(library,buffer,size,audio_uart_ft_memory_stream_close_525b02,&stream);
 if(error!=0u){audio_uart_font_mem_free(memory,buffer);return error;}
 uint32_t args[8];args[0]=2u;args[4]=(uint32_t)(uintptr_t)stream;
 if(driver_name!=0){args[0]=10u;args[5]=(uint32_t)(uintptr_t)audio_uart_ft_get_module_5273b8(library,driver_name);}
 error=audio_uart_ft_open_face_internal_5264a6(library,args,index,out,0u);
 if(error==0u){void *face=draw360_pointer(out,0u);draw360_store(face,8u,draw360_word(face,8u)&~1024u);}
 else{audio_uart_ft_stream_close_5288ce(stream);audio_uart_font_mem_free(memory,stream);}
 return error;
}
/* Whole open_face_PS_from_sfnt_stream525d32..525e16 228bytes. */
extern uint32_t audio_uart_ft_stream_read_528928(void *,void *,uint32_t);
uint32_t audio_uart_ft_open_ps_sfnt_525d32(void *library,void *stream,int32_t index,int32_t count,void *params,void **out)
{
 (void)count;(void)params;
 void *memory=draw360_pointer(library,0u);
 if(index>0)index=(int32_t)((uint32_t)index&65535u);
 uint32_t original=draw360_word(stream,8u),offset,length;uint8_t cid;
 uint32_t error=audio_uart_ft_lookup_ps_sfnt_525c08(stream,index,&offset,&length,&cid);
 if(error==0u){
  if(draw360_word(stream,4u)<offset || draw360_word(stream,4u)-offset<length)error=8u;
  else{
   error=audio_uart_ft_stream_seek_5288e0(stream,offset+original);
   if(error==0u){
    int32_t alloc_error;void *buffer=audio_uart_font_mem_alloc(memory,(int32_t)length,&alloc_error);error=(uint32_t)alloc_error;
    if(error==0u){
     error=audio_uart_ft_stream_read_528928(stream,buffer,length);
     if(error==0u){if(index>=0)index=0;error=audio_uart_ft_open_face_from_buffer_525b6e(library,buffer,length,index,cid?"cid":"type1",out);}
     else audio_uart_font_mem_free(memory,buffer);
    }
   }
  }
 }
 if((uint8_t)error==2u){uint32_t rewind=audio_uart_ft_stream_seek_5288e0(stream,original);if(rewind!=0u)return rewind;}
 return error;
}

/* Whole memory_stream_close525b02..525b20 30bytes. */
void audio_uart_ft_memory_stream_close_525b02(void *stream)
{
 void *memory=draw360_pointer(stream,28u);
 audio_uart_font_mem_free(memory,draw360_pointer(stream,0u));
 draw360_store(stream,0u,0u);draw360_store(stream,4u,0u);
 draw360_store(stream,0u,0u);draw360_store(stream,24u,0u);
}
/* Whole new_memory_stream525b20..525b6e78bytes; do not invent stream-memory initialization. */
uint32_t audio_uart_ft_new_memory_stream_525b20(void *library,void *buffer,uint32_t size,void (*close)(void *),void **out)
{
 if(library==0)return 33u;
 if(buffer==0)return 6u;
 draw360_store(out,0u,0u);
 void *memory=draw360_pointer(library,0u);
 int32_t error;void *stream=audio_uart_font_mem_alloc(memory,40,&error);
 if(error==0){audio_uart_ft_stream_open_memory_5288b8(stream,buffer,size);draw360_store(stream,24u,(uint32_t)(uintptr_t)close);draw360_store(out,0u,(uint32_t)(uintptr_t)stream);}
 return (uint32_t)error;
}

extern void audio_uart_checksum_copy(void *,const void *,uint32_t);
extern int32_t audio_uart_font_path_compare(const char *,const char *);

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

/* Mac_Read_POST_Resource: native 0x525e16..0x52609c, 646 bytes.
 * Analysis candidate only until native comparisons and ownership checks pass. */
uint32_t audio_uart_ft_mac_read_post_525e16(void *library,void *stream,void *offsets,int32_t count,int32_t index,void **face)
{
 void *memory=draw360_pointer(library,0u);
 uint32_t error=1u;
 if(index==-1)index=0;
 if(index!=0)return error;
 uint32_t total=0u;
 for(int32_t i=0;i<count;i++){
  error=audio_uart_ft_stream_seek_5288e0(stream,draw360_word(offsets,(uint32_t)i*4u));
  if(error!=0u)return error;
  int32_t read_error=0;
  uint32_t length=audio_uart_ft_stream_read_ulong_528ba8(stream,&read_error);
  if(read_error!=0)return (uint32_t)read_error;
  if(length>0xffffffu || 0xffffffu-length<total+6u)return 9u;
  total+=length+6u;
 }
 if(total+2u<6u)return 10u;
 int32_t alloc_error=0;
 uint8_t *pfb=(uint8_t *)audio_uart_font_mem_alloc(memory,(int32_t)(total+2u),&alloc_error);
 if(alloc_error!=0)return (uint32_t)alloc_error;
 pfb[0]=0x80u;pfb[1]=1u;pfb[2]=0u;pfb[3]=0u;pfb[4]=0u;pfb[5]=0u;
 uint32_t used=6u,header=2u,segment=0u;
 int32_t prior_type=1;
 int32_t i=0;
 while(i<count){
  error=audio_uart_ft_stream_seek_5288e0(stream,draw360_word(offsets,(uint32_t)i*4u));
  if(error!=0u)goto fail;
  int32_t read_error=0;
  uint32_t resource_length=audio_uart_ft_stream_read_ulong_528ba8(stream,&read_error);
  if(read_error!=0){error=(uint32_t)read_error;goto fail;}
  if(resource_length>0x7fffffffu){error=9u;goto fail;}
  uint32_t flags=audio_uart_ft_stream_read_ushort_528b4a(stream,&read_error);
  if(read_error!=0){error=(uint32_t)read_error;goto fail;}
  error=10u;
  int32_t type=(int32_t)(flags>>8);
  if(type!=0){
   uint32_t payload=resource_length<3u?0u:resource_length-2u;
   if(type==prior_type)segment+=payload;
   else{
    if(total+2u<header+3u)goto fail;
    pfb[header]=(uint8_t)segment;pfb[header+1]=(uint8_t)(segment>>8);
    pfb[header+2]=(uint8_t)(segment>>16);pfb[header+3]=(uint8_t)(segment>>24);
    if(type==5)break;
    if(total+2u<used+6u)goto fail;
    pfb[used]=0x80u;pfb[used+1]=(uint8_t)type;
    header=used+2u;
    pfb[header]=0u;pfb[header+1]=0u;pfb[header+2]=0u;pfb[header+3]=0u;
    used+=6u;segment=payload;
   }
   if(total<used || total<payload+used)goto fail;
   error=audio_uart_ft_stream_read_528928(stream,pfb+used,payload);
   if(error!=0u)goto fail;
   used+=payload;error=0u;prior_type=type;
  }
  i++;
 }
 error=10u;
 if(used+2u<=total+2u){
  pfb[used]=0x80u;pfb[used+1]=3u;
  if(header+3u<=total+2u){
   pfb[header]=(uint8_t)segment;pfb[header+1]=(uint8_t)(segment>>8);
   pfb[header+2]=(uint8_t)(segment>>16);pfb[header+3]=(uint8_t)(segment>>24);
   return audio_uart_ft_open_face_from_buffer_525b6e(library,pfb,used+2u,0,"type1",face);
  }
 }
fail:
 if(error!=0u)error=1u;
 audio_uart_font_mem_free(memory,pfb);
 return error;
}
