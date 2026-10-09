# 0 "/inputs/source/newlib/libc/misc/init.c"
# 0 "<built-in>"
# 0 "<command-line>"
# 1 "/inputs/source/newlib/libc/misc/init.c"
# 14 "/inputs/source/newlib/libc/misc/init.c"
# 1 "/tool/arm-none-eabi/include/sys/types.h" 1 3
# 20 "/tool/arm-none-eabi/include/sys/types.h" 3
# 1 "/tool/arm-none-eabi/include/_ansi.h" 1 3
# 10 "/tool/arm-none-eabi/include/_ansi.h" 3
# 1 "/tool/arm-none-eabi/include/newlib-nano/newlib.h" 1 3 4
# 10 "/tool/arm-none-eabi/include/newlib-nano/newlib.h" 3 4
# 1 "/tool/arm-none-eabi/include/_newlib_version.h" 1 3 4
# 11 "/tool/arm-none-eabi/include/newlib-nano/newlib.h" 2 3 4
# 11 "/tool/arm-none-eabi/include/_ansi.h" 2 3
# 1 "/tool/arm-none-eabi/include/sys/config.h" 1 3



# 1 "/tool/arm-none-eabi/include/machine/ieeefp.h" 1 3
# 5 "/tool/arm-none-eabi/include/sys/config.h" 2 3
# 1 "/tool/arm-none-eabi/include/sys/features.h" 1 3
# 6 "/tool/arm-none-eabi/include/sys/config.h" 2 3
# 12 "/tool/arm-none-eabi/include/_ansi.h" 2 3
# 21 "/tool/arm-none-eabi/include/sys/types.h" 2 3
# 1 "/tool/arm-none-eabi/include/sys/cdefs.h" 1 3
# 45 "/tool/arm-none-eabi/include/sys/cdefs.h" 3
# 1 "/tool/arm-none-eabi/include/machine/_default_types.h" 1 3
# 41 "/tool/arm-none-eabi/include/machine/_default_types.h" 3

# 41 "/tool/arm-none-eabi/include/machine/_default_types.h" 3
typedef signed char __int8_t;

typedef unsigned char __uint8_t;
# 55 "/tool/arm-none-eabi/include/machine/_default_types.h" 3
typedef short int __int16_t;

typedef short unsigned int __uint16_t;
# 77 "/tool/arm-none-eabi/include/machine/_default_types.h" 3
typedef long int __int32_t;

typedef long unsigned int __uint32_t;
# 103 "/tool/arm-none-eabi/include/machine/_default_types.h" 3
typedef long long int __int64_t;

typedef long long unsigned int __uint64_t;
# 134 "/tool/arm-none-eabi/include/machine/_default_types.h" 3
typedef signed char __int_least8_t;

typedef unsigned char __uint_least8_t;
# 160 "/tool/arm-none-eabi/include/machine/_default_types.h" 3
typedef short int __int_least16_t;

typedef short unsigned int __uint_least16_t;
# 182 "/tool/arm-none-eabi/include/machine/_default_types.h" 3
typedef long int __int_least32_t;

typedef long unsigned int __uint_least32_t;
# 200 "/tool/arm-none-eabi/include/machine/_default_types.h" 3
typedef long long int __int_least64_t;

typedef long long unsigned int __uint_least64_t;
# 214 "/tool/arm-none-eabi/include/machine/_default_types.h" 3
typedef long long int __intmax_t;







typedef long long unsigned int __uintmax_t;







typedef int __intptr_t;

typedef unsigned int __uintptr_t;
# 46 "/tool/arm-none-eabi/include/sys/cdefs.h" 2 3

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
# 48 "/tool/arm-none-eabi/include/sys/cdefs.h" 2 3
# 22 "/tool/arm-none-eabi/include/sys/types.h" 2 3
# 1 "/tool/arm-none-eabi/include/machine/_types.h" 1 3
# 23 "/tool/arm-none-eabi/include/sys/types.h" 2 3





typedef __uint8_t u_int8_t;


typedef __uint16_t u_int16_t;


typedef __uint32_t u_int32_t;


typedef __uint64_t u_int64_t;

typedef __intptr_t register_t;





# 1 "/tool/arm-none-eabi/include/sys/_types.h" 1 3
# 24 "/tool/arm-none-eabi/include/sys/_types.h" 3
# 1 "/tool/lib/gcc/arm-none-eabi/14.2.1/include/stddef.h" 1 3 4
# 359 "/tool/lib/gcc/arm-none-eabi/14.2.1/include/stddef.h" 3 4
typedef unsigned int wint_t;
# 25 "/tool/arm-none-eabi/include/sys/_types.h" 2 3





typedef long __blkcnt_t;



typedef long __blksize_t;



typedef __uint64_t __fsblkcnt_t;



