/* SPDX-License-Identifier: MIT
 *
 * Compilation shim for Ghidra decompiler output.
 *
 * Ghidra emits C that names types and helpers its own analysis invented:
 * width-tagged `undefined` types, CONCAT/SUB/ZEXT/SEXT bit-slicing helpers,
 * and register-artifact locals.  None of that is C.  This header supplies the
 * missing vocabulary so a decompiled function can be compiled, inspected, and
 * diffed as ordinary source.
 *
 * What this header does NOT do is make decompiled output *correct*.  A
 * function that compiles through this shim has been made syntactically
 * well-formed; nothing here establishes that it computes what the stock code
 * computed.  Treat every unit built against this header as unverified until a
 * reviewed source route replaces it.
 */

#ifndef OPENG2_DECOMPILED_RUNTIME_H
#define OPENG2_DECOMPILED_RUNTIME_H

#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

/* ---- Ghidra's base type vocabulary ------------------------------------- */

typedef uint8_t undefined;
typedef uint8_t undefined1;
typedef uint16_t undefined2;
typedef uint32_t undefined4;
typedef uint64_t undefined8;
typedef uint8_t byte;
typedef uint8_t uchar;
typedef uint16_t ushort;
typedef uint16_t word;
typedef uint32_t uint;
typedef uint32_t dword;
typedef uint64_t qword;
typedef unsigned long ulong;
typedef long long longlong;
typedef unsigned long long ulonglong;
typedef uint64_t undefined6;
typedef uint64_t undefined7;
typedef uint32_t undefined3;
typedef uint64_t undefined5;

/* Odd widths appear where the decompiler recovered a sub-word field. */
typedef uint8_t uint1;
typedef uint16_t uint2;
typedef uint32_t uint3;
typedef uint64_t uint5;
typedef uint64_t uint6;
typedef uint64_t uint7;
typedef int8_t int1;
typedef int16_t int2;
typedef int32_t int3;
typedef int64_t int5;
typedef int64_t int6;
typedef int64_t int7;

#ifndef INFINITY
#define INFINITY (__builtin_inff())
#endif
#ifndef NAN_VALUE
#define NAN_VALUE (__builtin_nanf(""))
#endif

/* Ghidra writes function pointers as `code *`, so `code` must be a function
 * type -- not `void`, which would make `(*(code *)x)()` a call on void.  It
 * returns a machine word rather than nothing: indirect calls through vtable
 * slots are routinely assigned from, and the decompiler does not know the
 * callee's return type at the call site. */
typedef undefined4 code();

/* 128-bit SIMD spill slots appear in vectorized Ambiq/LVGL helpers. */
typedef struct { uint64_t low; uint64_t high; } unkuint16;
typedef struct { uint64_t low; uint64_t high; } undefined16;

/* ---- Bit-slicing helpers ----------------------------------------------- */

/* CONCATab(x, y) joins an a-byte high half to a b-byte low half. */
#define OPENG2_CONCAT(name, result_type, high_type, low_type, low_bits)      \
    static inline result_type name(high_type high, low_type low)             \
    {                                                                        \
        return (result_type)(((result_type)high << (low_bits))               \
                             | (result_type)(low_type)low);                  \
    }

