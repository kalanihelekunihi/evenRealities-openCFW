/* SPDX-License-Identifier: MIT */
#ifndef OPEN_CFW_TLSF_COMPAT_STDIO_H
#define OPEN_CFW_TLSF_COMPAT_STDIO_H

/*
 * Preserve the diagnostic call boundary without depending on a console or
 * hosted stdio implementation. The default implementation is a deterministic
 * sink and can be replaced when a reviewed firmware logger is integrated.
 */
int open_cfw_tlsf_diagnostic(const char *format, ...);

#define printf open_cfw_tlsf_diagnostic

#endif