typedef __uint32_t __fsfilcnt_t;



typedef long _off_t;





typedef int __pid_t;



typedef short __dev_t;



typedef unsigned short __uid_t;


typedef unsigned short __gid_t;



typedef __uint32_t __id_t;







typedef unsigned short __ino_t;
# 90 "/tool/arm-none-eabi/include/sys/_types.h" 3
typedef __uint32_t __mode_t;





__extension__ typedef long long _off64_t;





typedef _off_t __off_t;


typedef _off64_t __loff_t;


typedef long __key_t;







typedef long _fpos_t;
# 131 "/tool/arm-none-eabi/include/sys/_types.h" 3
typedef unsigned int __size_t;
# 147 "/tool/arm-none-eabi/include/sys/_types.h" 3
typedef signed int _ssize_t;
# 158 "/tool/arm-none-eabi/include/sys/_types.h" 3
typedef _ssize_t __ssize_t;



typedef struct
{
  int __count;
  union
  {
    wint_t __wch;
    unsigned char __wchb[4];
  } __value;
} _mbstate_t;




typedef void *_iconv_t;






typedef unsigned long __clock_t;






typedef __int_least64_t __time_t;





typedef unsigned long __clockid_t;


typedef long __daddr_t;



typedef unsigned long __timer_t;


typedef __uint8_t __sa_family_t;



typedef __uint32_t __socklen_t;


typedef int __nl_item;
typedef unsigned short __nlink_t;
typedef long __suseconds_t;
typedef unsigned long __useconds_t;







typedef __builtin_va_list __va_list;
# 46 "/tool/arm-none-eabi/include/sys/types.h" 2 3
# 1 "/tool/arm-none-eabi/include/sys/_stdint.h" 1 3
# 20 "/tool/arm-none-eabi/include/sys/_stdint.h" 3
typedef __int8_t int8_t ;



typedef __uint8_t uint8_t ;







typedef __int16_t int16_t ;



typedef __uint16_t uint16_t ;







typedef __int32_t int32_t ;



typedef __uint32_t uint32_t ;







typedef __int64_t int64_t ;



typedef __uint64_t uint64_t ;






typedef __intmax_t intmax_t;




typedef __uintmax_t uintmax_t;




typedef __intptr_t intptr_t;




typedef __uintptr_t uintptr_t;
# 47 "/tool/arm-none-eabi/include/sys/types.h" 2 3


# 1 "/tool/arm-none-eabi/include/machine/endian.h" 1 3





# 1 "/tool/arm-none-eabi/include/machine/_endian.h" 1 3
# 7 "/tool/arm-none-eabi/include/machine/endian.h" 2 3
# 50 "/tool/arm-none-eabi/include/sys/types.h" 2 3
# 1 "/tool/arm-none-eabi/include/sys/select.h" 1 3
# 14 "/tool/arm-none-eabi/include/sys/select.h" 3
# 1 "/tool/arm-none-eabi/include/sys/_sigset.h" 1 3
# 41 "/tool/arm-none-eabi/include/sys/_sigset.h" 3
typedef unsigned long __sigset_t;
# 15 "/tool/arm-none-eabi/include/sys/select.h" 2 3
# 1 "/tool/arm-none-eabi/include/sys/_timeval.h" 1 3
# 37 "/tool/arm-none-eabi/include/sys/_timeval.h" 3
typedef __suseconds_t suseconds_t;




typedef __int_least64_t time_t;
# 54 "/tool/arm-none-eabi/include/sys/_timeval.h" 3
struct timeval {
 time_t tv_sec;
 suseconds_t tv_usec;
};
# 16 "/tool/arm-none-eabi/include/sys/select.h" 2 3
# 1 "/tool/arm-none-eabi/include/sys/timespec.h" 1 3
# 38 "/tool/arm-none-eabi/include/sys/timespec.h" 3
# 1 "/tool/arm-none-eabi/include/sys/_timespec.h" 1 3
# 47 "/tool/arm-none-eabi/include/sys/_timespec.h" 3
struct timespec {
 time_t tv_sec;
 long tv_nsec;
};
# 39 "/tool/arm-none-eabi/include/sys/timespec.h" 2 3
# 58 "/tool/arm-none-eabi/include/sys/timespec.h" 3
struct itimerspec {
 struct timespec it_interval;
 struct timespec it_value;
};
# 17 "/tool/arm-none-eabi/include/sys/select.h" 2 3



typedef __sigset_t sigset_t;
# 40 "/tool/arm-none-eabi/include/sys/select.h" 3
typedef unsigned long __fd_mask;

