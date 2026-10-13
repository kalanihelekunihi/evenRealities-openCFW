
/* Whole ft_open_face_internal5264a6..5267ee840bytes, FreeType2.9.1 with Mac branches. */
extern uint32_t audio_uart_ft_stream_new_524f96(void *,const void *,void **);
extern uint32_t audio_uart_ft_open_driver_face_5259be(void *,void **,uint32_t,int32_t,int32_t,void *,void **);
extern void audio_uart_ft_list_add_529304(void *,void *);
extern uint32_t audio_uart_ft_new_glyph_slot_525386(void *,void **);
extern uint32_t audio_uart_ft_new_size_52687e(void *,void **);
extern uint32_t audio_uart_ft_stream_seek_5288e0(void *,uint32_t);
extern uint32_t audio_uart_ft_open_ps_sfnt_525d32(void *,void *,int32_t,int32_t,void *,void **);
extern uint32_t audio_uart_ft_load_mac_face_526452(void *,void *,int32_t,void **,const void *);
uint32_t audio_uart_ft_open_face_internal_5264a6(void *library,const void *args,int32_t face_index,void **out,uint32_t test_mac_fonts)
{
 void *driver=0,*memory=0,*stream=0,*face=0,*node=0;
 if((out==0 && face_index>=0) || args==0)return 6u;
 uint32_t external=(*(const volatile uint8_t *)args&2u)!=0u && draw360_word(args,16u)!=0u;
 uint32_t error=audio_uart_ft_stream_new_524f96(library,args,&stream);
 if(error!=0u)goto scan_failure;
 memory=draw360_pointer(library,0u);
 if((*(const volatile uint8_t *)args&8u)!=0u && draw360_word(args,20u)!=0u){
  driver=draw360_pointer(args,20u);
  if((*(const volatile uint8_t *)draw360_pointer(driver,0u)&1u)!=0u){
   int32_t count=0;void *params=0;
   if((*(const volatile uint8_t *)args&16u)!=0u){count=(int32_t)draw360_word(args,24u);params=draw360_pointer(args,28u);}
   error=audio_uart_ft_open_driver_face_5259be(driver,&stream,external,face_index,count,params,&face);
   if(error==0u)goto success;
  }else error=32u;
  audio_uart_ft_stream_free_52502a(stream,external);goto failure;
 }
 error=11u;
 uint32_t cursor=(uint32_t)(uintptr_t)library+20u;
 uint32_t limit=cursor+draw360_word(library,16u)*4u;
 for(;cursor<limit;cursor+=4u){
  void *candidate=draw360_pointer((void *)(uintptr_t)cursor,0u);
  if((*(const volatile uint8_t *)draw360_pointer(candidate,0u)&1u)==0u)continue;
  driver=candidate;int32_t count=0;void *params=0;
  if((*(const volatile uint8_t *)args&16u)!=0u){count=(int32_t)draw360_word(args,24u);params=draw360_pointer(args,28u);}
  error=audio_uart_ft_open_driver_face_5259be(driver,&stream,external,face_index,count,params,&face);
  if(error==0u)goto success;
  if((uint8_t)test_mac_fonts!=0u && audio_uart_font_path_compare(draw360_pointer(draw360_pointer(draw360_pointer((void *)(uintptr_t)cursor,0u),0u),8u),"truetype")==0 && (uint8_t)error==142u){
   error=audio_uart_ft_stream_seek_5288e0(stream,0u);
   if(error!=0u)break;
   error=audio_uart_ft_open_ps_sfnt_525d32(library,stream,face_index,count,params,out);
   if(error==0u){audio_uart_ft_stream_free_52502a(stream,external);return error;}
  }
  if((uint8_t)error!=2u)break;
 }
scan_failure:
 if((uint8_t)error==81u || (uint8_t)error==2u || (uint8_t)error==85u){
  if((uint8_t)test_mac_fonts!=0u){
   error=audio_uart_ft_load_mac_face_526452(library,stream,face_index,out,args);
   if(error==0u){audio_uart_ft_stream_free_52502a(stream,external);return error;}
  }
  if((uint8_t)error==2u)error=2u;
 }
 audio_uart_ft_stream_free_52502a(stream,external);
 goto failure;
success:
 {
  int32_t alloc_error;node=audio_uart_font_mem_alloc(memory,12,&alloc_error);error=(uint32_t)alloc_error;
  if(error!=0u)goto failure;
 }
 draw360_store(node,8u,(uint32_t)(uintptr_t)face);
 audio_uart_ft_list_add_529304((uint8_t *)draw360_pointer(face,96u)+16u,node);
 if(face_index>=0){
  error=audio_uart_ft_new_glyph_slot_525386(face,0);
  if(error!=0u)goto failure;
  void *size;error=audio_uart_ft_new_size_52687e(face,&size);
  if(error!=0u)goto failure;
  draw360_store(face,88u,(uint32_t)(uintptr_t)size);error=0u;
 }
 if((*(const volatile uint8_t *)((const uint8_t *)face+8u)&1u)!=0u){
  volatile int16_t *height=(volatile int16_t *)((uint8_t *)face+74u);
  if(*height<0)*height=(int16_t)(0u-(uint32_t)(int32_t)*height);
  if((*(const volatile uint8_t *)((const uint8_t *)face+8u)&32u)==0u)
   *(volatile int16_t *)((uint8_t *)face+78u)=*height;
 }
 if((*(const volatile uint8_t *)((const uint8_t *)face+8u)&2u)!=0u){
  uint32_t i=0;
  for(;(int32_t)i<(int32_t)draw360_word(face,28u);i++){
   uint8_t *strike=(uint8_t *)draw360_pointer(face,32u)+i*16u;
   volatile int16_t *height=(volatile int16_t *)(void *)strike;
   if(*height<0)*height=(int16_t)(0u-(uint32_t)(int32_t)*height);
   if((int32_t)draw360_word(strike,8u)<0)draw360_store(strike,8u,0u-draw360_word(strike,8u));
   if((int32_t)draw360_word(strike,12u)<0)draw360_store(strike,12u,0u-draw360_word(strike,12u));
   if(*height<0 || (int32_t)draw360_word(strike,8u)<0 || (int32_t)draw360_word(strike,12u)<0)
    for(uint32_t j=0;j<8u;j++)((volatile uint16_t *)(void *)strike)[j]=0u;
  }
 }
 {
  void *internal=draw360_pointer(face,128u);
  draw360_store(internal,0u,65536u);draw360_store(internal,4u,0u);draw360_store(internal,8u,0u);draw360_store(internal,12u,65536u);
  draw360_store(internal,16u,0u);draw360_store(internal,20u,0u);draw360_store(internal,64u,1u);
  *(volatile uint8_t *)((uint8_t *)internal+56u)=255u;
 }
 if(out!=0)draw360_store(out,0u,(uint32_t)(uintptr_t)face);
 else (void)audio_uart_ft_done_face_526814(face);
 return error;
failure:
 if(node!=0)(void)audio_uart_ft_done_face_526814(face);
 else if(face!=0)audio_uart_ft_destroy_face_5258a8(memory,face,driver);
 return error;
}
