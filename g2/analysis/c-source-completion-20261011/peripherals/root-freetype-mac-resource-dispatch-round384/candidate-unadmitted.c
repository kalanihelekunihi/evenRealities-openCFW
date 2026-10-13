extern uint32_t audio_uart_ft_raccess_header_528064(void *,void *,uint32_t,uint32_t *,uint32_t *);
extern uint32_t audio_uart_ft_raccess_offsets_528298(void *,void *,uint32_t,uint32_t,uint32_t,uint32_t,void **,int32_t *);
extern uint32_t audio_uart_ft_mac_read_post_525e16(void *,void *,void *,int32_t,int32_t,void **);
extern uint32_t audio_uart_ft_mac_read_sfnt_5260a4(void *,void *,void *,int32_t,int32_t,void **);
/* Whole IsMacResource5261ac..52628a222bytes. Cached allocator, full status, fresh face pointer. */
uint32_t audio_uart_ft_read_mac_resource_5261ac(void *library,void *stream,uint32_t offset,int32_t index,void **face)
{
 void *memory=draw360_pointer(library,0u);
 uint32_t map,data;
 uint32_t error=audio_uart_ft_raccess_header_528064(library,stream,offset,&map,&data);
 if(error!=0u)return error;
 void *offsets;int32_t count;
 error=audio_uart_ft_raccess_offsets_528298(library,stream,map,data,0x504f5354u,1u,&offsets,&count);
 if(error==0u){
  error=audio_uart_ft_mac_read_post_525e16(library,stream,offsets,count,index,face);
  audio_uart_font_mem_free(memory,offsets);
  offsets=0;
  if(error==0u)draw360_store(*face,0u,1u);
  return error;
 }
 error=audio_uart_ft_raccess_offsets_528298(library,stream,map,data,0x73666e74u,0u,&offsets,&count);
 if(error==0u){
  /* Cortex-M SDIV contract includes divide-by-zero and INT_MIN/-1 results. */
  int32_t quotient=count==0?0:(index==(-2147483647-1) && count==-1?(-2147483647-1):index/count);
  int32_t internal=(int32_t)((uint32_t)index-(uint32_t)count*(uint32_t)quotient);
  error=audio_uart_ft_mac_read_sfnt_5260a4(library,stream,offsets,count,internal,face);
  audio_uart_font_mem_free(memory,offsets);
  offsets=0;
  if(error==0u)draw360_store(*face,0u,(uint32_t)count);
 }
 return error;
}
