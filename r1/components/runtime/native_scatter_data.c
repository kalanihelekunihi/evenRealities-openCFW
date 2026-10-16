#include <stdint.h>
/* The native decoder processes at least one token, even for output size zero.
 * Encoded literal counts include one; zero extended counts are not validated
 * by the native routine and remain malformed-input/memory-contract gates. */
uint32_t r1_native_scatter_decompress(const volatile uint8_t *source,volatile uint8_t *destination,uint32_t length)
{
 uint32_t end=(uint32_t)(uintptr_t)destination+length;
 do{
  uint32_t token=*source++,literals=token&7u;
  if(!literals)literals=*source++;
  uint32_t run=token>>4;if(!run)run=*source++;
  while(--literals){uint8_t value=*source++;*destination++=value;}
  if(token&8u){
   volatile uint8_t *back=destination-*source++;run+=2;
   while((int32_t)--run>=0){uint8_t value=*back++;*destination++=value;}
  }else while((int32_t)--run>=0)*destination++=0;
 }while((uint32_t)(uintptr_t)destination<end);
 return 0;
}
uint32_t r1_native_scatter_zero(const volatile uint8_t *source,volatile uint8_t *destination,uint32_t length)
{
 (void)source;
 volatile uint32_t *words=(volatile uint32_t *)(volatile void *)destination;
 while(length){*words++=0;length-=4;}
 return 0;
}
typedef uint32_t (*r1_scatter_handler)(const volatile uint8_t *,volatile uint8_t *,uint32_t);
struct r1_scatter_region{const volatile uint8_t *source;volatile uint8_t *destination;uint32_t length;r1_scatter_handler handler;};
/* Source callback relocations replace the table's native instruction pointers.
 * The compressed flash-data source is still an explicit authenticated input,
 * not claimed as source-owned initialization data or a complete startup. */
__attribute__((section(".r1.scatter.regions"),used))
const struct r1_scatter_region r1_native_scatter_regions[2]={
 {(const volatile uint8_t *)0xc4610u,(volatile uint8_t *)0x200064a8u,0x195cu,r1_native_scatter_decompress},
 {(const volatile uint8_t *)0xc4d08u,(volatile uint8_t *)0x20007e04u,0x340b4u,r1_native_scatter_zero}
};
_Static_assert(sizeof(struct r1_scatter_region)==16,"ARM scatter descriptor must be four words");
