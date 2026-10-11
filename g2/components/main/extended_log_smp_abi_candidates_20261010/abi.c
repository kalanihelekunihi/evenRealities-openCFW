#include <stdint.h>
#include "../extended_log_smp_onebit_candidates_20261010/onebit.h"

static const g2_log_onebit_providers *bound_providers;

void g2_log_candidate_bind_smp_providers(const g2_log_onebit_providers *p)
{
    bound_providers = p;
}

/* Exact stock register/stack argument positions for the two SMP formats:
 * r0..r3 = level,module,file,function; stack = line,format,arg0,arg1.
 * Precondition: bind_smp_providers was called and format is one of two
 * authenticated SMP literals. General variadic callers are outside domain. */
void g2_log_candidate_smp_stock_abi(uint32_t level, uint32_t module_word,
                                    uint32_t file_word, uint32_t function_word,
                                    uint32_t line, uint32_t format_word,
                                    uint32_t arg0, uint32_t arg1)
{
    uint32_t arguments[2] = {arg0,arg1};
    g2_log_candidate_smp_onebit(bound_providers,level,module_word,file_word,
                                function_word,line,format_word,
                                (uint32_t)(uintptr_t)arguments);
}

/* Bounded four-word stock stack layout observed at callers 0x43c922 and
 * 0x52fa9c. Precondition: format is 0x709f64 or 0x72d3e8 and the bound
 * formatter implements that exact literal's conversion contract. */
void g2_log_candidate_four_word_stock_abi(uint32_t level,
                                               uint32_t module_word,
                                               uint32_t file_word,
                                               uint32_t function_word,
                                               uint32_t line,
                                               uint32_t format_word,
                                               uint32_t arg0,
                                               uint32_t arg1,
                                               uint32_t arg2,
                                               uint32_t arg3)
{
    uint32_t arguments[4] = {arg0,arg1,arg2,arg3};
    g2_log_candidate_smp_onebit(bound_providers,level,module_word,file_word,
                                function_word,line,format_word,
                                (uint32_t)(uintptr_t)arguments);
}

/* Exact one-word stack layout at %c caller 0x4afa4e and %zu caller
 * 0x4d6626. Provider format must implement those authenticated literals. */
void g2_log_candidate_one_word_stock_abi(uint32_t level,
                                          uint32_t module_word,
                                          uint32_t file_word,
                                          uint32_t function_word,
                                          uint32_t line,
                                          uint32_t format_word,
                                          uint32_t arg0)
{
    uint32_t arguments[1]={arg0};
    g2_log_candidate_smp_onebit(bound_providers,level,module_word,file_word,
                                function_word,line,format_word,
                                (uint32_t)(uintptr_t)arguments);
}

/* Exact three-word stack layout at %llu/%d caller 0x4f624c.
 * arg0/arg1 hold the low/high words of unsigned 64-bit time difference. */
void g2_log_candidate_three_word_stock_abi(uint32_t level,
                                            uint32_t module_word,
                                            uint32_t file_word,
                                            uint32_t function_word,
                                            uint32_t line,
                                            uint32_t format_word,
                                            uint32_t arg0,uint32_t arg1,
                                            uint32_t arg2)
{
    uint32_t arguments[3]={arg0,arg1,arg2};
    g2_log_candidate_smp_onebit(bound_providers,level,module_word,file_word,
                                function_word,line,format_word,
                                (uint32_t)(uintptr_t)arguments);
}
