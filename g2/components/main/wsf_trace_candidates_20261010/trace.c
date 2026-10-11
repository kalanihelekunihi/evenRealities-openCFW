#include <stdint.h>

typedef struct {
    uint32_t (*format)(char *destination, uint32_t format_word,
                       const uint32_t *arguments);
    uint32_t (*print)(uint32_t string_word);
    void (*assert_failure)(uint32_t file_word, uint32_t line);
} g2_wsf_trace_providers;

/* Stock WsfTrace 0x52a63c..0x52a672, with lower format/output providers.
 * Three argument words cover its register varargs in SmpHandler's call. */
void g2_smp_candidate_log_fallback(void *context, uint32_t format_word,
                                    uint32_t arg1, uint32_t arg2,
                                    uint32_t arg3)
{
    const g2_wsf_trace_providers *p = (const g2_wsf_trace_providers *)context;
    char buffer[1024];
    uint32_t args[3] = {arg1, arg2, arg3};
    (void)p->format(buffer, format_word, args);
    uint32_t count = p->print((uint32_t)(uintptr_t)buffer);
    if (count >= 1024u)
        p->assert_failure(0x006df094u, 137u);
    (void)p->print(0x0052a674u);
}
