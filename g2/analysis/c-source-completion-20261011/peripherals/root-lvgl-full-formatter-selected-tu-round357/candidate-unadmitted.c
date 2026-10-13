#pragma clang attribute push (__attribute__((target("no-lob,no-mve,no-mve.fp"))), apply_to=function)

/* Entire pinned LVGL builtin formatter adapted for native-cluster qualification.
 * Unadmitted: configuration, allformatclasses, helpers anddata require qualification. */
#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>
#include <stdarg.h>
#define LVFMT354_UNUSED(x) ((void)(x))
_Static_assert(sizeof(size_t)==4 && sizeof(long)==4 && sizeof(long long)==8,"native widths");
_Static_assert(sizeof(va_list)==4,"native va-list pointer width");
static size_t lvfmt354_strnlen(const char *str,size_t max_len)
{size_t i=0;while(i<max_len && str[i])i++;return i;}
///////////////////////////////////////////////////////////////////////////////
// \author (c) Marco Paland (info@paland.com)
//             2014-2019, PALANDesign Hannover, Germany
//
// \license The MIT License (MIT)
//
// Permission is hereby granted, free of charge, to any person obtaining a copy
// of this software and associated documentation files (the "Software"), to deal
// in the Software without restriction, including without limitation the rights
// to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
// copies of the Software, and to permit persons to whom the Software is
// furnished to do so, subject to the following conditions:
//
// The above copyright notice and this permission notice shall be included in
// all copies or substantial portions of the Software.
//
// THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
// IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
// FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
// AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
// LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
// OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
// THE SOFTWARE.
//
// \brief Tiny printf, sprintf and (v)snprintf implementation, optimized for speed on
//        embedded systems with a very limited resources. These routines are thread
//        safe and reentrant!
//        Use this instead of the bloated standard/newlib printf cause these use
//        malloc for printf (and may not be thread safe).
//
///////////////////////////////////////////////////////////////////////////////

/*Original repository: https://github.com/mpaland/printf*/








#define LVFMT354_PRINTF_DISABLE_SUPPORT_FLOAT 0 /* Native fixed/exponential helpers present; candidate configuration. */

// 'ntoa' conversion buffer size, this must be big enough to hold one converted
// numeric number including padded zeros (dynamically created on stack)
// default: 32 byte
#ifndef LVFMT354_PRINTF_NTOA_BUFFER_SIZE
    #define LVFMT354_PRINTF_NTOA_BUFFER_SIZE    32U
#endif

// 'ftoa' conversion buffer size, this must be big enough to hold one converted
// float number including padded zeros (dynamically created on stack)
// default: 32 byte
#ifndef LVFMT354_PRINTF_FTOA_BUFFER_SIZE
    #define LVFMT354_PRINTF_FTOA_BUFFER_SIZE    32U
#endif

// support for the floating point type (%f)
// default: activated
#if !LVFMT354_PRINTF_DISABLE_SUPPORT_FLOAT
    #define LVFMT354_PRINTF_SUPPORT_FLOAT
#endif

// support for exponential floating point notation (%e/%g)
// default: activated
#ifndef LVFMT354_PRINTF_DISABLE_SUPPORT_EXPONENTIAL
    #define LVFMT354_PRINTF_SUPPORT_EXPONENTIAL
#endif

// define the default floating point precision
// default: 6 digits
#ifndef LVFMT354_PRINTF_DEFAULT_FLOAT_PRECISION
    #define LVFMT354_PRINTF_DEFAULT_FLOAT_PRECISION 6U
#endif

// define the largest float suitable to print with %f
// default: 1e9
#ifndef LVFMT354_PRINTF_MAX_FLOAT
    #define LVFMT354_PRINTF_MAX_FLOAT 1e9
#endif

// support for the long long types (%llu or %p)
// default: activated
#ifndef LVFMT354_PRINTF_DISABLE_SUPPORT_LONG_LONG
    #define LVFMT354_PRINTF_SUPPORT_LONG_LONG
#endif

// support for the ptrdiff_t type (%t)
// ptrdiff_t is normally defined in <stddef.h> as long or long long type
// default: activated
#ifndef LVFMT354_PRINTF_DISABLE_SUPPORT_PTRDIFF_T
    #define LVFMT354_PRINTF_SUPPORT_PTRDIFF_T
#endif

///////////////////////////////////////////////////////////////////////////////

// internal flag definitions
#define LVFMT354_FLAGS_ZEROPAD   (1U <<  0U)
#define LVFMT354_FLAGS_LEFT      (1U <<  1U)
#define LVFMT354_FLAGS_PLUS      (1U <<  2U)
#define LVFMT354_FLAGS_SPACE     (1U <<  3U)
#define LVFMT354_FLAGS_HASH      (1U <<  4U)
#define LVFMT354_FLAGS_UPPERCASE (1U <<  5U)
#define LVFMT354_FLAGS_CHAR      (1U <<  6U)
#define LVFMT354_FLAGS_SHORT     (1U <<  7U)
#define LVFMT354_FLAGS_LONG      (1U <<  8U)
#define LVFMT354_FLAGS_LONG_LONG (1U <<  9U)
#define LVFMT354_FLAGS_PRECISION (1U << 10U)
#define LVFMT354_FLAGS_ADAPT_EXP (1U << 11U)

typedef struct {
    const char * fmt;
    va_list * va;
} lvfmt354_vaformat_t;

