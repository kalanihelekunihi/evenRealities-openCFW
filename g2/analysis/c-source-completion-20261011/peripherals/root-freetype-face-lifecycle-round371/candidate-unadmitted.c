
/* FT_New_Face525ade..525b02 36bytes; flags/path/stream only initialized. */
extern uint32_t audio_uart_ft_open_face_internal_5264a6(void *,const void *,int32_t,void **,uint32_t);
uint32_t audio_uart_ft_new_face_525ade(void *library,const char *pathname,int32_t index,void **out)
{
 if(pathname==0)return 6u;
 uint32_t args[8];args[0]=4u;args[3]=(uint32_t)(uintptr_t)pathname;args[4]=0u;
 return audio_uart_ft_open_face_internal_5264a6(library,args,index,out,1u);
}
/* FT_Done_Face526814..52687c104bytes; native fresh reads preserved. */
extern void *audio_uart_ft_list_find_5292e6(void *,void *);
extern void audio_uart_ft_list_remove_529324(void *,void *);
extern void audio_uart_font_mem_free(void *,void *);
extern void audio_uart_ft_destroy_face_5258a8(void *,void *,void *);
uint32_t audio_uart_ft_done_face_526814(void *face)
{
 if(face==0)return 35u;
 if(draw360_word(face,96u)==0u)return 35u;
 void *internal=draw360_pointer(face,128u);
 uint32_t count=draw360_word(internal,64u)-1u;
 draw360_store(draw360_pointer(face,128u),64u,count);
 if((int32_t)draw360_word(draw360_pointer(face,128u),64u)>=1)return 0u;
 void *driver=draw360_pointer(face,96u);
 void *memory=draw360_pointer(driver,8u);
 void *node=audio_uart_ft_list_find_5292e6((uint8_t *)driver+16u,face);
 if(node==0)return 35u;
 audio_uart_ft_list_remove_529324((uint8_t *)driver+16u,node);
 audio_uart_font_mem_free(memory,node);
 audio_uart_ft_destroy_face_5258a8(memory,face,driver);return 0u;
}

/* Complete FT_List_Find5292e6..52930430bytes. */
void *audio_uart_ft_list_find_5292e6(void *list,void *data)
{
 if(list==0)return 0;
 void *node=draw360_pointer(list,0u);
 while(node!=0){if(draw360_pointer(node,8u)==data)return node;node=draw360_pointer(node,4u);}
 return 0;
}
/* Complete FT_List_Remove529324..52934836bytes; detached node retained. */
void audio_uart_ft_list_remove_529324(void *list,void *node)
{
 if(list==0 || node==0)return;
 void *previous=draw360_pointer(node,0u),*next=draw360_pointer(node,4u);
 if(previous!=0)draw360_store(previous,4u,(uint32_t)(uintptr_t)next);
 else draw360_store(list,0u,(uint32_t)(uintptr_t)next);
 if(next!=0)draw360_store(next,0u,(uint32_t)(uintptr_t)previous);
 else draw360_store(list,4u,(uint32_t)(uintptr_t)previous);
}
