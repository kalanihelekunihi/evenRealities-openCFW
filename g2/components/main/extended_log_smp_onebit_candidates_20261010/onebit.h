#ifndef G2_LOG_SMP_ONEBIT_H
#define G2_LOG_SMP_ONEBIT_H
#include <stdint.h>
typedef struct {
    int32_t (*format)(uint32_t, uint32_t, uint32_t, uint32_t);
    uint32_t (*find_token)(uint32_t, uint32_t);
    void (*output)(uint32_t, uint32_t, uint32_t);
    void (*guard_exit)(void);
    void (*guard_enter)(void);
    uint32_t (*date)(void);
    uint32_t (*time)(void);
    uint32_t (*tick)(void);
} g2_log_onebit_providers;
void g2_log_candidate_smp_onebit(const g2_log_onebit_providers *,
                                 uint32_t, uint32_t, uint32_t, uint32_t,
                                 uint32_t, uint32_t, uint32_t);
#endif