// import float.h for DBL_MAX
#if defined(LVFMT354_PRINTF_SUPPORT_FLOAT)
    #include <float.h>
#endif

// output function type
typedef void (*lvfmt354_out_type)(char character, void * buffer, size_t idx, size_t maxlen);

// wrapper (used as buffer) for output function type
typedef struct {
    void (*fct)(char character, void * arg);
    void * arg;
} lvfmt354_out_wrap;

// internal buffer output
static inline void lvfmt354_out_buffer(char character, void * buffer, size_t idx, size_t maxlen)
{
    if(idx < maxlen) {
        ((char *)buffer)[idx] = character;
    }
}

// internal null output
static inline void lvfmt354_out_null(char character, void * buffer, size_t idx, size_t maxlen)
{
    LVFMT354_UNUSED(character);
    LVFMT354_UNUSED(buffer);
    LVFMT354_UNUSED(idx);
    LVFMT354_UNUSED(maxlen);
}

// internal test if char is a digit (0-9)
// \return true if char is a digit
static inline bool lvfmt354_is_digit(char ch)
{
    return (ch >= '0') && (ch <= '9');
}

// internal ASCII string to unsigned int conversion
static unsigned int lvfmt354_atoi(const char ** str)
{
    unsigned int i = 0U;
    while(lvfmt354_is_digit(**str)) {
        i = i * 10U + (unsigned int)(*((*str)++) - '0');
    }
    return i;
}

// output the specified string in reverse, taking care of any zero-padding
static size_t lvfmt354_out_rev(lvfmt354_out_type out, char * buffer, size_t idx, size_t maxlen, const char * buf, size_t len,
                       unsigned int width, unsigned int flags)
{
    const size_t start_idx = idx;

    // pad spaces up to given width
    if(!(flags & LVFMT354_FLAGS_LEFT) && !(flags & LVFMT354_FLAGS_ZEROPAD)) {
        size_t i;
        for(i = len; i < width; i++) {
            out(' ', buffer, idx++, maxlen);
        }
    }

    // reverse string
    while(len) {
        out(buf[--len], buffer, idx++, maxlen);
    }

    // append pad spaces up to given width
    if(flags & LVFMT354_FLAGS_LEFT) {
        while(idx - start_idx < width) {
            out(' ', buffer, idx++, maxlen);
        }
    }

    return idx;
}

// internal itoa format
static size_t lvfmt354_ntoa_format(lvfmt354_out_type out, char * buffer, size_t idx, size_t maxlen, char * buf, size_t len,
                           bool negative, unsigned int base, unsigned int prec, unsigned int width, unsigned int flags)
{
    // pad leading zeros
    if(!(flags & LVFMT354_FLAGS_LEFT)) {
        if(width && (flags & LVFMT354_FLAGS_ZEROPAD) && (negative || (flags & (LVFMT354_FLAGS_PLUS | LVFMT354_FLAGS_SPACE)))) {
            width--;
        }
        while((len < prec) && (len < LVFMT354_PRINTF_NTOA_BUFFER_SIZE)) {
            buf[len++] = '0';
        }
        while((flags & LVFMT354_FLAGS_ZEROPAD) && (len < width) && (len < LVFMT354_PRINTF_NTOA_BUFFER_SIZE)) {
            buf[len++] = '0';
        }
    }

    // handle hash
    if(flags & LVFMT354_FLAGS_HASH) {
        if(!(flags & LVFMT354_FLAGS_PRECISION) && len && ((len == prec) || (len == width))) {
            len--;
            if(len && (base == 16U)) {
                len--;
            }
        }
        if((base == 16U) && !(flags & LVFMT354_FLAGS_UPPERCASE) && (len < LVFMT354_PRINTF_NTOA_BUFFER_SIZE)) {
            buf[len++] = 'x';
        }
        else if((base == 16U) && (flags & LVFMT354_FLAGS_UPPERCASE) && (len < LVFMT354_PRINTF_NTOA_BUFFER_SIZE)) {
            buf[len++] = 'X';
        }
        else if((base == 2U) && (len < LVFMT354_PRINTF_NTOA_BUFFER_SIZE)) {
            buf[len++] = 'b';
        }
        if(len < LVFMT354_PRINTF_NTOA_BUFFER_SIZE) {
            buf[len++] = '0';
        }
    }

    if(len < LVFMT354_PRINTF_NTOA_BUFFER_SIZE) {
        if(negative) {
            buf[len++] = '-';
        }
        else if(flags & LVFMT354_FLAGS_PLUS) {
            buf[len++] = '+';  // ignore the space if the '+' exists
        }
        else if(flags & LVFMT354_FLAGS_SPACE) {
            buf[len++] = ' ';
        }
    }

    return lvfmt354_out_rev(out, buffer, idx, maxlen, buf, len, width, flags);
}

// internal itoa for 'long' type
static size_t lvfmt354_ntoa_long(lvfmt354_out_type out, char * buffer, size_t idx, size_t maxlen, unsigned long value, bool negative,
                         unsigned long base, unsigned int prec, unsigned int width, unsigned int flags)
{
    char buf[LVFMT354_PRINTF_NTOA_BUFFER_SIZE];
    size_t len = 0U;

    // no hash for 0 values
    if(!value) {
        flags &= ~LVFMT354_FLAGS_HASH;
    }

    // write if precision != 0 and value is != 0
    if(!(flags & LVFMT354_FLAGS_PRECISION) || value) {
        do {
            const char digit = (char)(value % base);
            buf[len++] = digit < 10 ? '0' + digit : (flags & LVFMT354_FLAGS_UPPERCASE ? 'A' : 'a') + digit - 10;
            value /= base;
        } while(value && (len < LVFMT354_PRINTF_NTOA_BUFFER_SIZE));
    }

    return lvfmt354_ntoa_format(out, buffer, idx, maxlen, buf, len, negative, (unsigned int)base, prec, width, flags);
}

