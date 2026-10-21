#include <stdint.h>

/* Value contract of optimized stock strlen at 0x44a43c..0x44a472. */
uint32_t g2_log_candidate_module_length(const uint8_t *module)
{
    const uint8_t *p = module;
    while (*p != 0u) p++;
    return (uint32_t)(p - module);
}

/* Memory side-effect contract of stock fill at 0x43c0e4..0x43c14a.
 * Its r0 return is not consumed by the logger, so the API is void. */
void g2_log_candidate_stack_fill(uint8_t *destination, uint32_t count,
                                 uint32_t value)
{
    uint8_t byte = (uint8_t)value;
    for (uint32_t i = 0; i < count; i++) destination[i] = byte;
}
