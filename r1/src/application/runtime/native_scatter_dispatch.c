#include <stdint.h>
typedef uint32_t (*r1_scatter_handler)(const volatile uint8_t *,volatile uint8_t *,uint32_t);
struct r1_scatter_region{const volatile uint8_t *source;volatile uint8_t *destination;uint32_t length;r1_scatter_handler handler;};
extern const struct r1_scatter_region r1_native_scatter_regions[2];
/* Explicit next source provider, corresponding to the native handoff target
 * at0x75f64. It is not linked to stock executable code in the source bundle. */
extern void r1_native_application_entry(void);
/* Normal C return declarations permit tail-call stack restoration. The
 * observed startup path never returns from the application; hypothetical
 * return/LR behavior remains a raw startup ABI gate. */
__attribute__((noinline))
void r1_native_runtime_entry(void){r1_native_application_entry();}
void r1_native_scatterload(void)
{
 for(uint32_t i=0;i<2;++i){
  const volatile struct r1_scatter_region *region=&r1_native_scatter_regions[i];
  r1_scatter_handler handler=(r1_scatter_handler)((uintptr_t)region->handler|1u);
  const volatile uint8_t *source=region->source;
  volatile uint8_t *destination=region->destination;
  uint32_t length=region->length;
  handler(source,destination,length);
 }
 r1_native_runtime_entry();
}
