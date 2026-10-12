/* Native307fa0..307fcc: id<=5 byte stride and genuine wide-accumulator multiply. */
uint32_t opencfw_em9305_command_pair_apply_307fa0(uint32_t id,uint32_t value)
{
 if(id>=6u)return 0u;
 uint32_t offset=id*784u; /* bounded id makes native MPYUW stride exact */
 uintptr_t row=0x803e74u+offset;
 uint32_t factor=*(volatile uint32_t *)row;
 *(volatile uint16_t *)(uintptr_t)(0x803fe0u+offset)=(uint16_t)value;
 uint32_t product;
 __asm__ volatile("mpywhul %0,%1,%2":"=r"(product):"r"(factor),"r"(value));
 *(volatile uint32_t *)(row+8u)=product;
 return 1u;
}
