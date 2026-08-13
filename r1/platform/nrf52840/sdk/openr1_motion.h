#ifndef OPENR1_SDK_MOTION_H
#define OPENR1_SDK_MOTION_H

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

#include "sdk_errors.h"

#include "openr1/r1_motion.h"

#define OPENR1_MOTION_POLICY_DISABLED 0
#define OPENR1_MOTION_POLICY_AUTO_LICENSED 1
#define OPENR1_MOTION_POLICY_FORCE_LIS2DW12 2
#define OPENR1_MOTION_POLICY_FORCE_BMA456W 3

#ifndef OPENR1_MOTION_POLICY
#define OPENR1_MOTION_POLICY OPENR1_MOTION_POLICY_AUTO_LICENSED
#endif

ret_code_t openr1_motion_initialize(void);
ret_code_t openr1_motion_read_fifo(r1_motion_sample *samples,
                                   size_t capacity,
                                   size_t *sample_count);
ret_code_t openr1_motion_disable_double_tap(void);
r1_motion_variant openr1_motion_variant(void);
bool openr1_motion_is_enabled(void);

typedef struct {
    ret_code_t (*initialize)(void);
    ret_code_t (*read_fifo)(r1_motion_sample *samples, size_t capacity,
                            size_t *sample_count);
    ret_code_t (*disable_double_tap)(void);
    r1_motion_variant (*variant)(void);
    bool (*is_enabled)(void);
} openr1_motion_api;

extern const openr1_motion_api openr1_motion;

#endif
