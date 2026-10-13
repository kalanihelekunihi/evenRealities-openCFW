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
