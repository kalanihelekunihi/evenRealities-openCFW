#include <stdint.h>
#include "native_kv_class.h"
#include "native_battery_memory.h"
extern void *volatile r1_device_info_record_kv_handle;
/* The assembler boundary supplies an external raw 52-byte stack view. Failed
 * reads preserve those bytes; there is no uninitialized C automatic object or
 * invented default record. Preserve ordered reads for aliased input views. */
__attribute__((used,noinline)) static void r1_kv_dev_info_fields_set_body(const volatile uint8_t *input,volatile uint8_t *record)
{
    if (!input) return;
    (void)r1_kv_class_read(r1_device_info_record_kv_handle,(void *)record,52);
    write32(record+36,read32(input));
    uint32_t kind=input[4];
    write32(record+40,(read32(record+40)&0xfffffffcu)|(kind&3u));
    uint32_t voltage=read16(input+4)>>2;
    write32(record+40,(read32(record+40)&0xffff0003u)|(voltage<<2));
    (void)r1_kv_class_write(r1_device_info_record_kv_handle,(const void *)record,52);
}
/* Native0x73710: push12 bytes then reserve52 bytes. The selected target uses
 * the exact incoming stack slice, even when the cached read writes nothing.
 * This ABI boundary must be revalidated with other compilers/LTO settings. */
__attribute__((naked,noinline)) void r1_kv_dev_info_fields_set(volatile void *input __attribute__((unused)))
{
    __asm__ volatile("push {r4, r5, lr}\nsub sp, sp, #52\nmov r1, sp\nbl r1_kv_dev_info_fields_set_body\nadd sp, sp, #52\npop {r4, r5, pc}");
}