OPENG2_CONCAT(CONCAT11, uint16_t, uint8_t, uint8_t, 8)
OPENG2_CONCAT(CONCAT12, uint32_t, uint8_t, uint16_t, 16)
OPENG2_CONCAT(CONCAT13, uint32_t, uint8_t, uint32_t, 24)
OPENG2_CONCAT(CONCAT14, uint64_t, uint8_t, uint32_t, 32)
OPENG2_CONCAT(CONCAT17, uint64_t, uint8_t, uint64_t, 56)
OPENG2_CONCAT(CONCAT21, uint32_t, uint16_t, uint8_t, 8)
OPENG2_CONCAT(CONCAT22, uint32_t, uint16_t, uint16_t, 16)
OPENG2_CONCAT(CONCAT24, uint64_t, uint16_t, uint32_t, 32)
OPENG2_CONCAT(CONCAT26, uint64_t, uint16_t, uint64_t, 48)
OPENG2_CONCAT(CONCAT31, uint32_t, uint32_t, uint8_t, 8)
OPENG2_CONCAT(CONCAT35, uint64_t, uint32_t, uint64_t, 40)
OPENG2_CONCAT(CONCAT41, uint64_t, uint32_t, uint8_t, 8)
OPENG2_CONCAT(CONCAT42, uint64_t, uint32_t, uint16_t, 16)
OPENG2_CONCAT(CONCAT44, uint64_t, uint32_t, uint32_t, 32)
OPENG2_CONCAT(CONCAT53, uint64_t, uint64_t, uint32_t, 24)
OPENG2_CONCAT(CONCAT61, uint64_t, uint64_t, uint8_t, 8)
OPENG2_CONCAT(CONCAT62, uint64_t, uint64_t, uint16_t, 16)
OPENG2_CONCAT(CONCAT71, uint64_t, uint64_t, uint8_t, 8)

#undef OPENG2_CONCAT

/* SUBab(x, offset) takes b bytes out of an a-byte value.  Ghidra only ever
 * emits the low-slice form with a byte offset, so the shift is explicit. */
#define OPENG2_SUB(name, result_type, source_type)                           \
    static inline result_type name(source_type value, int offset)            \
    {                                                                        \
        return (result_type)(value >> (offset * 8));                         \
    }

OPENG2_SUB(SUB21, uint8_t, uint32_t)
OPENG2_SUB(SUB41, uint8_t, uint32_t)
OPENG2_SUB(SUB42, uint16_t, uint32_t)
OPENG2_SUB(SUB81, uint8_t, uint64_t)
OPENG2_SUB(SUB82, uint16_t, uint64_t)
OPENG2_SUB(SUB84, uint32_t, uint64_t)
OPENG2_SUB(SUBievaluate, uint32_t, uint64_t)

#undef OPENG2_SUB

static inline uint16_t ZEXT12(uint8_t value) { return value; }
static inline uint32_t ZEXT14(uint8_t value) { return value; }
static inline uint64_t ZEXT18(uint8_t value) { return value; }
static inline uint32_t ZEXT24(uint16_t value) { return value; }
static inline uint64_t ZEXT28(uint16_t value) { return value; }
static inline uint64_t ZEXT48(uint32_t value) { return value; }
static inline uint64_t ZEXT816(uint64_t value) { return value; }

static inline int16_t SEXT12(int8_t value) { return value; }
static inline int32_t SEXT14(int8_t value) { return value; }
static inline int64_t SEXT18(int8_t value) { return value; }
static inline int32_t SEXT24(int16_t value) { return value; }
static inline int64_t SEXT28(int16_t value) { return value; }
static inline int64_t SEXT48(int32_t value) { return value; }
static inline int64_t SEXT816(int64_t value) { return value; }

/* ---- Analysis artifacts ------------------------------------------------ */

/* Emitted where the decompiler could not prove a path terminates or could not
 * decode the bytes it was pointed at.  Reaching one at run time is a defect in
 * the recovered model, so it traps rather than falling through. */
void halt_baddata(void);
void switchD(void);

/* Ghidra models Cortex-M system operations as calls, but its recovered arity
 * and return type vary between call sites of the same operation: each site is
 * analyzed on its own.  Declaring these unprototyped, returning a machine
 * word, accepts every recovered spelling.  A unit that assigns from one of
 * these is reading a value the hardware operation may not produce -- another
 * reason units built through this shim are unverified. */
#define OPENG2_INTRINSIC(name) undefined4 name();

