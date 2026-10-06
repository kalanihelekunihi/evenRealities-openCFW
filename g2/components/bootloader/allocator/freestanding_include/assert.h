/* SPDX-License-Identifier: MIT */
#ifndef OPENCFW_ASSERT_H
#define OPENCFW_ASSERT_H
#ifdef NDEBUG
#define assert(x) ((void)0)
#else
void opencfw_boot_assert_failure(void);
#define assert(x) ((x)?(void)0:opencfw_boot_assert_failure())
#endif
#endif
