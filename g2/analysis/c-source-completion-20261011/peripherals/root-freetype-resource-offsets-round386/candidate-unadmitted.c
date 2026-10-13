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
