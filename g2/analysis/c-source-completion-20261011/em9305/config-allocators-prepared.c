static inline uint32_t opencfw_em9305_config_allocator_stride(uint32_t i,uint32_t width)
{
 uint32_t r;if(width==140u)__asm__ volatile("mpywhl %0,%1,140":"=r"(r):"r"(i));
 else __asm__ volatile("mpywhl %0,%1,656":"=r"(r):"r"(i));
 return r;
}
/* Native316b5c..316bbc: first inactive140B channel, typed initialization and shared request. */
uintptr_t opencfw_em9305_config_channel_allocate_316b5c(uint32_t id)
{
 uintptr_t config=*(volatile uint32_t *)(uintptr_t)0x805cacu;
 uint32_t count=*(volatile uint8_t *)(config+52u);
 if(!count)return 0u;
 uintptr_t base=*(volatile uint32_t *)(uintptr_t)0x805c64u;
 for(uint32_t i=0u;i<count;++i){uintptr_t row=base+opencfw_em9305_config_allocator_stride(i,140u);
  if(*(volatile uint8_t *)row!=0u)continue;
  (void)opencfw_em9305_memset((void *)row,0u,140u);
  *(volatile uint8_t *)row=1u;
  *(volatile uint32_t *)(row+92u)=0u;*(volatile uint32_t *)(row+88u)=0u;
  *(volatile uint16_t *)(row+8u)=(uint16_t)i;
  *(volatile uint8_t *)(row+6u)=(uint8_t)id;
  (void)opencfw_em9305_command_count_30e4bc();
  (void)opencfw_em9305_common_request_30455c(1u);
  return row;
 }
 return 0u;
}
/* Native316bbc..316c56: first inactive656B link and product-derived live fields. */
uintptr_t opencfw_em9305_config_link_allocate_316bbc(uintptr_t channel)
{
 uintptr_t config=*(volatile uint32_t *)(uintptr_t)0x805cacu;
 uint32_t count=*(volatile uint8_t *)(config+53u);
 if(!count)return 0u;
 uintptr_t base=*(volatile uint32_t *)(uintptr_t)0x805c68u;
 for(uint32_t i=0u;i<count;++i){uintptr_t row=base+opencfw_em9305_config_allocator_stride(i,656u);
  if(*(volatile uint8_t *)row!=0u)continue;
  (void)opencfw_em9305_memset((void *)row,0u,656u);
  uint32_t seed=*(volatile uint16_t *)(row+6u);
  config=*(volatile uint32_t *)(uintptr_t)0x805cacu;
  *(volatile uint16_t *)(row+80u)=(uint16_t)seed;
  uint32_t handler=*(volatile uint8_t *)(uintptr_t)0x805b18u;
  uint32_t capacity=*(volatile uint8_t *)(config+34u);
  *(volatile uint8_t *)(row+528u)=255u;*(volatile uint8_t *)(row+532u)=255u;
  *(volatile uint16_t *)(row+82u)=0x5201u;
  *(volatile uint16_t *)(row+458u)=0x470fu;
  *(volatile uint8_t *)(row+88u)=(uint8_t)handler;
  *(volatile uint8_t *)(row+464u)=(uint8_t)handler;
  uint32_t id=*(volatile uint8_t *)(channel+6u);
  uint32_t index=i+capacity;
  *(volatile uint8_t *)row=1u;
  *(volatile uint16_t *)(row+8u)=(uint16_t)index;
  *(volatile uint16_t *)(row+456u)=(uint16_t)index;
  *(volatile uint8_t *)(row+11u)=(uint8_t)id;
  return row;
 }
 return 0u;
}
