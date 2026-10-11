#include <stdint.h>

/* Original Apollo MAIN 0x5fa0a4: save BASEPRI, set threshold 0x30,
 * then DSB/ISB. The caller must pass the saved value to restore. */
uint32_t audio_mask_save(void) {
    uint32_t saved;
    __asm__ volatile("mrs %0, basepri\n\t"
                     "mov.w r1, #0x30\n\t"
                     "msr basepri, r1\n\t"
                     "dsb\n\t"
                     "isb"
                     : "=r"(saved) :: "r1", "memory");
    return saved;
}

/* A prior mutex integration receipt binds its no-argument, ignored-return
 * boundary call to this same Thumb entry. The caller observes only the
 * BASEPRI and barrier side effects. */
void mutex_assert_boundary(void) __attribute__((alias("audio_mask_save")));

/* Original 0x5fa0ba: restore BASEPRI, DSB, ISB. */
void audio_mask_restore(uint32_t saved) {
    __asm__ volatile("msr basepri, %0\n\tdsb\n\tisb"
                     :: "r"(saved) : "memory");
}
