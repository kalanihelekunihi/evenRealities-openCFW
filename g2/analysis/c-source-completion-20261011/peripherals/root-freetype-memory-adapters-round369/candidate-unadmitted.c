
/* Five complete FT system-memory adapters, authenticated product pool handle. */
extern void *audio_uart_lv_pool_allocate_484180(void *,uint32_t);
extern void *audio_uart_lv_pool_realloc_484234(void *,void *,uint32_t);
void *audio_uart_ft_memory_alloc_5676d4(void *memory,int32_t size)
{(void)memory;return audio_uart_lv_pool_allocate_484180((void *)(uintptr_t)0x20000354u,(uint32_t)size);}
void *audio_uart_ft_memory_realloc_5676e0(void *memory,int32_t old_size,int32_t new_size,void *block)
{(void)memory;(void)old_size;return audio_uart_lv_pool_realloc_484234((void *)(uintptr_t)0x20000354u,block,(uint32_t)new_size);}
void audio_uart_ft_memory_free_5676ec(void *memory,void *block)
{(void)memory;audio_uart_lv_pool_free_48429e((void *)(uintptr_t)0x20000354u,block);}
void *audio_uart_ft_new_memory_5676a0(void)
{
 void *memory=audio_uart_lv_pool_allocate_484180((void *)(uintptr_t)0x20000354u,16u);
 if(memory!=0){
  draw360_store(memory,0u,0u);
  draw360_store(memory,4u,(uint32_t)(uintptr_t)&audio_uart_ft_memory_alloc_5676d4);
  draw360_store(memory,12u,(uint32_t)(uintptr_t)&audio_uart_ft_memory_realloc_5676e0);
  draw360_store(memory,8u,(uint32_t)(uintptr_t)&audio_uart_ft_memory_free_5676ec);
 }
 return memory;
}
void audio_uart_ft_done_memory_5676c6(void *memory)
{audio_uart_lv_pool_free_48429e((void *)(uintptr_t)0x20000354u,memory);}
