
/* Whole native bounded-copy entry0x454778..0x4547ad; qualification draft. */
extern uint32_t g2_log_module_length(const char *);
extern void *audio_queue_copy_bytes(void *,const void *,uint32_t);
uint32_t audio_uart_lv_strlcpy_454778(char *destination,const char *source,uint32_t capacity)
{
 uint32_t length=g2_log_module_length(source);
 if(capacity!=0u){
  uint32_t count=length;
  if(length>=capacity)count=capacity-1u;
  (void)audio_queue_copy_bytes(destination,source,count);
  *(volatile uint8_t *)(destination+count)=0u;
 }
 return length;
}