OPENG2_INTRINSIC(coprocessor_function)
OPENG2_INTRINSIC(coprocessor_function2)
OPENG2_INTRINSIC(coprocessor_load)
OPENG2_INTRINSIC(coprocessor_loadlong)
OPENG2_INTRINSIC(coprocessor_store)
OPENG2_INTRINSIC(coprocessor_storelong)
OPENG2_INTRINSIC(coprocessor_moveto)
OPENG2_INTRINSIC(coprocessor_movefrom)
OPENG2_INTRINSIC(coprocessor_movefrom2)
OPENG2_INTRINSIC(coprocessor_moveto2)
OPENG2_INTRINSIC(DataMemoryBarrier)
OPENG2_INTRINSIC(DataSynchronizationBarrier)
OPENG2_INTRINSIC(InstructionSynchronizationBarrier)
OPENG2_INTRINSIC(SoftwareBreakpoint)
OPENG2_INTRINSIC(WaitForEvent)
OPENG2_INTRINSIC(WaitForInterrupt)
OPENG2_INTRINSIC(SendEvent)
OPENG2_INTRINSIC(enableIRQinterrupts)
OPENG2_INTRINSIC(disableIRQinterrupts)
OPENG2_INTRINSIC(enableFIQinterrupts)
OPENG2_INTRINSIC(disableFIQinterrupts)
OPENG2_INTRINSIC(setThreadModePrivileged)
OPENG2_INTRINSIC(setProcessStackPointer)
OPENG2_INTRINSIC(setMainStackPointer)
OPENG2_INTRINSIC(setStackMode)
OPENG2_INTRINSIC(setBASEPRI)
OPENG2_INTRINSIC(setPRIMASK)
OPENG2_INTRINSIC(setFAULTMASK)
OPENG2_INTRINSIC(getBASEPRI)
OPENG2_INTRINSIC(getPRIMASK)
OPENG2_INTRINSIC(getFAULTMASK)
OPENG2_INTRINSIC(getMainStackPointer)
OPENG2_INTRINSIC(getProcessStackPointer)
OPENG2_INTRINSIC(isCurrentModePrivileged)
OPENG2_INTRINSIC(isThreadMode)
OPENG2_INTRINSIC(isUsingMainStack)
OPENG2_INTRINSIC(ReverseBitOrder)
OPENG2_INTRINSIC(CountLeadingZeros)
OPENG2_INTRINSIC(HintDebug)
OPENG2_INTRINSIC(HintYield)
OPENG2_INTRINSIC(ExclusiveMonitorPass)
OPENG2_INTRINSIC(ExclusiveMonitorsReset)
OPENG2_INTRINSIC(ClearExclusiveLocal)
OPENG2_INTRINSIC(SignedDoesSaturate)
OPENG2_INTRINSIC(UnsignedDoesSaturate)
OPENG2_INTRINSIC(SignedSaturate)
OPENG2_INTRINSIC(UnsignedSaturate)
OPENG2_INTRINSIC(NaN)
OPENG2_INTRINSIC(isnan)
OPENG2_INTRINSIC(isinf)
OPENG2_INTRINSIC(VectorTableFetch)
OPENG2_INTRINSIC(ProcessorID)

/* Freestanding declarations for the handful of libc entry points the stock
 * image links against; the decompiler names them by their recovered symbols. */
void *memcpy(void *, const void *, size_t);
void *memmove(void *, const void *, size_t);
void *memset(void *, int, size_t);
int memcmp(const void *, const void *, size_t);
size_t strlen(const char *);
char *strcpy(char *, const char *);
int strcmp(const char *, const char *);

/* ---- Unrecovered-behavior boundary ------------------------------------- */

/* Emitted in place of a function whose behavior the corpus does not establish.
 * openCFW does not invent behavior it cannot attribute: an unrecovered
 * function traps loudly instead of returning a plausible value. */
void openg2_unrecovered(uint32_t address);

#define OPENG2_UNRECOVERED(address)                                          \
    do {                                                                     \
        openg2_unrecovered((uint32_t)(address));                             \
    } while (0)

#endif /* OPENG2_DECOMPILED_RUNTIME_H */