// internal itoa for 'long long' type
#if defined(LVFMT354_PRINTF_SUPPORT_LONG_LONG)
static size_t lvfmt354_ntoa_long_long(lvfmt354_out_type out, char * buffer, size_t idx, size_t maxlen, unsigned long long value,
                              bool negative, unsigned long long base, unsigned int prec, unsigned int width, unsigned int flags)
{
    char buf[LVFMT354_PRINTF_NTOA_BUFFER_SIZE];
    size_t len = 0U;

    // no hash for 0 values
    if(!value) {
        flags &= ~LVFMT354_FLAGS_HASH;
    }

    // write if precision != 0 and value is != 0
    if(!(flags & LVFMT354_FLAGS_PRECISION) || value) {
        do {
            const char digit = (char)(value % base);
            buf[len++] = digit < 10 ? '0' + digit : (flags & LVFMT354_FLAGS_UPPERCASE ? 'A' : 'a') + digit - 10;
            value /= base;
        } while(value && (len < LVFMT354_PRINTF_NTOA_BUFFER_SIZE));
    }

    return lvfmt354_ntoa_format(out, buffer, idx, maxlen, buf, len, negative, (unsigned int)base, prec, width, flags);
}
#endif  // LVFMT354_PRINTF_SUPPORT_LONG_LONG

#if defined(LVFMT354_PRINTF_SUPPORT_FLOAT)

#if defined(LVFMT354_PRINTF_SUPPORT_EXPONENTIAL)
// forward declaration so that lvfmt354_ftoa can switch to exp notation for values > LVFMT354_PRINTF_MAX_FLOAT
static size_t lvfmt354_etoa(lvfmt354_out_type out, char * buffer, size_t idx, size_t maxlen, double value, unsigned int prec,
                    unsigned int width, unsigned int flags);
#endif

// internal ftoa for fixed decimal floating point
static size_t lvfmt354_ftoa(lvfmt354_out_type out, char * buffer, size_t idx, size_t maxlen, double value, unsigned int prec,
                    unsigned int width, unsigned int flags)
{
    char buf[LVFMT354_PRINTF_FTOA_BUFFER_SIZE];
    size_t len  = 0U;
    double diff = 0.0;

    // powers of 10
    static const double pow10[] = { 1, 10, 100, 1000, 10000, 100000, 1000000, 10000000, 100000000, 1000000000 };

    // test for special values
    if(value != value)
        return lvfmt354_out_rev(out, buffer, idx, maxlen, "nan", 3, width, flags);
    if(value < -DBL_MAX)
        return lvfmt354_out_rev(out, buffer, idx, maxlen, "fni-", 4, width, flags);
    if(value > DBL_MAX)
        return lvfmt354_out_rev(out, buffer, idx, maxlen, (flags & LVFMT354_FLAGS_PLUS) ? "fni+" : "fni", (flags & LVFMT354_FLAGS_PLUS) ? 4U : 3U, width,
                        flags);

    // test for very large values
    // standard printf behavior is to print EVERY whole number digit -- which could be 100s of characters overflowing your buffers == bad
    if((value > LVFMT354_PRINTF_MAX_FLOAT) || (value < -LVFMT354_PRINTF_MAX_FLOAT)) {
#if defined(LVFMT354_PRINTF_SUPPORT_EXPONENTIAL)
        return lvfmt354_etoa(out, buffer, idx, maxlen, value, prec, width, flags);
#else
        return 0U;
#endif
    }

    // test for negative
    bool negative = false;
    if(value < 0) {
        negative = true;
        value = 0 - value;
    }

    // set default precision, if not set explicitly
    if(!(flags & LVFMT354_FLAGS_PRECISION)) {
        prec = LVFMT354_PRINTF_DEFAULT_FLOAT_PRECISION;
    }
    // limit precision to 9, cause a prec >= 10 can lead to overflow errors
    while((len < LVFMT354_PRINTF_FTOA_BUFFER_SIZE) && (prec > 9U)) {
        buf[len++] = '0';
        prec--;
    }

    int whole = (int)value;
    double tmp = (value - whole) * pow10[prec];
    unsigned long frac = (unsigned long)tmp;
    diff = tmp - frac;

    if(diff > 0.5) {
        ++frac;
        // handle rollover, e.g. case 0.99 with prec 1 is 1.0
        if(frac >= pow10[prec]) {
            frac = 0;
            ++whole;
        }
    }
    else if(diff < 0.5) {
    }
    else if((frac == 0U) || (frac & 1U)) {
        // if halfway, round up if odd OR if last digit is 0
        ++frac;
    }

    if(prec == 0U) {
        diff = value - (double)whole;
        if((!(diff < 0.5) || (diff > 0.5)) && (whole & 1)) {
            // exactly 0.5 and ODD, then round up
            // 1.5 -> 2, but 2.5 -> 2
            ++whole;
        }
    }
    else {
        unsigned int count = prec;
        // now do fractional part, as an unsigned number
        while(len < LVFMT354_PRINTF_FTOA_BUFFER_SIZE) {
            --count;
            buf[len++] = (char)(48U + (frac % 10U));
            if(!(frac /= 10U)) {
                break;
            }
        }
        // add extra 0s
        while((len < LVFMT354_PRINTF_FTOA_BUFFER_SIZE) && (count-- > 0U)) {
            buf[len++] = '0';
        }
        if(len < LVFMT354_PRINTF_FTOA_BUFFER_SIZE) {
            // add decimal
            buf[len++] = '.';
        }
    }

    // do whole part, number is reversed
    while(len < LVFMT354_PRINTF_FTOA_BUFFER_SIZE) {
        buf[len++] = (char)(48 + (whole % 10));
        if(!(whole /= 10)) {
            break;
        }
    }

    // pad leading zeros
    if(!(flags & LVFMT354_FLAGS_LEFT) && (flags & LVFMT354_FLAGS_ZEROPAD)) {
        if(width && (negative || (flags & (LVFMT354_FLAGS_PLUS | LVFMT354_FLAGS_SPACE)))) {
            width--;
        }
        while((len < width) && (len < LVFMT354_PRINTF_FTOA_BUFFER_SIZE)) {
            buf[len++] = '0';
        }
    }

    if(len < LVFMT354_PRINTF_FTOA_BUFFER_SIZE) {
        if(negative) {
            buf[len++] = '-';
        }
        else if(flags & LVFMT354_FLAGS_PLUS) {
            buf[len++] = '+';  // ignore the space if the '+' exists
        }
        else if(flags & LVFMT354_FLAGS_SPACE) {
            buf[len++] = ' ';
        }
    }

    return lvfmt354_out_rev(out, buffer, idx, maxlen, buf, len, width, flags);
}

