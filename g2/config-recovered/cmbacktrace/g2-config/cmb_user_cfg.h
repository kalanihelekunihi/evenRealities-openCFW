/*
 * openCFW recovered CmBacktrace configuration boundary for Even G2.
 *
 * This file is production-excluded.  Define CMB_USER_CFG so the pinned
 * upstream cmb_cfg.h includes it.  The switches in the first block are
 * directly recovered from the authenticated G2 2.2.6.10 Apollo image.
 */
#ifndef OPENCFW_G2_CMB_USER_CFG_H
#define OPENCFW_G2_CMB_USER_CFG_H

/* Proven effective settings. */
#define CMB_USING_OS_PLATFORM
#define CMB_OS_PLATFORM_TYPE CMB_OS_PLATFORM_FREERTOS
#define CMB_USING_DUMP_STACK_INFO
#define CMB_NAME_MAX 40
#define CMB_CALL_STACK_MAX_DEPTH 32
#define CMB_DUMP_STACK_DEPTH_SIZE 16

/*
 * Compatibility choices, not exact vendor-macro claims:
 *
 * - G2 has M33-class retained behavior, including STKOF diagnostics and the
 *   FPU exception-frame paths.  Upstream's M33 selector is the newest
 *   compatible snapshot's matching choice, but a vendor-added M55 alias
 *   cannot be excluded.
 * - The retained 39-message table is English.  A patched en-US header and
 *   the post-2023 custom-language selector are byte-indistinguishable in the
 *   official image, so selecting upstream English is an openCFW choice.
 */
#define CMB_CPU_PLATFORM_TYPE CMB_CPU_ARM_CORTEX_M33
#define CMB_PRINT_LANGUAGE CMB_PRINT_LANGUAGE_ENGLISH

/*
 * Unresolved integration seam.  The firmware's logger fans out to two
 * retained logging calls, but its source-level macro/function contract is
 * not proven.  A future integration must supply this function-like macro;
 * this snapshot intentionally supplies no default or production binding.
 */
#ifndef OPENCFW_CMB_PRINTLN
#error "Define OPENCFW_CMB_PRINTLN(...) for an explicit CmBacktrace logging port"
#endif
#define cmb_println(...) OPENCFW_CMB_PRINTLN(__VA_ARGS__)

#endif /* OPENCFW_G2_CMB_USER_CFG_H */
