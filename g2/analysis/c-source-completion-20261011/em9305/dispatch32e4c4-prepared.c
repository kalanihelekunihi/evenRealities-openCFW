extern void opencfw_em9305_native_stack_check_302820(void);
__asm__(
".text\n.align 2\n.global opencfw_em9305_native_stack_check_302820\n"
".type opencfw_em9305_native_stack_check_302820,@function\n"
"opencfw_em9305_native_stack_check_302820:\n"
"push_s r12\nmov r12,0x80e978\n"
"brlo.nt sp,r12,.Lcfw_stack_bad_302820\n"
"mov r12,0x80f978\n"
"brlo.nt r12,sp,.Lcfw_stack_bad_302820\n"
"pop_s r12\nj [blink]\n.Lcfw_stack_bad_302820:\nbrk_s\n"
".size opencfw_em9305_native_stack_check_302820,.-opencfw_em9305_native_stack_check_302820\n");
extern uint32_t opencfw_em9305_command_records_apply_30dc48(uint32_t,uint32_t,uintptr_t);
extern void opencfw_em9305_command_struct_decode_332abc(uintptr_t,uintptr_t,uintptr_t,uintptr_t);
extern uint32_t opencfw_em9305_command_struct_apply_30b974(uintptr_t,uintptr_t,uintptr_t);
/* Native32e4c4..32e5a8: packed record command, structured command and existing fallback. */
uint32_t opencfw_em9305_dispatch_32e4c4(uintptr_t request,uintptr_t input)
{
 uint32_t command=*(volatile uint16_t *)request;
 if(command==0x2082u){uint32_t count=*(volatile uint8_t *)(input+1u),id=*(volatile uint8_t *)input;
  uintptr_t records=(uintptr_t)__builtin_alloca((3u+count*8u)&2040u);
  opencfw_em9305_native_stack_check_302820();
  uintptr_t row=input+2u;
  for(uint32_t i=0u;i<count;++i){
   uint32_t size=*(volatile uint8_t *)(row+3u),a=*(volatile uint8_t *)row,b=*(volatile uint8_t *)(row+1u),c=*(volatile uint8_t *)(row+2u);
   uintptr_t data=row+4u;row+=size+4u;
   uintptr_t out=records+i*8u;*(volatile uint32_t *)(out+4u)=(uint32_t)data;
   *(volatile uint8_t *)out=(uint8_t)a;*(volatile uint8_t *)(out+1u)=(uint8_t)b;
   *(volatile uint8_t *)(out+2u)=(uint8_t)c;*(volatile uint8_t *)(out+3u)=(uint8_t)size;
  }
  uint32_t status=opencfw_em9305_command_records_apply_30dc48(id,count,records);
  uintptr_t response=opencfw_em9305_ll_response_allocate_32e428(2u,*(volatile uint16_t *)request);
  if(response){*(volatile uint8_t *)response=(uint8_t)status;
   if(*(volatile uint16_t *)request==0x2082u)*(volatile uint8_t *)(response+1u)=(uint8_t)id;
   (void)opencfw_em9305_ll_event_send(response-5u);
  }
  return 1u;
 }
 if(command==0x2085u){uint8_t scratch[60] __attribute__((aligned(4)));
  uintptr_t base=(uintptr_t)scratch;
  (void)opencfw_em9305_memset(scratch,0u,36u);
  opencfw_em9305_command_struct_decode_332abc(base+48u,base+36u,base,input);
  uint32_t status=opencfw_em9305_command_struct_apply_30b974(base+48u,base+36u,base);
  (void)opencfw_em9305_ll_status_event_331bf8(request,status);return 1u;
 }
 return opencfw_em9305_dispatch_331204(request,input);
}