#if defined(LVFMT354_PRINTF_SUPPORT_EXPONENTIAL)
// internal ftoa variant for exponential floating-point type, contributed by Martijn Jasperse <m.jasperse@gmail.com>
static size_t lvfmt354_etoa(lvfmt354_out_type out, char * buffer, size_t idx, size_t maxlen, double value, unsigned int prec,
                    unsigned int width, unsigned int flags)
{
    // check for NaN and special values
    if((value != value) || (value > DBL_MAX) || (value < -DBL_MAX)) {
        return lvfmt354_ftoa(out, buffer, idx, maxlen, value, prec, width, flags);
    }

    // determine the sign
    const bool negative = value < 0;
    if(negative) {
        value = -value;
    }

    // default precision
    if(!(flags & LVFMT354_FLAGS_PRECISION)) {
        prec = LVFMT354_PRINTF_DEFAULT_FLOAT_PRECISION;
    }

    // determine the decimal exponent
    // based on the algorithm by David Gay (https://www.ampl.com/netlib/fp/dtoa.c)
    union {
        uint64_t U;
        double   F;
    } conv;

    conv.F = value;
    int exp2 = (int)((conv.U >> 52U) & 0x07FFU) - 1023;           // effectively log2
    conv.U = (conv.U & ((1ULL << 52U) - 1U)) | (1023ULL << 52U);  // drop the exponent so conv.F is now in [1,2)
    // now approximate log10 from the log2 integer part and an expansion of ln around 1.5
    int expval = (int)(0.1760912590558 + exp2 * 0.301029995663981 + (conv.F - 1.5) * 0.289529654602168);
    // now we want to compute 10^expval but we want to be sure it won't overflow
    exp2 = (int)(expval * 3.321928094887362 + 0.5);
    const double z  = expval * 2.302585092994046 - exp2 * 0.6931471805599453;
    const double z2 = z * z;
    conv.U = (uint64_t)(exp2 + 1023) << 52U;
    // compute exp(z) using continued fractions, see https://en.wikipedia.org/wiki/Exponential_function#Continued_fractions_for_ex
    conv.F *= 1 + 2 * z / (2 - z + (z2 / (6 + (z2 / (10 + z2 / 14)))));
    // correct for rounding errors
    if(value < conv.F) {
        expval--;
        conv.F /= 10;
    }

    // the exponent format is "%+03d" and largest value is "307", so set aside 4-5 characters
    unsigned int minwidth = ((expval < 100) && (expval > -100)) ? 4U : 5U;

    // in "%g" mode, "prec" is the number of *significant figures* not decimals
    if(flags & LVFMT354_FLAGS_ADAPT_EXP) {
        // do we want to fall-back to "%f" mode?
        if((value >= 1e-4) && (value < 1e6)) {
            if((int)prec > expval) {
                prec = (unsigned)((int)prec - expval - 1);
            }
            else {
                prec = 0;
            }
            flags |= LVFMT354_FLAGS_PRECISION;   // make sure lvfmt354_ftoa respects precision
            // no characters in exponent
            minwidth = 0U;
            expval   = 0;
        }
        else {
            // we use one sigfig for the whole part
            if((prec > 0) && (flags & LVFMT354_FLAGS_PRECISION)) {
                --prec;
            }
        }
    }

    // will everything fit?
    unsigned int fwidth = width;
    if(width > minwidth) {
        // we didn't fall-back so subtract the characters required for the exponent
        fwidth -= minwidth;
    }
    else {
        // not enough characters, so go back to default sizing
        fwidth = 0U;
    }
    if((flags & LVFMT354_FLAGS_LEFT) && minwidth) {
        // if we're padding on the right, DON'T pad the floating part
        fwidth = 0U;
    }

    // rescale the float value
    if(expval) {
        value /= conv.F;
    }

    // output the floating part
    const size_t start_idx = idx;
    idx = lvfmt354_ftoa(out, buffer, idx, maxlen, negative ? -value : value, prec, fwidth, flags & ~LVFMT354_FLAGS_ADAPT_EXP);

    // output the exponent part
    if(minwidth) {
        // output the exponential symbol
        out((flags & LVFMT354_FLAGS_UPPERCASE) ? 'E' : 'e', buffer, idx++, maxlen);
        // output the exponent value
        idx = lvfmt354_ntoa_long(out, buffer, idx, maxlen, (expval < 0) ? -expval : expval, expval < 0, 10, 0, minwidth - 1,
                         LVFMT354_FLAGS_ZEROPAD | LVFMT354_FLAGS_PLUS);
        // might need to right-pad spaces
        if(flags & LVFMT354_FLAGS_LEFT) {
            while(idx - start_idx < width) out(' ', buffer, idx++, maxlen);
        }
    }
    return idx;
}
#endif  // LVFMT354_PRINTF_SUPPORT_EXPONENTIAL
#endif  // LVFMT354_PRINTF_SUPPORT_FLOAT

