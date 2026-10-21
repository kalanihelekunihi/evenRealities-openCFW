#include <stdint.h>

/* Apollo MAIN 0x480028. The archive's soft-float callers pass the float
 * bits in R1; the original hard-float entry consumes the same bits in S0. */
extern uint32_t stock_dispatch(uint32_t action, uint32_t enable, void *payload);

uint32_t stock_temperature_request(uint32_t bounds[2], float temperature) {
    union { float number; uint32_t bits; } value = { .number = temperature };
    uint32_t response[3];
    response[0] = value.bits;
    uint32_t status = stock_dispatch(2u, 0u, response);
    if (status == 0u) {
        bounds[0] = response[1];
        bounds[1] = response[2];
        return 0;
    }
    bounds[0] = 0u;
    bounds[1] = 0u;
    return 1u;
}
