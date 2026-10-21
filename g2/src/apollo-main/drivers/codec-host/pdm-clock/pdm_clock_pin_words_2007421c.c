/* Native PDM clock pin words read at 0x2007421c and 0x20074220.
 * Their runtime values and startup writer are not yet authenticated.
 * This C source owns only the observed contiguous eight-byte RAM span. */
#include <stdint.h>

struct g2_pdm_clock_pin_pair {
    uint32_t pin50;
    uint32_t pin51;
};
_Static_assert(sizeof(struct g2_pdm_clock_pin_pair) == 8u, "PDM pin pair span");

__attribute__((used, section(".g2_pdm_clock_pin_words")))
struct g2_pdm_clock_pin_pair g2_pdm_clock_pin_pair;

__asm__(".global g2_pdm_clock_pin_50\n"
        ".set g2_pdm_clock_pin_50,g2_pdm_clock_pin_pair\n"
        ".size g2_pdm_clock_pin_50,4\n"
        ".global g2_pdm_clock_pin_51\n"
        ".set g2_pdm_clock_pin_51,g2_pdm_clock_pin_pair+4\n"
        ".size g2_pdm_clock_pin_51,4\n");
