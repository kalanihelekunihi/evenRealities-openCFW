#include <stdint.h>

/* Locked main literal 0x52bab8; WSF nesting byte, distinct from FreeRTOS NEST. */
#define WSF_NEST (*(volatile uint8_t *)(uintptr_t)0x20075045u)

typedef struct { uint32_t head, tail; } g2_wsf_queue;
typedef struct { uint32_t next; uint8_t handler_id; uint8_t reserved[3]; } g2_wsf_msg_header;
typedef struct { void (*buffer_free)(uint32_t hidden_header); } g2_wsf_free_provider;

void g2_wsf_candidate_cs_enter(void)
{
    if (WSF_NEST == 0u) __asm__ volatile("cpsid i" ::: "memory");
    WSF_NEST = (uint8_t)(WSF_NEST + 1u);
}

void g2_wsf_candidate_cs_exit(void)
{
    WSF_NEST = (uint8_t)(WSF_NEST - 1u);
    if (WSF_NEST == 0u) __asm__ volatile("cpsie i" ::: "memory");
}



void g2_smp_candidate_message_free(void *context, uint32_t message_word)
{
    const g2_wsf_free_provider *provider = (const g2_wsf_free_provider *)context;
    provider->buffer_free(message_word - 8u);
}
