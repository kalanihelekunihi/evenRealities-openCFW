/* SPDX-License-Identifier: GPL-3.0-only */
#ifndef OPEN_CFW_RUNTIME_AEABI_DOUBLE_H
#define OPEN_CFW_RUNTIME_AEABI_DOUBLE_H

#if defined(__arm__) || defined(__thumb__)
#define OPEN_CFW_AEABI_DOUBLE_PCS __attribute__((pcs("aapcs")))
#else
#define OPEN_CFW_AEABI_DOUBLE_PCS
#endif

OPEN_CFW_AEABI_DOUBLE_PCS double __aeabi_dadd(double left, double right);
OPEN_CFW_AEABI_DOUBLE_PCS double __aeabi_dmul(double left, double right);
OPEN_CFW_AEABI_DOUBLE_PCS double __aeabi_ddiv(double numerator, double denominator);
OPEN_CFW_AEABI_DOUBLE_PCS double __aeabi_ui2d(unsigned int value);
OPEN_CFW_AEABI_DOUBLE_PCS float __aeabi_d2f(double value);

#undef OPEN_CFW_AEABI_DOUBLE_PCS

#endif
