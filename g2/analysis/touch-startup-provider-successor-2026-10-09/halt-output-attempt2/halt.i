# 0 "/source/libgloss/libnosys/_exit.c"
# 0 "<built-in>"
# 0 "<command-line>"
# 1 "/source/libgloss/libnosys/_exit.c"


# 1 "/tool/lib/gcc/arm-none-eabi/14.2.1/include/limits.h" 1 3 4
# 34 "/tool/lib/gcc/arm-none-eabi/14.2.1/include/limits.h" 3 4
# 1 "/tool/lib/gcc/arm-none-eabi/14.2.1/include/syslimits.h" 1 3 4






# 1 "/tool/lib/gcc/arm-none-eabi/14.2.1/include/limits.h" 1 3 4
# 210 "/tool/lib/gcc/arm-none-eabi/14.2.1/include/limits.h" 3 4
# 1 "/tool/arm-none-eabi/include/limits.h" 1 3 4



# 1 "/tool/arm-none-eabi/include/newlib.h" 1 3 4
# 10 "/tool/arm-none-eabi/include/newlib.h" 3 4
# 1 "/tool/arm-none-eabi/include/_newlib_version.h" 1 3 4
# 11 "/tool/arm-none-eabi/include/newlib.h" 2 3 4
# 5 "/tool/arm-none-eabi/include/limits.h" 2 3 4
# 1 "/tool/arm-none-eabi/include/sys/cdefs.h" 1 3 4
# 45 "/tool/arm-none-eabi/include/sys/cdefs.h" 3 4
# 1 "/tool/arm-none-eabi/include/machine/_default_types.h" 1 3 4







# 1 "/tool/arm-none-eabi/include/sys/features.h" 1 3 4
# 9 "/tool/arm-none-eabi/include/machine/_default_types.h" 2 3 4
# 41 "/tool/arm-none-eabi/include/machine/_default_types.h" 3 4

# 41 "/tool/arm-none-eabi/include/machine/_default_types.h" 3 4
typedef signed char __int8_t;

typedef unsigned char __uint8_t;
# 55 "/tool/arm-none-eabi/include/machine/_default_types.h" 3 4
typedef short int __int16_t;

typedef short unsigned int __uint16_t;
# 77 "/tool/arm-none-eabi/include/machine/_default_types.h" 3 4
typedef long int __int32_t;

typedef long unsigned int __uint32_t;
# 103 "/tool/arm-none-eabi/include/machine/_default_types.h" 3 4
typedef long long int __int64_t;

typedef long long unsigned int __uint64_t;
# 134 "/tool/arm-none-eabi/include/machine/_default_types.h" 3 4
typedef signed char __int_least8_t;

typedef unsigned char __uint_least8_t;
# 160 "/tool/arm-none-eabi/include/machine/_default_types.h" 3 4
typedef short int __int_least16_t;

typedef short unsigned int __uint_least16_t;
# 182 "/tool/arm-none-eabi/include/machine/_default_types.h" 3 4
typedef long int __int_least32_t;

typedef long unsigned int __uint_least32_t;
# 200 "/tool/arm-none-eabi/include/machine/_default_types.h" 3 4
typedef long long int __int_least64_t;

typedef long long unsigned int __uint_least64_t;
# 214 "/tool/arm-none-eabi/include/machine/_default_types.h" 3 4
typedef long long int __intmax_t;







typedef long long unsigned int __uintmax_t;







typedef int __intptr_t;

typedef unsigned int __uintptr_t;
# 46 "/tool/arm-none-eabi/include/sys/cdefs.h" 2 3 4

# 1 "/tool/lib/gcc/arm-none-eabi/14.2.1/include/stddef.h" 1 3 4
# 145 "/tool/lib/gcc/arm-none-eabi/14.2.1/include/stddef.h" 3 4
typedef int ptrdiff_t;
# 214 "/tool/lib/gcc/arm-none-eabi/14.2.1/include/stddef.h" 3 4
typedef unsigned int size_t;
# 329 "/tool/lib/gcc/arm-none-eabi/14.2.1/include/stddef.h" 3 4
typedef unsigned int wchar_t;
# 425 "/tool/lib/gcc/arm-none-eabi/14.2.1/include/stddef.h" 3 4
typedef struct {
  long long __max_align_ll __attribute__((__aligned__(__alignof__(long long))));
  long double __max_align_ld __attribute__((__aligned__(__alignof__(long double))));
# 436 "/tool/lib/gcc/arm-none-eabi/14.2.1/include/stddef.h" 3 4
} max_align_t;
# 48 "/tool/arm-none-eabi/include/sys/cdefs.h" 2 3 4
# 6 "/tool/arm-none-eabi/include/limits.h" 2 3 4
# 1 "/tool/arm-none-eabi/include/sys/syslimits.h" 1 3 4
# 7 "/tool/arm-none-eabi/include/limits.h" 2 3 4
# 211 "/tool/lib/gcc/arm-none-eabi/14.2.1/include/limits.h" 2 3 4
# 8 "/tool/lib/gcc/arm-none-eabi/14.2.1/include/syslimits.h" 2 3 4
# 35 "/tool/lib/gcc/arm-none-eabi/14.2.1/include/limits.h" 2 3 4
# 4 "/source/libgloss/libnosys/_exit.c" 2
# 1 "/out/config.h" 1
# 5 "/source/libgloss/libnosys/_exit.c" 2
# 1 "/tool/arm-none-eabi/include/_ansi.h" 1 3
# 11 "/tool/arm-none-eabi/include/_ansi.h" 3
# 1 "/tool/arm-none-eabi/include/sys/config.h" 1 3



# 1 "/tool/arm-none-eabi/include/machine/ieeefp.h" 1 3
# 5 "/tool/arm-none-eabi/include/sys/config.h" 2 3
# 12 "/tool/arm-none-eabi/include/_ansi.h" 2 3
# 6 "/source/libgloss/libnosys/_exit.c" 2
# 1 "/tool/arm-none-eabi/include/_syslist.h" 1 3
# 7 "/source/libgloss/libnosys/_exit.c" 2


# 8 "/source/libgloss/libnosys/_exit.c"
void
_exit (int rc)
{

  int x = rc / 0x7fffffff
# 12 "/source/libgloss/libnosys/_exit.c"
                     ;
  x = 4 / x;


  for (;;)
    ;
}
