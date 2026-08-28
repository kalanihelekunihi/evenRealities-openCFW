/* SPDX-License-Identifier: MIT */
#ifndef OPEN_CFW_RUNTIME_AMBIQ_NEMA_HAL_CANDIDATE_H
#define OPEN_CFW_RUNTIME_AMBIQ_NEMA_HAL_CANDIDATE_H

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

struct open_cfw_nema_buffer {
    uint32_t size;
    int32_t fd;
    void *base_virt;
    uintptr_t base_phys;
};

struct open_cfw_nema_ringbuffer {
    struct open_cfw_nema_buffer bo;
    int32_t offset;
    int32_t last_submission_id;
};

struct open_cfw_nema_heap {
    uintptr_t arena;
    uint32_t arena_size;
    bool cacheable;
    void *context;
};

struct open_cfw_nema_hal_ports {
    void *(*allocate)(void *heap, uint32_t size, uint32_t alignment);
    void (*release)(void *heap, void *allocation);
    int32_t (*semaphore_acquire)(void *semaphore, uint32_t timeout_ms);
    int32_t (*semaphore_release)(void *semaphore);
    void *(*semaphore_create)(uint32_t maximum, uint32_t initial, uint32_t type);
    int32_t (*ringbuffer_init)(struct open_cfw_nema_ringbuffer *ring, int reset);
    void (*cache_clean)(uintptr_t address, uint32_t size);
    void (*cache_invalidate)(uintptr_t address, uint32_t size);
    void (*clear_pending_irq)(uint32_t irq);
    void (*enable_irq)(uint32_t irq);
    void (*set_irq_priority)(uint32_t irq, uint32_t priority);
    void (*pend_context_switch)(void);
    void (*diagnostic)(const char *message);
    void (*fatal)(void);
};

struct open_cfw_nema_hal {
    volatile uint32_t *registers;
    struct open_cfw_nema_heap *render_heap;
    struct open_cfw_nema_heap *assets_heap;
    struct open_cfw_nema_heap *cpu_heap;
    struct open_cfw_nema_ringbuffer ring;
    void *semaphore;
    volatile int32_t last_cl_id;
    void (*interrupt_callback)(int32_t cl_id);
    const struct open_cfw_nema_hal_ports *ports;
};

enum {
    OPEN_CFW_NEMA_POOL_CL = 0,
    OPEN_CFW_NEMA_POOL_FB = 1,
    OPEN_CFW_NEMA_POOL_ASSETS = 2,
    OPEN_CFW_NEMA_POOL_CLIPPED_PATH = 3,
    OPEN_CFW_NEMA_IRQ = 28,
    OPEN_CFW_NEMA_INTERRUPT = 0xF8,
    OPEN_CFW_NEMA_CLID = 0x148
};

uint32_t open_cfw_nema_reg_read_candidate(struct open_cfw_nema_hal *hal, uint32_t reg);
void open_cfw_nema_reg_write_candidate(struct open_cfw_nema_hal *hal, uint32_t reg, uint32_t value);
struct open_cfw_nema_buffer open_cfw_nema_buffer_create_pool_candidate(struct open_cfw_nema_hal *hal, int32_t pool, uint32_t size);
void open_cfw_nema_buffer_destroy_candidate(struct open_cfw_nema_hal *hal, struct open_cfw_nema_buffer *buffer);
void open_cfw_nema_buffer_flush_candidate(struct open_cfw_nema_hal *hal, const struct open_cfw_nema_buffer *buffer);
void open_cfw_nema_buffer_invalidate_candidate(struct open_cfw_nema_hal *hal, const struct open_cfw_nema_buffer *buffer);
bool open_cfw_nema_buffer_is_within_pool_candidate(struct open_cfw_nema_hal *hal, int32_t pool, uint32_t start, uint32_t length);
void *open_cfw_nema_host_malloc_candidate(struct open_cfw_nema_hal *hal, uint32_t size);
void open_cfw_nema_host_free_candidate(struct open_cfw_nema_hal *hal, void *allocation);
int32_t open_cfw_nema_wait_irq_candidate(struct open_cfw_nema_hal *hal);
int32_t open_cfw_nema_wait_irq_cl_candidate(struct open_cfw_nema_hal *hal, int32_t cl_id);
void open_cfw_nema_irq_candidate(struct open_cfw_nema_hal *hal);
int32_t open_cfw_nema_sys_init_candidate(struct open_cfw_nema_hal *hal);
void open_cfw_nema_reset_last_cl_id_candidate(struct open_cfw_nema_hal *hal);
int32_t open_cfw_nema_get_last_cl_id_candidate(const struct open_cfw_nema_hal *hal);
int32_t open_cfw_nema_get_last_submission_id_candidate(const struct open_cfw_nema_hal *hal);

#endif
