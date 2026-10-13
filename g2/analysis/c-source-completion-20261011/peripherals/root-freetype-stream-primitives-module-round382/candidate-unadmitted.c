
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
