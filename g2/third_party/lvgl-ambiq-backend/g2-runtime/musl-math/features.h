/* SPDX-License-Identifier: MIT */
#ifndef OPENCFW_MUSL_FEATURES_H
#define OPENCFW_MUSL_FEATURES_H

/* The isolated math closure only requires this include to exist. */
#ifndef hidden
#define hidden __attribute__((visibility("hidden")))
#endif

#endif /* OPENCFW_MUSL_FEATURES_H */