// internal vsnprintf
static int lvfmt354_inner(lvfmt354_out_type out, char * buffer, const size_t maxlen, const char * format, va_list va)
{
    unsigned int flags, width, precision, n;
    size_t idx = 0U;

    if(!buffer) {
        // use null output function
        out = lvfmt354_out_null;
    }

    while(*format) {
        // format specifier?  %[flags][width][.precision][length]
        if(*format != '%') {
            // no
            out(*format, buffer, idx++, maxlen);
            format++;
            continue;
        }
        else {
            // yes, evaluate it
            format++;
        }

        // evaluate flags
        flags = 0U;
        do {
            switch(*format) {
                case '0':
                    flags |= LVFMT354_FLAGS_ZEROPAD;
                    format++;
                    n = 1U;
                    break;
                case '-':
                    flags |= LVFMT354_FLAGS_LEFT;
                    format++;
                    n = 1U;
                    break;
                case '+':
                    flags |= LVFMT354_FLAGS_PLUS;
                    format++;
                    n = 1U;
                    break;
                case ' ':
                    flags |= LVFMT354_FLAGS_SPACE;
                    format++;
                    n = 1U;
                    break;
                case '#':
                    flags |= LVFMT354_FLAGS_HASH;
                    format++;
                    n = 1U;
                    break;
                default :
                    n = 0U;
                    break;
            }
        } while(n);

        // evaluate width field
        width = 0U;
        if(lvfmt354_is_digit(*format)) {
            width = lvfmt354_atoi(&format);
        }
        else if(*format == '*') {
            const int w = va_arg(va, int);
            if(w < 0) {
                flags |= LVFMT354_FLAGS_LEFT;    // reverse padding
                width = (unsigned int) - w;
            }
            else {
                width = (unsigned int)w;
            }
            format++;
        }

        // evaluate precision field
        precision = 0U;
        if(*format == '.') {
            flags |= LVFMT354_FLAGS_PRECISION;
            format++;
            if(lvfmt354_is_digit(*format)) {
                precision = lvfmt354_atoi(&format);
            }
            else if(*format == '*') {
                const int prec = (int)va_arg(va, int);
                precision = prec > 0 ? (unsigned int)prec : 0U;
                format++;
            }
        }

        // evaluate length field
        switch(*format) {
            case 'l' :
                flags |= LVFMT354_FLAGS_LONG;
                format++;
                if(*format == 'l') {
                    flags |= LVFMT354_FLAGS_LONG_LONG;
                    format++;
                }
                break;
            case 'h' :
                flags |= LVFMT354_FLAGS_SHORT;
                format++;
                if(*format == 'h') {
                    flags |= LVFMT354_FLAGS_CHAR;
                    format++;
                }
                break;
#if defined(LVFMT354_PRINTF_SUPPORT_PTRDIFF_T)
            case 't' :
                flags |= (sizeof(ptrdiff_t) == sizeof(long) ? LVFMT354_FLAGS_LONG : LVFMT354_FLAGS_LONG_LONG);
                format++;
                break;
#endif
            case 'j' :
                flags |= (sizeof(intmax_t) == sizeof(long) ? LVFMT354_FLAGS_LONG : LVFMT354_FLAGS_LONG_LONG);
                format++;
                break;
            case 'z' :
                flags |= (sizeof(size_t) == sizeof(long) ? LVFMT354_FLAGS_LONG : LVFMT354_FLAGS_LONG_LONG);
                format++;
                break;
            default :
                break;
        }

        // evaluate specifier
        switch(*format) {
            case 'd' :
            case 'i' :
            case 'u' :
            case 'x' :
            case 'X' :
            case 'p' :
            case 'P' :
            case 'o' :
            case 'b' : {
                    // set the base
                    unsigned int base;
                    if(*format == 'x' || *format == 'X') {
                        base = 16U;
                    }
                    else if(*format == 'p' || *format == 'P') {
                        base = 16U;
                        flags |= LVFMT354_FLAGS_HASH;   // always hash for pointer format
#if defined(LVFMT354_PRINTF_SUPPORT_LONG_LONG)
                        if(sizeof(uintptr_t) == sizeof(long long))
                            flags |= LVFMT354_FLAGS_LONG_LONG;
                        else
#endif
                            flags |= LVFMT354_FLAGS_LONG;

                        if(*(format + 1) == 'V')
                            format++;
                    }
                    else if(*format == 'o') {
                        base =  8U;
                    }
                    else if(*format == 'b') {
                        base =  2U;
                    }
                    else {
                        base = 10U;
                        flags &= ~LVFMT354_FLAGS_HASH;   // no hash for dec format
                    }
                    // uppercase
                    if(*format == 'X' || *format == 'P') {
                        flags |= LVFMT354_FLAGS_UPPERCASE;
                    }

                    // no plus or space flag for u, x, X, o, b
                    if((*format != 'i') && (*format != 'd')) {
                        flags &= ~(LVFMT354_FLAGS_PLUS | LVFMT354_FLAGS_SPACE);
                    }

                    // ignore '0' flag when precision is given
                    if(flags & LVFMT354_FLAGS_PRECISION) {
                        flags &= ~LVFMT354_FLAGS_ZEROPAD;
                    }

                    // convert the integer
                    if((*format == 'i') || (*format == 'd')) {
                        // signed
                        if(flags & LVFMT354_FLAGS_LONG_LONG) {
#if defined(LVFMT354_PRINTF_SUPPORT_LONG_LONG)
                            const long long value = va_arg(va, long long);
                            idx = lvfmt354_ntoa_long_long(out, buffer, idx, maxlen, (unsigned long long)(value > 0 ? value : 0 - value), value < 0, base,
                                                  precision, width, flags);
#endif
                        }
                        else if(flags & LVFMT354_FLAGS_LONG) {
                            const long value = va_arg(va, long);
                            idx = lvfmt354_ntoa_long(out, buffer, idx, maxlen, (unsigned long)(value > 0 ? value : 0 - value), value < 0, base, precision,
                                             width, flags);
                        }
                        else {
                            const int value = (flags & LVFMT354_FLAGS_CHAR) ? (char)va_arg(va, int) : (flags & LVFMT354_FLAGS_SHORT) ? (short int)va_arg(va,
                                                                                                                                       int) : va_arg(va, int);
                            idx = lvfmt354_ntoa_long(out, buffer, idx, maxlen, (unsigned int)(value > 0 ? value : 0 - value), value < 0, base, precision,
                                             width, flags);
                        }
                    }
                    else if(*format == 'V') {
                        lvfmt354_vaformat_t * vaf = va_arg(va, lvfmt354_vaformat_t *);
                        va_list copy;

                        va_copy(copy, *vaf->va);
                        idx += lvfmt354_inner(out, buffer + idx, maxlen - idx, vaf->fmt, copy);
                        va_end(copy);
                    }
                    else {
                        // unsigned
                        if(flags & LVFMT354_FLAGS_LONG_LONG) {
#if defined(LVFMT354_PRINTF_SUPPORT_LONG_LONG)
                            idx = lvfmt354_ntoa_long_long(out, buffer, idx, maxlen, va_arg(va, unsigned long long), false, base, precision, width, flags);
#endif
                        }
                        else if(flags & LVFMT354_FLAGS_LONG) {
                            idx = lvfmt354_ntoa_long(out, buffer, idx, maxlen, va_arg(va, unsigned long), false, base, precision, width, flags);
                        }
                        else {
                            const unsigned int value = (flags & LVFMT354_FLAGS_CHAR) ? (unsigned char)va_arg(va,
                                                                                                    unsigned int) : (flags & LVFMT354_FLAGS_SHORT) ? (unsigned short int)va_arg(va, unsigned int) : va_arg(va, unsigned int);
                            idx = lvfmt354_ntoa_long(out, buffer, idx, maxlen, value, false, base, precision, width, flags);
                        }
                    }
                    format++;
                    break;
                }
#if defined(LVFMT354_PRINTF_SUPPORT_FLOAT)
            case 'f' :
            case 'F' :
                if(*format == 'F') flags |= LVFMT354_FLAGS_UPPERCASE;
                idx = lvfmt354_ftoa(out, buffer, idx, maxlen, va_arg(va, double), precision, width, flags);
                format++;
                break;
#if defined(LVFMT354_PRINTF_SUPPORT_EXPONENTIAL)
            case 'e':
            case 'E':
            case 'g':
            case 'G':
                if((*format == 'g') || (*format == 'G')) flags |= LVFMT354_FLAGS_ADAPT_EXP;
                if((*format == 'E') || (*format == 'G')) flags |= LVFMT354_FLAGS_UPPERCASE;
                idx = lvfmt354_etoa(out, buffer, idx, maxlen, va_arg(va, double), precision, width, flags);
                format++;
                break;
#endif  // LVFMT354_PRINTF_SUPPORT_EXPONENTIAL
#endif  // LVFMT354_PRINTF_SUPPORT_FLOAT
            case 'c' : {
                    unsigned int l = 1U;
                    // pre padding
                    if(!(flags & LVFMT354_FLAGS_LEFT)) {
                        while(l++ < width) {
                            out(' ', buffer, idx++, maxlen);
                        }
                    }
                    // char output
                    out((char)va_arg(va, int), buffer, idx++, maxlen);
                    // post padding
                    if(flags & LVFMT354_FLAGS_LEFT) {
                        while(l++ < width) {
                            out(' ', buffer, idx++, maxlen);
                        }
                    }
                    format++;
                    break;
                }

            case 's' : {
                    const char * p = va_arg(va, char *);
                    unsigned int l = lvfmt354_strnlen(p, precision ? precision : (size_t) -1);
                    // pre padding
                    if(flags & LVFMT354_FLAGS_PRECISION) {
                        l = (l < precision ? l : precision);
                    }
                    if(!(flags & LVFMT354_FLAGS_LEFT)) {
                        while(l++ < width) {
                            out(' ', buffer, idx++, maxlen);
                        }
                    }
                    // string output
                    while((*p != 0) && (!(flags & LVFMT354_FLAGS_PRECISION) || precision--)) {
                        out(*(p++), buffer, idx++, maxlen);
                    }
                    // post padding
                    if(flags & LVFMT354_FLAGS_LEFT) {
                        while(l++ < width) {
                            out(' ', buffer, idx++, maxlen);
                        }
                    }
                    format++;
                    break;
                }

            case '%' :
                out('%', buffer, idx++, maxlen);
                format++;
                break;

            default :
                out(*format, buffer, idx++, maxlen);
                format++;
                break;
        }
    }

    // termination
    out((char)0, buffer, idx < maxlen ? idx : maxlen - 1U, maxlen);

    // return written chars without terminating \0
    return (int)idx;
}

