/* Complete native316e74..316f4c, six fixed784-byte slots; DSP MPYWHL
 * decoded in authenticated little-endian ARC dump. Fresh config after reset. */
uint32_t opencfw_em9305_init_secondary_allocate_316e74(void)
{
 uint32_t index;uintptr_t record=0u;
 for(index=0u;index<6u;index++){
  uintptr_t candidate=0x803d78u+index*784u;
  if(*(volatile uint8_t *)candidate==0u){record=candidate;break;}
 }
 if(record==0u)return 0u;
 (void)opencfw_em9305_memset((void *)record,0u,784u);
 uintptr_t first=0x803e90u+index*784u,second=0x804040u+index*784u;
 *(volatile uint16_t *)(first-172u)=257u;
 uint32_t handler=*(volatile uint8_t *)(uintptr_t)0x805b18u;
 uint32_t option=*(volatile uint8_t *)(uintptr_t)0x805acau;
 uint32_t context=*(volatile uint32_t *)(uintptr_t)(0x803d58u+index*4u);
 *(volatile uint8_t *)second=(uint8_t)handler;
 *(volatile uint8_t *)record=1u;
 *(volatile uint16_t *)(second-6u)=1037u;
 *(volatile uint16_t *)(second-8u)=(uint16_t)index;
 *(volatile uint8_t *)(second+64u)=(uint8_t)option;
 *(volatile uint32_t *)(first-240u)=context;
 uintptr_t cursor=first;
 for(unsigned i=0u;i<15u;i++){*(volatile uint16_t *)cursor=4095u;cursor+=2u;}
 uintptr_t cfg=*(volatile uint32_t *)(uintptr_t)0x805cacu;
 *(volatile uint16_t *)(first+320u)=0u;
 uint32_t version=*(volatile uint8_t *)(cfg+4u);
 *(volatile uint8_t *)(second-110u)=0u;
 if(version>=13u){
  uintptr_t extra=*(volatile uint32_t *)(uintptr_t)(0x805c44u+index*4u);
  if(extra!=0u){
   *(volatile uint32_t *)(second+68u)=(uint32_t)extra;
   (void)opencfw_em9305_memset((void *)extra,0u,584u);
   extra=*(volatile uint32_t *)(second+68u);
   uint32_t pointer=*(volatile uint32_t *)(uintptr_t)0x805cecu;
   *(volatile uint8_t *)(extra+96u)=1u;
   *(volatile uint32_t *)(extra+92u)=pointer;
  }
 }
 return (uint32_t)record;
}
