
/* Full find_unicode_charmap52594a..5259be116bytes, backward UCS-4 preference. */
uint32_t audio_uart_ft_find_unicode_charmap_52594a(void *face)
{
 uint32_t array=draw360_word(face,40u);
 if(array==0u)return 38u;
 uint32_t cursor=array+draw360_word(face,36u)*4u-4u;
 for(;cursor>=array;cursor-=4u){
  void *map=draw360_pointer((void *)(uintptr_t)cursor,0u);
  if(draw360_word(map,4u)!=0x756e6963u)continue;
  uint16_t platform=*(const volatile uint16_t *)((const uint8_t *)map+8u);
  if((platform==3u && *(const volatile uint16_t *)((const uint8_t *)map+10u)==10u)
   || (*(const volatile uint16_t *)((const uint8_t *)map+8u)==0u
    && *(const volatile uint16_t *)((const uint8_t *)map+10u)==4u)){
   draw360_store(face,92u,draw360_word((void *)(uintptr_t)cursor,0u));return 0u;
  }
 }
 cursor=array+draw360_word(face,36u)*4u-4u;
 for(;cursor>=array;cursor-=4u){
  void *map=draw360_pointer((void *)(uintptr_t)cursor,0u);
  if(draw360_word(map,4u)==0x756e6963u){draw360_store(face,92u,draw360_word((void *)(uintptr_t)cursor,0u));return 0u;}
 }
 return 38u;
}
/* Full LVGL filesystem read callback567734..56777a70bytes. */
extern uint32_t audio_uart_lv_fs_file_read_4c6f46(void *,void *,uint32_t,uint32_t *);
uint32_t audio_uart_ft_lv_fs_stream_io_567734(void *stream,uint32_t offset,void *buffer,uint32_t count)
{
 if(count==0u && draw360_word(stream,4u)<offset)return 1u;
 void *file=draw360_pointer(stream,12u);
 if(draw360_word(stream,8u)!=offset)(void)audio_uart_lv_fs_file_seek_4c6fba(file,offset,0u);
 if(count==0u)return 0u;
 uint32_t read_count;
 uint32_t result=audio_uart_lv_fs_file_read_4c6f46(file,buffer,count,&read_count);
 return (uint8_t)result==0u?read_count:0u;
}
/* Full LVGL filesystem close callback5676f8..56771a34bytes. */
void audio_uart_ft_lv_fs_stream_close_5676f8(void *stream)
{
 void *file=draw360_pointer(stream,12u);
 (void)audio_uart_lv_fs_file_close_4c6ee0(file);
 audio_uart_lv_pool_free_48429e((void *)(uintptr_t)0x20000354u,file);
 draw360_store(stream,12u,0u);draw360_store(stream,4u,0u);draw360_store(stream,0u,0u);
}
/* Full product FT_Stream_Open5675e8..5676a0184bytes, pinned LVGL adapter contract. */
uint32_t audio_uart_ft_stream_open_path_5675e8(void *stream,const char *pathname)
{
 if(stream==0)return 40u;
 draw360_store(stream,12u,0u);draw360_store(stream,16u,(uint32_t)(uintptr_t)pathname);
 draw360_store(stream,0u,0u);draw360_store(stream,8u,0u);
 draw360_store(stream,20u,0u);draw360_store(stream,24u,0u);
 uint32_t file[3];
 if((uint8_t)audio_uart_lv_fs_file_open_4c6d9a(file,pathname,2u)!=0u)return 1u;
 (void)audio_uart_lv_fs_file_seek_4c6fba(file,0u,2u);
 uint32_t size;
 if((uint8_t)audio_uart_lv_fs_file_tell_4c7018(file,&size)!=0u){(void)audio_uart_lv_fs_file_close_4c6ee0(file);return 81u;}
 draw360_store(stream,4u,size);
 (void)audio_uart_lv_fs_file_seek_4c6fba(file,0u,0u);
 void *file_p=audio_uart_lv_pool_allocate_484180((void *)(uintptr_t)0x20000354u,12u);
 if(file_p==0){
  audio_uart_lvgl_log(3u,"D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\lvgl_v9.3\\lvgl_ambiq_demo\\lvgl_ttf\\src\\am_ftsystem.c",129u,"FT_Stream_Open","Asserted at expression: %s (%s)","file_p != NULL","Out of memory");
  for(;;){}
 }
 if(file_p==0){(void)audio_uart_lv_fs_file_close_4c6ee0(file);return 81u;}
 uint32_t a=file[0],b=file[1],c=file[2];
 draw360_store(file_p,0u,a);draw360_store(file_p,4u,b);draw360_store(file_p,8u,c);
 draw360_store(stream,12u,(uint32_t)(uintptr_t)file_p);
 draw360_store(stream,20u,(uint32_t)(uintptr_t)&audio_uart_ft_lv_fs_stream_io_567734);
 draw360_store(stream,24u,(uint32_t)(uintptr_t)&audio_uart_ft_lv_fs_stream_close_5676f8);
 return 0u;
}