///////////////////////////////////////////////////////////////////////////////
/// GLOBAL FUNCTIONS FOR LVGL
///////////////////////////////////////////////////////////////////////////////

int audio_uart_lv_snprintf_483fd0(char * buffer, size_t count, const char * format, ...)
{
    va_list va;
    va_start(va, format);
    const int ret = lvfmt354_inner(lvfmt354_out_buffer, buffer, count, format, va);
    va_end(va);
    return ret;
}

int audio_uart_lv_vsnprintf_483fea(char * buffer, size_t count, const char * format, va_list va)
{
    return lvfmt354_inner(lvfmt354_out_buffer, buffer, count, format, va);
}



#pragma clang attribute pop

/* Source-owned compiler-rt numerical providers: pinned LLVM20.1.8.
 * Upstream licenses retained through directsource inclusion; no executableblobs.
 * Defaultnearest numerical qualification only; nativeIAR/FPstatus equality remainsopen. */
#pragma clang attribute push (__attribute__((target("no-lob,no-mve,no-mve.fp"))), apply_to=function)
#define fixuint_t lvfmt357_adddf3_fixuint_t
#define fixint_t lvfmt357_adddf3_fixint_t
#define __udivXi3 lvfmt357_adddf3___udivXi3
#define __umodXi3 lvfmt357_adddf3___umodXi3
#include "../../../../third-party/upstream/llvm-compiler-rt-format-20.1.8/adddf3.c"
#undef fixuint_t
#undef fixint_t
#undef __udivXi3
#undef __umodXi3
#define fixuint_t lvfmt357_ashldi3_fixuint_t
#define fixint_t lvfmt357_ashldi3_fixint_t
#define __udivXi3 lvfmt357_ashldi3___udivXi3
#define __umodXi3 lvfmt357_ashldi3___umodXi3
#include "../../../../third-party/upstream/llvm-compiler-rt-format-20.1.8/ashldi3.c"
#undef fixuint_t
#undef fixint_t
#undef __udivXi3
#undef __umodXi3
#define fixuint_t lvfmt357_comparedf2_fixuint_t
#define fixint_t lvfmt357_comparedf2_fixint_t
#define __udivXi3 lvfmt357_comparedf2___udivXi3
#define __umodXi3 lvfmt357_comparedf2___umodXi3
#include "../../../../third-party/upstream/llvm-compiler-rt-format-20.1.8/comparedf2.c"
#undef fixuint_t
#undef fixint_t
#undef __udivXi3
#undef __umodXi3
#define fixuint_t lvfmt357_divdf3_fixuint_t
#define fixint_t lvfmt357_divdf3_fixint_t
#define __udivXi3 lvfmt357_divdf3___udivXi3
#define __umodXi3 lvfmt357_divdf3___umodXi3
#include "../../../../third-party/upstream/llvm-compiler-rt-format-20.1.8/divdf3.c"
#undef fixuint_t
#undef fixint_t
#undef __udivXi3
#undef __umodXi3
#define fixuint_t lvfmt357_fixdfsi_fixuint_t
#define fixint_t lvfmt357_fixdfsi_fixint_t
#define __udivXi3 lvfmt357_fixdfsi___udivXi3
#define __umodXi3 lvfmt357_fixdfsi___umodXi3
#include "../../../../third-party/upstream/llvm-compiler-rt-format-20.1.8/fixdfsi.c"
#undef fixuint_t
#undef fixint_t
#undef __udivXi3
#undef __umodXi3
#define fixuint_t lvfmt357_fixunsdfsi_fixuint_t
#define fixint_t lvfmt357_fixunsdfsi_fixint_t
#define __udivXi3 lvfmt357_fixunsdfsi___udivXi3
#define __umodXi3 lvfmt357_fixunsdfsi___umodXi3
#include "../../../../third-party/upstream/llvm-compiler-rt-format-20.1.8/fixunsdfsi.c"
#undef fixuint_t
#undef fixint_t
#undef __udivXi3
#undef __umodXi3
#define fixuint_t lvfmt357_floatsidf_fixuint_t
#define fixint_t lvfmt357_floatsidf_fixint_t
#define __udivXi3 lvfmt357_floatsidf___udivXi3
#define __umodXi3 lvfmt357_floatsidf___umodXi3
#include "../../../../third-party/upstream/llvm-compiler-rt-format-20.1.8/floatsidf.c"
#undef fixuint_t
#undef fixint_t
#undef __udivXi3
#undef __umodXi3
#define fixuint_t lvfmt357_floatunsidf_fixuint_t
#define fixint_t lvfmt357_floatunsidf_fixint_t
#define __udivXi3 lvfmt357_floatunsidf___udivXi3
#define __umodXi3 lvfmt357_floatunsidf___umodXi3
#include "../../../../third-party/upstream/llvm-compiler-rt-format-20.1.8/floatunsidf.c"
#undef fixuint_t
#undef fixint_t
#undef __udivXi3
#undef __umodXi3
#define fixuint_t lvfmt357_fp_mode_fixuint_t
#define fixint_t lvfmt357_fp_mode_fixint_t
#define __udivXi3 lvfmt357_fp_mode___udivXi3
#define __umodXi3 lvfmt357_fp_mode___umodXi3
#include "../../../../third-party/upstream/llvm-compiler-rt-format-20.1.8/fp_mode.c"
#undef fixuint_t
#undef fixint_t
#undef __udivXi3
#undef __umodXi3
#define fixuint_t lvfmt357_lshrdi3_fixuint_t
#define fixint_t lvfmt357_lshrdi3_fixint_t
#define __udivXi3 lvfmt357_lshrdi3___udivXi3
#define __umodXi3 lvfmt357_lshrdi3___umodXi3
#include "../../../../third-party/upstream/llvm-compiler-rt-format-20.1.8/lshrdi3.c"
#undef fixuint_t
#undef fixint_t
#undef __udivXi3
#undef __umodXi3
#define fixuint_t lvfmt357_muldf3_fixuint_t
#define fixint_t lvfmt357_muldf3_fixint_t
#define __udivXi3 lvfmt357_muldf3___udivXi3
#define __umodXi3 lvfmt357_muldf3___umodXi3
#include "../../../../third-party/upstream/llvm-compiler-rt-format-20.1.8/muldf3.c"
#undef fixuint_t
#undef fixint_t
#undef __udivXi3
#undef __umodXi3
#define fixuint_t lvfmt357_subdf3_fixuint_t
#define fixint_t lvfmt357_subdf3_fixint_t
#define __udivXi3 lvfmt357_subdf3___udivXi3
#define __umodXi3 lvfmt357_subdf3___umodXi3
#include "../../../../third-party/upstream/llvm-compiler-rt-format-20.1.8/subdf3.c"
#undef fixuint_t
#undef fixint_t
#undef __udivXi3
#undef __umodXi3
#define fixuint_t lvfmt357_truncdfsf2_fixuint_t
#define fixint_t lvfmt357_truncdfsf2_fixint_t
#define __udivXi3 lvfmt357_truncdfsf2___udivXi3
#define __umodXi3 lvfmt357_truncdfsf2___umodXi3
#include "../../../../third-party/upstream/llvm-compiler-rt-format-20.1.8/truncdfsf2.c"
#undef fixuint_t
#undef fixint_t
#undef __udivXi3
#undef __umodXi3
#define fixuint_t lvfmt357_udivdi3_fixuint_t
#define fixint_t lvfmt357_udivdi3_fixint_t
#define __udivXi3 lvfmt357_udivdi3___udivXi3
#define __umodXi3 lvfmt357_udivdi3___umodXi3
#include "../../../../third-party/upstream/llvm-compiler-rt-format-20.1.8/udivdi3.c"
#undef fixuint_t
#undef fixint_t
#undef __udivXi3
#undef __umodXi3
#define fixuint_t lvfmt357_udivmoddi4_fixuint_t
#define fixint_t lvfmt357_udivmoddi4_fixint_t
#define __udivXi3 lvfmt357_udivmoddi4___udivXi3
#define __umodXi3 lvfmt357_udivmoddi4___umodXi3
#include "../../../../third-party/upstream/llvm-compiler-rt-format-20.1.8/udivmoddi4.c"
#undef fixuint_t
#undef fixint_t
#undef __udivXi3
#undef __umodXi3
#define fixuint_t lvfmt357_umoddi3_fixuint_t
#define fixint_t lvfmt357_umoddi3_fixint_t
#define __udivXi3 lvfmt357_umoddi3___udivXi3
#define __umodXi3 lvfmt357_umoddi3___umodXi3
#include "../../../../third-party/upstream/llvm-compiler-rt-format-20.1.8/umoddi3.c"
#undef fixuint_t
#undef fixint_t
#undef __udivXi3
#undef __umodXi3
#include <stdint.h>



int __aeabi_dcmpge(double a,double b){return __gedf2(a,b)>=0;}
int __aeabi_dcmpgt(double a,double b){return __gedf2(a,b)>0;}
int __aeabi_dcmple(double a,double b){return __ledf2(a,b)<=0;}
int __aeabi_dcmplt(double a,double b){return __ledf2(a,b)<0;}
int __aeabi_dcmpeq(double a,double b){return __eqdf2(a,b)==0;}
__attribute__((naked)) void __aeabi_uldivmod(void){__asm__ volatile(
 "push {r4,lr}\nsub sp,sp,#16\nadd r4,sp,#8\nstr r4,[sp]\nbl __udivmoddi4\nldr r2,[sp,#8]\nldr r3,[sp,#12]\nadd sp,sp,#16\npop {r4,pc}\n");}


#pragma clang attribute pop
