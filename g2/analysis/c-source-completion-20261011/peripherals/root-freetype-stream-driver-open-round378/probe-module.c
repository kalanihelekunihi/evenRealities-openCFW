#include <stdint.h>
static uint32_t draw360_word(const void *p,uint32_t offset)
{return *(const volatile uint32_t *)((const uint8_t *)p+offset);}
static void draw360_store(void *p,uint32_t offset,uint32_t value)
{*(volatile uint32_t *)((uint8_t *)p+offset)=value;}
static void *draw360_pointer(const void *p,uint32_t offset)
{return (void *)(uintptr_t)draw360_word(p,offset);}

extern void *audio_uart_font_mem_alloc(void *,int32_t,int32_t *);
extern void audio_uart_font_mem_free(void *,void *);
void audio_uart_ft_cmap_done_internal_526e38(void *cmap)
{
 void *clazz=draw360_pointer(cmap,12u);
 void *face=draw360_pointer(cmap,0u);
 void *memory=draw360_pointer(face,100u);
 if(draw360_word(clazz,8u)!=0u){uint32_t callback=draw360_word(clazz,8u);((void (*)(void *))(uintptr_t)callback)(cmap);}
 audio_uart_font_mem_free(memory,cmap);
}
void audio_uart_ft_destroy_charmaps_52586e(void *face,void *memory)
{
 if(face==0)return;
 uint32_t index=0u;
 while((int32_t)index<(int32_t)draw360_word(face,36u)){
  void *array=draw360_pointer(face,40u);
  audio_uart_ft_cmap_done_internal_526e38(draw360_pointer(array,index*4u));
  draw360_store(draw360_pointer(face,40u),index*4u,0u);index+=1u;
 }
 audio_uart_font_mem_free(memory,draw360_pointer(face,40u));
 draw360_store(face,40u,0u);draw360_store(face,36u,0u);
}

/* Whole FT_Stream_New524f96..52502a148bytes; output cleared before validation. */
extern void audio_uart_ft_stream_open_memory_5288b8(void *,const void *,uint32_t);
extern uint32_t audio_uart_ft_stream_open_path_5675e8(void *,const char *);
uint32_t audio_uart_ft_stream_new_524f96(void *library,const void *args,void **out)
{
 draw360_store(out,0u,0u);
 if(library==0)return 33u;
 if(args==0)return 6u;
 void *memory=draw360_pointer(library,0u);
 int32_t error;void *stream=audio_uart_font_mem_alloc(memory,40,&error);
 if(error!=0)return (uint32_t)error;
 draw360_store(stream,28u,(uint32_t)(uintptr_t)memory);
 if((*(const volatile uint8_t *)args&1u)!=0u)
  audio_uart_ft_stream_open_memory_5288b8(stream,draw360_pointer(args,4u),draw360_word(args,8u));
 else if((*(const volatile uint8_t *)args&4u)!=0u){
  error=(int32_t)audio_uart_ft_stream_open_path_5675e8(stream,draw360_pointer(args,12u));
  draw360_store(stream,16u,draw360_word(args,12u));
 }else if((*(const volatile uint8_t *)args&2u)!=0u && draw360_word(args,16u)!=0u){
  audio_uart_font_mem_free(memory,stream);stream=draw360_pointer(args,16u);
 }else error=6;
 if(error==0)draw360_store(stream,28u,(uint32_t)(uintptr_t)memory);
 else{audio_uart_font_mem_free(memory,stream);stream=0;}
 draw360_store(out,0u,(uint32_t)(uintptr_t)stream);return (uint32_t)error;
}
/* Whole open_face5259be..525ade288bytes; all seven call arguments explicit. */
extern uint32_t audio_uart_ft_find_unicode_charmap_52594a(void *);
uint32_t audio_uart_ft_open_driver_face_5259be(void *driver,void **stream_cell,uint32_t external,int32_t index,int32_t param_count,void *params,void **out)
{
 void *clazz=draw360_pointer(driver,12u);
 void *memory=draw360_pointer(driver,8u);
 void *internal=0;
 int32_t error;
 void *face=audio_uart_font_mem_alloc(memory,(int32_t)draw360_word(clazz,36u),&error);
 if(error!=0)goto failed;
 draw360_store(face,96u,(uint32_t)(uintptr_t)driver);draw360_store(face,100u,(uint32_t)(uintptr_t)memory);
 draw360_store(face,104u,draw360_word(stream_cell,0u));
 if((uint8_t)external!=0u)draw360_store(face,8u,draw360_word(face,8u)|1024u);
 internal=audio_uart_font_mem_alloc(memory,68,&error);
 if(error!=0)goto failed;
 draw360_store(face,128u,(uint32_t)(uintptr_t)internal);
 draw360_store(draw360_pointer(face,128u),52u,0u);
 for(uint32_t i=0;(int32_t)i<param_count && draw360_word(draw360_pointer(face,128u),52u)==0u;i++){
  if(draw360_word(params,i*8u)==0x696e6372u)
   draw360_store(draw360_pointer(face,128u),52u,draw360_word(params,i*8u+4u));
 }
 draw360_store(draw360_pointer(face,128u),60u,UINT32_MAX);
 if(draw360_word(clazz,48u)!=0u){
  uint32_t callback=draw360_word(clazz,48u);
  error=(int32_t)((uint32_t (*)(void *,void *,int32_t,int32_t,void *))(uintptr_t)callback)
   (draw360_pointer(stream_cell,0u),face,index,param_count,params);
 }
 draw360_store(stream_cell,0u,draw360_word(face,104u));
 if(error==0){
  uint32_t lookup=audio_uart_ft_find_unicode_charmap_52594a(face);
  if(lookup==0u || (uint8_t)lookup==38u){draw360_store(out,0u,(uint32_t)(uintptr_t)face);return (uint32_t)error;}
  error=(int32_t)lookup;
 }
failed:
 if(error!=0){
  audio_uart_ft_destroy_charmaps_52586e(face,memory);
  if(draw360_word(clazz,52u)!=0u){uint32_t callback=draw360_word(clazz,52u);((void (*)(void *))(uintptr_t)callback)(face);}
  audio_uart_font_mem_free(memory,internal);audio_uart_font_mem_free(memory,face);
  draw360_store(out,0u,0u);
 }
 return (uint32_t)error;
}

/* Whole FT_Stream_OpenMemory5288b8..5288ce22bytes. */
void audio_uart_ft_stream_open_memory_5288b8(void *stream,const void *base,uint32_t size)
{
 draw360_store(stream,0u,(uint32_t)(uintptr_t)base);draw360_store(stream,4u,size);
 draw360_store(stream,8u,0u);draw360_store(stream,32u,0u);
 draw360_store(stream,20u,0u);draw360_store(stream,24u,0u);
}
