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
