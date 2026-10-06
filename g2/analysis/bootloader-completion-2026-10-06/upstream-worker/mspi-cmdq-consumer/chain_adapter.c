#include <stdint.h>

void opencfw_bl_mspi_cq_init(uint32_t module, uint32_t queue_size_input,
                             uint32_t queue_buffer_address);

void mspi_cq_init(uint32_t module, uint32_t queue_size_input,
                  uint32_t queue_buffer_address)
{
    opencfw_bl_mspi_cq_init(module, queue_size_input, queue_buffer_address);
}