typedef __fd_mask fd_mask;
# 54 "/tool/arm-none-eabi/include/sys/select.h" 3
typedef struct fd_set {
 __fd_mask __fds_bits[(((64) + ((((int)sizeof(__fd_mask) * 8)) - 1)) / (((int)sizeof(__fd_mask) * 8)))];
} fd_set;
# 80 "/tool/arm-none-eabi/include/sys/select.h" 3


int select (int __n, fd_set *__readfds, fd_set *__writefds, fd_set *__exceptfds, struct timeval *__timeout)
                                                   ;

int pselect (int __n, fd_set *__readfds, fd_set *__writefds, fd_set *__exceptfds, const struct timespec *__timeout, const sigset_t *__set)

                           ;



# 51 "/tool/arm-none-eabi/include/sys/types.h" 2 3




typedef __uint32_t in_addr_t;




typedef __uint16_t in_port_t;



typedef __uintptr_t u_register_t;






typedef unsigned char u_char;



typedef unsigned short u_short;



typedef unsigned int u_int;



typedef unsigned long u_long;







typedef unsigned short ushort;
typedef unsigned int uint;
typedef unsigned long ulong;



typedef __blkcnt_t blkcnt_t;




typedef __blksize_t blksize_t;




typedef unsigned long clock_t;
# 118 "/tool/arm-none-eabi/include/sys/types.h" 3
typedef __daddr_t daddr_t;


typedef char * caddr_t;




typedef __fsblkcnt_t fsblkcnt_t;
typedef __fsfilcnt_t fsfilcnt_t;




typedef __id_t id_t;




typedef __ino_t ino_t;
# 155 "/tool/arm-none-eabi/include/sys/types.h" 3
typedef __off_t off_t;



typedef __dev_t dev_t;



typedef __uid_t uid_t;



typedef __gid_t gid_t;




typedef __pid_t pid_t;




typedef __key_t key_t;




typedef _ssize_t ssize_t;




typedef __mode_t mode_t;




typedef __nlink_t nlink_t;




typedef __clockid_t clockid_t;





typedef __timer_t timer_t;





typedef __useconds_t useconds_t;
# 218 "/tool/arm-none-eabi/include/sys/types.h" 3
typedef __int64_t sbintime_t;


# 1 "/tool/arm-none-eabi/include/sys/_pthreadtypes.h" 1 3
# 23 "/tool/arm-none-eabi/include/sys/_pthreadtypes.h" 3
# 1 "/tool/arm-none-eabi/include/sys/sched.h" 1 3
# 48 "/tool/arm-none-eabi/include/sys/sched.h" 3
struct sched_param {
  int sched_priority;
# 61 "/tool/arm-none-eabi/include/sys/sched.h" 3
};
# 24 "/tool/arm-none-eabi/include/sys/_pthreadtypes.h" 2 3
# 32 "/tool/arm-none-eabi/include/sys/_pthreadtypes.h" 3
typedef __uint32_t pthread_t;
# 61 "/tool/arm-none-eabi/include/sys/_pthreadtypes.h" 3
typedef struct {
  int is_initialized;
  void *stackaddr;
  int stacksize;
  int contentionscope;
  int inheritsched;
  int schedpolicy;
  struct sched_param schedparam;





  int detachstate;
} pthread_attr_t;
# 154 "/tool/arm-none-eabi/include/sys/_pthreadtypes.h" 3
typedef __uint32_t pthread_mutex_t;

typedef struct {
  int is_initialized;
# 168 "/tool/arm-none-eabi/include/sys/_pthreadtypes.h" 3
  int recursive;
} pthread_mutexattr_t;






typedef __uint32_t pthread_cond_t;



typedef struct {
  int is_initialized;
  clock_t clock;



} pthread_condattr_t;



typedef __uint32_t pthread_key_t;

typedef struct {
  int is_initialized;
  int init_executed;
} pthread_once_t;
# 222 "/tool/arm-none-eabi/include/sys/types.h" 2 3
# 1 "/tool/arm-none-eabi/include/machine/types.h" 1 3
# 223 "/tool/arm-none-eabi/include/sys/types.h" 2 3
# 15 "/inputs/source/newlib/libc/misc/init.c" 2





# 19 "/inputs/source/newlib/libc/misc/init.c"
extern void (*__preinit_array_start []) (void) __attribute__((weak));
extern void (*__preinit_array_end []) (void) __attribute__((weak));
extern void (*__init_array_start []) (void) __attribute__((weak));
extern void (*__init_array_end []) (void) __attribute__((weak));


extern void _init (void);



void
__libc_init_array (void)
{
  size_t count;
  size_t i;

  count = __preinit_array_end - __preinit_array_start;
  for (i = 0; i < count; i++)
    __preinit_array_start[i] ();


  _init ();


  count = __init_array_end - __init_array_start;
  for (i = 0; i < count; i++)
    __init_array_start[i] ();
}
