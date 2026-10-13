
/* Full FT_List_Finalize529378..5293be70bytes. Cache next before destructor/free. */
void audio_uart_ft_list_finalize_529378(void *list,void (*destroy)(void *,void *,void *),void *memory,void *user)
{
 if(list==0 || memory==0)return;
 void *node=draw360_pointer(list,0u);
 while(node!=0){
  void *next=draw360_pointer(node,4u);
  void *data=draw360_pointer(node,8u);
  if(destroy!=0)destroy(memory,data,user);
  audio_uart_font_mem_free(memory,node);node=next;
 }
 draw360_store(list,0u,0u);draw360_store(list,4u,0u);
}
