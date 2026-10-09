# 0 "/previous/source/libgcc/crtstuff.c"
# 0 "<built-in>"
# 0 "<command-line>"
# 1 "/previous/source/libgcc/crtstuff.c"
# 54 "/previous/source/libgcc/crtstuff.c"
# 1 "/tool/lib/gcc/arm-none-eabi/14.2.1/plugin/include/auto-host.h" 1
# 55 "/previous/source/libgcc/crtstuff.c" 2





# 1 "/out/tconfig.h" 1





# 1 "/tool/lib/gcc/arm-none-eabi/14.2.1/plugin/include/auto-host.h" 1
# 7 "/out/tconfig.h" 2

# 1 "/tool/lib/gcc/arm-none-eabi/14.2.1/plugin/include/ansidecl.h" 1
# 9 "/out/tconfig.h" 2
# 61 "/previous/source/libgcc/crtstuff.c" 2
# 1 "/tool/lib/gcc/arm-none-eabi/14.2.1/plugin/include/tsystem.h" 1
# 44 "/tool/lib/gcc/arm-none-eabi/14.2.1/plugin/include/tsystem.h"
# 1 "/tool/lib/gcc/arm-none-eabi/14.2.1/include/stddef.h" 1 3 4
# 145 "/tool/lib/gcc/arm-none-eabi/14.2.1/include/stddef.h" 3 4

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
# 45 "/tool/lib/gcc/arm-none-eabi/14.2.1/plugin/include/tsystem.h" 2
# 1 "/tool/lib/gcc/arm-none-eabi/14.2.1/include/float.h" 1 3 4
# 46 "/tool/lib/gcc/arm-none-eabi/14.2.1/plugin/include/tsystem.h" 2
# 92 "/tool/lib/gcc/arm-none-eabi/14.2.1/plugin/include/tsystem.h"
# 1 "/tool/lib/gcc/arm-none-eabi/14.2.1/include/stdarg.h" 1 3 4
# 40 "/tool/lib/gcc/arm-none-eabi/14.2.1/include/stdarg.h" 3 4
typedef __builtin_va_list __gnuc_va_list;
# 103 "/tool/lib/gcc/arm-none-eabi/14.2.1/include/stdarg.h" 3 4
typedef __gnuc_va_list va_list;
# 93 "/tool/lib/gcc/arm-none-eabi/14.2.1/plugin/include/tsystem.h" 2


# 1 "/tool/arm-none-eabi/include/stdio.h" 1 3
# 29 "/tool/arm-none-eabi/include/stdio.h" 3
# 1 "/tool/arm-none-eabi/include/_ansi.h" 1 3
# 10 "/tool/arm-none-eabi/include/_ansi.h" 3
# 1 "/tool/arm-none-eabi/include/newlib.h" 1 3
# 10 "/tool/arm-none-eabi/include/newlib.h" 3
# 1 "/tool/arm-none-eabi/include/_newlib_version.h" 1 3
# 11 "/tool/arm-none-eabi/include/newlib.h" 2 3
# 11 "/tool/arm-none-eabi/include/_ansi.h" 2 3
# 1 "/tool/arm-none-eabi/include/sys/config.h" 1 3



# 1 "/tool/arm-none-eabi/include/machine/ieeefp.h" 1 3
# 5 "/tool/arm-none-eabi/include/sys/config.h" 2 3
# 1 "/tool/arm-none-eabi/include/sys/features.h" 1 3
# 6 "/tool/arm-none-eabi/include/sys/config.h" 2 3
# 12 "/tool/arm-none-eabi/include/_ansi.h" 2 3
# 30 "/tool/arm-none-eabi/include/stdio.h" 2 3





# 1 "/tool/arm-none-eabi/include/sys/cdefs.h" 1 3
# 45 "/tool/arm-none-eabi/include/sys/cdefs.h" 3
# 1 "/tool/arm-none-eabi/include/machine/_default_types.h" 1 3
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
# 48 "/tool/arm-none-eabi/include/sys/cdefs.h" 2 3
# 36 "/tool/arm-none-eabi/include/stdio.h" 2 3
# 1 "/tool/lib/gcc/arm-none-eabi/14.2.1/include/stddef.h" 1 3 4
# 37 "/tool/arm-none-eabi/include/stdio.h" 2 3
# 60 "/tool/arm-none-eabi/include/stdio.h" 3
# 1 "/tool/arm-none-eabi/include/sys/reent.h" 1 3
# 13 "/tool/arm-none-eabi/include/sys/reent.h" 3
# 1 "/tool/arm-none-eabi/include/_ansi.h" 1 3
# 14 "/tool/arm-none-eabi/include/sys/reent.h" 2 3
# 1 "/tool/lib/gcc/arm-none-eabi/14.2.1/include/stddef.h" 1 3 4
# 15 "/tool/arm-none-eabi/include/sys/reent.h" 2 3

# 1 "/tool/arm-none-eabi/include/sys/_types.h" 1 3
# 24 "/tool/arm-none-eabi/include/sys/_types.h" 3
# 1 "/tool/lib/gcc/arm-none-eabi/14.2.1/include/stddef.h" 1 3 4
# 359 "/tool/lib/gcc/arm-none-eabi/14.2.1/include/stddef.h" 3 4
typedef unsigned int wint_t;
# 25 "/tool/arm-none-eabi/include/sys/_types.h" 2 3


# 1 "/tool/arm-none-eabi/include/machine/_types.h" 1 3
# 28 "/tool/arm-none-eabi/include/sys/_types.h" 2 3


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
# 17 "/tool/arm-none-eabi/include/sys/reent.h" 2 3






typedef unsigned long __ULong;
# 35 "/tool/arm-none-eabi/include/sys/reent.h" 3
# 1 "/tool/arm-none-eabi/include/sys/lock.h" 1 3
# 33 "/tool/arm-none-eabi/include/sys/lock.h" 3
struct __lock;
typedef struct __lock * _LOCK_T;






extern void __retarget_lock_init(_LOCK_T *lock);

extern void __retarget_lock_init_recursive(_LOCK_T *lock);

extern void __retarget_lock_close(_LOCK_T lock);

extern void __retarget_lock_close_recursive(_LOCK_T lock);

extern void __retarget_lock_acquire(_LOCK_T lock);

extern void __retarget_lock_acquire_recursive(_LOCK_T lock);

extern int __retarget_lock_try_acquire(_LOCK_T lock);

extern int __retarget_lock_try_acquire_recursive(_LOCK_T lock);


extern void __retarget_lock_release(_LOCK_T lock);

extern void __retarget_lock_release_recursive(_LOCK_T lock);
# 36 "/tool/arm-none-eabi/include/sys/reent.h" 2 3
typedef _LOCK_T _flock_t;







struct _reent;

struct __locale_t;






struct _Bigint
{
  struct _Bigint *_next;
  int _k, _maxwds, _sign, _wds;
  __ULong _x[1];
};


struct __tm
{
  int __tm_sec;
  int __tm_min;
  int __tm_hour;
  int __tm_mday;
  int __tm_mon;
  int __tm_year;
  int __tm_wday;
  int __tm_yday;
  int __tm_isdst;
};







struct _on_exit_args {
 void * _fnargs[32];
 void * _dso_handle[32];

 __ULong _fntypes;


 __ULong _is_cxa;
};
# 99 "/tool/arm-none-eabi/include/sys/reent.h" 3
struct _atexit {
 struct _atexit *_next;
 int _ind;

 void (*_fns[32])(void);
        struct _on_exit_args _on_exit_args;
};
# 116 "/tool/arm-none-eabi/include/sys/reent.h" 3
struct __sbuf {
 unsigned char *_base;
 int _size;
};
# 153 "/tool/arm-none-eabi/include/sys/reent.h" 3
struct __sFILE {
  unsigned char *_p;
  int _r;
  int _w;
  short _flags;
  short _file;
  struct __sbuf _bf;
  int _lbfsize;






  void * _cookie;

  int (*_read) (struct _reent *, void *,
        char *, int);
  int (*_write) (struct _reent *, void *,
         const char *,
         int);
  _fpos_t (*_seek) (struct _reent *, void *, _fpos_t, int);
  int (*_close) (struct _reent *, void *);


  struct __sbuf _ub;
  unsigned char *_up;
  int _ur;


  unsigned char _ubuf[3];
  unsigned char _nbuf[1];


  struct __sbuf _lb;


  int _blksize;
  _off_t _offset;


  struct _reent *_data;



  _flock_t _lock;

  _mbstate_t _mbstate;
  int _flags2;
};
# 270 "/tool/arm-none-eabi/include/sys/reent.h" 3
typedef struct __sFILE __FILE;



extern __FILE __sf[3];

struct _glue
{
  struct _glue *_next;
  int _niobs;
  __FILE *_iobs;
};

extern struct _glue __sglue;
# 306 "/tool/arm-none-eabi/include/sys/reent.h" 3
struct _rand48 {
  unsigned short _seed[3];
  unsigned short _mult[3];
  unsigned short _add;




};
# 578 "/tool/arm-none-eabi/include/sys/reent.h" 3
struct _reent
{
  int _errno;




  __FILE *_stdin, *_stdout, *_stderr;

  int _inc;
  char _emergency[25];




  struct __locale_t *_locale;





  void (*__cleanup) (struct _reent *);


  struct _Bigint *_result;
  int _result_k;
  struct _Bigint *_p5s;
  struct _Bigint **_freelist;


  int _cvtlen;
  char *_cvtbuf;

  union
    {
      struct
        {



          char * _strtok_last;
          char _asctime_buf[26];
          struct __tm _localtime_buf;
          int _gamma_signgam;
          __extension__ unsigned long long _rand_next;
          struct _rand48 _r48;
          _mbstate_t _mblen_state;
          _mbstate_t _mbtowc_state;
          _mbstate_t _wctomb_state;
          char _l64a_buf[8];
          char _signal_buf[24];
          int _getdate_err;
          _mbstate_t _mbrlen_state;
          _mbstate_t _mbrtowc_state;
          _mbstate_t _mbsrtowcs_state;
          _mbstate_t _wcrtomb_state;
          _mbstate_t _wcsrtombs_state;
   int _h_errno;
# 647 "/tool/arm-none-eabi/include/sys/reent.h" 3
   char _getlocalename_l_buf[32 ];
        } _reent;







    } _new;







  void (**_sig_func)(int);
};
# 797 "/tool/arm-none-eabi/include/sys/reent.h" 3
extern struct _reent *_impure_ptr ;





extern struct _reent _impure_data ;
# 917 "/tool/arm-none-eabi/include/sys/reent.h" 3
extern struct _atexit *__atexit;
extern struct _atexit __atexit0;

extern void (*__stdio_exit_handler) (void);

void _reclaim_reent (struct _reent *);

extern int _fwalk_sglue (struct _reent *, int (*)(struct _reent *, __FILE *),
    struct _glue *);
# 61 "/tool/arm-none-eabi/include/stdio.h" 2 3





typedef __FILE FILE;



typedef _fpos_t fpos_t;





typedef __off_t off_t;




typedef _ssize_t ssize_t;



# 1 "/tool/arm-none-eabi/include/sys/stdio.h" 1 3
# 86 "/tool/arm-none-eabi/include/stdio.h" 2 3
# 187 "/tool/arm-none-eabi/include/stdio.h" 3
char * ctermid (char *);


char * cuserid (char *);

FILE * tmpfile (void);
char * tmpnam (char *);

char * tempnam (const char *, const char *) __attribute__((__malloc__)) __attribute__((__warn_unused_result__));

int fclose (FILE *);
int fflush (FILE *);
FILE * freopen (const char *restrict, const char *restrict, FILE *restrict);
void setbuf (FILE *restrict, char *restrict);
int setvbuf (FILE *restrict, char *restrict, int, size_t);
int fprintf (FILE *restrict, const char *restrict, ...)
               __attribute__ ((__format__ (__printf__, 2, 3)));
int fscanf (FILE *restrict, const char *restrict, ...)
               __attribute__ ((__format__ (__scanf__, 2, 3)));
int printf (const char *restrict, ...)
               __attribute__ ((__format__ (__printf__, 1, 2)));
int scanf (const char *restrict, ...)
               __attribute__ ((__format__ (__scanf__, 1, 2)));
int sscanf (const char *restrict, const char *restrict, ...)
               __attribute__ ((__format__ (__scanf__, 2, 3)));
int vfprintf (FILE *restrict, const char *restrict, __gnuc_va_list)
               __attribute__ ((__format__ (__printf__, 2, 0)));
int vprintf (const char *, __gnuc_va_list)
               __attribute__ ((__format__ (__printf__, 1, 0)));
int vsprintf (char *restrict, const char *restrict, __gnuc_va_list)
               __attribute__ ((__format__ (__printf__, 2, 0)));
int fgetc (FILE *);
char * fgets (char *restrict, int, FILE *restrict);
int fputc (int, FILE *);
int fputs (const char *restrict, FILE *restrict);
int getc (FILE *);
int getchar (void);
char * gets (char *);
int putc (int, FILE *);
int putchar (int);
int puts (const char *);
int ungetc (int, FILE *);
size_t fread (void *restrict, size_t _size, size_t _n, FILE *restrict);
size_t fwrite (const void *restrict , size_t _size, size_t _n, FILE *);



int fgetpos (FILE *restrict, fpos_t *restrict);

int fseek (FILE *, long, int);



int fsetpos (FILE *, const fpos_t *);

long ftell ( FILE *);
void rewind (FILE *);
void clearerr (FILE *);
int feof (FILE *);
int ferror (FILE *);
void perror (const char *);

FILE * fopen (const char *restrict _name, const char *restrict _type);
int sprintf (char *restrict, const char *restrict, ...)
               __attribute__ ((__format__ (__printf__, 2, 3)));
int remove (const char *);
int rename (const char *, const char *);
# 263 "/tool/arm-none-eabi/include/stdio.h" 3
int fseeko (FILE *, off_t, int);
off_t ftello (FILE *);



int fcloseall (void);



int snprintf (char *restrict, size_t, const char *restrict, ...)
               __attribute__ ((__format__ (__printf__, 3, 4)));
int vsnprintf (char *restrict, size_t, const char *restrict, __gnuc_va_list)
               __attribute__ ((__format__ (__printf__, 3, 0)));
int vfscanf (FILE *restrict, const char *restrict, __gnuc_va_list)
               __attribute__ ((__format__ (__scanf__, 2, 0)));
int vscanf (const char *, __gnuc_va_list)
               __attribute__ ((__format__ (__scanf__, 1, 0)));
int vsscanf (const char *restrict, const char *restrict, __gnuc_va_list)
               __attribute__ ((__format__ (__scanf__, 2, 0)));


int asprintf (char **restrict, const char *restrict, ...)
               __attribute__ ((__format__ (__printf__, 2, 3)));
int vasprintf (char **, const char *, __gnuc_va_list)
               __attribute__ ((__format__ (__printf__, 2, 0)));


int asiprintf (char **, const char *, ...)
               __attribute__ ((__format__ (__printf__, 2, 3)));
char * asniprintf (char *, size_t *, const char *, ...)
               __attribute__ ((__format__ (__printf__, 3, 4)));
char * asnprintf (char *restrict, size_t *restrict, const char *restrict, ...)
               __attribute__ ((__format__ (__printf__, 3, 4)));

int diprintf (int, const char *, ...)
               __attribute__ ((__format__ (__printf__, 2, 3)));

int fiprintf (FILE *, const char *, ...)
               __attribute__ ((__format__ (__printf__, 2, 3)));
int fiscanf (FILE *, const char *, ...)
               __attribute__ ((__format__ (__scanf__, 2, 3)));
int iprintf (const char *, ...)
               __attribute__ ((__format__ (__printf__, 1, 2)));
int iscanf (const char *, ...)
               __attribute__ ((__format__ (__scanf__, 1, 2)));
int siprintf (char *, const char *, ...)
               __attribute__ ((__format__ (__printf__, 2, 3)));
int siscanf (const char *, const char *, ...)
               __attribute__ ((__format__ (__scanf__, 2, 3)));
int sniprintf (char *, size_t, const char *, ...)
               __attribute__ ((__format__ (__printf__, 3, 4)));
int vasiprintf (char **, const char *, __gnuc_va_list)
               __attribute__ ((__format__ (__printf__, 2, 0)));
char * vasniprintf (char *, size_t *, const char *, __gnuc_va_list)
               __attribute__ ((__format__ (__printf__, 3, 0)));
char * vasnprintf (char *, size_t *, const char *, __gnuc_va_list)
               __attribute__ ((__format__ (__printf__, 3, 0)));
int vdiprintf (int, const char *, __gnuc_va_list)
               __attribute__ ((__format__ (__printf__, 2, 0)));
int vfiprintf (FILE *, const char *, __gnuc_va_list)
               __attribute__ ((__format__ (__printf__, 2, 0)));
int vfiscanf (FILE *, const char *, __gnuc_va_list)
               __attribute__ ((__format__ (__scanf__, 2, 0)));
int viprintf (const char *, __gnuc_va_list)
               __attribute__ ((__format__ (__printf__, 1, 0)));
int viscanf (const char *, __gnuc_va_list)
               __attribute__ ((__format__ (__scanf__, 1, 0)));
int vsiprintf (char *, const char *, __gnuc_va_list)
               __attribute__ ((__format__ (__printf__, 2, 0)));
int vsiscanf (const char *, const char *, __gnuc_va_list)
               __attribute__ ((__format__ (__scanf__, 2, 0)));
int vsniprintf (char *, size_t, const char *, __gnuc_va_list)
               __attribute__ ((__format__ (__printf__, 3, 0)));
# 345 "/tool/arm-none-eabi/include/stdio.h" 3
FILE * fdopen (int, const char *);

int fileno (FILE *);


int pclose (FILE *);
FILE * popen (const char *, const char *);



void setbuffer (FILE *, char *, int);
int setlinebuf (FILE *);



int getw (FILE *);
int putw (int, FILE *);


int getc_unlocked (FILE *);
int getchar_unlocked (void);
void flockfile (FILE *);
int ftrylockfile (FILE *);
void funlockfile (FILE *);
int putc_unlocked (int, FILE *);
int putchar_unlocked (int);
# 380 "/tool/arm-none-eabi/include/stdio.h" 3
int dprintf (int, const char *restrict, ...)
               __attribute__ ((__format__ (__printf__, 2, 3)));

FILE * fmemopen (void *restrict, size_t, const char *restrict);


FILE * open_memstream (char **, size_t *);
int vdprintf (int, const char *restrict, __gnuc_va_list)
               __attribute__ ((__format__ (__printf__, 2, 0)));



int renameat (int, const char *, int, const char *);
# 402 "/tool/arm-none-eabi/include/stdio.h" 3
int _asiprintf_r (struct _reent *, char **, const char *, ...)
               __attribute__ ((__format__ (__printf__, 3, 4)));
char * _asniprintf_r (struct _reent *, char *, size_t *, const char *, ...)
               __attribute__ ((__format__ (__printf__, 4, 5)));
char * _asnprintf_r (struct _reent *, char *restrict, size_t *restrict, const char *restrict, ...)
               __attribute__ ((__format__ (__printf__, 4, 5)));
int _asprintf_r (struct _reent *, char **restrict, const char *restrict, ...)
               __attribute__ ((__format__ (__printf__, 3, 4)));
int _diprintf_r (struct _reent *, int, const char *, ...)
               __attribute__ ((__format__ (__printf__, 3, 4)));
int _dprintf_r (struct _reent *, int, const char *restrict, ...)
               __attribute__ ((__format__ (__printf__, 3, 4)));
int _fclose_r (struct _reent *, FILE *);
int _fcloseall_r (struct _reent *);
FILE * _fdopen_r (struct _reent *, int, const char *);
int _fflush_r (struct _reent *, FILE *);
int _fgetc_r (struct _reent *, FILE *);
int _fgetc_unlocked_r (struct _reent *, FILE *);
char * _fgets_r (struct _reent *, char *restrict, int, FILE *restrict);
char * _fgets_unlocked_r (struct _reent *, char *restrict, int, FILE *restrict);




int _fgetpos_r (struct _reent *, FILE *, fpos_t *);
int _fsetpos_r (struct _reent *, FILE *, const fpos_t *);

int _fiprintf_r (struct _reent *, FILE *, const char *, ...)
               __attribute__ ((__format__ (__printf__, 3, 4)));
int _fiscanf_r (struct _reent *, FILE *, const char *, ...)
               __attribute__ ((__format__ (__scanf__, 3, 4)));
FILE * _fmemopen_r (struct _reent *, void *restrict, size_t, const char *restrict);
FILE * _fopen_r (struct _reent *, const char *restrict, const char *restrict);
FILE * _freopen_r (struct _reent *, const char *restrict, const char *restrict, FILE *restrict);
int _fprintf_r (struct _reent *, FILE *restrict, const char *restrict, ...)
               __attribute__ ((__format__ (__printf__, 3, 4)));
int _fpurge_r (struct _reent *, FILE *);
int _fputc_r (struct _reent *, int, FILE *);
int _fputc_unlocked_r (struct _reent *, int, FILE *);
int _fputs_r (struct _reent *, const char *restrict, FILE *restrict);
int _fputs_unlocked_r (struct _reent *, const char *restrict, FILE *restrict);
size_t _fread_r (struct _reent *, void *restrict, size_t _size, size_t _n, FILE *restrict);
size_t _fread_unlocked_r (struct _reent *, void *restrict, size_t _size, size_t _n, FILE *restrict);
int _fscanf_r (struct _reent *, FILE *restrict, const char *restrict, ...)
               __attribute__ ((__format__ (__scanf__, 3, 4)));
int _fseek_r (struct _reent *, FILE *, long, int);
int _fseeko_r (struct _reent *, FILE *, _off_t, int);
long _ftell_r (struct _reent *, FILE *);
_off_t _ftello_r (struct _reent *, FILE *);
void _rewind_r (struct _reent *, FILE *);
size_t _fwrite_r (struct _reent *, const void *restrict, size_t _size, size_t _n, FILE *restrict);
size_t _fwrite_unlocked_r (struct _reent *, const void *restrict, size_t _size, size_t _n, FILE *restrict);
int _getc_r (struct _reent *, FILE *);
int _getc_unlocked_r (struct _reent *, FILE *);
int _getchar_r (struct _reent *);
int _getchar_unlocked_r (struct _reent *);
char * _gets_r (struct _reent *, char *);
int _iprintf_r (struct _reent *, const char *, ...)
               __attribute__ ((__format__ (__printf__, 2, 3)));
int _iscanf_r (struct _reent *, const char *, ...)
               __attribute__ ((__format__ (__scanf__, 2, 3)));
FILE * _open_memstream_r (struct _reent *, char **, size_t *);
void _perror_r (struct _reent *, const char *);
int _printf_r (struct _reent *, const char *restrict, ...)
               __attribute__ ((__format__ (__printf__, 2, 3)));
int _putc_r (struct _reent *, int, FILE *);
int _putc_unlocked_r (struct _reent *, int, FILE *);
int _putchar_unlocked_r (struct _reent *, int);
int _putchar_r (struct _reent *, int);
int _puts_r (struct _reent *, const char *);
int _remove_r (struct _reent *, const char *);
int _rename_r (struct _reent *,
      const char *_old, const char *_new);
int _scanf_r (struct _reent *, const char *restrict, ...)
               __attribute__ ((__format__ (__scanf__, 2, 3)));
int _siprintf_r (struct _reent *, char *, const char *, ...)
               __attribute__ ((__format__ (__printf__, 3, 4)));
int _siscanf_r (struct _reent *, const char *, const char *, ...)
               __attribute__ ((__format__ (__scanf__, 3, 4)));
int _sniprintf_r (struct _reent *, char *, size_t, const char *, ...)
               __attribute__ ((__format__ (__printf__, 4, 5)));
int _snprintf_r (struct _reent *, char *restrict, size_t, const char *restrict, ...)
               __attribute__ ((__format__ (__printf__, 4, 5)));
int _sprintf_r (struct _reent *, char *restrict, const char *restrict, ...)
               __attribute__ ((__format__ (__printf__, 3, 4)));
int _sscanf_r (struct _reent *, const char *restrict, const char *restrict, ...)
               __attribute__ ((__format__ (__scanf__, 3, 4)));
char * _tempnam_r (struct _reent *, const char *, const char *);
FILE * _tmpfile_r (struct _reent *);
char * _tmpnam_r (struct _reent *, char *);
int _ungetc_r (struct _reent *, int, FILE *);
int _vasiprintf_r (struct _reent *, char **, const char *, __gnuc_va_list)
               __attribute__ ((__format__ (__printf__, 3, 0)));
char * _vasniprintf_r (struct _reent*, char *, size_t *, const char *, __gnuc_va_list)
               __attribute__ ((__format__ (__printf__, 4, 0)));
char * _vasnprintf_r (struct _reent*, char *, size_t *, const char *, __gnuc_va_list)
               __attribute__ ((__format__ (__printf__, 4, 0)));
int _vasprintf_r (struct _reent *, char **, const char *, __gnuc_va_list)
               __attribute__ ((__format__ (__printf__, 3, 0)));
int _vdiprintf_r (struct _reent *, int, const char *, __gnuc_va_list)
               __attribute__ ((__format__ (__printf__, 3, 0)));
int _vdprintf_r (struct _reent *, int, const char *restrict, __gnuc_va_list)
               __attribute__ ((__format__ (__printf__, 3, 0)));
int _vfiprintf_r (struct _reent *, FILE *, const char *, __gnuc_va_list)
               __attribute__ ((__format__ (__printf__, 3, 0)));
int _vfiscanf_r (struct _reent *, FILE *, const char *, __gnuc_va_list)
               __attribute__ ((__format__ (__scanf__, 3, 0)));
int _vfprintf_r (struct _reent *, FILE *restrict, const char *restrict, __gnuc_va_list)
               __attribute__ ((__format__ (__printf__, 3, 0)));
int _vfscanf_r (struct _reent *, FILE *restrict, const char *restrict, __gnuc_va_list)
               __attribute__ ((__format__ (__scanf__, 3, 0)));
int _viprintf_r (struct _reent *, const char *, __gnuc_va_list)
               __attribute__ ((__format__ (__printf__, 2, 0)));
int _viscanf_r (struct _reent *, const char *, __gnuc_va_list)
               __attribute__ ((__format__ (__scanf__, 2, 0)));
int _vprintf_r (struct _reent *, const char *restrict, __gnuc_va_list)
               __attribute__ ((__format__ (__printf__, 2, 0)));
int _vscanf_r (struct _reent *, const char *restrict, __gnuc_va_list)
               __attribute__ ((__format__ (__scanf__, 2, 0)));
int _vsiprintf_r (struct _reent *, char *, const char *, __gnuc_va_list)
               __attribute__ ((__format__ (__printf__, 3, 0)));
int _vsiscanf_r (struct _reent *, const char *, const char *, __gnuc_va_list)
               __attribute__ ((__format__ (__scanf__, 3, 0)));
int _vsniprintf_r (struct _reent *, char *, size_t, const char *, __gnuc_va_list)
               __attribute__ ((__format__ (__printf__, 4, 0)));
int _vsnprintf_r (struct _reent *, char *restrict, size_t, const char *restrict, __gnuc_va_list)
               __attribute__ ((__format__ (__printf__, 4, 0)));
int _vsprintf_r (struct _reent *, char *restrict, const char *restrict, __gnuc_va_list)
               __attribute__ ((__format__ (__printf__, 3, 0)));
int _vsscanf_r (struct _reent *, const char *restrict, const char *restrict, __gnuc_va_list)
               __attribute__ ((__format__ (__scanf__, 3, 0)));



int fpurge (FILE *);
ssize_t __getdelim (char **, size_t *, int, FILE *);
ssize_t __getline (char **, size_t *, FILE *);


void clearerr_unlocked (FILE *);
int feof_unlocked (FILE *);
int ferror_unlocked (FILE *);
int fileno_unlocked (FILE *);
int fflush_unlocked (FILE *);
int fgetc_unlocked (FILE *);
int fputc_unlocked (int, FILE *);
size_t fread_unlocked (void *restrict, size_t _size, size_t _n, FILE *restrict);
size_t fwrite_unlocked (const void *restrict , size_t _size, size_t _n, FILE *);



char * fgets_unlocked (char *restrict, int, FILE *restrict);
int fputs_unlocked (const char *restrict, FILE *restrict);
# 583 "/tool/arm-none-eabi/include/stdio.h" 3
int __srget_r (struct _reent *, FILE *);
int __swbuf_r (struct _reent *, int, FILE *);
# 607 "/tool/arm-none-eabi/include/stdio.h" 3
FILE *funopen (const void *__cookie,
  int (*__readfn)(void *__cookie, char *__buf,
    int __n),
  int (*__writefn)(void *__cookie, const char *__buf,
     int __n),
  fpos_t (*__seekfn)(void *__cookie, fpos_t __off, int __whence),
  int (*__closefn)(void *__cookie));
FILE *_funopen_r (struct _reent *, const void *__cookie,
  int (*__readfn)(void *__cookie, char *__buf,
    int __n),
  int (*__writefn)(void *__cookie, const char *__buf,
     int __n),
  fpos_t (*__seekfn)(void *__cookie, fpos_t __off, int __whence),
  int (*__closefn)(void *__cookie));







typedef ssize_t cookie_read_function_t(void *__cookie, char *__buf, size_t __n);
typedef ssize_t cookie_write_function_t(void *__cookie, const char *__buf,
     size_t __n);




typedef int cookie_seek_function_t(void *__cookie, off_t *__off, int __whence);

typedef int cookie_close_function_t(void *__cookie);
typedef struct
{


  cookie_read_function_t *read;
  cookie_write_function_t *write;
  cookie_seek_function_t *seek;
  cookie_close_function_t *close;
} cookie_io_functions_t;
FILE *fopencookie (void *__cookie,
  const char *__mode, cookie_io_functions_t __functions);
FILE *_fopencookie_r (struct _reent *, void *__cookie,
  const char *__mode, cookie_io_functions_t __functions);
# 691 "/tool/arm-none-eabi/include/stdio.h" 3
static __inline__ int __sputc_r(struct _reent *_ptr, int _c, FILE *_p) {




 if (--_p->_w >= 0 || (_p->_w >= _p->_lbfsize && (char)_c != '\n'))
  return (*_p->_p++ = _c);
 else
  return (__swbuf_r(_ptr, _c, _p));
}
# 745 "/tool/arm-none-eabi/include/stdio.h" 3
static __inline int
_getchar_unlocked(void)
{
 struct _reent *_ptr;

 _ptr = _impure_ptr;
 return ((--(((_ptr)->_stdin))->_r < 0 ? __srget_r(_ptr, ((_ptr)->_stdin)) : (int)(*(((_ptr)->_stdin))->_p++)));
}

static __inline int
_putchar_unlocked(int _c)
{
 struct _reent *_ptr;

 _ptr = _impure_ptr;
 return (__sputc_r(_ptr, _c, ((_ptr)->_stdout)));
}
# 801 "/tool/arm-none-eabi/include/stdio.h" 3

# 96 "/tool/lib/gcc/arm-none-eabi/14.2.1/plugin/include/tsystem.h" 2


# 1 "/tool/arm-none-eabi/include/sys/types.h" 1 3
# 28 "/tool/arm-none-eabi/include/sys/types.h" 3
typedef __uint8_t u_int8_t;


typedef __uint16_t u_int16_t;


typedef __uint32_t u_int32_t;


typedef __uint64_t u_int64_t;

typedef __intptr_t register_t;






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
# 159 "/tool/arm-none-eabi/include/sys/types.h" 3
typedef __dev_t dev_t;



typedef __uid_t uid_t;



typedef __gid_t gid_t;




typedef __pid_t pid_t;




typedef __key_t key_t;
# 187 "/tool/arm-none-eabi/include/sys/types.h" 3
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
# 99 "/tool/lib/gcc/arm-none-eabi/14.2.1/plugin/include/tsystem.h" 2


# 1 "/tool/arm-none-eabi/include/errno.h" 1 3




typedef int error_t;



# 1 "/tool/arm-none-eabi/include/sys/errno.h" 1 3
# 19 "/tool/arm-none-eabi/include/sys/errno.h" 3
extern int *__errno (void);






extern const char * const _sys_errlist[];
extern int _sys_nerr;
# 10 "/tool/arm-none-eabi/include/errno.h" 2 3
# 102 "/tool/lib/gcc/arm-none-eabi/14.2.1/plugin/include/tsystem.h" 2






# 1 "/tool/arm-none-eabi/include/string.h" 1 3
# 17 "/tool/arm-none-eabi/include/string.h" 3
# 1 "/tool/lib/gcc/arm-none-eabi/14.2.1/include/stddef.h" 1 3 4
# 18 "/tool/arm-none-eabi/include/string.h" 2 3


# 1 "/tool/arm-none-eabi/include/sys/_locale.h" 1 3
# 9 "/tool/arm-none-eabi/include/sys/_locale.h" 3
struct __locale_t;
typedef struct __locale_t *locale_t;
# 21 "/tool/arm-none-eabi/include/string.h" 2 3



# 1 "/tool/arm-none-eabi/include/strings.h" 1 3
# 44 "/tool/arm-none-eabi/include/strings.h" 3


int bcmp(const void *, const void *, size_t) __attribute__((__pure__));
void bcopy(const void *, void *, size_t);
void bzero(void *, size_t);


void explicit_bzero(void *, size_t);


int ffs(int) __attribute__((__const__));


int ffsl(long) __attribute__((__const__));
int ffsll(long long) __attribute__((__const__));
int fls(int) __attribute__((__const__));
int flsl(long) __attribute__((__const__));
int flsll(long long) __attribute__((__const__));


char *index(const char *, int) __attribute__((__pure__));
char *rindex(const char *, int) __attribute__((__pure__));

int strcasecmp(const char *, const char *) __attribute__((__pure__));
int strncasecmp(const char *, const char *, size_t) __attribute__((__pure__));


int strcasecmp_l (const char *, const char *, locale_t);
int strncasecmp_l (const char *, const char *, size_t, locale_t);


# 25 "/tool/arm-none-eabi/include/string.h" 2 3




void * memchr (const void *, int, size_t);
int memcmp (const void *, const void *, size_t);
void * memcpy (void *restrict, const void *restrict, size_t);
void * memmove (void *, const void *, size_t);
void * memset (void *, int, size_t);
char *strcat (char *restrict, const char *restrict);
char *strchr (const char *, int);
int strcmp (const char *, const char *);
int strcoll (const char *, const char *);
char *strcpy (char *restrict, const char *restrict);
size_t strcspn (const char *, const char *);
char *strerror (int);
size_t strlen (const char *);
char *strncat (char *restrict, const char *restrict, size_t);
int strncmp (const char *, const char *, size_t);
char *strncpy (char *restrict, const char *restrict, size_t);
char *strpbrk (const char *, const char *);
char *strrchr (const char *, int);
size_t strspn (const char *, const char *);
char *strstr (const char *, const char *);

char *strtok (char *restrict, const char *restrict);

size_t strxfrm (char *restrict, const char *restrict, size_t);


int strcoll_l (const char *, const char *, locale_t);
char *strerror_l (int, locale_t);
size_t strxfrm_l (char *restrict, const char *restrict, size_t, locale_t);


char *strtok_r (char *restrict, const char *restrict, char **restrict);


int timingsafe_bcmp (const void *, const void *, size_t);
int timingsafe_memcmp (const void *, const void *, size_t);


void * memccpy (void *restrict, const void *restrict, int, size_t);


void * mempcpy (void *, const void *, size_t);
void * memmem (const void *, size_t, const void *, size_t);
void * memrchr (const void *, int, size_t);
void * rawmemchr (const void *, int);


char *stpcpy (char *restrict, const char *restrict);
char *stpncpy (char *restrict, const char *restrict, size_t);


char *strcasestr (const char *, const char *);
char *strchrnul (const char *, int);


char *strdup (const char *) __attribute__((__malloc__)) __attribute__((__warn_unused_result__));

char *_strdup_r (struct _reent *, const char *);

char *strndup (const char *, size_t) __attribute__((__malloc__)) __attribute__((__warn_unused_result__));

char *_strndup_r (struct _reent *, const char *, size_t);






char *strerror_r (int, char *, size_t);
# 112 "/tool/arm-none-eabi/include/string.h" 3
char * _strerror_r (struct _reent *, int, int, int *);


size_t strlcat (char *, const char *, size_t);
size_t strlcpy (char *, const char *, size_t);


size_t strnlen (const char *, size_t);


char *strsep (char **, const char *);


char *strnstr(const char *, const char *, size_t) __attribute__((__pure__));



char *strlwr (char *);
char *strupr (char *);



char *strsignal (int __signo);







int strverscmp (const char *, const char *);
# 172 "/tool/arm-none-eabi/include/string.h" 3
char *__attribute__((__nonnull__ (1))) basename (const char *) __asm__("" "__gnu_basename");


# 1 "/tool/arm-none-eabi/include/sys/string.h" 1 3
# 176 "/tool/arm-none-eabi/include/string.h" 2 3


# 109 "/tool/lib/gcc/arm-none-eabi/14.2.1/plugin/include/tsystem.h" 2
# 1 "/tool/arm-none-eabi/include/stdlib.h" 1 3
# 10 "/tool/arm-none-eabi/include/stdlib.h" 3
# 1 "/tool/arm-none-eabi/include/machine/ieeefp.h" 1 3
# 11 "/tool/arm-none-eabi/include/stdlib.h" 2 3





# 1 "/tool/lib/gcc/arm-none-eabi/14.2.1/include/stddef.h" 1 3 4
# 17 "/tool/arm-none-eabi/include/stdlib.h" 2 3



# 1 "/tool/arm-none-eabi/include/machine/stdlib.h" 1 3
# 21 "/tool/arm-none-eabi/include/stdlib.h" 2 3

# 1 "/tool/arm-none-eabi/include/alloca.h" 1 3
# 23 "/tool/arm-none-eabi/include/stdlib.h" 2 3
# 33 "/tool/arm-none-eabi/include/stdlib.h" 3


typedef struct
{
  int quot;
  int rem;
} div_t;

typedef struct
{
  long quot;
  long rem;
} ldiv_t;


typedef struct
{
  long long int quot;
  long long int rem;
} lldiv_t;




typedef int (*__compar_fn_t) (const void *, const void *);







int __locale_mb_cur_max (void);



void abort (void) __attribute__ ((__noreturn__));
int abs (int);

__uint32_t arc4random (void);
__uint32_t arc4random_uniform (__uint32_t);
void arc4random_buf (void *, size_t);

int atexit (void (*__func)(void));
double atof (const char *__nptr);

float atoff (const char *__nptr);

int atoi (const char *__nptr);
int _atoi_r (struct _reent *, const char *__nptr);
long atol (const char *__nptr);
long _atol_r (struct _reent *, const char *__nptr);
void * bsearch (const void *__key,
         const void *__base,
         size_t __nmemb,
         size_t __size,
         __compar_fn_t _compar);
void *calloc(size_t, size_t) __attribute__((__malloc__)) __attribute__((__warn_unused_result__))
      __attribute__((__alloc_size__(1, 2))) ;
div_t div (int __numer, int __denom);
void exit (int __status) __attribute__ ((__noreturn__));
void free (void *) ;
char * getenv (const char *__string);
char * _getenv_r (struct _reent *, const char *__string);

char * secure_getenv (const char *__string);

char * _findenv (const char *, int *);
char * _findenv_r (struct _reent *, const char *, int *);

extern char *suboptarg;
int getsubopt (char **, char * const *, char **);

long labs (long);
ldiv_t ldiv (long __numer, long __denom);
void *malloc(size_t) __attribute__((__malloc__)) __attribute__((__warn_unused_result__)) __attribute__((__alloc_size__(1))) ;
int mblen (const char *, size_t);
int _mblen_r (struct _reent *, const char *, size_t, _mbstate_t *);
int mbtowc (wchar_t *restrict, const char *restrict, size_t);
int _mbtowc_r (struct _reent *, wchar_t *restrict, const char *restrict, size_t, _mbstate_t *);
int wctomb (char *, wchar_t);
int _wctomb_r (struct _reent *, char *, wchar_t, _mbstate_t *);
size_t mbstowcs (wchar_t *restrict, const char *restrict, size_t);
size_t _mbstowcs_r (struct _reent *, wchar_t *restrict, const char *restrict, size_t, _mbstate_t *);
size_t wcstombs (char *restrict, const wchar_t *restrict, size_t);
size_t _wcstombs_r (struct _reent *, char *restrict, const wchar_t *restrict, size_t, _mbstate_t *);


char * mkdtemp (char *);


int mkostemp (char *, int);
int mkostemps (char *, int, int);


int mkstemp (char *);


int mkstemps (char *, int);


char * mktemp (char *) __attribute__ ((__deprecated__("the use of `mktemp' is dangerous; use `mkstemp' instead")));


char * _mkdtemp_r (struct _reent *, char *);
int _mkostemp_r (struct _reent *, char *, int);
int _mkostemps_r (struct _reent *, char *, int, int);
int _mkstemp_r (struct _reent *, char *);
int _mkstemps_r (struct _reent *, char *, int);
char * _mktemp_r (struct _reent *, char *) __attribute__ ((__deprecated__("the use of `mktemp' is dangerous; use `mkstemp' instead")));
void qsort (void *__base, size_t __nmemb, size_t __size, __compar_fn_t _compar);
int rand (void);
void *realloc(void *, size_t) __attribute__((__warn_unused_result__)) __attribute__((__alloc_size__(2))) ;

void *reallocarray(void *, size_t, size_t) __attribute__((__warn_unused_result__)) __attribute__((__alloc_size__(2, 3)));
void *reallocf(void *, size_t) __attribute__((__warn_unused_result__)) __attribute__((__alloc_size__(2)));


char * realpath (const char *restrict path, char *restrict resolved_path);


int rpmatch (const char *response);


void setkey (const char *__key);

void srand (unsigned __seed);
double strtod (const char *restrict __n, char **restrict __end_PTR);
double _strtod_r (struct _reent *,const char *restrict __n, char **restrict __end_PTR);

float strtof (const char *restrict __n, char **restrict __end_PTR);







long strtol (const char *restrict __n, char **restrict __end_PTR, int __base);
long _strtol_r (struct _reent *,const char *restrict __n, char **restrict __end_PTR, int __base);
unsigned long strtoul (const char *restrict __n, char **restrict __end_PTR, int __base);
unsigned long _strtoul_r (struct _reent *,const char *restrict __n, char **restrict __end_PTR, int __base);


double strtod_l (const char *restrict, char **restrict, locale_t);
float strtof_l (const char *restrict, char **restrict, locale_t);

extern long double strtold_l (const char *restrict, char **restrict,
         locale_t);

long strtol_l (const char *restrict, char **restrict, int, locale_t);
unsigned long strtoul_l (const char *restrict, char **restrict, int,
    locale_t __loc);
long long strtoll_l (const char *restrict, char **restrict, int, locale_t);
unsigned long long strtoull_l (const char *restrict, char **restrict, int,
          locale_t __loc);


int system (const char *__string);


long a64l (const char *__input);
char * l64a (long __input);
char * _l64a_r (struct _reent *,long __input);


int on_exit (void (*__func)(int, void *),void *__arg);


void _Exit (int __status) __attribute__ ((__noreturn__));


int putenv (char *__string);

int _putenv_r (struct _reent *, char *__string);
void * _reallocf_r (struct _reent *, void *, size_t);

int setenv (const char *__string, const char *__value, int __overwrite);

int _setenv_r (struct _reent *, const char *__string, const char *__value, int __overwrite);
# 225 "/tool/arm-none-eabi/include/stdlib.h" 3
char * __itoa (int, char *, int);
char * __utoa (unsigned, char *, int);

char * itoa (int, char *, int);
char * utoa (unsigned, char *, int);



int rand_r (unsigned *__seed);



double drand48 (void);
double _drand48_r (struct _reent *);
double erand48 (unsigned short [3]);
double _erand48_r (struct _reent *, unsigned short [3]);
long jrand48 (unsigned short [3]);
long _jrand48_r (struct _reent *, unsigned short [3]);
void lcong48 (unsigned short [7]);
void _lcong48_r (struct _reent *, unsigned short [7]);
long lrand48 (void);
long _lrand48_r (struct _reent *);
long mrand48 (void);
long _mrand48_r (struct _reent *);
long nrand48 (unsigned short [3]);
long _nrand48_r (struct _reent *, unsigned short [3]);
unsigned short *
       seed48 (unsigned short [3]);
unsigned short *
       _seed48_r (struct _reent *, unsigned short [3]);
void srand48 (long);
void _srand48_r (struct _reent *, long);


char * initstate (unsigned, char *, size_t);
long random (void);
char * setstate (char *);
void srandom (unsigned);


long long atoll (const char *__nptr);

long long _atoll_r (struct _reent *, const char *__nptr);

long long llabs (long long);
lldiv_t lldiv (long long __numer, long long __denom);
long long strtoll (const char *restrict __n, char **restrict __end_PTR, int __base);

long long _strtoll_r (struct _reent *, const char *restrict __n, char **restrict __end_PTR, int __base);

unsigned long long strtoull (const char *restrict __n, char **restrict __end_PTR, int __base);

unsigned long long _strtoull_r (struct _reent *, const char *restrict __n, char **restrict __end_PTR, int __base);



void cfree (void *);


int unsetenv (const char *__string);

int _unsetenv_r (struct _reent *, const char *__string);



int posix_memalign (void **, size_t, size_t) __attribute__((__nonnull__ (1)))
     __attribute__((__warn_unused_result__));


char * _dtoa_r (struct _reent *, double, int, int, int *, int*, char**);

void * _malloc_r (struct _reent *, size_t) ;
void * _calloc_r (struct _reent *, size_t, size_t) ;
void _free_r (struct _reent *, void *) ;
void * _realloc_r (struct _reent *, void *, size_t) ;
void _mstats_r (struct _reent *, char *);

int _system_r (struct _reent *, const char *);

void __eprintf (const char *, const char *, unsigned int, const char *);






void qsort_r (void *__base, size_t __nmemb, size_t __size, int (*_compar)(const void *, const void *, void *), void *__thunk);
# 324 "/tool/arm-none-eabi/include/stdlib.h" 3
extern long double _strtold_r (struct _reent *, const char *restrict, char **restrict);

extern long double strtold (const char *restrict, char **restrict);







void * aligned_alloc(size_t, size_t) __attribute__((__malloc__)) __attribute__((__alloc_align__(1)))
     __attribute__((__alloc_size__(2))) __attribute__((__warn_unused_result__));
int at_quick_exit(void (*)(void));
_Noreturn void
 quick_exit(int);



# 110 "/tool/lib/gcc/arm-none-eabi/14.2.1/plugin/include/tsystem.h" 2
# 1 "/tool/arm-none-eabi/include/unistd.h" 1 3



# 1 "/tool/arm-none-eabi/include/sys/unistd.h" 1 3
# 14 "/tool/arm-none-eabi/include/sys/unistd.h" 3
# 1 "/tool/lib/gcc/arm-none-eabi/14.2.1/include/stddef.h" 1 3 4
# 15 "/tool/arm-none-eabi/include/sys/unistd.h" 2 3

extern char **environ;

void _exit (int __status) __attribute__ ((__noreturn__));

int access (const char *__path, int __amode);
unsigned alarm (unsigned __secs);
int chdir (const char *__path);
int chmod (const char *__path, mode_t __mode);
int chown (const char *__path, uid_t __owner, gid_t __group);

int chroot (const char *__path);

int close (int __fildes);







size_t confstr (int __name, char *__buf, size_t __len);


char * crypt (const char *__key, const char *__salt);
# 48 "/tool/arm-none-eabi/include/sys/unistd.h" 3
int daemon (int nochdir, int noclose);

int dup (int __fildes);
int dup2 (int __fildes, int __fildes2);

int dup3 (int __fildes, int __fildes2, int flags);
int eaccess (const char *__path, int __mode);


void encrypt (char *__block, int __edflag);


void endusershell (void);


int euidaccess (const char *__path, int __mode);

int execl (const char *__path, const char *, ...);
int execle (const char *__path, const char *, ...);
int execlp (const char *__file, const char *, ...);

int execlpe (const char *__file, const char *, ...);

int execv (const char *__path, char * const __argv[]);
int execve (const char *__path, char * const __argv[], char * const __envp[]);
int execvp (const char *__file, char * const __argv[]);

int execvpe (const char *__file, char * const __argv[], char * const __envp[]);


int faccessat (int __dirfd, const char *__path, int __mode, int __flags);


int fchdir (int __fildes);


int fchmod (int __fildes, mode_t __mode);


int fchown (int __fildes, uid_t __owner, gid_t __group);


int fchownat (int __dirfd, const char *__path, uid_t __owner, gid_t __group, int __flags);


int fexecve (int __fd, char * const __argv[], char * const __envp[]);

pid_t fork (void);
long fpathconf (int __fd, int __name);
int fsync (int __fd);

int fdatasync (int __fd);


char * get_current_dir_name (void);

char * getcwd (char *__buf, size_t __size);

int getdomainname (char *__name, size_t __len);


int getentropy (void *, size_t);

gid_t getegid (void);
uid_t geteuid (void);
gid_t getgid (void);
int getgroups (int __gidsetsize, gid_t __grouplist[]);

long gethostid (void);

char * getlogin (void);




char * getpass (const char *__prompt);
int getpagesize (void);


int getpeereid (int, uid_t *, gid_t *);


pid_t getpgid (pid_t);

pid_t getpgrp (void);
pid_t getpid (void);
pid_t getppid (void);

pid_t getsid (pid_t);

uid_t getuid (void);

char * getusershell (void);


char * getwd (char *__buf);


int iruserok (unsigned long raddr, int superuser, const char *ruser, const char *luser);

int isatty (int __fildes);

int issetugid (void);


int lchown (const char *__path, uid_t __owner, gid_t __group);

int link (const char *__path1, const char *__path2);

int linkat (int __dirfd1, const char *__path1, int __dirfd2, const char *__path2, int __flags);


int nice (int __nice_value);


off_t lseek (int __fildes, off_t __offset, int __whence);






int lockf (int __fd, int __cmd, off_t __len);

long pathconf (const char *__path, int __name);
int pause (void);

int pthread_atfork (void (*)(void), void (*)(void), void (*)(void));

int pipe (int __fildes[2]);

int pipe2 (int __fildes[2], int flags);


ssize_t pread (int __fd, void *__buf, size_t __nbytes, off_t __offset);
ssize_t pwrite (int __fd, const void *__buf, size_t __nbytes, off_t __offset);

int read (int __fd, void *__buf, size_t __nbyte);

int rresvport (int *__alport);
int revoke (char *__path);

int rmdir (const char *__path);

int ruserok (const char *rhost, int superuser, const char *ruser, const char *luser);


void * sbrk (ptrdiff_t __incr);


int setegid (gid_t __gid);
int seteuid (uid_t __uid);

int setgid (gid_t __gid);

int setgroups (int ngroups, const gid_t *grouplist);


int sethostname (const char *, size_t);

int setpgid (pid_t __pid, pid_t __pgid);

int setpgrp (void);
# 221 "/tool/arm-none-eabi/include/sys/unistd.h" 3
int setregid (gid_t __rgid, gid_t __egid);
int setreuid (uid_t __ruid, uid_t __euid);

pid_t setsid (void);
int setuid (uid_t __uid);

void setusershell (void);

unsigned sleep (unsigned int __seconds);

void swab (const void *restrict, void *restrict, ssize_t);

long sysconf (int __name);
pid_t tcgetpgrp (int __fildes);
int tcsetpgrp (int __fildes, pid_t __pgrp_id);
char * ttyname (int __fildes);
int ttyname_r (int, char *, size_t);
int unlink (const char *__path);

int usleep (useconds_t __useconds);


int vhangup (void);

int write (int __fd, const void *__buf, size_t __nbyte);






extern char *optarg;
extern int optind, opterr, optopt;
int getopt(int, char * const [], const char *);
extern int optreset;



pid_t vfork (void);
# 284 "/tool/arm-none-eabi/include/sys/unistd.h" 3
int ftruncate (int __fd, off_t __length);


int truncate (const char *, off_t __length);




int getdtablesize (void);


useconds_t ualarm (useconds_t __useconds, useconds_t __interval);





 int gethostname (char *__name, size_t __len);




int setdtablesize (int);



void sync (void);



ssize_t readlink (const char *restrict __path,
                          char *restrict __buf, size_t __buflen);
int symlink (const char *__name1, const char *__name2);


ssize_t readlinkat (int __dirfd1, const char *restrict __path,
                            char *restrict __buf, size_t __buflen);
int symlinkat (const char *, int, const char *);
int unlinkat (int, const char *, int);
# 5 "/tool/arm-none-eabi/include/unistd.h" 2 3
# 111 "/tool/lib/gcc/arm-none-eabi/14.2.1/plugin/include/tsystem.h" 2


# 1 "/tool/lib/gcc/arm-none-eabi/14.2.1/include/limits.h" 1 3 4
# 34 "/tool/lib/gcc/arm-none-eabi/14.2.1/include/limits.h" 3 4
# 1 "/tool/lib/gcc/arm-none-eabi/14.2.1/include/syslimits.h" 1 3 4






# 1 "/tool/lib/gcc/arm-none-eabi/14.2.1/include/limits.h" 1 3 4
# 210 "/tool/lib/gcc/arm-none-eabi/14.2.1/include/limits.h" 3 4
# 1 "/tool/arm-none-eabi/include/limits.h" 1 3 4





# 1 "/tool/arm-none-eabi/include/sys/syslimits.h" 1 3 4
# 7 "/tool/arm-none-eabi/include/limits.h" 2 3 4
# 211 "/tool/lib/gcc/arm-none-eabi/14.2.1/include/limits.h" 2 3 4
# 8 "/tool/lib/gcc/arm-none-eabi/14.2.1/include/syslimits.h" 2 3 4
# 35 "/tool/lib/gcc/arm-none-eabi/14.2.1/include/limits.h" 2 3 4
# 114 "/tool/lib/gcc/arm-none-eabi/14.2.1/plugin/include/tsystem.h" 2


# 1 "/tool/arm-none-eabi/include/time.h" 1 3
# 16 "/tool/arm-none-eabi/include/time.h" 3
# 1 "/tool/lib/gcc/arm-none-eabi/14.2.1/include/stddef.h" 1 3 4
# 17 "/tool/arm-none-eabi/include/time.h" 2 3


# 1 "/tool/arm-none-eabi/include/machine/time.h" 1 3
# 20 "/tool/arm-none-eabi/include/time.h" 2 3
# 35 "/tool/arm-none-eabi/include/time.h" 3


struct tm
{
  int tm_sec;
  int tm_min;
  int tm_hour;
  int tm_mday;
  int tm_mon;
  int tm_year;
  int tm_wday;
  int tm_yday;
  int tm_isdst;






};

clock_t clock (void);
double difftime (time_t _time2, time_t _time1);
time_t mktime (struct tm *_timeptr);
time_t time (time_t *_timer);

char *asctime (const struct tm *_tblock);
char *ctime (const time_t *_time);
struct tm *gmtime (const time_t *_timer);
struct tm *localtime (const time_t *_timer);

size_t strftime (char *restrict _s,
        size_t _maxsize, const char *restrict _fmt,
        const struct tm *restrict _t);


extern size_t strftime_l (char *restrict _s, size_t _maxsize,
     const char *restrict _fmt,
     const struct tm *restrict _t, locale_t _l);


char *asctime_r (const struct tm *restrict,
     char *restrict);
char *ctime_r (const time_t *, char *);
struct tm *gmtime_r (const time_t *restrict,
     struct tm *restrict);
struct tm *localtime_r (const time_t *restrict,
     struct tm *restrict);








char *strptime (const char *restrict,
     const char *restrict,
     struct tm *restrict);


char *strptime_l (const char *restrict, const char *restrict,
    struct tm *restrict, locale_t);



void tzset (void);

void _tzset_r (struct _reent *);
# 134 "/tool/arm-none-eabi/include/time.h" 3
extern long _timezone;
extern int _daylight;


extern char *_tzname[2];
# 117 "/tool/lib/gcc/arm-none-eabi/14.2.1/plugin/include/tsystem.h" 2
# 143 "/tool/lib/gcc/arm-none-eabi/14.2.1/plugin/include/tsystem.h"
# 1 "/tool/lib/gcc/arm-none-eabi/14.2.1/plugin/include/filenames.h" 1
# 29 "/tool/lib/gcc/arm-none-eabi/14.2.1/plugin/include/filenames.h"
# 1 "/tool/lib/gcc/arm-none-eabi/14.2.1/plugin/include/hashtab.h" 1
# 39 "/tool/lib/gcc/arm-none-eabi/14.2.1/plugin/include/hashtab.h"
# 1 "/tool/lib/gcc/arm-none-eabi/14.2.1/plugin/include/ansidecl.h" 1
# 40 "/tool/lib/gcc/arm-none-eabi/14.2.1/plugin/include/hashtab.h" 2



# 42 "/tool/lib/gcc/arm-none-eabi/14.2.1/plugin/include/hashtab.h"
typedef unsigned int hashval_t;




typedef hashval_t (*htab_hash) (const void *);






typedef int (*htab_eq) (const void *, const void *);



typedef void (*htab_del) (void *);





typedef int (*htab_trav) (void **, void *);





typedef void *(*htab_alloc) (size_t, size_t);


typedef void (*htab_free) (void *);



typedef void *(*htab_alloc_with_arg) (void *, size_t, size_t);
typedef void (*htab_free_with_arg) (void *, void *);
# 95 "/tool/lib/gcc/arm-none-eabi/14.2.1/plugin/include/hashtab.h"
struct htab {

  htab_hash hash_f;


  htab_eq eq_f;


  htab_del del_f;


  void **entries;


  size_t size;


  size_t n_elements;


  size_t n_deleted;



  unsigned int searches;



  unsigned int collisions;


  htab_alloc alloc_f;
  htab_free free_f;


  void *alloc_arg;
  htab_alloc_with_arg alloc_with_arg_f;
  htab_free_with_arg free_with_arg_f;



  unsigned int size_prime_index;
};

typedef struct htab *htab_t;


enum insert_option {NO_INSERT, INSERT};



extern htab_t htab_create_alloc (size_t, htab_hash,
                                    htab_eq, htab_del,
                                    htab_alloc, htab_free);

extern htab_t htab_create_alloc_ex (size_t, htab_hash,
                                      htab_eq, htab_del,
                                      void *, htab_alloc_with_arg,
                                      htab_free_with_arg);

extern htab_t htab_create_typed_alloc (size_t, htab_hash, htab_eq, htab_del,
     htab_alloc, htab_alloc, htab_free);


extern htab_t htab_create (size_t, htab_hash, htab_eq, htab_del);
extern htab_t htab_try_create (size_t, htab_hash, htab_eq, htab_del);

extern void htab_set_functions_ex (htab_t, htab_hash,
                                       htab_eq, htab_del,
                                       void *, htab_alloc_with_arg,
                                       htab_free_with_arg);

extern void htab_delete (htab_t);
extern void htab_empty (htab_t);

extern void * htab_find (htab_t, const void *);
extern void ** htab_find_slot (htab_t, const void *, enum insert_option);
extern void * htab_find_with_hash (htab_t, const void *, hashval_t);
extern void ** htab_find_slot_with_hash (htab_t, const void *,
       hashval_t, enum insert_option);
extern void htab_clear_slot (htab_t, void **);
extern void htab_remove_elt (htab_t, const void *);
extern void htab_remove_elt_with_hash (htab_t, const void *, hashval_t);

extern void htab_traverse (htab_t, htab_trav, void *);
extern void htab_traverse_noresize (htab_t, htab_trav, void *);

extern size_t htab_size (htab_t);
extern size_t htab_elements (htab_t);
extern double htab_collisions (htab_t);


extern htab_hash htab_hash_pointer;


extern htab_eq htab_eq_pointer;


extern hashval_t htab_hash_string (const void *);


extern int htab_eq_string (const void *, const void *);


extern hashval_t iterative_hash (const void *, size_t, hashval_t);
# 30 "/tool/lib/gcc/arm-none-eabi/14.2.1/plugin/include/filenames.h" 2
# 84 "/tool/lib/gcc/arm-none-eabi/14.2.1/plugin/include/filenames.h"
extern int filename_cmp (const char *s1, const char *s2);


extern int filename_ncmp (const char *s1, const char *s2,
     size_t n);

extern hashval_t filename_hash (const void *s);

extern int filename_eq (const void *s1, const void *s2);

extern int canonical_filename_eq (const char *a, const char *b);
# 144 "/tool/lib/gcc/arm-none-eabi/14.2.1/plugin/include/tsystem.h" 2
# 62 "/previous/source/libgcc/crtstuff.c" 2
# 1 "/tool/lib/gcc/arm-none-eabi/14.2.1/plugin/include/coretypes.h" 1
# 387 "/tool/lib/gcc/arm-none-eabi/14.2.1/plugin/include/coretypes.h"
struct _dont_use_rtx_here_;
struct _dont_use_rtvec_here_;
struct _dont_use_rtx_insn_here_;
union _dont_use_tree_here_;
# 399 "/tool/lib/gcc/arm-none-eabi/14.2.1/plugin/include/coretypes.h"
typedef struct scalar_mode scalar_mode;
typedef struct scalar_int_mode scalar_int_mode;
typedef struct scalar_float_mode scalar_float_mode;
typedef struct complex_mode complex_mode;





enum function_class {
  function_c94,
  function_c99_misc,
  function_c99_math_complex,
  function_sincos,
  function_c11_misc,
  function_c23_misc
};



enum symbol_visibility
{
  VISIBILITY_DEFAULT,
  VISIBILITY_PROTECTED,
  VISIBILITY_HIDDEN,
  VISIBILITY_INTERNAL
};



enum flt_eval_method
{
  FLT_EVAL_METHOD_UNPREDICTABLE = -1,
  FLT_EVAL_METHOD_PROMOTE_TO_FLOAT = 0,
  FLT_EVAL_METHOD_PROMOTE_TO_DOUBLE = 1,
  FLT_EVAL_METHOD_PROMOTE_TO_LONG_DOUBLE = 2,
  FLT_EVAL_METHOD_PROMOTE_TO_FLOAT16 = 16
};

enum excess_precision_type
{
  EXCESS_PRECISION_TYPE_IMPLICIT,
  EXCESS_PRECISION_TYPE_STANDARD,
  EXCESS_PRECISION_TYPE_FAST,
  EXCESS_PRECISION_TYPE_FLOAT16
};



enum optimize_size_level
{

  OPTIMIZE_SIZE_NO,

  OPTIMIZE_SIZE_BALANCED,

  OPTIMIZE_SIZE_MAX
};





typedef void (*gt_pointer_operator) (void *, void *, void *);


typedef unsigned char uchar;
# 63 "/previous/source/libgcc/crtstuff.c" 2
# 1 "/tool/lib/gcc/arm-none-eabi/14.2.1/plugin/include/tm.h" 1
# 20 "/tool/lib/gcc/arm-none-eabi/14.2.1/plugin/include/tm.h"
# 1 "/tool/lib/gcc/arm-none-eabi/14.2.1/plugin/include/options.h" 1





# 1 "/tool/lib/gcc/arm-none-eabi/14.2.1/plugin/include/flag-types.h" 1
# 7 "/tool/lib/gcc/arm-none-eabi/14.2.1/plugin/include/options.h" 2

# 1 "/tool/lib/gcc/arm-none-eabi/14.2.1/plugin/include/config/arm/aarch-common.h" 1
# 29 "/tool/lib/gcc/arm-none-eabi/14.2.1/plugin/include/config/arm/aarch-common.h"
enum aarch_parse_opt_result
{
  AARCH_PARSE_OK,
  AARCH_PARSE_MISSING_ARG,
  AARCH_PARSE_INVALID_FEATURE,
  AARCH_PARSE_INVALID_ARG,
  AARCH_PARSE_DUPLICATE_FEATURE
};


enum aarch_function_type {

  AARCH_FUNCTION_NONE,

  AARCH_FUNCTION_NON_LEAF,

  AARCH_FUNCTION_ALL
};
# 9 "/tool/lib/gcc/arm-none-eabi/14.2.1/plugin/include/options.h" 2
# 1 "/tool/lib/gcc/arm-none-eabi/14.2.1/plugin/include/config/arm/arm-opts.h" 1
# 28 "/tool/lib/gcc/arm-none-eabi/14.2.1/plugin/include/config/arm/arm-opts.h"
# 1 "/tool/lib/gcc/arm-none-eabi/14.2.1/plugin/include/config/arm/arm-flags.h" 1
# 29 "/tool/lib/gcc/arm-none-eabi/14.2.1/plugin/include/config/arm/arm-opts.h" 2
# 1 "/tool/lib/gcc/arm-none-eabi/14.2.1/plugin/include/arm-isa.h" 1
# 23 "/tool/lib/gcc/arm-none-eabi/14.2.1/plugin/include/arm-isa.h"
enum isa_feature {
  isa_nobit = 0,
  isa_bit_quirk_vlldm,
  isa_bit_fp16fml,
  isa_bit_mve,
  isa_bit_cmse,
  isa_bit_quirk_armv6kz,
  isa_bit_dotprod,
  isa_bit_crc32,
  isa_bit_xscale,
  isa_bit_pacbti,
  isa_bit_vfpv2,
  isa_bit_vfpv3,
  isa_bit_vfpv4,
  isa_bit_lpae,
  isa_bit_armv7em,
  isa_bit_fp16,
  isa_bit_adiv,
  isa_bit_fp_d32,
  isa_bit_be8,
  isa_bit_fp16conv,
  isa_bit_thumb2,
  isa_bit_crypto,
  isa_bit_mp,
  isa_bit_sec,
  isa_bit_sb,
  isa_bit_bf16,
  isa_bit_predres,
  isa_bit_armv4,
  isa_bit_quirk_cm3_ldrd,
  isa_bit_smallmul,
  isa_bit_armv5t,
  isa_bit_armv8_1m_main,
  isa_bit_armv6,
  isa_bit_thumb,
  isa_bit_quirk_no_asmcpu,
  isa_bit_armv7,
  isa_bit_armv8,
  isa_bit_armv9,
  isa_bit_i8mm,
  isa_bit_fp_dbl,
  isa_bit_armv5te,
  isa_bit_fpv5,
  isa_bit_iwmmxt2,
  isa_bit_quirk_aes_1742098,
  isa_bit_notm,
  isa_bit_cdecp0,
  isa_bit_cdecp1,
  isa_bit_cdecp2,
  isa_bit_cdecp3,
  isa_bit_iwmmxt,
  isa_bit_cdecp4,
  isa_bit_cdecp5,
  isa_bit_cdecp6,
  isa_bit_cdecp7,
  isa_bit_mve_float,
  isa_bit_armv8_1,
  isa_bit_armv8_2,
  isa_bit_armv8_3,
  isa_bit_tdiv,
  isa_bit_armv8_4,
  isa_bit_armv8_5,
  isa_bit_armv8_6,
  isa_bit_neon,
  isa_bit_quirk_no_volatile_ce,
  isa_bit_armv6k,
  isa_bit_vfp_base,
  isa_num_bits
};
# 652 "/tool/lib/gcc/arm-none-eabi/14.2.1/plugin/include/arm-isa.h"
struct fbit_implication {




  enum isa_feature ante;
  enum isa_feature cons;
};

static const struct fbit_implication all_implied_fbits[] =
{
  { isa_bit_neon, isa_bit_vfp_base },
  { isa_bit_vfpv4, isa_bit_vfp_base },
  { isa_bit_fp_d32, isa_bit_vfp_base },
  { isa_bit_fp_dbl, isa_bit_vfp_base },
  { isa_bit_mve_float, isa_bit_vfp_base },
  { isa_bit_mve, isa_bit_vfp_base },
  { isa_bit_dotprod, isa_bit_vfp_base },
  { isa_bit_crypto, isa_bit_vfp_base },
  { isa_bit_fp16, isa_bit_vfp_base },
  { isa_bit_armv7em, isa_bit_vfp_base },
  { isa_bit_i8mm, isa_bit_vfp_base },
  { isa_bit_fp16conv, isa_bit_vfp_base },
  { isa_bit_fpv5, isa_bit_vfp_base },
  { isa_bit_fp16fml, isa_bit_vfp_base },
  { isa_bit_bf16, isa_bit_vfp_base },
  { isa_bit_vfpv2, isa_bit_vfp_base },
  { isa_bit_vfpv3, isa_bit_vfp_base },
  { isa_nobit, isa_nobit }
};
# 30 "/tool/lib/gcc/arm-none-eabi/14.2.1/plugin/include/config/arm/arm-opts.h" 2
# 1 "/tool/lib/gcc/arm-none-eabi/14.2.1/plugin/include/arm-cpu.h" 1
# 23 "/tool/lib/gcc/arm-none-eabi/14.2.1/plugin/include/arm-cpu.h"
enum processor_type
{
  TARGET_CPU_arm8,
  TARGET_CPU_arm810,
  TARGET_CPU_strongarm,
  TARGET_CPU_fa526,
  TARGET_CPU_fa626,
  TARGET_CPU_arm7tdmi,
  TARGET_CPU_arm710t,
  TARGET_CPU_arm9,
  TARGET_CPU_arm9tdmi,
  TARGET_CPU_arm920t,
  TARGET_CPU_arm10tdmi,
  TARGET_CPU_arm9e,
  TARGET_CPU_arm10e,
  TARGET_CPU_xscale,
  TARGET_CPU_iwmmxt,
  TARGET_CPU_iwmmxt2,
  TARGET_CPU_fa606te,
  TARGET_CPU_fa626te,
  TARGET_CPU_fmp626,
  TARGET_CPU_fa726te,
  TARGET_CPU_arm926ejs,
  TARGET_CPU_arm1026ejs,
  TARGET_CPU_arm1136js,
  TARGET_CPU_arm1136jfs,
  TARGET_CPU_arm1176jzs,
  TARGET_CPU_arm1176jzfs,
  TARGET_CPU_mpcorenovfp,
  TARGET_CPU_mpcore,
  TARGET_CPU_arm1156t2s,
  TARGET_CPU_arm1156t2fs,
  TARGET_CPU_cortexm1,
  TARGET_CPU_cortexm0,
  TARGET_CPU_cortexm0plus,
  TARGET_CPU_cortexm1smallmultiply,
  TARGET_CPU_cortexm0smallmultiply,
  TARGET_CPU_cortexm0plussmallmultiply,
  TARGET_CPU_genericv7a,
  TARGET_CPU_cortexa5,
  TARGET_CPU_cortexa7,
  TARGET_CPU_cortexa8,
  TARGET_CPU_cortexa9,
  TARGET_CPU_cortexa12,
  TARGET_CPU_cortexa15,
  TARGET_CPU_cortexa17,
  TARGET_CPU_cortexr4,
  TARGET_CPU_cortexr4f,
  TARGET_CPU_cortexr5,
  TARGET_CPU_cortexr7,
  TARGET_CPU_cortexr8,
  TARGET_CPU_cortexm7,
  TARGET_CPU_cortexm4,
  TARGET_CPU_cortexm3,
  TARGET_CPU_marvell_pj4,
  TARGET_CPU_cortexa15cortexa7,
  TARGET_CPU_cortexa17cortexa7,
  TARGET_CPU_cortexa32,
  TARGET_CPU_cortexa35,
  TARGET_CPU_cortexa53,
  TARGET_CPU_cortexa57,
  TARGET_CPU_cortexa72,
  TARGET_CPU_cortexa73,
  TARGET_CPU_exynosm1,
  TARGET_CPU_xgene1,
  TARGET_CPU_cortexa57cortexa53,
  TARGET_CPU_cortexa72cortexa53,
  TARGET_CPU_cortexa73cortexa35,
  TARGET_CPU_cortexa73cortexa53,
  TARGET_CPU_cortexa55,
  TARGET_CPU_cortexa75,
  TARGET_CPU_cortexa76,
  TARGET_CPU_cortexa76ae,
  TARGET_CPU_cortexa77,
  TARGET_CPU_cortexa78,
  TARGET_CPU_cortexa78ae,
  TARGET_CPU_cortexa78c,
  TARGET_CPU_cortexa710,
  TARGET_CPU_cortexx1,
  TARGET_CPU_cortexx1c,
  TARGET_CPU_neoversen1,
  TARGET_CPU_cortexa75cortexa55,
  TARGET_CPU_cortexa76cortexa55,
  TARGET_CPU_neoversev1,
  TARGET_CPU_neoversen2,
  TARGET_CPU_cortexm23,
  TARGET_CPU_cortexm33,
  TARGET_CPU_cortexm35p,
  TARGET_CPU_cortexm52,
  TARGET_CPU_cortexm55,
  TARGET_CPU_starmc1,
  TARGET_CPU_cortexm85,
  TARGET_CPU_cortexr52,
  TARGET_CPU_cortexr52plus,
  TARGET_CPU_arm_none
};

enum arch_type
{
  TARGET_ARCH_armv4,
  TARGET_ARCH_armv4t,
  TARGET_ARCH_armv5t,
  TARGET_ARCH_armv5te,
  TARGET_ARCH_armv5tej,
  TARGET_ARCH_armv6,
  TARGET_ARCH_armv6j,
  TARGET_ARCH_armv6k,
  TARGET_ARCH_armv6z,
  TARGET_ARCH_armv6kz,
  TARGET_ARCH_armv6zk,
  TARGET_ARCH_armv6t2,
  TARGET_ARCH_armv6_m,
  TARGET_ARCH_armv6s_m,
  TARGET_ARCH_armv7,
  TARGET_ARCH_armv7_a,
  TARGET_ARCH_armv7ve,
  TARGET_ARCH_armv7_r,
  TARGET_ARCH_armv7_m,
  TARGET_ARCH_armv7e_m,
  TARGET_ARCH_armv8_a,
  TARGET_ARCH_armv8_1_a,
  TARGET_ARCH_armv8_2_a,
  TARGET_ARCH_armv8_3_a,
  TARGET_ARCH_armv8_4_a,
  TARGET_ARCH_armv8_5_a,
  TARGET_ARCH_armv8_6_a,
  TARGET_ARCH_armv8_m_base,
  TARGET_ARCH_armv8_m_main,
  TARGET_ARCH_armv8_r,
  TARGET_ARCH_armv8_1_m_main,
  TARGET_ARCH_armv9_a,
  TARGET_ARCH_iwmmxt,
  TARGET_ARCH_iwmmxt2,
  TARGET_ARCH_arm_none
};

enum fpu_type
{
  TARGET_FPU_vfp,
  TARGET_FPU_vfpv2,
  TARGET_FPU_vfpv3,
  TARGET_FPU_vfpv3_fp16,
  TARGET_FPU_vfpv3_d16,
  TARGET_FPU_vfpv3_d16_fp16,
  TARGET_FPU_vfpv3xd,
  TARGET_FPU_vfpv3xd_fp16,
  TARGET_FPU_neon,
  TARGET_FPU_neon_vfpv3,
  TARGET_FPU_neon_fp16,
  TARGET_FPU_vfpv4,
  TARGET_FPU_neon_vfpv4,
  TARGET_FPU_vfpv4_d16,
  TARGET_FPU_fpv4_sp_d16,
  TARGET_FPU_fpv5_sp_d16,
  TARGET_FPU_fpv5_d16,
  TARGET_FPU_fp_armv8,
  TARGET_FPU_neon_fp_armv8,
  TARGET_FPU_crypto_neon_fp_armv8,
  TARGET_FPU_vfp3,
  TARGET_FPU_auto
};
# 31 "/tool/lib/gcc/arm-none-eabi/14.2.1/plugin/include/config/arm/arm-opts.h" 2





enum arm_fp16_format_type
{
  ARM_FP16_FORMAT_NONE = 0,
  ARM_FP16_FORMAT_IEEE = 1,
  ARM_FP16_FORMAT_ALTERNATIVE = 2
};


enum arm_abi_type
{
  ARM_ABI_APCS,
  ARM_ABI_ATPCS,
  ARM_ABI_AAPCS,
  ARM_ABI_IWMMXT,
  ARM_ABI_AAPCS_LINUX
};

enum float_abi_type
{
  ARM_FLOAT_ABI_SOFT,
  ARM_FLOAT_ABI_SOFTFP,
  ARM_FLOAT_ABI_HARD
};


enum arm_tp_type {
  TP_AUTO,
  TP_SOFT,
  TP_TPIDRURW,
  TP_TPIDRURO,
  TP_TPIDRPRW
};


enum arm_tls_type {
  TLS_GNU,
  TLS_GNU2
};


enum stack_protector_guard {
  SSP_TLSREG,
  SSP_GLOBAL
};
# 10 "/tool/lib/gcc/arm-none-eabi/14.2.1/plugin/include/options.h" 2
# 9497 "/tool/lib/gcc/arm-none-eabi/14.2.1/plugin/include/options.h"
enum opt_code
{
  OPT____ = 0,
# 9508 "/tool/lib/gcc/arm-none-eabi/14.2.1/plugin/include/options.h"
  OPT__completion_ = 9,
# 9528 "/tool/lib/gcc/arm-none-eabi/14.2.1/plugin/include/options.h"
  OPT__help = 29,
  OPT__help_ = 30,
# 9556 "/tool/lib/gcc/arm-none-eabi/14.2.1/plugin/include/options.h"
  OPT__no_sysroot_suffix = 57,



  OPT__output_pch = 61,

  OPT__param_align_loop_iterations_ = 63,
  OPT__param_align_threshold_ = 64,
  OPT__param_analyzer_bb_explosion_factor_ = 65,
  OPT__param_analyzer_max_constraints_ = 66,
  OPT__param_analyzer_max_enodes_for_full_dump_ = 67,
  OPT__param_analyzer_max_enodes_per_program_point_ = 68,
  OPT__param_analyzer_max_infeasible_edges_ = 69,
  OPT__param_analyzer_max_recursion_depth_ = 70,
  OPT__param_analyzer_max_svalue_depth_ = 71,
  OPT__param_analyzer_min_snodes_for_call_summary_ = 72,
  OPT__param_analyzer_text_art_ideal_canvas_width_ = 73,
  OPT__param_analyzer_text_art_string_ellipsis_head_len_ = 74,
  OPT__param_analyzer_text_art_string_ellipsis_tail_len_ = 75,
  OPT__param_analyzer_text_art_string_ellipsis_threshold_ = 76,
  OPT__param_asan_globals_ = 77,
  OPT__param_asan_instrument_allocas_ = 78,
  OPT__param_asan_instrument_reads_ = 79,
  OPT__param_asan_instrument_writes_ = 80,
  OPT__param_asan_instrumentation_with_call_threshold_ = 81,
  OPT__param_asan_kernel_mem_intrinsic_prefix_ = 82,
  OPT__param_asan_memintrin_ = 83,
  OPT__param_asan_stack_ = 84,
  OPT__param_asan_use_after_return_ = 85,
  OPT__param_avg_loop_niter_ = 86,
  OPT__param_avoid_fma_max_bits_ = 87,
  OPT__param_builtin_expect_probability_ = 88,
  OPT__param_builtin_string_cmp_inline_length_ = 89,
  OPT__param_case_values_threshold_ = 90,
  OPT__param_comdat_sharing_probability_ = 91,
  OPT__param_constructive_interference_size_ = 92,
  OPT__param_cxx_max_namespaces_for_diagnostic_help_ = 93,
  OPT__param_destructive_interference_size_ = 94,
  OPT__param_dse_max_alias_queries_per_store_ = 95,
  OPT__param_dse_max_object_size_ = 96,
  OPT__param_early_inlining_insns_ = 97,
  OPT__param_fsm_scale_path_stmts_ = 98,
  OPT__param_fully_pipelined_fma_ = 99,
  OPT__param_gcse_after_reload_critical_fraction_ = 100,
  OPT__param_gcse_after_reload_partial_fraction_ = 101,
  OPT__param_gcse_cost_distance_ratio_ = 102,
  OPT__param_gcse_unrestricted_cost_ = 103,
  OPT__param_ggc_min_expand_ = 104,
  OPT__param_ggc_min_heapsize_ = 105,
  OPT__param_gimple_fe_computed_hot_bb_threshold_ = 106,
  OPT__param_graphite_allow_codegen_errors_ = 107,
  OPT__param_graphite_max_arrays_per_scop_ = 108,
  OPT__param_graphite_max_nb_scop_params_ = 109,
  OPT__param_hardcfr_max_blocks_ = 110,
  OPT__param_hardcfr_max_inline_blocks_ = 111,
  OPT__param_hash_table_verification_limit_ = 112,
  OPT__param_hot_bb_count_fraction_ = 113,
  OPT__param_hot_bb_count_ws_permille_ = 114,
  OPT__param_hot_bb_frequency_fraction_ = 115,
  OPT__param_hwasan_instrument_allocas_ = 116,
  OPT__param_hwasan_instrument_mem_intrinsics_ = 117,
  OPT__param_hwasan_instrument_reads_ = 118,
  OPT__param_hwasan_instrument_stack_ = 119,
  OPT__param_hwasan_instrument_writes_ = 120,
  OPT__param_hwasan_random_frame_tag_ = 121,
  OPT__param_inline_heuristics_hint_percent_ = 122,
  OPT__param_inline_min_speedup_ = 123,
  OPT__param_inline_unit_growth_ = 124,
  OPT__param_integer_share_limit_ = 125,
  OPT__param_ipa_cp_eval_threshold_ = 126,
  OPT__param_ipa_cp_large_unit_insns_ = 127,
  OPT__param_ipa_cp_loop_hint_bonus_ = 128,
  OPT__param_ipa_cp_max_recursive_depth_ = 129,
  OPT__param_ipa_cp_min_recursive_probability_ = 130,
  OPT__param_ipa_cp_profile_count_base_ = 131,
  OPT__param_ipa_cp_recursion_penalty_ = 132,
  OPT__param_ipa_cp_recursive_freq_factor_ = 133,
  OPT__param_ipa_cp_single_call_penalty_ = 134,
  OPT__param_ipa_cp_unit_growth_ = 135,
  OPT__param_ipa_cp_value_list_size_ = 136,
  OPT__param_ipa_jump_function_lookups_ = 137,
  OPT__param_ipa_max_aa_steps_ = 138,
  OPT__param_ipa_max_agg_items_ = 139,
  OPT__param_ipa_max_loop_predicates_ = 140,
  OPT__param_ipa_max_param_expr_ops_ = 141,
  OPT__param_ipa_max_switch_predicate_bounds_ = 142,
  OPT__param_ipa_sra_deref_prob_threshold_ = 143,
  OPT__param_ipa_sra_max_replacements_ = 144,
  OPT__param_ipa_sra_ptr_growth_factor_ = 145,
  OPT__param_ipa_sra_ptrwrap_growth_factor_ = 146,
  OPT__param_ira_consider_dup_in_all_alts_ = 147,
  OPT__param_ira_loop_reserved_regs_ = 148,
  OPT__param_ira_max_conflict_table_size_ = 149,
  OPT__param_ira_max_loops_num_ = 150,
  OPT__param_ira_simple_lra_insn_threshold_ = 151,
  OPT__param_iv_always_prune_cand_set_bound_ = 152,
  OPT__param_iv_consider_all_candidates_bound_ = 153,
  OPT__param_iv_max_considered_uses_ = 154,
  OPT__param_jump_table_max_growth_ratio_for_size_ = 155,
  OPT__param_jump_table_max_growth_ratio_for_speed_ = 156,
  OPT__param_l1_cache_line_size_ = 157,
  OPT__param_l1_cache_size_ = 158,
  OPT__param_l2_cache_size_ = 159,
  OPT__param_large_function_growth_ = 160,
  OPT__param_large_function_insns_ = 161,
  OPT__param_large_stack_frame_growth_ = 162,
  OPT__param_large_stack_frame_ = 163,
  OPT__param_large_unit_insns_ = 164,
  OPT__param_lazy_modules_ = 165,
  OPT__param_lim_expensive_ = 166,
  OPT__param_logical_op_non_short_circuit_ = 167,
  OPT__param_loop_block_tile_size_ = 168,
  OPT__param_loop_interchange_max_num_stmts_ = 169,
  OPT__param_loop_interchange_stride_ratio_ = 170,
  OPT__param_loop_invariant_max_bbs_in_loop_ = 171,
  OPT__param_loop_max_datarefs_for_datadeps_ = 172,
  OPT__param_loop_versioning_max_inner_insns_ = 173,
  OPT__param_loop_versioning_max_outer_insns_ = 174,
  OPT__param_lra_inheritance_ebb_probability_cutoff_ = 175,
  OPT__param_lra_max_considered_reload_pseudos_ = 176,
  OPT__param_lto_max_partition_ = 177,
  OPT__param_lto_max_streaming_parallelism_ = 178,
  OPT__param_lto_min_partition_ = 179,
  OPT__param_lto_partitions_ = 180,
  OPT__param_max_average_unrolled_insns_ = 181,
  OPT__param_max_combine_insns_ = 182,
  OPT__param_max_completely_peel_loop_nest_depth_ = 183,
  OPT__param_max_completely_peel_times_ = 184,
  OPT__param_max_completely_peeled_insns_ = 185,
  OPT__param_max_crossjump_edges_ = 186,
  OPT__param_max_cse_insns_ = 187,
  OPT__param_max_cse_path_length_ = 188,
  OPT__param_max_cselib_memory_locations_ = 189,
  OPT__param_max_debug_marker_count_ = 190,
  OPT__param_max_delay_slot_insn_search_ = 191,
  OPT__param_max_delay_slot_live_search_ = 192,
  OPT__param_max_dse_active_local_stores_ = 193,
  OPT__param_max_early_inliner_iterations_ = 194,
  OPT__param_max_fields_for_field_sensitive_ = 195,
  OPT__param_max_find_base_term_values_ = 196,
  OPT__param_max_fsm_thread_path_insns_ = 197,
  OPT__param_max_gcse_insertion_ratio_ = 198,
  OPT__param_max_gcse_memory_ = 199,
  OPT__param_max_goto_duplication_insns_ = 200,
  OPT__param_max_grow_copy_bb_insns_ = 201,
  OPT__param_max_hoist_depth_ = 202,
  OPT__param_max_inline_functions_called_once_insns_ = 203,
  OPT__param_max_inline_functions_called_once_loop_depth_ = 204,
  OPT__param_max_inline_insns_auto_ = 205,
  OPT__param_max_inline_insns_recursive_auto_ = 206,
  OPT__param_max_inline_insns_recursive_ = 207,
  OPT__param_max_inline_insns_single_ = 208,
  OPT__param_max_inline_insns_size_ = 209,
  OPT__param_max_inline_insns_small_ = 210,
  OPT__param_max_inline_recursive_depth_auto_ = 211,
  OPT__param_max_inline_recursive_depth_ = 212,
  OPT__param_max_isl_operations_ = 213,
  OPT__param_max_iterations_computation_cost_ = 214,
  OPT__param_max_iterations_to_track_ = 215,
  OPT__param_max_jump_thread_duplication_stmts_ = 216,
  OPT__param_max_jump_thread_paths_ = 217,
  OPT__param_max_last_value_rtl_ = 218,
  OPT__param_max_loop_header_insns_ = 219,
  OPT__param_max_modulo_backtrack_attempts_ = 220,
  OPT__param_max_partial_antic_length_ = 221,
  OPT__param_max_peel_branches_ = 222,
  OPT__param_max_peel_times_ = 223,
  OPT__param_max_peeled_insns_ = 224,
  OPT__param_max_pending_list_length_ = 225,
  OPT__param_max_pipeline_region_blocks_ = 226,
  OPT__param_max_pipeline_region_insns_ = 227,
  OPT__param_max_pow_sqrt_depth_ = 228,
  OPT__param_max_predicted_iterations_ = 229,
  OPT__param_max_reload_search_insns_ = 230,
  OPT__param_max_rtl_if_conversion_insns_ = 231,
  OPT__param_max_rtl_if_conversion_predictable_cost_ = 232,
  OPT__param_max_rtl_if_conversion_unpredictable_cost_ = 233,
  OPT__param_max_sched_extend_regions_iters_ = 234,
  OPT__param_max_sched_insn_conflict_delay_ = 235,
  OPT__param_max_sched_ready_insns_ = 236,
  OPT__param_max_sched_region_blocks_ = 237,
  OPT__param_max_sched_region_insns_ = 238,
  OPT__param_max_slsr_cand_scan_ = 239,
  OPT__param_max_speculative_devirt_maydefs_ = 240,
  OPT__param_max_ssa_name_query_depth_ = 241,
  OPT__param_max_store_chains_to_track_ = 242,
  OPT__param_max_stores_to_merge_ = 243,
  OPT__param_max_stores_to_sink_ = 244,
  OPT__param_max_stores_to_track_ = 245,
  OPT__param_max_tail_merge_comparisons_ = 246,
  OPT__param_max_tail_merge_iterations_ = 247,
  OPT__param_max_tracked_strlens_ = 248,
  OPT__param_max_tree_if_conversion_phi_args_ = 249,
  OPT__param_max_unroll_times_ = 250,
  OPT__param_max_unrolled_insns_ = 251,
  OPT__param_max_unswitch_depth_ = 252,
  OPT__param_max_unswitch_insns_ = 253,
  OPT__param_max_variable_expansions_in_unroller_ = 254,
  OPT__param_max_vartrack_expr_depth_ = 255,
  OPT__param_max_vartrack_reverse_op_size_ = 256,
  OPT__param_max_vartrack_size_ = 257,
  OPT__param_min_crossjump_insns_ = 258,
  OPT__param_min_inline_recursive_probability_ = 259,
  OPT__param_min_insn_to_prefetch_ratio_ = 260,
  OPT__param_min_loop_cond_split_prob_ = 261,
  OPT__param_min_nondebug_insn_uid_ = 262,
  OPT__param_min_pagesize_ = 263,
  OPT__param_min_size_for_stack_sharing_ = 264,
  OPT__param_min_spec_prob_ = 265,
  OPT__param_min_vect_loop_bound_ = 266,
  OPT__param_modref_max_accesses_ = 267,
  OPT__param_modref_max_adjustments_ = 268,
  OPT__param_modref_max_bases_ = 269,
  OPT__param_modref_max_depth_ = 270,
  OPT__param_modref_max_escape_points_ = 271,
  OPT__param_modref_max_refs_ = 272,
  OPT__param_modref_max_tests_ = 273,
  OPT__param_openacc_kernels_ = 274,
  OPT__param_openacc_privatization_ = 275,
  OPT__param_parloops_chunk_size_ = 276,
  OPT__param_parloops_min_per_thread_ = 277,
  OPT__param_parloops_schedule_ = 278,
  OPT__param_partial_inlining_entry_probability_ = 279,
  OPT__param_predictable_branch_outcome_ = 280,
  OPT__param_prefetch_dynamic_strides_ = 281,
  OPT__param_prefetch_latency_ = 282,
  OPT__param_prefetch_min_insn_to_mem_ratio_ = 283,
  OPT__param_prefetch_minimum_stride_ = 284,
  OPT__param_profile_func_internal_id_ = 285,
  OPT__param_ranger_debug_ = 286,
  OPT__param_ranger_logical_depth_ = 287,
  OPT__param_ranger_recompute_depth_ = 288,
  OPT__param_relation_block_limit_ = 289,
  OPT__param_rpo_vn_max_loop_depth_ = 290,
  OPT__param_sccvn_max_alias_queries_per_access_ = 291,
  OPT__param_scev_max_expr_complexity_ = 292,
  OPT__param_scev_max_expr_size_ = 293,
  OPT__param_sched_autopref_queue_depth_ = 294,
  OPT__param_sched_mem_true_dep_cost_ = 295,
  OPT__param_sched_pressure_algorithm_ = 296,
  OPT__param_sched_spec_prob_cutoff_ = 297,
  OPT__param_sched_state_edge_prob_cutoff_ = 298,
  OPT__param_selsched_insns_to_rename_ = 299,
  OPT__param_selsched_max_lookahead_ = 300,
  OPT__param_selsched_max_sched_times_ = 301,
  OPT__param_simultaneous_prefetches_ = 302,
  OPT__param_sink_frequency_threshold_ = 303,
  OPT__param_sms_dfa_history_ = 304,
  OPT__param_sms_loop_average_count_threshold_ = 305,
  OPT__param_sms_max_ii_factor_ = 306,
  OPT__param_sms_min_sc_ = 307,
  OPT__param_sra_max_propagations_ = 308,
  OPT__param_sra_max_scalarization_size_Osize_ = 309,
  OPT__param_sra_max_scalarization_size_Ospeed_ = 310,
  OPT__param_ssa_name_def_chain_limit_ = 311,
  OPT__param_ssp_buffer_size_ = 312,
  OPT__param_stack_clash_protection_guard_size_ = 313,
  OPT__param_stack_clash_protection_probe_interval_ = 314,
  OPT__param_store_merging_allow_unaligned_ = 315,
  OPT__param_store_merging_max_size_ = 316,
  OPT__param_switch_conversion_max_branch_ratio_ = 317,
  OPT__param_threader_debug_ = 318,
  OPT__param_tm_max_aggregate_size_ = 319,
  OPT__param_tracer_dynamic_coverage_feedback_ = 320,
  OPT__param_tracer_dynamic_coverage_ = 321,
  OPT__param_tracer_max_code_growth_ = 322,
  OPT__param_tracer_min_branch_probability_feedback_ = 323,
  OPT__param_tracer_min_branch_probability_ = 324,
  OPT__param_tracer_min_branch_ratio_ = 325,
  OPT__param_tree_reassoc_width_ = 326,
  OPT__param_tsan_distinguish_volatile_ = 327,
  OPT__param_tsan_instrument_func_entry_exit_ = 328,
  OPT__param_uninit_control_dep_attempts_ = 329,
  OPT__param_uninit_max_chain_len_ = 330,
  OPT__param_uninit_max_num_chains_ = 331,
  OPT__param_uninlined_function_insns_ = 332,
  OPT__param_uninlined_function_time_ = 333,
  OPT__param_uninlined_thunk_insns_ = 334,
  OPT__param_uninlined_thunk_time_ = 335,
  OPT__param_unlikely_bb_count_fraction_ = 336,
  OPT__param_unroll_jam_max_unroll_ = 337,
  OPT__param_unroll_jam_min_percent_ = 338,
  OPT__param_use_after_scope_direct_emission_threshold_ = 339,
  OPT__param_use_canonical_types_ = 340,
  OPT__param_vect_epilogues_nomask_ = 341,
  OPT__param_vect_induction_float_ = 342,
  OPT__param_vect_inner_loop_cost_factor_ = 343,
  OPT__param_vect_max_layout_candidates_ = 344,
  OPT__param_vect_max_peeling_for_alignment_ = 345,
  OPT__param_vect_max_version_for_alias_checks_ = 346,
  OPT__param_vect_max_version_for_alignment_checks_ = 347,
  OPT__param_vect_partial_vector_usage_ = 348,
  OPT__param_vrp_sparse_threshold_ = 349,
  OPT__param_vrp_switch_limit_ = 350,
  OPT__param_vrp_vector_threshold_ = 351,
# 9881 "/tool/lib/gcc/arm-none-eabi/14.2.1/plugin/include/options.h"
  OPT__sysroot_ = 382,
  OPT__target_help = 383,
# 9892 "/tool/lib/gcc/arm-none-eabi/14.2.1/plugin/include/options.h"
  OPT__version = 393,


  OPT_A = 396,
  OPT_B = 397,
  OPT_C = 398,
  OPT_CC = 399,
  OPT_D = 400,
  OPT_E = 401,
  OPT_F = 402,
  OPT_H = 403,
  OPT_Hd = 404,
  OPT_Hf = 405,
  OPT_I = 406,
  OPT_J = 407,
  OPT_L = 408,
  OPT_M = 409,
  OPT_MD = 410,
  OPT_MF = 411,
  OPT_MG = 412,
  OPT_MM = 413,
  OPT_MMD = 414,
  OPT_MP = 415,
  OPT_MQ = 416,
  OPT_MT = 417,
  OPT_Mmodules = 418,
  OPT_Mno_modules = 419,
  OPT_N = 420,
  OPT_O = 421,
  OPT_Ofast = 422,
  OPT_Og = 423,
  OPT_Os = 424,
  OPT_Oz = 425,
  OPT_P = 426,
  OPT_Q = 427,
  OPT_Qn = 428,
  OPT_Qy = 429,
  OPT_R = 430,
  OPT_S = 431,
  OPT_T = 432,
  OPT_Tbss = 433,
  OPT_Tbss_ = 434,
  OPT_Tdata = 435,
  OPT_Tdata_ = 436,
  OPT_Ttext = 437,
  OPT_Ttext_ = 438,
  OPT_U = 439,

  OPT_WNSObject_attribute = 441,
  OPT_Wa_ = 442,
  OPT_Wabi = 443,
  OPT_Wabi_tag = 444,
  OPT_Wabi_ = 445,
  OPT_Wabsolute_value = 446,
  OPT_Waddress = 447,
  OPT_Waddress_of_packed_member = 448,
  OPT_Waggregate_return = 449,
  OPT_Waggressive_loop_optimizations = 450,
  OPT_Waliasing = 451,
  OPT_Walign_commons = 452,

  OPT_Waligned_new_ = 454,
  OPT_Wall = 455,
  OPT_Walloc_size = 456,
  OPT_Walloc_size_larger_than_ = 457,
  OPT_Walloc_zero = 458,
  OPT_Walloca = 459,
  OPT_Walloca_larger_than_ = 460,
  OPT_Wampersand = 461,
  OPT_Wanalyzer_allocation_size = 462,
  OPT_Wanalyzer_deref_before_check = 463,
  OPT_Wanalyzer_double_fclose = 464,
  OPT_Wanalyzer_double_free = 465,
  OPT_Wanalyzer_exposure_through_output_file = 466,
  OPT_Wanalyzer_exposure_through_uninit_copy = 467,
  OPT_Wanalyzer_fd_access_mode_mismatch = 468,
  OPT_Wanalyzer_fd_double_close = 469,
  OPT_Wanalyzer_fd_leak = 470,
  OPT_Wanalyzer_fd_phase_mismatch = 471,
  OPT_Wanalyzer_fd_type_mismatch = 472,
  OPT_Wanalyzer_fd_use_after_close = 473,
  OPT_Wanalyzer_fd_use_without_check = 474,
  OPT_Wanalyzer_file_leak = 475,
  OPT_Wanalyzer_free_of_non_heap = 476,
  OPT_Wanalyzer_imprecise_fp_arithmetic = 477,
  OPT_Wanalyzer_infinite_loop = 478,
  OPT_Wanalyzer_infinite_recursion = 479,
  OPT_Wanalyzer_jump_through_null = 480,
  OPT_Wanalyzer_malloc_leak = 481,
  OPT_Wanalyzer_mismatching_deallocation = 482,
  OPT_Wanalyzer_null_argument = 483,
  OPT_Wanalyzer_null_dereference = 484,
  OPT_Wanalyzer_out_of_bounds = 485,
  OPT_Wanalyzer_overlapping_buffers = 486,
  OPT_Wanalyzer_possible_null_argument = 487,
  OPT_Wanalyzer_possible_null_dereference = 488,
  OPT_Wanalyzer_putenv_of_auto_var = 489,
  OPT_Wanalyzer_shift_count_negative = 490,
  OPT_Wanalyzer_shift_count_overflow = 491,
  OPT_Wanalyzer_stale_setjmp_buffer = 492,
  OPT_Wanalyzer_symbol_too_complex = 493,
  OPT_Wanalyzer_tainted_allocation_size = 494,
  OPT_Wanalyzer_tainted_array_index = 495,
  OPT_Wanalyzer_tainted_assertion = 496,
  OPT_Wanalyzer_tainted_divisor = 497,
  OPT_Wanalyzer_tainted_offset = 498,
  OPT_Wanalyzer_tainted_size = 499,
  OPT_Wanalyzer_too_complex = 500,
  OPT_Wanalyzer_undefined_behavior_strtok = 501,
  OPT_Wanalyzer_unsafe_call_within_signal_handler = 502,
  OPT_Wanalyzer_use_after_free = 503,
  OPT_Wanalyzer_use_of_pointer_in_stale_stack_frame = 504,
  OPT_Wanalyzer_use_of_uninitialized_value = 505,
  OPT_Wanalyzer_va_arg_type_mismatch = 506,
  OPT_Wanalyzer_va_list_exhausted = 507,
  OPT_Wanalyzer_va_list_leak = 508,
  OPT_Wanalyzer_va_list_use_after_va_end = 509,
  OPT_Wanalyzer_write_to_const = 510,
  OPT_Wanalyzer_write_to_string_literal = 511,
  OPT_Wargument_mismatch = 512,
  OPT_Warith_conversion = 513,

  OPT_Warray_bounds_ = 515,
  OPT_Warray_compare = 516,

  OPT_Warray_parameter_ = 518,
  OPT_Warray_temporaries = 519,
  OPT_Wassign_intercept = 520,

  OPT_Wattribute_alias_ = 522,
  OPT_Wattribute_warning = 523,
  OPT_Wattributes = 524,
  OPT_Wattributes_ = 525,
  OPT_Wbad_function_cast = 526,

  OPT_Wbidi_chars_ = 528,
  OPT_Wbool_compare = 529,
  OPT_Wbool_operation = 530,
  OPT_Wbuiltin_declaration_mismatch = 531,
  OPT_Wbuiltin_macro_redefined = 532,
  OPT_Wc___compat = 533,

  OPT_Wc__11_compat = 535,
  OPT_Wc__11_extensions = 536,
  OPT_Wc__14_compat = 537,
  OPT_Wc__14_extensions = 538,
  OPT_Wc__17_compat = 539,
  OPT_Wc__17_extensions = 540,

  OPT_Wc__20_compat = 542,
  OPT_Wc__20_extensions = 543,
  OPT_Wc__23_extensions = 544,
  OPT_Wc__26_extensions = 545,

  OPT_Wc_binding_type = 547,
  OPT_Wc11_c23_compat = 548,

  OPT_Wc90_c99_compat = 550,
  OPT_Wc99_c11_compat = 551,
  OPT_Wcalloc_transposed_args = 552,
  OPT_Wcannot_profile = 553,
  OPT_Wcase_enum = 554,
  OPT_Wcast_align = 555,
  OPT_Wcast_align_strict = 556,
  OPT_Wcast_function_type = 557,
  OPT_Wcast_qual = 558,
  OPT_Wcast_result = 559,
  OPT_Wcast_user_defined = 560,

  OPT_Wcatch_value_ = 562,
  OPT_Wchanges_meaning = 563,
  OPT_Wchar_subscripts = 564,
  OPT_Wcharacter_truncation = 565,
  OPT_Wchkp = 566,
  OPT_Wclass_conversion = 567,
  OPT_Wclass_memaccess = 568,
  OPT_Wclobbered = 569,
  OPT_Wcomma_subscript = 570,
  OPT_Wcomment = 571,

  OPT_Wcompare_distinct_pointer_types = 573,
  OPT_Wcompare_reals = 574,
  OPT_Wcomplain_wrong_lang = 575,
  OPT_Wconditionally_supported = 576,
  OPT_Wconversion = 577,
  OPT_Wconversion_extra = 578,
  OPT_Wconversion_null = 579,
  OPT_Wcoverage_invalid_line_number = 580,
  OPT_Wcoverage_mismatch = 581,
  OPT_Wcoverage_too_many_conditions = 582,
  OPT_Wcpp = 583,
  OPT_Wctad_maybe_unsupported = 584,
  OPT_Wctor_dtor_privacy = 585,
  OPT_Wdangling_else = 586,

  OPT_Wdangling_pointer_ = 588,
  OPT_Wdangling_reference = 589,
  OPT_Wdate_time = 590,
  OPT_Wdeclaration_after_statement = 591,
  OPT_Wdeclaration_missing_parameter_type = 592,
  OPT_Wdelete_incomplete = 593,
  OPT_Wdelete_non_virtual_dtor = 594,
  OPT_Wdeprecated = 595,
  OPT_Wdeprecated_copy = 596,
  OPT_Wdeprecated_copy_dtor = 597,
  OPT_Wdeprecated_declarations = 598,
  OPT_Wdeprecated_enum_enum_conversion = 599,
  OPT_Wdeprecated_enum_float_conversion = 600,
  OPT_Wdesignated_init = 601,
  OPT_Wdisabled_optimization = 602,
  OPT_Wdiscarded_array_qualifiers = 603,
  OPT_Wdiscarded_qualifiers = 604,
  OPT_Wdiv_by_zero = 605,
  OPT_Wdo_subscript = 606,
  OPT_Wdouble_promotion = 607,
  OPT_Wduplicate_decl_specifier = 608,
  OPT_Wduplicated_branches = 609,
  OPT_Wduplicated_cond = 610,
  OPT_Weffc__ = 611,
  OPT_Welaborated_enum_base = 612,
  OPT_Wempty_body = 613,
  OPT_Wendif_labels = 614,
  OPT_Wenum_compare = 615,
  OPT_Wenum_conversion = 616,
  OPT_Wenum_int_mismatch = 617,
  OPT_Werror = 618,

  OPT_Werror_ = 620,
  OPT_Wexceptions = 621,
  OPT_Wexpansion_to_defined = 622,
  OPT_Wextra = 623,
  OPT_Wextra_semi = 624,
  OPT_Wfatal_errors = 625,
  OPT_Wflex_array_member_not_at_end = 626,
  OPT_Wfloat_conversion = 627,
  OPT_Wfloat_equal = 628,

  OPT_Wformat_contains_nul = 630,
  OPT_Wformat_diag = 631,
  OPT_Wformat_extra_args = 632,
  OPT_Wformat_nonliteral = 633,

  OPT_Wformat_overflow_ = 635,
  OPT_Wformat_security = 636,
  OPT_Wformat_signedness = 637,

  OPT_Wformat_truncation_ = 639,
  OPT_Wformat_y2k = 640,
  OPT_Wformat_zero_length = 641,
  OPT_Wformat_ = 642,
  OPT_Wframe_address = 643,
  OPT_Wframe_larger_than_ = 644,
  OPT_Wfree_nonheap_object = 645,
  OPT_Wfrontend_loop_interchange = 646,
  OPT_Wfunction_elimination = 647,
  OPT_Wglobal_module = 648,
  OPT_Whardened = 649,

  OPT_Wif_not_aligned = 651,
  OPT_Wignored_attributes = 652,
  OPT_Wignored_qualifiers = 653,
  OPT_Wimplicit = 654,

  OPT_Wimplicit_fallthrough_ = 656,
  OPT_Wimplicit_function_declaration = 657,
  OPT_Wimplicit_int = 658,
  OPT_Wimplicit_interface = 659,
  OPT_Wimplicit_procedure = 660,

  OPT_Winaccessible_base = 662,
  OPT_Wincompatible_pointer_types = 663,
  OPT_Winfinite_recursion = 664,
  OPT_Winherited_variadic_ctor = 665,
  OPT_Winit_list_lifetime = 666,
  OPT_Winit_self = 667,
  OPT_Winline = 668,
  OPT_Wint_conversion = 669,
  OPT_Wint_in_bool_context = 670,
  OPT_Wint_to_pointer_cast = 671,
  OPT_Winteger_division = 672,
  OPT_Winterference_size = 673,
  OPT_Wintrinsic_shadow = 674,
  OPT_Wintrinsics_std = 675,
  OPT_Winvalid_constexpr = 676,
  OPT_Winvalid_imported_macros = 677,
  OPT_Winvalid_memory_model = 678,
  OPT_Winvalid_offsetof = 679,
  OPT_Winvalid_pch = 680,
  OPT_Winvalid_utf8 = 681,
  OPT_Wjump_misses_init = 682,
  OPT_Wl_ = 683,

  OPT_Wlarger_than_ = 685,
  OPT_Wline_truncation = 686,
  OPT_Wliteral_suffix = 687,
  OPT_Wlogical_not_parentheses = 688,
  OPT_Wlogical_op = 689,
  OPT_Wlong_long = 690,
  OPT_Wlto_type_mismatch = 691,
  OPT_Wmain = 692,
  OPT_Wmaybe_uninitialized = 693,
  OPT_Wmemset_elt_size = 694,
  OPT_Wmemset_transposed_args = 695,
  OPT_Wmisleading_indentation = 696,
  OPT_Wmismatched_dealloc = 697,
  OPT_Wmismatched_new_delete = 698,
  OPT_Wmismatched_special_enum = 699,
  OPT_Wmismatched_tags = 700,
  OPT_Wmissing_attributes = 701,
  OPT_Wmissing_braces = 702,
  OPT_Wmissing_declarations = 703,
  OPT_Wmissing_field_initializers = 704,

  OPT_Wmissing_include_dirs = 706,

  OPT_Wmissing_parameter_type = 708,
  OPT_Wmissing_profile = 709,
  OPT_Wmissing_prototypes = 710,
  OPT_Wmissing_requires = 711,
  OPT_Wmissing_template_keyword = 712,
  OPT_Wmissing_variable_declarations = 713,
  OPT_Wmudflap = 714,
  OPT_Wmultichar = 715,
  OPT_Wmultiple_inheritance = 716,
  OPT_Wmultistatement_macros = 717,
  OPT_Wnamespaces = 718,
  OPT_Wnarrowing = 719,
  OPT_Wnested_externs = 720,






  OPT_Wnoexcept = 727,
  OPT_Wnoexcept_type = 728,
  OPT_Wnon_template_friend = 729,
  OPT_Wnon_virtual_dtor = 730,
  OPT_Wnonnull = 731,
  OPT_Wnonnull_compare = 732,

  OPT_Wnormalized_ = 734,
  OPT_Wnrvo = 735,
  OPT_Wnull_dereference = 736,
  OPT_Wobjc_root_class = 737,
  OPT_Wodr = 738,
  OPT_Wold_style_cast = 739,
  OPT_Wold_style_declaration = 740,
  OPT_Wold_style_definition = 741,
  OPT_Wopenacc_parallelism = 742,
  OPT_Wopenmp = 743,
  OPT_Wopenmp_simd = 744,
  OPT_Woverflow = 745,
  OPT_Woverlength_strings = 746,

  OPT_Woverloaded_virtual_ = 748,
  OPT_Woverride_init = 749,
  OPT_Woverride_init_side_effects = 750,
  OPT_Woverwrite_recursive = 751,
  OPT_Wp_ = 752,
  OPT_Wpacked = 753,
  OPT_Wpacked_bitfield_compat = 754,
  OPT_Wpacked_not_aligned = 755,
  OPT_Wpadded = 756,
  OPT_Wparentheses = 757,
  OPT_Wpedantic = 758,
  OPT_Wpedantic_cast = 759,
  OPT_Wpedantic_param_names = 760,
  OPT_Wpessimizing_move = 761,

  OPT_Wplacement_new_ = 763,
  OPT_Wpmf_conversions = 764,
  OPT_Wpointer_arith = 765,
  OPT_Wpointer_compare = 766,
  OPT_Wpointer_sign = 767,
  OPT_Wpointer_to_int_cast = 768,
  OPT_Wpragmas = 769,
  OPT_Wprio_ctor_dtor = 770,
  OPT_Wproperty_assign_default = 771,
  OPT_Wprotocol = 772,
  OPT_Wpsabi = 773,
  OPT_Wrange_loop_construct = 774,
  OPT_Wreal_q_constant = 775,
  OPT_Wrealloc_lhs = 776,
  OPT_Wrealloc_lhs_all = 777,
  OPT_Wredundant_decls = 778,
  OPT_Wredundant_move = 779,
  OPT_Wredundant_tags = 780,
  OPT_Wregister = 781,
  OPT_Wreorder = 782,
  OPT_Wrestrict = 783,
  OPT_Wreturn_local_addr = 784,
  OPT_Wreturn_mismatch = 785,
  OPT_Wreturn_type = 786,
  OPT_Wscalar_storage_order = 787,
  OPT_Wselector = 788,
  OPT_Wself_move = 789,
  OPT_Wsequence_point = 790,
  OPT_Wshadow = 791,

  OPT_Wshadow_ivar = 793,

  OPT_Wshadow_compatible_local = 795,

  OPT_Wshadow_local = 797,
  OPT_Wshift_count_negative = 798,
  OPT_Wshift_count_overflow = 799,
  OPT_Wshift_negative_value = 800,

  OPT_Wshift_overflow_ = 802,
  OPT_Wsign_compare = 803,
  OPT_Wsign_conversion = 804,
  OPT_Wsign_promo = 805,
  OPT_Wsized_deallocation = 806,
  OPT_Wsizeof_array_argument = 807,
  OPT_Wsizeof_array_div = 808,
  OPT_Wsizeof_pointer_div = 809,
  OPT_Wsizeof_pointer_memaccess = 810,
  OPT_Wspeculative = 811,
  OPT_Wstack_protector = 812,
  OPT_Wstack_usage_ = 813,
  OPT_Wstrict_aliasing = 814,
  OPT_Wstrict_aliasing_ = 815,
  OPT_Wstrict_flex_arrays = 816,
  OPT_Wstrict_null_sentinel = 817,
  OPT_Wstrict_overflow = 818,
  OPT_Wstrict_overflow_ = 819,
  OPT_Wstrict_prototypes = 820,
  OPT_Wstrict_selector_match = 821,
  OPT_Wstring_compare = 822,

  OPT_Wstringop_overflow_ = 824,
  OPT_Wstringop_overread = 825,
  OPT_Wstringop_truncation = 826,
  OPT_Wstyle = 827,
  OPT_Wsubobject_linkage = 828,
  OPT_Wsuggest_attribute_cold = 829,
  OPT_Wsuggest_attribute_const = 830,
  OPT_Wsuggest_attribute_format = 831,
  OPT_Wsuggest_attribute_malloc = 832,
  OPT_Wsuggest_attribute_noreturn = 833,
  OPT_Wsuggest_attribute_pure = 834,
  OPT_Wsuggest_attribute_returns_nonnull = 835,
  OPT_Wsuggest_final_methods = 836,
  OPT_Wsuggest_final_types = 837,
  OPT_Wsuggest_override = 838,
  OPT_Wsurprising = 839,
  OPT_Wswitch = 840,
  OPT_Wswitch_bool = 841,
  OPT_Wswitch_default = 842,
  OPT_Wswitch_enum = 843,
  OPT_Wswitch_outside_range = 844,
  OPT_Wswitch_unreachable = 845,
  OPT_Wsync_nand = 846,
  OPT_Wsynth = 847,
  OPT_Wsystem_headers = 848,
  OPT_Wtabs = 849,
  OPT_Wtarget_lifetime = 850,
  OPT_Wtautological_compare = 851,
  OPT_Wtemplate_id_cdtor = 852,
  OPT_Wtemplates = 853,
  OPT_Wterminate = 854,
  OPT_Wtraditional = 855,
  OPT_Wtraditional_conversion = 856,
  OPT_Wtrampolines = 857,
  OPT_Wtrigraphs = 858,
  OPT_Wtrivial_auto_var_init = 859,
  OPT_Wtsan = 860,
  OPT_Wtype_limits = 861,
  OPT_Wundeclared_selector = 862,
  OPT_Wundef = 863,
  OPT_Wundefined_do_loop = 864,
  OPT_Wunderflow = 865,
  OPT_Wunicode = 866,
  OPT_Wuninit_variable_checking = 867,
  OPT_Wuninit_variable_checking_ = 868,
  OPT_Wuninitialized = 869,
  OPT_Wunknown_pragmas = 870,


  OPT_Wunsuffixed_float_constants = 873,
  OPT_Wunused = 874,
  OPT_Wunused_but_set_parameter = 875,
  OPT_Wunused_but_set_variable = 876,

  OPT_Wunused_const_variable_ = 878,
  OPT_Wunused_dummy_argument = 879,
  OPT_Wunused_function = 880,
  OPT_Wunused_label = 881,
  OPT_Wunused_local_typedefs = 882,
  OPT_Wunused_macros = 883,
  OPT_Wunused_parameter = 884,
  OPT_Wunused_result = 885,
  OPT_Wunused_value = 886,
  OPT_Wunused_variable = 887,
  OPT_Wuse_after_free = 888,
  OPT_Wuse_after_free_ = 889,
  OPT_Wuse_without_only = 890,
  OPT_Wuseless_cast = 891,
  OPT_Wvarargs = 892,
  OPT_Wvariadic_macros = 893,
  OPT_Wvector_operation_performance = 894,
  OPT_Wverbose_unbounded = 895,
  OPT_Wvexing_parse = 896,
  OPT_Wvirtual_inheritance = 897,
  OPT_Wvirtual_move_assign = 898,
  OPT_Wvla = 899,
  OPT_Wvla_larger_than_ = 900,
  OPT_Wvla_parameter = 901,
  OPT_Wvolatile = 902,
  OPT_Wvolatile_register_var = 903,
  OPT_Wwrite_strings = 904,
  OPT_Wxor_used_as_pow = 905,
  OPT_Wzero_as_null_pointer_constant = 906,
  OPT_Wzero_length_bounds = 907,
  OPT_Wzerotrip = 908,
  OPT_X = 909,
  OPT_Xassembler = 910,
  OPT_Xf = 911,
  OPT_Xlinker = 912,
  OPT_Xpreprocessor = 913,
  OPT_Z = 914,
  OPT_ansi = 915,
  OPT_aux_info = 916,

  OPT_c = 918,
  OPT_callgraph = 919,
  OPT_coverage = 920,
  OPT_cpp = 921,
  OPT_cpp_ = 922,
  OPT_d = 923,
  OPT_debuglib_ = 924,
  OPT_defaultlib_ = 925,
  OPT_defined_only = 926,
  OPT_demangle = 927,
  OPT_dstartfiles = 928,
  OPT_dump_body_ = 929,
  OPT_dump_level_ = 930,
  OPT_dumpbase = 931,
  OPT_dumpbase_ext = 932,
  OPT_dumpdir = 933,
  OPT_dumpfullversion = 934,
  OPT_dumpmachine = 935,
  OPT_dumpspecs = 936,
  OPT_dumpversion = 937,
  OPT_e = 938,
  OPT_export_dynamic = 939,
  OPT_fPIC = 940,
  OPT_fPIE = 941,
  OPT_fRTS_ = 942,
  OPT_fabi_compat_version_ = 943,
  OPT_fabi_version_ = 944,
  OPT_faccess_control = 945,
  OPT_fada_spec_parent_ = 946,
  OPT_faggressive_function_elimination = 947,
  OPT_faggressive_loop_optimizations = 948,
  OPT_falign_commons = 949,
  OPT_falign_functions = 950,
  OPT_falign_functions_ = 951,
  OPT_falign_jumps = 952,
  OPT_falign_jumps_ = 953,
  OPT_falign_labels = 954,
  OPT_falign_labels_ = 955,
  OPT_falign_loops = 956,
  OPT_falign_loops_ = 957,

  OPT_faligned_new_ = 959,
  OPT_fall_instantiations = 960,
  OPT_fall_intrinsics = 961,
  OPT_fall_virtual = 962,
  OPT_fallocation_dce = 963,
  OPT_fallow_argument_mismatch = 964,
  OPT_fallow_invalid_boz = 965,
  OPT_fallow_leading_underscore = 966,

  OPT_fallow_store_data_races = 968,
  OPT_falt_external_templates = 969,
  OPT_fanalyzer = 970,
  OPT_fanalyzer_call_summaries = 971,
  OPT_fanalyzer_checker_ = 972,
  OPT_fanalyzer_debug_text_art = 973,
  OPT_fanalyzer_feasibility = 974,
  OPT_fanalyzer_fine_grained = 975,
  OPT_fanalyzer_show_duplicate_count = 976,
  OPT_fanalyzer_show_events_in_system_headers = 977,
  OPT_fanalyzer_state_merge = 978,
  OPT_fanalyzer_state_purge = 979,
  OPT_fanalyzer_suppress_followups = 980,
  OPT_fanalyzer_transitivity = 981,
  OPT_fanalyzer_undo_inlining = 982,
  OPT_fanalyzer_verbose_edges = 983,
  OPT_fanalyzer_verbose_state_changes = 984,
  OPT_fanalyzer_verbosity_ = 985,




  OPT_fasan_shadow_offset_ = 990,
  OPT_fasm = 991,
  OPT_fassert = 992,
  OPT_fassociative_math = 993,
  OPT_fasynchronous_unwind_tables = 994,
  OPT_fauto_inc_dec = 995,
  OPT_fauto_init = 996,
  OPT_fauto_profile = 997,
  OPT_fauto_profile_ = 998,
  OPT_fautomatic = 999,
  OPT_fbackslash = 1000,
  OPT_fbacktrace = 1001,
  OPT_fbit_tests = 1002,
  OPT_fblas_matmul_limit_ = 1003,
  OPT_fbounds = 1004,
  OPT_fbounds_check = 1005,
  OPT_fbounds_check_ = 1006,
  OPT_fbranch_count_reg = 1007,
  OPT_fbranch_probabilities = 1008,



  OPT_fbuilding_libgcc = 1012,
  OPT_fbuilding_libgfortran = 1013,
  OPT_fbuilding_libphobos_tests = 1014,
  OPT_fbuiltin = 1015,
  OPT_fbuiltin_ = 1016,
  OPT_fbuiltin_printf = 1017,
  OPT_fc_prototypes = 1018,
  OPT_fc_prototypes_external = 1019,
  OPT_fcall_saved_ = 1020,
  OPT_fcall_used_ = 1021,
  OPT_fcaller_saves = 1022,
  OPT_fcallgraph_info = 1023,
  OPT_fcallgraph_info_ = 1024,
  OPT_fcanon_prefix_map = 1025,
  OPT_fcanonical_system_headers = 1026,
  OPT_fcase = 1027,

  OPT_fcf_protection_ = 1029,
  OPT_fchar8_t = 1030,
  OPT_fcheck_array_temporaries = 1031,

  OPT_fcheck_new = 1033,
  OPT_fcheck_pointer_bounds = 1034,
  OPT_fcheck_ = 1035,






  OPT_fcheckaction_ = 1042,
  OPT_fchecking = 1043,
  OPT_fchecking_ = 1044,
  OPT_fchkp_check_incomplete_type = 1045,
  OPT_fchkp_check_read = 1046,
  OPT_fchkp_check_write = 1047,
  OPT_fchkp_first_field_has_own_bounds = 1048,
  OPT_fchkp_flexible_struct_trailing_arrays = 1049,
  OPT_fchkp_instrument_calls = 1050,
  OPT_fchkp_instrument_marked_only = 1051,
  OPT_fchkp_narrow_bounds = 1052,
  OPT_fchkp_narrow_to_innermost_array = 1053,
  OPT_fchkp_optimize = 1054,
  OPT_fchkp_store_bounds = 1055,
  OPT_fchkp_treat_zero_dynamic_size_as_infinite = 1056,
  OPT_fchkp_use_fast_string_functions = 1057,
  OPT_fchkp_use_nochk_string_functions = 1058,
  OPT_fchkp_use_static_bounds = 1059,
  OPT_fchkp_use_static_const_bounds = 1060,
  OPT_fchkp_use_wrappers = 1061,
  OPT_fchkp_zero_input_bounds_for_main = 1062,

  OPT_fcoarray_ = 1064,
  OPT_fcode_hoisting = 1065,
  OPT_fcombine_stack_adjustments = 1066,
  OPT_fcommon = 1067,
  OPT_fcompare_debug = 1068,
  OPT_fcompare_debug_second = 1069,
  OPT_fcompare_debug_ = 1070,
  OPT_fcompare_elim = 1071,
  OPT_fconcepts = 1072,
  OPT_fconcepts_diagnostics_depth_ = 1073,
  OPT_fconcepts_ts = 1074,
  OPT_fcond_mismatch = 1075,
  OPT_fcondition_coverage = 1076,

  OPT_fconserve_stack = 1078,
  OPT_fconstant_string_class_ = 1079,
  OPT_fconstexpr_cache_depth_ = 1080,
  OPT_fconstexpr_depth_ = 1081,
  OPT_fconstexpr_fp_except = 1082,
  OPT_fconstexpr_loop_limit_ = 1083,
  OPT_fconstexpr_ops_limit_ = 1084,
  OPT_fcontract_assumption_mode_ = 1085,
  OPT_fcontract_build_level_ = 1086,
  OPT_fcontract_continuation_mode_ = 1087,
  OPT_fcontract_mode_ = 1088,
  OPT_fcontract_role_ = 1089,
  OPT_fcontract_semantic_ = 1090,
  OPT_fcontract_strict_declarations_ = 1091,
  OPT_fcontracts = 1092,
  OPT_fconvert_ = 1093,
  OPT_fcoroutines = 1094,
  OPT_fcpp = 1095,
  OPT_fcpp_begin = 1096,
  OPT_fcpp_end = 1097,
  OPT_fcprop_registers = 1098,
  OPT_fcray_pointer = 1099,
  OPT_fcrossjumping = 1100,
  OPT_fcse_follow_jumps = 1101,

  OPT_fcx_fortran_rules = 1103,
  OPT_fcx_limited_range = 1104,
  OPT_fd = 1105,
  OPT_fd_lines_as_code = 1106,
  OPT_fd_lines_as_comments = 1107,
  OPT_fdata_sections = 1108,
  OPT_fdbg_cnt_list = 1109,
  OPT_fdbg_cnt_ = 1110,
  OPT_fdce = 1111,
  OPT_fdebug = 1112,
  OPT_fdebug_aux_vars = 1113,
  OPT_fdebug_builtins = 1114,
  OPT_fdebug_cpp = 1115,
  OPT_fdebug_function_line_numbers = 1116,
  OPT_fdebug_prefix_map_ = 1117,
  OPT_fdebug_types_section = 1118,
  OPT_fdebug_ = 1119,
  OPT_fdec = 1120,
  OPT_fdec_blank_format_item = 1121,
  OPT_fdec_char_conversions = 1122,
  OPT_fdec_format_defaults = 1123,
  OPT_fdec_include = 1124,
  OPT_fdec_intrinsic_ints = 1125,
  OPT_fdec_math = 1126,
  OPT_fdec_static = 1127,
  OPT_fdec_structure = 1128,
  OPT_fdeclone_ctor_dtor = 1129,

  OPT_fdef_ = 1131,
  OPT_fdefault_double_8 = 1132,

  OPT_fdefault_integer_8 = 1134,
  OPT_fdefault_real_10 = 1135,
  OPT_fdefault_real_16 = 1136,
  OPT_fdefault_real_8 = 1137,
  OPT_fdefer_pop = 1138,
  OPT_fdelayed_branch = 1139,
  OPT_fdelete_dead_exceptions = 1140,
  OPT_fdelete_null_pointer_checks = 1141,
  OPT_fdeps_file_ = 1142,
  OPT_fdeps_format_ = 1143,
  OPT_fdeps_target_ = 1144,
  OPT_fdevirtualize = 1145,
  OPT_fdevirtualize_at_ltrans = 1146,
  OPT_fdevirtualize_speculatively = 1147,
  OPT_fdiagnostics_all_candidates = 1148,

  OPT_fdiagnostics_color_ = 1150,
  OPT_fdiagnostics_column_origin_ = 1151,
  OPT_fdiagnostics_column_unit_ = 1152,
  OPT_fdiagnostics_escape_format_ = 1153,
  OPT_fdiagnostics_format_ = 1154,
  OPT_fdiagnostics_generate_patch = 1155,
  OPT_fdiagnostics_json_formatting = 1156,
  OPT_fdiagnostics_minimum_margin_width_ = 1157,
  OPT_fdiagnostics_parseable_fixits = 1158,
  OPT_fdiagnostics_path_format_ = 1159,
  OPT_fdiagnostics_plain_output = 1160,
  OPT_fdiagnostics_show_caret = 1161,
  OPT_fdiagnostics_show_cwe = 1162,
  OPT_fdiagnostics_show_labels = 1163,
  OPT_fdiagnostics_show_line_numbers = 1164,
  OPT_fdiagnostics_show_location_ = 1165,
  OPT_fdiagnostics_show_option = 1166,
  OPT_fdiagnostics_show_path_depths = 1167,
  OPT_fdiagnostics_show_rules = 1168,
  OPT_fdiagnostics_show_template_tree = 1169,
  OPT_fdiagnostics_text_art_charset_ = 1170,
  OPT_fdiagnostics_urls_ = 1171,
  OPT_fdirectives_only = 1172,
  OPT_fdisable_ = 1173,
  OPT_fdoc = 1174,
  OPT_fdoc_dir_ = 1175,
  OPT_fdoc_file_ = 1176,
  OPT_fdoc_inc_ = 1177,
  OPT_fdollar_ok = 1178,
  OPT_fdollars_in_identifiers = 1179,
  OPT_fdruntime = 1180,
  OPT_fdse = 1181,
  OPT_fdump_ = 1182,
  OPT_fdump_ada_spec = 1183,
  OPT_fdump_ada_spec_slim = 1184,
  OPT_fdump_analyzer = 1185,
  OPT_fdump_analyzer_callgraph = 1186,
  OPT_fdump_analyzer_exploded_graph = 1187,
  OPT_fdump_analyzer_exploded_nodes = 1188,
  OPT_fdump_analyzer_exploded_nodes_2 = 1189,
  OPT_fdump_analyzer_exploded_nodes_3 = 1190,
  OPT_fdump_analyzer_exploded_paths = 1191,
  OPT_fdump_analyzer_feasibility = 1192,
  OPT_fdump_analyzer_infinite_loop = 1193,
  OPT_fdump_analyzer_json = 1194,
  OPT_fdump_analyzer_state_purge = 1195,
  OPT_fdump_analyzer_stderr = 1196,
  OPT_fdump_analyzer_supergraph = 1197,
  OPT_fdump_analyzer_untracked = 1198,
  OPT_fdump_c___spec_verbose = 1199,
  OPT_fdump_c___spec_ = 1200,

  OPT_fdump_d_original = 1202,
  OPT_fdump_final_insns = 1203,
  OPT_fdump_final_insns_ = 1204,
  OPT_fdump_fortran_global = 1205,
  OPT_fdump_fortran_optimized = 1206,
  OPT_fdump_fortran_original = 1207,
  OPT_fdump_go_spec_ = 1208,
  OPT_fdump_internal_locations = 1209,
  OPT_fdump_noaddr = 1210,

  OPT_fdump_passes = 1212,
  OPT_fdump_scos = 1213,
  OPT_fdump_system_exports = 1214,
  OPT_fdump_unnumbered = 1215,
  OPT_fdump_unnumbered_links = 1216,
  OPT_fdwarf2_cfi_asm = 1217,
  OPT_fearly_inlining = 1218,
  OPT_felide_constructors = 1219,
  OPT_felide_type = 1220,

  OPT_feliminate_unused_debug_symbols = 1222,
  OPT_feliminate_unused_debug_types = 1223,
  OPT_femit_class_debug_always = 1224,
  OPT_femit_struct_debug_baseonly = 1225,
  OPT_femit_struct_debug_detailed_ = 1226,
  OPT_femit_struct_debug_reduced = 1227,
  OPT_fenable_ = 1228,
  OPT_fenforce_eh_specs = 1229,
  OPT_fenum_int_equiv = 1230,
  OPT_fexceptions = 1231,
  OPT_fexcess_precision_ = 1232,
  OPT_fexec_charset_ = 1233,
  OPT_fexpensive_optimizations = 1234,
  OPT_fext_numeric_literals = 1235,
  OPT_fextended_identifiers = 1236,
  OPT_fextended_opaque = 1237,
  OPT_fextern_std_ = 1238,
  OPT_fextern_tls_init = 1239,
  OPT_fexternal_blas = 1240,
  OPT_fexternal_templates = 1241,
  OPT_ff2c = 1242,
  OPT_ffast_math = 1243,
  OPT_ffat_lto_objects = 1244,
  OPT_ffile_prefix_map_ = 1245,
  OPT_ffinite_loops = 1246,
  OPT_ffinite_math_only = 1247,
  OPT_ffixed_ = 1248,
  OPT_ffixed_form = 1249,
  OPT_ffixed_line_length_ = 1250,
  OPT_ffixed_line_length_none = 1251,
  OPT_ffloat_store = 1252,
  OPT_ffloatvalue = 1253,
  OPT_ffold_mem_offsets = 1254,
  OPT_ffold_simple_inlines = 1255,
  OPT_ffor_scope = 1256,

  OPT_fforward_propagate = 1258,
  OPT_ffp_contract_ = 1259,
  OPT_ffp_int_builtin_inexact = 1260,
  OPT_ffpe_summary_ = 1261,
  OPT_ffpe_trap_ = 1262,
  OPT_ffree_form = 1263,
  OPT_ffree_line_length_ = 1264,
  OPT_ffree_line_length_none = 1265,
  OPT_ffreestanding = 1266,
  OPT_ffriend_injection = 1267,
  OPT_ffrontend_loop_interchange = 1268,
  OPT_ffrontend_optimize = 1269,
  OPT_ffunction_cse = 1270,
  OPT_ffunction_sections = 1271,
  OPT_fgcse = 1272,
  OPT_fgcse_after_reload = 1273,
  OPT_fgcse_las = 1274,
  OPT_fgcse_lm = 1275,
  OPT_fgcse_sm = 1276,
  OPT_fgen_module_list_ = 1277,
  OPT_fgimple = 1278,
  OPT_fgnat_encodings_ = 1279,
  OPT_fgnu_keywords = 1280,
  OPT_fgnu_runtime = 1281,
  OPT_fgnu_tm = 1282,
  OPT_fgnu_unique = 1283,
  OPT_fgnu89_inline = 1284,
  OPT_fgo_c_header_ = 1285,
  OPT_fgo_check_divide_overflow = 1286,
  OPT_fgo_check_divide_zero = 1287,
  OPT_fgo_compiling_runtime = 1288,
  OPT_fgo_debug_escape = 1289,
  OPT_fgo_debug_escape_hash_ = 1290,
  OPT_fgo_debug_optimization = 1291,
  OPT_fgo_dump_ = 1292,
  OPT_fgo_embedcfg_ = 1293,
  OPT_fgo_importcfg_ = 1294,
  OPT_fgo_optimize_ = 1295,
  OPT_fgo_pkgpath_ = 1296,
  OPT_fgo_prefix_ = 1297,
  OPT_fgo_relative_import_path_ = 1298,
  OPT_fgraphite = 1299,
  OPT_fgraphite_identity = 1300,
  OPT_fguess_branch_probability = 1301,
  OPT_fguiding_decls = 1302,

  OPT_fhardcfr_check_exceptions = 1304,
  OPT_fhardcfr_check_noreturn_calls_ = 1305,
  OPT_fhardcfr_check_returning_calls = 1306,
  OPT_fhardcfr_skip_leaf = 1307,
  OPT_fharden_compares = 1308,
  OPT_fharden_conditional_branches = 1309,
  OPT_fharden_control_flow_redundancy = 1310,
  OPT_fhardened = 1311,


  OPT_fhoist_adjacent_loads = 1314,
  OPT_fhonor_std = 1315,
  OPT_fhosted = 1316,
  OPT_fhuge_objects = 1317,
  OPT_fident = 1318,
  OPT_fif_conversion = 1319,
  OPT_fif_conversion2 = 1320,
  OPT_fignore_unknown_pragmas = 1321,
  OPT_fimmediate_escalation = 1322,
  OPT_fimplement_inlines = 1323,
  OPT_fimplicit_constexpr = 1324,
  OPT_fimplicit_inline_templates = 1325,
  OPT_fimplicit_none = 1326,
  OPT_fimplicit_templates = 1327,
  OPT_findex = 1328,
  OPT_findirect_inlining = 1329,
  OPT_finhibit_size_directive = 1330,
  OPT_finit_character_ = 1331,
  OPT_finit_derived = 1332,
  OPT_finit_integer_ = 1333,
  OPT_finit_local_zero = 1334,
  OPT_finit_logical_ = 1335,
  OPT_finit_real_ = 1336,
  OPT_finline = 1337,
  OPT_finline_arg_packing = 1338,
  OPT_finline_atomics = 1339,
  OPT_finline_functions = 1340,
  OPT_finline_functions_called_once = 1341,

  OPT_finline_limit_ = 1343,
  OPT_finline_matmul_limit_ = 1344,
  OPT_finline_small_functions = 1345,
  OPT_finline_stringops = 1346,
  OPT_finline_stringops_ = 1347,
  OPT_finput_charset_ = 1348,
  OPT_finstrument_functions = 1349,
  OPT_finstrument_functions_exclude_file_list_ = 1350,
  OPT_finstrument_functions_exclude_function_list_ = 1351,
  OPT_finstrument_functions_once = 1352,
  OPT_finteger_4_integer_8 = 1353,
  OPT_fintrinsic_modules_path = 1354,
  OPT_fintrinsic_modules_path_ = 1355,
  OPT_finvariants = 1356,
  OPT_fipa_bit_cp = 1357,
  OPT_fipa_cp = 1358,

  OPT_fipa_cp_clone = 1360,
  OPT_fipa_icf = 1361,
  OPT_fipa_icf_functions = 1362,
  OPT_fipa_icf_variables = 1363,

  OPT_fipa_modref = 1365,
  OPT_fipa_profile = 1366,
  OPT_fipa_pta = 1367,
  OPT_fipa_pure_const = 1368,
  OPT_fipa_ra = 1369,
  OPT_fipa_reference = 1370,
  OPT_fipa_reference_addressable = 1371,
  OPT_fipa_sra = 1372,
  OPT_fipa_stack_alignment = 1373,
  OPT_fipa_strict_aliasing = 1374,

  OPT_fipa_vrp = 1376,
  OPT_fira_algorithm_ = 1377,
  OPT_fira_hoist_pressure = 1378,
  OPT_fira_loop_pressure = 1379,
  OPT_fira_region_ = 1380,
  OPT_fira_share_save_slots = 1381,
  OPT_fira_share_spill_slots = 1382,
  OPT_fira_verbose_ = 1383,
  OPT_fiso = 1384,
  OPT_fisolate_erroneous_paths_attribute = 1385,
  OPT_fisolate_erroneous_paths_dereference = 1386,
  OPT_fivar_visibility_ = 1387,
  OPT_fivopts = 1388,
  OPT_fjump_tables = 1389,
  OPT_fkeep_gc_roots_live = 1390,
  OPT_fkeep_inline_dllexport = 1391,
  OPT_fkeep_inline_functions = 1392,
  OPT_fkeep_static_consts = 1393,
  OPT_fkeep_static_functions = 1394,
  OPT_flabels_ok = 1395,
  OPT_flang_info_include_translate = 1396,
  OPT_flang_info_include_translate_not = 1397,
  OPT_flang_info_include_translate_ = 1398,
  OPT_flang_info_module_cmi = 1399,
  OPT_flang_info_module_cmi_ = 1400,
  OPT_flarge_source_files = 1401,
  OPT_flax_vector_conversions = 1402,
  OPT_fleading_underscore = 1403,
  OPT_flibs_ = 1404,
  OPT_flifetime_dse = 1405,
  OPT_flifetime_dse_ = 1406,
  OPT_flimit_function_alignment = 1407,
  OPT_flinker_output_ = 1408,

  OPT_flive_patching_ = 1410,
  OPT_flive_range_shrinkage = 1411,
  OPT_flocal_ivars = 1412,
  OPT_flocation_ = 1413,


  OPT_floop_interchange = 1416,
  OPT_floop_nest_optimize = 1417,

  OPT_floop_parallelize_all = 1419,

  OPT_floop_unroll_and_jam = 1421,
  OPT_flra_remat = 1422,
  OPT_flto = 1423,
  OPT_flto_compression_level_ = 1424,

  OPT_flto_partition_ = 1426,
  OPT_flto_report = 1427,
  OPT_flto_report_wpa = 1428,
  OPT_flto_ = 1429,
  OPT_fltrans = 1430,
  OPT_fltrans_output_list_ = 1431,
  OPT_fm2_debug_trace_ = 1432,
  OPT_fm2_g = 1433,
  OPT_fm2_lower_case = 1434,
  OPT_fm2_pathname_ = 1435,
  OPT_fm2_pathnameI = 1436,
  OPT_fm2_plugin = 1437,
  OPT_fm2_prefix_ = 1438,
  OPT_fm2_statistics = 1439,
  OPT_fm2_strict_type = 1440,
  OPT_fm2_whole_program = 1441,
  OPT_fmacro_prefix_map_ = 1442,
  OPT_fmain = 1443,
  OPT_fmath_errno = 1444,
  OPT_fmax_array_constructor_ = 1445,
  OPT_fmax_errors_ = 1446,
  OPT_fmax_identifier_length_ = 1447,
  OPT_fmax_include_depth_ = 1448,
  OPT_fmax_stack_var_size_ = 1449,
  OPT_fmax_subrecord_length_ = 1450,
  OPT_fmem_report = 1451,
  OPT_fmem_report_wpa = 1452,
  OPT_fmerge_all_constants = 1453,
  OPT_fmerge_constants = 1454,
  OPT_fmerge_debug_strings = 1455,
  OPT_fmessage_length_ = 1456,
  OPT_fmin_function_alignment_ = 1457,
  OPT_fmod_ = 1458,
  OPT_fmodule_file_ = 1459,
  OPT_fmodule_header = 1460,
  OPT_fmodule_header_ = 1461,
  OPT_fmodule_implicit_inline = 1462,
  OPT_fmodule_lazy = 1463,
  OPT_fmodule_mapper_ = 1464,
  OPT_fmodule_only = 1465,
  OPT_fmodule_private = 1466,
  OPT_fmodule_version_ignore = 1467,
  OPT_fmoduleinfo = 1468,
  OPT_fmodules_ts = 1469,
  OPT_fmodulo_sched = 1470,
  OPT_fmodulo_sched_allow_regmoves = 1471,
  OPT_fmove_loop_invariants = 1472,
  OPT_fmove_loop_stores = 1473,
  OPT_fms_extensions = 1474,
  OPT_fmudflap = 1475,
  OPT_fmudflapir = 1476,
  OPT_fmudflapth = 1477,
  OPT_fmultiflags = 1478,
  OPT_fname_mangling_version_ = 1479,
  OPT_fnew_abi = 1480,
  OPT_fnew_inheriting_ctors = 1481,
  OPT_fnew_ttp_matching = 1482,
  OPT_fnext_runtime = 1483,
  OPT_fnil = 1484,
  OPT_fnil_receivers = 1485,
  OPT_fno_inline_stringops = 1486,
  OPT_fno_modules = 1487,
  OPT_fnon_call_exceptions = 1488,
  OPT_fnonansi_builtins = 1489,
  OPT_fnonnull_objects = 1490,
  OPT_fnothrow_opt = 1491,
  OPT_fobjc_abi_version_ = 1492,
  OPT_fobjc_call_cxx_cdtors = 1493,
  OPT_fobjc_direct_dispatch = 1494,
  OPT_fobjc_exceptions = 1495,
  OPT_fobjc_gc = 1496,
  OPT_fobjc_nilcheck = 1497,
  OPT_fobjc_sjlj_exceptions = 1498,
  OPT_fobjc_std_objc1 = 1499,
  OPT_foffload_abi_ = 1500,
  OPT_foffload_options_ = 1501,
  OPT_foffload_ = 1502,
  OPT_fomit_frame_pointer = 1503,
  OPT_fonly_ = 1504,
  OPT_fopenacc = 1505,
  OPT_fopenacc_dim_ = 1506,
  OPT_fopenmp = 1507,
  OPT_fopenmp_allocators = 1508,
  OPT_fopenmp_simd = 1509,

  OPT_fopenmp_target_simd_clone_ = 1511,
  OPT_foperator_names = 1512,
  OPT_fopt_info = 1513,
  OPT_fopt_info_ = 1514,

  OPT_foptimize_sibling_calls = 1516,
  OPT_foptimize_strlen = 1517,

  OPT_fpack_derived = 1519,
  OPT_fpack_struct = 1520,
  OPT_fpack_struct_ = 1521,
  OPT_fpad_source = 1522,
  OPT_fpartial_inlining = 1523,
  OPT_fpatchable_function_entry_ = 1524,
  OPT_fpcc_struct_return = 1525,
  OPT_fpch_deps = 1526,
  OPT_fpch_preprocess = 1527,
  OPT_fpeel_loops = 1528,
  OPT_fpeephole = 1529,
  OPT_fpeephole2 = 1530,
  OPT_fpermissive = 1531,
  OPT_fpermitted_flt_eval_methods_ = 1532,
  OPT_fpic = 1533,
  OPT_fpie = 1534,
  OPT_fpim = 1535,
  OPT_fpim2 = 1536,
  OPT_fpim3 = 1537,
  OPT_fpim4 = 1538,
  OPT_fplan9_extensions = 1539,
  OPT_fplt = 1540,
  OPT_fplugin_arg_ = 1541,
  OPT_fplugin_ = 1542,
  OPT_fpositive_mod_floor_div = 1543,
  OPT_fpost_ipa_mem_report = 1544,
  OPT_fpostconditions = 1545,
  OPT_fpre_include_ = 1546,
  OPT_fpre_ipa_mem_report = 1547,
  OPT_fpreconditions = 1548,
  OPT_fpredictive_commoning = 1549,
  OPT_fprefetch_loop_arrays = 1550,
  OPT_fpreprocessed = 1551,
  OPT_fpretty_templates = 1552,
  OPT_fpreview_all = 1553,
  OPT_fpreview_bitfields = 1554,
  OPT_fpreview_dip1000 = 1555,
  OPT_fpreview_dip1008 = 1556,
  OPT_fpreview_dip1021 = 1557,
  OPT_fpreview_dtorfields = 1558,
  OPT_fpreview_fieldwise = 1559,
  OPT_fpreview_fixaliasthis = 1560,
  OPT_fpreview_fiximmutableconv = 1561,
  OPT_fpreview_in = 1562,
  OPT_fpreview_inclusiveincontracts = 1563,
  OPT_fpreview_nosharedaccess = 1564,
  OPT_fpreview_rvaluerefparam = 1565,
  OPT_fpreview_systemvariables = 1566,
  OPT_fprintf_return_value = 1567,
  OPT_fprofile = 1568,
  OPT_fprofile_abs_path = 1569,
  OPT_fprofile_arcs = 1570,
  OPT_fprofile_correction = 1571,
  OPT_fprofile_dir_ = 1572,
  OPT_fprofile_exclude_files_ = 1573,
  OPT_fprofile_filter_files_ = 1574,
  OPT_fprofile_generate = 1575,
  OPT_fprofile_generate_ = 1576,
  OPT_fprofile_info_section = 1577,
  OPT_fprofile_info_section_ = 1578,
  OPT_fprofile_note_ = 1579,
  OPT_fprofile_partial_training = 1580,
  OPT_fprofile_prefix_map_ = 1581,
  OPT_fprofile_prefix_path_ = 1582,
  OPT_fprofile_reorder_functions = 1583,
  OPT_fprofile_report = 1584,
  OPT_fprofile_reproducible_ = 1585,
  OPT_fprofile_update_ = 1586,
  OPT_fprofile_use = 1587,
  OPT_fprofile_use_ = 1588,
  OPT_fprofile_values = 1589,
  OPT_fprotect_parens = 1590,
  OPT_fpthread = 1591,
  OPT_fq = 1592,
  OPT_frandom_seed = 1593,
  OPT_frandom_seed_ = 1594,
  OPT_frange = 1595,
  OPT_frange_check = 1596,
  OPT_freal_4_real_10 = 1597,
  OPT_freal_4_real_16 = 1598,
  OPT_freal_4_real_8 = 1599,
  OPT_freal_8_real_10 = 1600,
  OPT_freal_8_real_16 = 1601,
  OPT_freal_8_real_4 = 1602,
  OPT_frealloc_lhs = 1603,
  OPT_freciprocal_math = 1604,
  OPT_frecord_gcc_switches = 1605,
  OPT_frecord_marker_4 = 1606,
  OPT_frecord_marker_8 = 1607,
  OPT_frecursive = 1608,
  OPT_free = 1609,
  OPT_freg_struct_return = 1610,

  OPT_frelease = 1612,
  OPT_frename_registers = 1613,
  OPT_freorder_blocks = 1614,
  OPT_freorder_blocks_algorithm_ = 1615,
  OPT_freorder_blocks_and_partition = 1616,
  OPT_freorder_functions = 1617,
  OPT_frepack_arrays = 1618,
  OPT_freplace_objc_classes = 1619,
  OPT_frepo = 1620,
  OPT_freport_bug = 1621,
  OPT_frequire_return_statement = 1622,
  OPT_frerun_cse_after_loop = 1623,

  OPT_freschedule_modulo_scheduled_loops = 1625,
  OPT_fresolution_ = 1626,
  OPT_freturn = 1627,
  OPT_frevert_all = 1628,
  OPT_frevert_dip1000 = 1629,
  OPT_frevert_dtorfields = 1630,
  OPT_frevert_intpromote = 1631,
  OPT_frounding_math = 1632,
  OPT_frtti = 1633,
  OPT_fruntime_modules_ = 1634,
  OPT_frust_borrowcheck = 1635,
  OPT_frust_cfg_ = 1636,
  OPT_frust_compile_until_ = 1637,
  OPT_frust_crate_type_ = 1638,
  OPT_frust_crate_ = 1639,
  OPT_frust_debug = 1640,
  OPT_frust_dump_ = 1641,
  OPT_frust_edition_ = 1642,
  OPT_frust_embed_metadata = 1643,
  OPT_frust_extern_ = 1644,
  OPT_frust_incomplete_and_experimental_compiler_do_not_use = 1645,
  OPT_frust_mangling_ = 1646,
  OPT_frust_max_recursion_depth_ = 1647,
  OPT_frust_metadata_output_ = 1648,
  OPT_frust_name_resolution_2_0 = 1649,
  OPT_fsanitize_address_use_after_scope = 1650,
  OPT_fsanitize_coverage_ = 1651,
  OPT_fsanitize_recover = 1652,
  OPT_fsanitize_recover_ = 1653,
  OPT_fsanitize_sections_ = 1654,
  OPT_fsanitize_trap = 1655,
  OPT_fsanitize_trap_ = 1656,

  OPT_fsanitize_ = 1658,
  OPT_fsave_mixins_ = 1659,
  OPT_fsave_optimization_record = 1660,
  OPT_fscaffold_c = 1661,
  OPT_fscaffold_c__ = 1662,
  OPT_fscaffold_dynamic = 1663,
  OPT_fscaffold_main = 1664,
  OPT_fscaffold_static = 1665,
  OPT_fsched_critical_path_heuristic = 1666,
  OPT_fsched_dep_count_heuristic = 1667,
  OPT_fsched_group_heuristic = 1668,
  OPT_fsched_interblock = 1669,
  OPT_fsched_last_insn_heuristic = 1670,
  OPT_fsched_pressure = 1671,
  OPT_fsched_rank_heuristic = 1672,
  OPT_fsched_spec = 1673,
  OPT_fsched_spec_insn_heuristic = 1674,
  OPT_fsched_spec_load = 1675,
  OPT_fsched_spec_load_dangerous = 1676,
  OPT_fsched_stalled_insns = 1677,
  OPT_fsched_stalled_insns_dep = 1678,
  OPT_fsched_stalled_insns_dep_ = 1679,
  OPT_fsched_stalled_insns_ = 1680,
  OPT_fsched_verbose_ = 1681,
  OPT_fsched2_use_superblocks = 1682,

  OPT_fschedule_fusion = 1684,
  OPT_fschedule_insns = 1685,
  OPT_fschedule_insns2 = 1686,
  OPT_fsecond_underscore = 1687,
  OPT_fsection_anchors = 1688,

  OPT_fsel_sched_pipelining = 1690,
  OPT_fsel_sched_pipelining_outer_loops = 1691,
  OPT_fsel_sched_reschedule_pipelined = 1692,
  OPT_fselective_scheduling = 1693,
  OPT_fselective_scheduling2 = 1694,
  OPT_fself_test_ = 1695,
  OPT_fsemantic_interposition = 1696,
  OPT_fshared = 1697,
  OPT_fshort_enums = 1698,
  OPT_fshort_wchar = 1699,
  OPT_fshow_column = 1700,
  OPT_fshrink_wrap = 1701,
  OPT_fshrink_wrap_separate = 1702,
  OPT_fsign_zero = 1703,
  OPT_fsignaling_nans = 1704,
  OPT_fsigned_bitfields = 1705,
  OPT_fsigned_char = 1706,
  OPT_fsigned_zeros = 1707,
  OPT_fsimd_cost_model_ = 1708,
  OPT_fsingle_precision_constant = 1709,
  OPT_fsized_deallocation = 1710,
  OPT_fsoft_check_all = 1711,
  OPT_fsources = 1712,
  OPT_fsplit_ivs_in_unroller = 1713,
  OPT_fsplit_loops = 1714,
  OPT_fsplit_paths = 1715,
  OPT_fsplit_stack = 1716,
  OPT_fsplit_wide_types = 1717,
  OPT_fsplit_wide_types_early = 1718,
  OPT_fsquangle = 1719,
  OPT_fssa_backprop = 1720,
  OPT_fssa_phiopt = 1721,
  OPT_fsso_struct_ = 1722,
  OPT_fstack_arrays = 1723,

  OPT_fstack_check_ = 1725,
  OPT_fstack_clash_protection = 1726,
  OPT_fstack_limit = 1727,
  OPT_fstack_limit_register_ = 1728,
  OPT_fstack_limit_symbol_ = 1729,
  OPT_fstack_protector = 1730,
  OPT_fstack_protector_all = 1731,
  OPT_fstack_protector_explicit = 1732,
  OPT_fstack_protector_strong = 1733,
  OPT_fstack_reuse_ = 1734,
  OPT_fstack_usage = 1735,
  OPT_fstats = 1736,
  OPT_fstdarg_opt = 1737,
  OPT_fstore_merging = 1738,

  OPT_fstrict_aliasing = 1740,
  OPT_fstrict_enums = 1741,

  OPT_fstrict_flex_arrays_ = 1743,
  OPT_fstrict_overflow = 1744,
  OPT_fstrict_prototype = 1745,
  OPT_fstrict_volatile_bitfields = 1746,

  OPT_fstrong_eval_order_ = 1748,
  OPT_fstrub_all = 1749,
  OPT_fstrub_at_calls = 1750,
  OPT_fstrub_disable = 1751,
  OPT_fstrub_internal = 1752,
  OPT_fstrub_relaxed = 1753,
  OPT_fstrub_strict = 1754,
  OPT_fswig = 1755,
  OPT_fswitch_errors = 1756,
  OPT_fsync_libcalls = 1757,
  OPT_fsyntax_only = 1758,
  OPT_ftabstop_ = 1759,

  OPT_ftail_call_workaround_ = 1761,

  OPT_ftemplate_backtrace_limit_ = 1763,

  OPT_ftemplate_depth_ = 1765,
  OPT_ftest_coverage = 1766,
  OPT_ftest_forall_temp = 1767,
  OPT_fthis_is_variable = 1768,
  OPT_fthread_jumps = 1769,
  OPT_fthreadsafe_statics = 1770,
  OPT_ftime_report = 1771,
  OPT_ftime_report_details = 1772,
  OPT_ftls_model_ = 1773,
  OPT_ftoplevel_reorder = 1774,
  OPT_ftracer = 1775,
  OPT_ftrack_macro_expansion = 1776,
  OPT_ftrack_macro_expansion_ = 1777,
  OPT_ftrampoline_impl_ = 1778,
  OPT_ftrampolines = 1779,
  OPT_ftransition_all = 1780,
  OPT_ftransition_field = 1781,
  OPT_ftransition_in = 1782,
  OPT_ftransition_nogc = 1783,
  OPT_ftransition_templates = 1784,
  OPT_ftransition_tls = 1785,
  OPT_ftrapping_math = 1786,
  OPT_ftrapv = 1787,
  OPT_ftree_bit_ccp = 1788,
  OPT_ftree_builtin_call_dce = 1789,
  OPT_ftree_ccp = 1790,
  OPT_ftree_ch = 1791,

  OPT_ftree_coalesce_vars = 1793,
  OPT_ftree_copy_prop = 1794,

  OPT_ftree_cselim = 1796,
  OPT_ftree_dce = 1797,
  OPT_ftree_dominator_opts = 1798,
  OPT_ftree_dse = 1799,
  OPT_ftree_forwprop = 1800,
  OPT_ftree_fre = 1801,
  OPT_ftree_loop_distribute_patterns = 1802,
  OPT_ftree_loop_distribution = 1803,
  OPT_ftree_loop_if_convert = 1804,

  OPT_ftree_loop_im = 1806,
  OPT_ftree_loop_ivcanon = 1807,

  OPT_ftree_loop_optimize = 1809,
  OPT_ftree_loop_vectorize = 1810,
  OPT_ftree_lrs = 1811,
  OPT_ftree_parallelize_loops_ = 1812,
  OPT_ftree_partial_pre = 1813,
  OPT_ftree_phiprop = 1814,
  OPT_ftree_pre = 1815,
  OPT_ftree_pta = 1816,
  OPT_ftree_reassoc = 1817,

  OPT_ftree_scev_cprop = 1819,
  OPT_ftree_sink = 1820,
  OPT_ftree_slp_vectorize = 1821,
  OPT_ftree_slsr = 1822,
  OPT_ftree_sra = 1823,


  OPT_ftree_switch_conversion = 1826,
  OPT_ftree_tail_merge = 1827,
  OPT_ftree_ter = 1828,

  OPT_ftree_vectorize = 1830,

  OPT_ftree_vrp = 1832,
  OPT_ftrivial_auto_var_init_ = 1833,
  OPT_funbounded_by_reference = 1834,
  OPT_funconstrained_commons = 1835,
  OPT_funderscoring = 1836,
  OPT_funit_at_a_time = 1837,
  OPT_funittest = 1838,
  OPT_funreachable_traps = 1839,
  OPT_funroll_all_loops = 1840,
  OPT_funroll_completely_grow_size = 1841,
  OPT_funroll_loops = 1842,

  OPT_funsafe_math_optimizations = 1844,
  OPT_funsigned_bitfields = 1845,
  OPT_funsigned_char = 1846,
  OPT_funswitch_loops = 1847,
  OPT_funwind_tables = 1848,
  OPT_fuse_cxa_atexit = 1849,
  OPT_fuse_cxa_get_exception_ptr = 1850,
  OPT_fuse_ld_bfd = 1851,
  OPT_fuse_ld_gold = 1852,
  OPT_fuse_ld_lld = 1853,
  OPT_fuse_ld_mold = 1854,
  OPT_fuse_linker_plugin = 1855,
  OPT_fuse_list_ = 1856,
  OPT_fvar_tracking = 1857,
  OPT_fvar_tracking_assignments = 1858,
  OPT_fvar_tracking_assignments_toggle = 1859,
  OPT_fvar_tracking_uninit = 1860,
  OPT_fvariable_expansion_in_unroller = 1861,

  OPT_fvect_cost_model_ = 1863,
  OPT_fverbose_asm = 1864,

  OPT_fversion_loops_for_strides = 1866,
  OPT_fversion_ = 1867,
  OPT_fvisibility_inlines_hidden = 1868,
  OPT_fvisibility_ms_compat = 1869,
  OPT_fvisibility_ = 1870,
  OPT_fvpt = 1871,
  OPT_fvtable_gc = 1872,
  OPT_fvtable_thunks = 1873,
  OPT_fvtable_verify_ = 1874,
  OPT_fvtv_counts = 1875,
  OPT_fvtv_debug = 1876,
  OPT_fweak = 1877,
  OPT_fweak_templates = 1878,
  OPT_fweb = 1879,

  OPT_fwhole_program = 1881,
  OPT_fwholediv = 1882,
  OPT_fwholevalue = 1883,
  OPT_fwide_exec_charset_ = 1884,
  OPT_fworking_directory = 1885,
  OPT_fwpa = 1886,
  OPT_fwpa_ = 1887,
  OPT_fwrapv = 1888,
  OPT_fwrapv_pointer = 1889,
  OPT_fxref = 1890,

  OPT_fzero_call_used_regs_ = 1892,
  OPT_fzero_initialized_in_bss = 1893,
  OPT_fzero_link = 1894,
  OPT_g = 1895,
  OPT_gant = 1896,
  OPT_gas_loc_support = 1897,
  OPT_gas_locview_support = 1898,
  OPT_gbtf = 1899,
  OPT_gcodeview = 1900,
  OPT_gcoff = 1901,
  OPT_gcoff1 = 1902,
  OPT_gcoff2 = 1903,
  OPT_gcoff3 = 1904,
  OPT_gcolumn_info = 1905,
  OPT_gctf = 1906,
  OPT_gdescribe_dies = 1907,
  OPT_gdwarf = 1908,
  OPT_gdwarf_ = 1909,
  OPT_gdwarf32 = 1910,
  OPT_gdwarf64 = 1911,
  OPT_gen_decls = 1912,
  OPT_ggdb = 1913,
  OPT_ggnu_pubnames = 1914,
  OPT_gimple_stats = 1915,
  OPT_ginline_points = 1916,
  OPT_ginternal_reset_location_views = 1917,
  OPT_gnat = 1918,
  OPT_gnatO = 1919,
  OPT_gno_ = 1920,
  OPT_gno_pubnames = 1921,
  OPT_gpubnames = 1922,
  OPT_grecord_gcc_switches = 1923,
  OPT_gsplit_dwarf = 1924,
  OPT_gstabs = 1925,
  OPT_gstabs_ = 1926,
  OPT_gstatement_frontiers = 1927,
  OPT_gstrict_dwarf = 1928,
  OPT_gtoggle = 1929,
  OPT_gvariable_location_views = 1930,
  OPT_gvariable_location_views_incompat5 = 1931,
  OPT_gvms = 1932,
  OPT_gxcoff = 1933,
  OPT_gxcoff_ = 1934,
  OPT_gz = 1935,
  OPT_gz_ = 1936,
  OPT_h = 1937,
  OPT_help = 1938,
  OPT_idirafter = 1939,
  OPT_imacros = 1940,
  OPT_imultiarch = 1941,
  OPT_imultilib = 1942,
  OPT_include = 1943,
  OPT_iplugindir_ = 1944,
  OPT_iprefix = 1945,
  OPT_iquote = 1946,
  OPT_isysroot = 1947,
  OPT_isystem = 1948,
  OPT_iwithprefix = 1949,
  OPT_iwithprefixbefore = 1950,
  OPT_k8 = 1951,
  OPT_l = 1952,
  OPT_lang_asm = 1953,
  OPT_list = 1954,
  OPT_mabi_ = 1955,
  OPT_mabort_on_noreturn = 1956,
  OPT_mapcs = 1957,
  OPT_mapcs_frame = 1958,
  OPT_mapcs_reentrant = 1959,
  OPT_mapcs_stack_check = 1960,
  OPT_march_ = 1961,
  OPT_marm = 1962,
  OPT_masm_syntax_unified = 1963,
  OPT_mbe32 = 1964,
  OPT_mbe8 = 1965,
  OPT_mbig_endian = 1966,
  OPT_mbranch_cost_ = 1967,
  OPT_mbranch_protection_ = 1968,
  OPT_mcallee_super_interworking = 1969,
  OPT_mcaller_super_interworking = 1970,
  OPT_mcmse = 1971,
  OPT_mcpu_ = 1972,
  OPT_mdlstp = 1973,
  OPT_mfdpic = 1974,
  OPT_mfix_cmse_cve_2021_35465 = 1975,
  OPT_mfix_cortex_a57_aes_1742098 = 1976,

  OPT_mfix_cortex_m3_ldrd = 1978,
  OPT_mflip_thumb = 1979,
  OPT_mfloat_abi_ = 1980,
  OPT_mfp16_format_ = 1981,
  OPT_mfpu_ = 1982,
  OPT_mgeneral_regs_only = 1983,

  OPT_mlibarch_ = 1985,
  OPT_mlittle_endian = 1986,
  OPT_mlong_calls = 1987,
  OPT_mneon_for_64bits = 1988,
  OPT_mpic_data_is_text_relative = 1989,
  OPT_mpic_register_ = 1990,
  OPT_mpoke_function_name = 1991,
  OPT_mprint_tune_info = 1992,
  OPT_mpure_code = 1993,
  OPT_mrestrict_it = 1994,
  OPT_msched_prolog = 1995,
  OPT_msingle_pic_base = 1996,
  OPT_mslow_flash_data = 1997,

  OPT_mstack_protector_guard_offset_ = 1999,
  OPT_mstack_protector_guard_ = 2000,
  OPT_mstructure_size_boundary_ = 2001,
  OPT_mthumb = 2002,
  OPT_mthumb_interwork = 2003,
  OPT_mtls_dialect_ = 2004,
  OPT_mtp_ = 2005,
  OPT_mtpcs_frame = 2006,
  OPT_mtpcs_leaf_frame = 2007,
  OPT_mtune_ = 2008,
  OPT_munaligned_access = 2009,
  OPT_mvectorize_with_neon_double = 2010,
  OPT_mvectorize_with_neon_quad = 2011,
  OPT_mverbose_cost_dump = 2012,
  OPT_mword_relocations = 2013,
  OPT_n = 2014,
  OPT_name_sort = 2015,
  OPT_no_canonical_prefixes = 2016,
  OPT_no_integrated_cpp = 2017,
  OPT_no_pie = 2018,
  OPT_nocpp = 2019,
  OPT_nodefaultlibs = 2020,
  OPT_nolibc = 2021,
  OPT_nophoboslib = 2022,
  OPT_nostartfiles = 2023,
  OPT_nostdinc = 2024,
  OPT_nostdinc__ = 2025,
  OPT_nostdlib = 2026,
  OPT_nostdlib__ = 2027,
  OPT_o = 2028,
  OPT_objects = 2029,
  OPT_p = 2030,
  OPT_pass_exit_codes = 2031,

  OPT_pedantic_errors = 2033,
  OPT_pg = 2034,
  OPT_pie = 2035,
  OPT_pipe = 2036,
  OPT_print_file_name_ = 2037,
  OPT_print_libgcc_file_name = 2038,
  OPT_print_multi_directory = 2039,
  OPT_print_multi_lib = 2040,
  OPT_print_multi_os_directory = 2041,
  OPT_print_multiarch = 2042,
  OPT_print_objc_runtime_info = 2043,
  OPT_print_prog_name_ = 2044,
  OPT_print_search_dirs = 2045,
  OPT_print_sysroot = 2046,
  OPT_print_sysroot_headers_suffix = 2047,
  OPT_print_value = 2048,
  OPT_quiet = 2049,
  OPT_r = 2050,
  OPT_remap = 2051,
  OPT_reverse_sort = 2052,
  OPT_s = 2053,
  OPT_save_temps = 2054,
  OPT_save_temps_ = 2055,
  OPT_shared = 2056,
  OPT_shared_libgcc = 2057,
  OPT_shared_libphobos = 2058,
  OPT_size_sort = 2059,

  OPT_specs_ = 2061,
  OPT_static = 2062,
  OPT_static_libasan = 2063,
  OPT_static_libgcc = 2064,
  OPT_static_libgfortran = 2065,
  OPT_static_libgm2 = 2066,
  OPT_static_libgo = 2067,
  OPT_static_libhwasan = 2068,
  OPT_static_liblsan = 2069,
  OPT_static_libmpx = 2070,
  OPT_static_libmpxwrappers = 2071,
  OPT_static_libphobos = 2072,
  OPT_static_libquadmath = 2073,
  OPT_static_libstdc__ = 2074,
  OPT_static_libtsan = 2075,
  OPT_static_libubsan = 2076,
  OPT_static_pie = 2077,


  OPT_std_c__11 = 2080,
  OPT_std_c__14 = 2081,
  OPT_std_c__17 = 2082,


  OPT_std_c__20 = 2085,
  OPT_std_c__23 = 2086,
  OPT_std_c__26 = 2087,



  OPT_std_c__98 = 2091,
  OPT_std_c11 = 2092,
  OPT_std_c17 = 2093,


  OPT_std_c23 = 2096,


  OPT_std_c90 = 2099,
  OPT_std_c99 = 2100,

  OPT_std_f2003 = 2102,
  OPT_std_f2008 = 2103,
  OPT_std_f2008ts = 2104,
  OPT_std_f2018 = 2105,
  OPT_std_f2023 = 2106,
  OPT_std_f95 = 2107,
  OPT_std_gnu = 2108,


  OPT_std_gnu__11 = 2111,
  OPT_std_gnu__14 = 2112,
  OPT_std_gnu__17 = 2113,


  OPT_std_gnu__20 = 2116,
  OPT_std_gnu__23 = 2117,
  OPT_std_gnu__26 = 2118,



  OPT_std_gnu__98 = 2122,
  OPT_std_gnu11 = 2123,
  OPT_std_gnu17 = 2124,


  OPT_std_gnu23 = 2127,


  OPT_std_gnu90 = 2130,
  OPT_std_gnu99 = 2131,


  OPT_std_iso9899_199409 = 2134,






  OPT_std_legacy = 2141,
  OPT_stdlib_ = 2142,
  OPT_symbol_ = 2143,
  OPT_symbolic = 2144,
  OPT_t = 2145,
  OPT_time = 2146,
  OPT_time_ = 2147,
  OPT_traditional = 2148,
  OPT_traditional_cpp = 2149,
  OPT_tree_stats = 2150,
  OPT_trigraphs = 2151,
  OPT_type_stats = 2152,
  OPT_u = 2153,
  OPT_undef = 2154,
  OPT_v = 2155,
  OPT_version = 2156,
  OPT_w = 2157,
  OPT_wrapper = 2158,
  OPT_x = 2159,
  OPT_z = 2160,
  N_OPTS,
  OPT_SPECIAL_unknown,
  OPT_SPECIAL_ignore,
  OPT_SPECIAL_warn_removed,
  OPT_SPECIAL_program_name,
  OPT_SPECIAL_input_file
};
# 21 "/tool/lib/gcc/arm-none-eabi/14.2.1/plugin/include/tm.h" 2
# 1 "/tool/lib/gcc/arm-none-eabi/14.2.1/plugin/include/insn-constants.h" 1
# 35 "/tool/lib/gcc/arm-none-eabi/14.2.1/plugin/include/insn-constants.h"
enum unspec {
  UNSPEC_PUSH_MULT = 0,
  UNSPEC_PIC_SYM = 1,
  UNSPEC_PIC_BASE = 2,
  UNSPEC_PRLG_STK = 3,
  UNSPEC_REGISTER_USE = 4,
  UNSPEC_CHECK_ARCH = 5,
  UNSPEC_WSHUFH = 6,
  UNSPEC_WACC = 7,
  UNSPEC_TMOVMSK = 8,
  UNSPEC_WSAD = 9,
  UNSPEC_WSADZ = 10,
  UNSPEC_WMACS = 11,
  UNSPEC_WMACU = 12,
  UNSPEC_WMACSZ = 13,
  UNSPEC_WMACUZ = 14,
  UNSPEC_CLRDI = 15,
  UNSPEC_WALIGNI = 16,
  UNSPEC_TLS = 17,
  UNSPEC_PIC_LABEL = 18,
  UNSPEC_PIC_OFFSET = 19,
  UNSPEC_GOTSYM_OFF = 20,
  UNSPEC_THUMB1_CASESI = 21,
  UNSPEC_RBIT = 22,
  UNSPEC_SYMBOL_OFFSET = 23,
  UNSPEC_MEMORY_BARRIER = 24,
  UNSPEC_UNALIGNED_LOAD = 25,
  UNSPEC_UNALIGNED_STORE = 26,
  UNSPEC_PIC_UNIFIED = 27,
  UNSPEC_Q_SET = 28,
  UNSPEC_GE_SET = 29,
  UNSPEC_APSR_READ = 30,
  UNSPEC_LL = 31,
  UNSPEC_VRINTZ = 32,
  UNSPEC_VRINTP = 33,
  UNSPEC_VRINTM = 34,
  UNSPEC_VRINTR = 35,
  UNSPEC_VRINTX = 36,
  UNSPEC_VRINTA = 37,
  UNSPEC_PROBE_STACK = 38,
  UNSPEC_NONSECURE_MEM = 39,
  UNSPEC_SP_SET = 40,
  UNSPEC_SP_TEST = 41,
  UNSPEC_PIC_RESTORE = 42,
  UNSPEC_SXTAB16 = 43,
  UNSPEC_UXTAB16 = 44,
  UNSPEC_SXTB16 = 45,
  UNSPEC_UXTB16 = 46,
  UNSPEC_QADD8 = 47,
  UNSPEC_QSUB8 = 48,
  UNSPEC_SHADD8 = 49,
  UNSPEC_SHSUB8 = 50,
  UNSPEC_UHADD8 = 51,
  UNSPEC_UHSUB8 = 52,
  UNSPEC_UQADD8 = 53,
  UNSPEC_UQSUB8 = 54,
  UNSPEC_QADD16 = 55,
  UNSPEC_QASX = 56,
  UNSPEC_QSAX = 57,
  UNSPEC_QSUB16 = 58,
  UNSPEC_SHADD16 = 59,
  UNSPEC_SHASX = 60,
  UNSPEC_SHSAX = 61,
  UNSPEC_SHSUB16 = 62,
  UNSPEC_UHADD16 = 63,
  UNSPEC_UHASX = 64,
  UNSPEC_UHSAX = 65,
  UNSPEC_UHSUB16 = 66,
  UNSPEC_UQADD16 = 67,
  UNSPEC_UQASX = 68,
  UNSPEC_UQSAX = 69,
  UNSPEC_UQSUB16 = 70,
  UNSPEC_SMUSD = 71,
  UNSPEC_SMUSDX = 72,
  UNSPEC_USAD8 = 73,
  UNSPEC_USADA8 = 74,
  UNSPEC_SMLALD = 75,
  UNSPEC_SMLALDX = 76,
  UNSPEC_SMLSLD = 77,
  UNSPEC_SMLSLDX = 78,
  UNSPEC_SMLAWB = 79,
  UNSPEC_SMLAWT = 80,
  UNSPEC_SEL = 81,
  UNSPEC_SADD8 = 82,
  UNSPEC_SSUB8 = 83,
  UNSPEC_UADD8 = 84,
  UNSPEC_USUB8 = 85,
  UNSPEC_SADD16 = 86,
  UNSPEC_SASX = 87,
  UNSPEC_SSAX = 88,
  UNSPEC_SSUB16 = 89,
  UNSPEC_UADD16 = 90,
  UNSPEC_UASX = 91,
  UNSPEC_USAX = 92,
  UNSPEC_USUB16 = 93,
  UNSPEC_SMLAD = 94,
  UNSPEC_SMLADX = 95,
  UNSPEC_SMLSD = 96,
  UNSPEC_SMLSDX = 97,
  UNSPEC_SMUAD = 98,
  UNSPEC_SMUADX = 99,
  UNSPEC_SSAT16 = 100,
  UNSPEC_USAT16 = 101,
  UNSPEC_CDE = 102,
  UNSPEC_CDEA = 103,
  UNSPEC_VCDE = 104,
  UNSPEC_VCDEA = 105,
  UNSPEC_DLS = 106,
  UNSPEC_PAC_NOP = 107,
  UNSPEC_WADDC = 108,
  UNSPEC_WABS = 109,
  UNSPEC_WQMULWMR = 110,
  UNSPEC_WQMULMR = 111,
  UNSPEC_WQMULWM = 112,
  UNSPEC_WQMULM = 113,
  UNSPEC_WQMIAxyn = 114,
  UNSPEC_WQMIAxy = 115,
  UNSPEC_TANDC = 116,
  UNSPEC_TORC = 117,
  UNSPEC_TORVSC = 118,
  UNSPEC_TEXTRC = 119,
  UNSPEC_GET_FPSCR_NZCVQC = 120,
  UNSPEC_ASHIFT_SIGNED = 121,
  UNSPEC_ASHIFT_UNSIGNED = 122,
  UNSPEC_CRC32B = 123,
  UNSPEC_CRC32H = 124,
  UNSPEC_CRC32W = 125,
  UNSPEC_CRC32CB = 126,
  UNSPEC_CRC32CH = 127,
  UNSPEC_CRC32CW = 128,
  UNSPEC_AESD = 129,
  UNSPEC_AESE = 130,
  UNSPEC_AESIMC = 131,
  UNSPEC_AESMC = 132,
  UNSPEC_AES_PROTECT = 133,
  UNSPEC_SHA1C = 134,
  UNSPEC_SHA1M = 135,
  UNSPEC_SHA1P = 136,
  UNSPEC_SHA1H = 137,
  UNSPEC_SHA1SU0 = 138,
  UNSPEC_SHA1SU1 = 139,
  UNSPEC_SHA256H = 140,
  UNSPEC_SHA256H2 = 141,
  UNSPEC_SHA256SU0 = 142,
  UNSPEC_SHA256SU1 = 143,
  UNSPEC_VMULLP64 = 144,
  UNSPEC_LOAD_COUNT = 145,
  UNSPEC_VABAL_S = 146,
  UNSPEC_VABAL_U = 147,
  UNSPEC_VABD_F = 148,
  UNSPEC_VABD_S = 149,
  UNSPEC_VABD_U = 150,
  UNSPEC_VABDL_S = 151,
  UNSPEC_VABDL_U = 152,
  UNSPEC_VADD = 153,
  UNSPEC_VADDHN = 154,
  UNSPEC_VRADDHN = 155,
  UNSPEC_VADDL_S = 156,
  UNSPEC_VADDL_U = 157,
  UNSPEC_VADDW_S = 158,
  UNSPEC_VADDW_U = 159,
  UNSPEC_VBSL = 160,
  UNSPEC_VCAGE = 161,
  UNSPEC_VCAGT = 162,
  UNSPEC_VCALE = 163,
  UNSPEC_VCALT = 164,
  UNSPEC_VCEQ = 165,
  UNSPEC_VCGE = 166,
  UNSPEC_VCGEU = 167,
  UNSPEC_VCGT = 168,
  UNSPEC_VCGTU = 169,
  UNSPEC_VCLS = 170,
  UNSPEC_VCONCAT = 171,
  UNSPEC_VCVT = 172,
  UNSPEC_VCVT_S = 173,
  UNSPEC_VCVT_U = 174,
  UNSPEC_VCVT_S_N = 175,
  UNSPEC_VCVT_U_N = 176,
  UNSPEC_VCVT_HF_S_N = 177,
  UNSPEC_VCVT_HF_U_N = 178,
  UNSPEC_VCVT_SI_S_N = 179,
  UNSPEC_VCVT_SI_U_N = 180,
  UNSPEC_VCVTH_S = 181,
  UNSPEC_VCVTH_U = 182,
  UNSPEC_VCVTA_S = 183,
  UNSPEC_VCVTA_U = 184,
  UNSPEC_VCVTM_S = 185,
  UNSPEC_VCVTM_U = 186,
  UNSPEC_VCVTN_S = 187,
  UNSPEC_VCVTN_U = 188,
  UNSPEC_VCVTP_S = 189,
  UNSPEC_VCVTP_U = 190,
  UNSPEC_VEXT = 191,
  UNSPEC_VHADD_S = 192,
  UNSPEC_VHADD_U = 193,
  UNSPEC_VRHADD_S = 194,
  UNSPEC_VRHADD_U = 195,
  UNSPEC_VHSUB_S = 196,
  UNSPEC_VHSUB_U = 197,
  UNSPEC_VLD1 = 198,
  UNSPEC_VLD1X3A = 199,
  UNSPEC_VLD1X3B = 200,
  UNSPEC_VLD1X4A = 201,
  UNSPEC_VLD1X4B = 202,
  UNSPEC_VLD1_LANE = 203,
  UNSPEC_VLD2 = 204,
  UNSPEC_VLD2_DUP = 205,
  UNSPEC_VLD2_LANE = 206,
  UNSPEC_VLD3 = 207,
  UNSPEC_VLD3A = 208,
  UNSPEC_VLD3B = 209,
  UNSPEC_VLD3_DUP = 210,
  UNSPEC_VLD3_LANE = 211,
  UNSPEC_VLD4 = 212,
  UNSPEC_VLD4A = 213,
  UNSPEC_VLD4B = 214,
  UNSPEC_VLD4_DUP = 215,
  UNSPEC_VLD4_LANE = 216,
  UNSPEC_VMAX = 217,
  UNSPEC_VMAX_U = 218,
  UNSPEC_VMAXNM = 219,
  UNSPEC_VMIN = 220,
  UNSPEC_VMIN_U = 221,
  UNSPEC_VMINNM = 222,
  UNSPEC_VMLA = 223,
  UNSPEC_VMLA_LANE = 224,
  UNSPEC_VMLAL_S = 225,
  UNSPEC_VMLAL_U = 226,
  UNSPEC_VMLAL_S_LANE = 227,
  UNSPEC_VMLAL_U_LANE = 228,
  UNSPEC_VMLS = 229,
  UNSPEC_VMLS_LANE = 230,
  UNSPEC_VMLSL_S = 231,
  UNSPEC_VMLSL_U = 232,
  UNSPEC_VMLSL_S_LANE = 233,
  UNSPEC_VMLSL_U_LANE = 234,
  UNSPEC_VMLSL_LANE = 235,
  UNSPEC_VFMA_LANE = 236,
  UNSPEC_VFMS_LANE = 237,
  UNSPEC_VMOVL_S = 238,
  UNSPEC_VMOVL_U = 239,
  UNSPEC_VMOVN = 240,
  UNSPEC_VMUL = 241,
  UNSPEC_VMULL_P = 242,
  UNSPEC_VMULL_S = 243,
  UNSPEC_VMULL_U = 244,
  UNSPEC_VMUL_LANE = 245,
  UNSPEC_VMULL_S_LANE = 246,
  UNSPEC_VMULL_U_LANE = 247,
  UNSPEC_VPADAL_S = 248,
  UNSPEC_VPADAL_U = 249,
  UNSPEC_VPADD = 250,
  UNSPEC_VPADDL_S = 251,
  UNSPEC_VPADDL_U = 252,
  UNSPEC_VPMAX = 253,
  UNSPEC_VPMAX_U = 254,
  UNSPEC_VPMIN = 255,
  UNSPEC_VPMIN_U = 256,
  UNSPEC_VPSMAX = 257,
  UNSPEC_VPSMIN = 258,
  UNSPEC_VPUMAX = 259,
  UNSPEC_VPUMIN = 260,
  UNSPEC_VQABS = 261,
  UNSPEC_VQADD_S = 262,
  UNSPEC_VQADD_U = 263,
  UNSPEC_VQDMLAL = 264,
  UNSPEC_VQDMLAL_LANE = 265,
  UNSPEC_VQDMLSL = 266,
  UNSPEC_VQDMLSL_LANE = 267,
  UNSPEC_VQDMULH = 268,
  UNSPEC_VQDMULH_LANE = 269,
  UNSPEC_VQRDMULH = 270,
  UNSPEC_VQRDMULH_LANE = 271,
  UNSPEC_VQDMULL = 272,
  UNSPEC_VQDMULL_LANE = 273,
  UNSPEC_VQMOVN_S = 274,
  UNSPEC_VQMOVN_U = 275,
  UNSPEC_VQMOVUN = 276,
  UNSPEC_VQNEG = 277,
  UNSPEC_VQSHL_S = 278,
  UNSPEC_VQSHL_U = 279,
  UNSPEC_VQRSHL_S = 280,
  UNSPEC_VQRSHL_U = 281,
  UNSPEC_VQSHL_S_N = 282,
  UNSPEC_VQSHL_U_N = 283,
  UNSPEC_VQSHLU_N = 284,
  UNSPEC_VQSHRN_S_N = 285,
  UNSPEC_VQSHRN_U_N = 286,
  UNSPEC_VQRSHRN_S_N = 287,
  UNSPEC_VQRSHRN_U_N = 288,
  UNSPEC_VQSHRUN_N = 289,
  UNSPEC_VQRSHRUN_N = 290,
  UNSPEC_VQSUB_S = 291,
  UNSPEC_VQSUB_U = 292,
  UNSPEC_VRECPE = 293,
  UNSPEC_VRECPS = 294,
  UNSPEC_VREV16 = 295,
  UNSPEC_VREV32 = 296,
  UNSPEC_VREV64 = 297,
  UNSPEC_VRSQRTE = 298,
  UNSPEC_VRSQRTS = 299,
  UNSPEC_VSHL_S = 300,
  UNSPEC_VSHL_U = 301,
  UNSPEC_VRSHL_S = 302,
  UNSPEC_VRSHL_U = 303,
  UNSPEC_VSHLL_S_N = 304,
  UNSPEC_VSHLL_U_N = 305,
  UNSPEC_VSHL_N = 306,
  UNSPEC_VSHR_S_N = 307,
  UNSPEC_VSHR_U_N = 308,
  UNSPEC_VRSHR_S_N = 309,
  UNSPEC_VRSHR_U_N = 310,
  UNSPEC_VSHRN_N = 311,
  UNSPEC_VRSHRN_N = 312,
  UNSPEC_VSLI = 313,
  UNSPEC_VSRA_S_N = 314,
  UNSPEC_VSRA_U_N = 315,
  UNSPEC_VRSRA_S_N = 316,
  UNSPEC_VRSRA_U_N = 317,
  UNSPEC_VSRI = 318,
  UNSPEC_VST1 = 319,
  UNSPEC_VST1X3A = 320,
  UNSPEC_VST1X3B = 321,
  UNSPEC_VST1X4A = 322,
  UNSPEC_VST1X4B = 323,
  UNSPEC_VST1_LANE = 324,
  UNSPEC_VST2 = 325,
  UNSPEC_VST2_LANE = 326,
  UNSPEC_VST3 = 327,
  UNSPEC_VST3A = 328,
  UNSPEC_VST3B = 329,
  UNSPEC_VST3_LANE = 330,
  UNSPEC_VST4 = 331,
  UNSPEC_VST4A = 332,
  UNSPEC_VST4B = 333,
  UNSPEC_VST4_LANE = 334,
  UNSPEC_VSTRUCTDUMMY = 335,
  UNSPEC_VSUB = 336,
  UNSPEC_VSUBHN = 337,
  UNSPEC_VRSUBHN = 338,
  UNSPEC_VSUBL_S = 339,
  UNSPEC_VSUBL_U = 340,
  UNSPEC_VSUBW_S = 341,
  UNSPEC_VSUBW_U = 342,
  UNSPEC_VTBL = 343,
  UNSPEC_VTBX = 344,
  UNSPEC_VTRN1 = 345,
  UNSPEC_VTRN2 = 346,
  UNSPEC_VTST = 347,
  UNSPEC_VUZP1 = 348,
  UNSPEC_VUZP2 = 349,
  UNSPEC_VZIP1 = 350,
  UNSPEC_VZIP2 = 351,
  UNSPEC_MISALIGNED_ACCESS = 352,
  UNSPEC_VCLE = 353,
  UNSPEC_VCLT = 354,
  UNSPEC_NVRINTZ = 355,
  UNSPEC_NVRINTP = 356,
  UNSPEC_NVRINTM = 357,
  UNSPEC_NVRINTX = 358,
  UNSPEC_NVRINTA = 359,
  UNSPEC_NVRINTN = 360,
  UNSPEC_VQRDMLAH = 361,
  UNSPEC_VQRDMLSH = 362,
  UNSPEC_VRND = 363,
  UNSPEC_VRNDA = 364,
  UNSPEC_VRNDI = 365,
  UNSPEC_VRNDM = 366,
  UNSPEC_VRNDN = 367,
  UNSPEC_VRNDP = 368,
  UNSPEC_VRNDX = 369,
  UNSPEC_DOT_S = 370,
  UNSPEC_DOT_U = 371,
  UNSPEC_DOT_US = 372,
  UNSPEC_DOT_SU = 373,
  UNSPEC_VFML_LO = 374,
  UNSPEC_VFML_HI = 375,
  UNSPEC_VCADD90 = 376,
  UNSPEC_VCADD270 = 377,
  UNSPEC_VCMLA = 378,
  UNSPEC_VCMLA90 = 379,
  UNSPEC_VCMLA180 = 380,
  UNSPEC_VCMLA270 = 381,
  UNSPEC_VCMLA_CONJ = 382,
  UNSPEC_VCMLA180_CONJ = 383,
  UNSPEC_VCMUL = 384,
  UNSPEC_VCMUL90 = 385,
  UNSPEC_VCMUL180 = 386,
  UNSPEC_VCMUL270 = 387,
  UNSPEC_VCMUL_CONJ = 388,
  UNSPEC_MATMUL_S = 389,
  UNSPEC_MATMUL_U = 390,
  UNSPEC_MATMUL_US = 391,
  UNSPEC_BFCVT = 392,
  UNSPEC_BFCVT_HIGH = 393,
  UNSPEC_BFMMLA = 394,
  UNSPEC_BFMAB = 395,
  UNSPEC_BFMAT = 396,
  VST4Q = 397,
  VRNDXQ_F = 398,
  VRNDQ_F = 399,
  VRNDPQ_F = 400,
  VRNDNQ_F = 401,
  VRNDMQ_F = 402,
  VRNDAQ_F = 403,
  VREV64Q_F = 404,
  VDUPQ_N_F = 405,
  VREV32Q_F = 406,
  VCVTTQ_F32_F16 = 407,
  VCVTBQ_F32_F16 = 408,
  VCVTQ_TO_F_S = 409,
  VQNEGQ_S = 410,
  VCVTQ_TO_F_U = 411,
  VREV16Q_S = 412,
  VREV16Q_U = 413,
  VADDLVQ_S = 414,
  VMVNQ_N_S = 415,
  VMVNQ_N_U = 416,
  VCVTAQ_S = 417,
  VCVTAQ_U = 418,
  VREV64Q_S = 419,
  VREV64Q_U = 420,
  VQABSQ_S = 421,
  VDUPQ_N_U = 422,
  VDUPQ_N_S = 423,
  VCLSQ_S = 424,
  VADDVQ_S = 425,
  VADDVQ_U = 426,
  VREV32Q_U = 427,
  VREV32Q_S = 428,
  VMOVLTQ_U = 429,
  VMOVLTQ_S = 430,
  VMOVLBQ_S = 431,
  VMOVLBQ_U = 432,
  VCVTQ_FROM_F_S = 433,
  VCVTQ_FROM_F_U = 434,
  VCVTPQ_S = 435,
  VCVTPQ_U = 436,
  VCVTNQ_S = 437,
  VCVTNQ_U = 438,
  VCVTMQ_S = 439,
  VCVTMQ_U = 440,
  VADDLVQ_U = 441,
  VCTP = 442,
  VCTP_M = 443,
  LETP8 = 444,
  LETP16 = 445,
  LETP32 = 446,
  LETP64 = 447,
  VPNOT = 448,
  VCREATEQ_F = 449,
  VCVTQ_N_TO_F_S = 450,
  VCVTQ_N_TO_F_U = 451,
  VBRSRQ_N_F = 452,
  VSUBQ_N_F = 453,
  VCREATEQ_U = 454,
  VCREATEQ_S = 455,
  VSHRQ_N_S = 456,
  VSHRQ_N_U = 457,
  VCVTQ_N_FROM_F_S = 458,
  VCVTQ_N_FROM_F_U = 459,
  VADDLVQ_P_S = 460,
  VADDLVQ_P_U = 461,
  VSHLQ_S = 462,
  VSHLQ_U = 463,
  VABDQ_S = 464,
  VADDQ_N_S = 465,
  VADDVAQ_S = 466,
  VADDVQ_P_S = 467,
  VBRSRQ_N_S = 468,
  VHADDQ_S = 469,
  VHADDQ_N_S = 470,
  VHSUBQ_S = 471,
  VHSUBQ_N_S = 472,
  VMAXQ_S = 473,
  VMAXVQ_S = 474,
  VMINQ_S = 475,
  VMINVQ_S = 476,
  VMLADAVQ_S = 477,
  VMULHQ_S = 478,
  VMULLBQ_INT_S = 479,
  VMULLTQ_INT_S = 480,
  VMULQ_S = 481,
  VMULQ_N_S = 482,
  VQADDQ_S = 483,
  VQADDQ_N_S = 484,
  VQRSHLQ_S = 485,
  VQRSHLQ_N_S = 486,
  VQSHLQ_S = 487,
  VQSHLQ_N_S = 488,
  VQSHLQ_R_S = 489,
  VQSUBQ_S = 490,
  VQSUBQ_N_S = 491,
  VRHADDQ_S = 492,
  VRMULHQ_S = 493,
  VRSHLQ_S = 494,
  VRSHLQ_N_S = 495,
  VRSHRQ_N_S = 496,
  VSHLQ_N_S = 497,
  VSHLQ_R_S = 498,
  VSUBQ_S = 499,
  VSUBQ_N_S = 500,
  VABDQ_U = 501,
  VADDQ_N_U = 502,
  VADDVAQ_U = 503,
  VADDVQ_P_U = 504,
  VBRSRQ_N_U = 505,
  VHADDQ_U = 506,
  VHADDQ_N_U = 507,
  VHSUBQ_U = 508,
  VHSUBQ_N_U = 509,
  VMAXQ_U = 510,
  VMAXVQ_U = 511,
  VMINQ_U = 512,
  VMINVQ_U = 513,
  VMLADAVQ_U = 514,
  VMULHQ_U = 515,
  VMULLBQ_INT_U = 516,
  VMULLTQ_INT_U = 517,
  VMULQ_U = 518,
  VMULQ_N_U = 519,
  VQADDQ_U = 520,
  VQADDQ_N_U = 521,
  VQRSHLQ_U = 522,
  VQRSHLQ_N_U = 523,
  VQSHLQ_U = 524,
  VQSHLQ_N_U = 525,
  VQSHLQ_R_U = 526,
  VQSUBQ_U = 527,
  VQSUBQ_N_U = 528,
  VRHADDQ_U = 529,
  VRMULHQ_U = 530,
  VRSHLQ_U = 531,
  VRSHLQ_N_U = 532,
  VRSHRQ_N_U = 533,
  VSHLQ_N_U = 534,
  VSHLQ_R_U = 535,
  VSUBQ_U = 536,
  VSUBQ_N_U = 537,
  VHCADDQ_ROT270_S = 538,
  VHCADDQ_ROT90_S = 539,
  VMAXAQ_S = 540,
  VMAXAVQ_S = 541,
  VMINAQ_S = 542,
  VMINAVQ_S = 543,
  VMLADAVXQ_S = 544,
  VMLSDAVQ_S = 545,
  VMLSDAVXQ_S = 546,
  VQDMULHQ_N_S = 547,
  VQDMULHQ_S = 548,
  VQRDMULHQ_N_S = 549,
  VQRDMULHQ_S = 550,
  VQSHLUQ_N_S = 551,
  VABDQ_M_S = 552,
  VABDQ_M_U = 553,
  VABDQ_F = 554,
  VADDQ_N_F = 555,
  VMAXNMAQ_F = 556,
  VMAXNMAVQ_F = 557,
  VMAXNMQ_F = 558,
  VMAXNMVQ_F = 559,
  VMINNMAQ_F = 560,
  VMINNMAVQ_F = 561,
  VMINNMQ_F = 562,
  VMINNMVQ_F = 563,
  VMULQ_F = 564,
  VMULQ_N_F = 565,
  VSUBQ_F = 566,
  VADDLVAQ_U = 567,
  VADDLVAQ_S = 568,
  VBICQ_N_U = 569,
  VBICQ_N_S = 570,
  VCVTBQ_F16_F32 = 571,
  VCVTTQ_F16_F32 = 572,
  VMLALDAVQ_U = 573,
  VMLALDAVXQ_S = 574,
  VMLALDAVQ_S = 575,
  VMLSLDAVQ_S = 576,
  VMLSLDAVXQ_S = 577,
  VMOVNBQ_U = 578,
  VMOVNBQ_S = 579,
  VMOVNTQ_U = 580,
  VMOVNTQ_S = 581,
  VORRQ_N_S = 582,
  VORRQ_N_U = 583,
  VQDMULLBQ_N_S = 584,
  VQDMULLBQ_S = 585,
  VQDMULLTQ_N_S = 586,
  VQDMULLTQ_S = 587,
  VQMOVNBQ_U = 588,
  VQMOVNBQ_S = 589,
  VQMOVUNBQ_S = 590,
  VQMOVUNTQ_S = 591,
  VRMLALDAVHXQ_S = 592,
  VRMLSLDAVHQ_S = 593,
  VRMLSLDAVHXQ_S = 594,
  VSHLLBQ_S = 595,
  VSHLLBQ_U = 596,
  VSHLLTQ_U = 597,
  VSHLLTQ_S = 598,
  VQMOVNTQ_U = 599,
  VQMOVNTQ_S = 600,
  VSHLLBQ_N_S = 601,
  VSHLLBQ_N_U = 602,
  VSHLLTQ_N_U = 603,
  VSHLLTQ_N_S = 604,
  VRMLALDAVHQ_U = 605,
  VRMLALDAVHQ_S = 606,
  VMULLTQ_POLY_P = 607,
  VMULLBQ_POLY_P = 608,
  VBICQ_M_N_S = 609,
  VBICQ_M_N_U = 610,
  VCMPEQQ_M_F = 611,
  VCVTAQ_M_S = 612,
  VCVTAQ_M_U = 613,
  VCVTQ_M_TO_F_S = 614,
  VCVTQ_M_TO_F_U = 615,
  VQRSHRNBQ_N_U = 616,
  VQRSHRNBQ_N_S = 617,
  VQRSHRUNBQ_N_S = 618,
  VRMLALDAVHAQ_S = 619,
  VABAVQ_S = 620,
  VABAVQ_U = 621,
  VSHLCQ_S = 622,
  VSHLCQ_U = 623,
  VRMLALDAVHAQ_U = 624,
  VABSQ_M_S = 625,
  VADDVAQ_P_S = 626,
  VADDVAQ_P_U = 627,
  VCLSQ_M_S = 628,
  VCLZQ_M_S = 629,
  VCLZQ_M_U = 630,
  VCMPCSQ_M_N_U = 631,
  VCMPCSQ_M_U = 632,
  VCMPEQQ_M_N_S = 633,
  VCMPEQQ_M_N_U = 634,
  VCMPEQQ_M_S = 635,
  VCMPEQQ_M_U = 636,
  VCMPGEQ_M_N_S = 637,
  VCMPGEQ_M_S = 638,
  VCMPGTQ_M_N_S = 639,
  VCMPGTQ_M_S = 640,
  VCMPHIQ_M_N_U = 641,
  VCMPHIQ_M_U = 642,
  VCMPLEQ_M_N_S = 643,
  VCMPLEQ_M_S = 644,
  VCMPLTQ_M_N_S = 645,
  VCMPLTQ_M_S = 646,
  VCMPNEQ_M_N_S = 647,
  VCMPNEQ_M_N_U = 648,
  VCMPNEQ_M_S = 649,
  VCMPNEQ_M_U = 650,
  VDUPQ_M_N_S = 651,
  VDUPQ_M_N_U = 652,
  VDWDUPQ_N_U = 653,
  VDWDUPQ_WB_U = 654,
  VIWDUPQ_N_U = 655,
  VIWDUPQ_WB_U = 656,
  VMAXAQ_M_S = 657,
  VMAXAVQ_P_S = 658,
  VMAXVQ_P_S = 659,
  VMAXVQ_P_U = 660,
  VMINAQ_M_S = 661,
  VMINAVQ_P_S = 662,
  VMINVQ_P_S = 663,
  VMINVQ_P_U = 664,
  VMLADAVAQ_S = 665,
  VMLADAVAQ_U = 666,
  VMLADAVQ_P_S = 667,
  VMLADAVQ_P_U = 668,
  VMLADAVXQ_P_S = 669,
  VMLAQ_N_S = 670,
  VMLAQ_N_U = 671,
  VMLASQ_N_S = 672,
  VMLASQ_N_U = 673,
  VMLSDAVQ_P_S = 674,
  VMLSDAVXQ_P_S = 675,
  VMVNQ_M_S = 676,
  VMVNQ_M_U = 677,
  VNEGQ_M_S = 678,
  VPSELQ_S = 679,
  VPSELQ_U = 680,
  VQABSQ_M_S = 681,
  VQDMLAHQ_N_S = 682,
  VQDMLASHQ_N_S = 683,
  VQNEGQ_M_S = 684,
  VQRDMLADHQ_S = 685,
  VQRDMLADHXQ_S = 686,
  VQRDMLAHQ_N_S = 687,
  VQRDMLASHQ_N_S = 688,
  VQRDMLSDHQ_S = 689,
  VQRDMLSDHXQ_S = 690,
  VQRSHLQ_M_N_S = 691,
  VQRSHLQ_M_N_U = 692,
  VQSHLQ_M_R_S = 693,
  VQSHLQ_M_R_U = 694,
  VREV64Q_M_S = 695,
  VREV64Q_M_U = 696,
  VRSHLQ_M_N_S = 697,
  VRSHLQ_M_N_U = 698,
  VSHLQ_M_R_S = 699,
  VSHLQ_M_R_U = 700,
  VSLIQ_N_S = 701,
  VSLIQ_N_U = 702,
  VSRIQ_N_S = 703,
  VSRIQ_N_U = 704,
  VQDMLSDHXQ_S = 705,
  VQDMLSDHQ_S = 706,
  VQDMLADHXQ_S = 707,
  VQDMLADHQ_S = 708,
  VMLSDAVAXQ_S = 709,
  VMLSDAVAQ_S = 710,
  VMLADAVAXQ_S = 711,
  VCMPGEQ_M_F = 712,
  VCMPGTQ_M_N_F = 713,
  VMLSLDAVQ_P_S = 714,
  VRMLALDAVHAXQ_S = 715,
  VMLSLDAVXQ_P_S = 716,
  VFMAQ_F = 717,
  VMLSLDAVAQ_S = 718,
  VQSHRUNBQ_N_S = 719,
  VQRSHRUNTQ_N_S = 720,
  VMINNMAQ_M_F = 721,
  VFMASQ_N_F = 722,
  VDUPQ_M_N_F = 723,
  VCMPGTQ_M_F = 724,
  VCMPLTQ_M_F = 725,
  VRMLSLDAVHQ_P_S = 726,
  VQSHRUNTQ_N_S = 727,
  VABSQ_M_F = 728,
  VMAXNMAVQ_P_F = 729,
  VFMAQ_N_F = 730,
  VRMLSLDAVHXQ_P_S = 731,
  VREV32Q_M_F = 732,
  VRMLSLDAVHAQ_S = 733,
  VRMLSLDAVHAXQ_S = 734,
  VCMPLTQ_M_N_F = 735,
  VCMPNEQ_M_F = 736,
  VRNDAQ_M_F = 737,
  VRNDPQ_M_F = 738,
  VADDLVAQ_P_S = 739,
  VQMOVUNBQ_M_S = 740,
  VCMPLEQ_M_F = 741,
  VMLSLDAVAXQ_S = 742,
  VRNDXQ_M_F = 743,
  VFMSQ_F = 744,
  VMINNMVQ_P_F = 745,
  VMAXNMVQ_P_F = 746,
  VPSELQ_F = 747,
  VQMOVUNTQ_M_S = 748,
  VREV64Q_M_F = 749,
  VNEGQ_M_F = 750,
  VRNDMQ_M_F = 751,
  VCMPLEQ_M_N_F = 752,
  VCMPGEQ_M_N_F = 753,
  VRNDNQ_M_F = 754,
  VMINNMAVQ_P_F = 755,
  VCMPNEQ_M_N_F = 756,
  VRMLALDAVHQ_P_S = 757,
  VRMLALDAVHXQ_P_S = 758,
  VCMPEQQ_M_N_F = 759,
  VMAXNMAQ_M_F = 760,
  VRNDQ_M_F = 761,
  VMLALDAVQ_P_U = 762,
  VMLALDAVQ_P_S = 763,
  VQMOVNBQ_M_S = 764,
  VQMOVNBQ_M_U = 765,
  VMOVLTQ_M_U = 766,
  VMOVLTQ_M_S = 767,
  VMOVNBQ_M_U = 768,
  VMOVNBQ_M_S = 769,
  VRSHRNTQ_N_U = 770,
  VRSHRNTQ_N_S = 771,
  VORRQ_M_N_S = 772,
  VORRQ_M_N_U = 773,
  VREV32Q_M_S = 774,
  VREV32Q_M_U = 775,
  VQRSHRNTQ_N_U = 776,
  VQRSHRNTQ_N_S = 777,
  VMOVNTQ_M_U = 778,
  VMOVNTQ_M_S = 779,
  VMOVLBQ_M_U = 780,
  VMOVLBQ_M_S = 781,
  VMLALDAVAQ_S = 782,
  VMLALDAVAQ_U = 783,
  VQSHRNBQ_N_U = 784,
  VQSHRNBQ_N_S = 785,
  VSHRNBQ_N_U = 786,
  VSHRNBQ_N_S = 787,
  VRSHRNBQ_N_S = 788,
  VRSHRNBQ_N_U = 789,
  VMLALDAVXQ_P_S = 790,
  VQMOVNTQ_M_U = 791,
  VQMOVNTQ_M_S = 792,
  VMVNQ_M_N_U = 793,
  VMVNQ_M_N_S = 794,
  VQSHRNTQ_N_U = 795,
  VQSHRNTQ_N_S = 796,
  VMLALDAVAXQ_S = 797,
  VSHRNTQ_N_S = 798,
  VSHRNTQ_N_U = 799,
  VCVTBQ_M_F16_F32 = 800,
  VCVTBQ_M_F32_F16 = 801,
  VCVTTQ_M_F16_F32 = 802,
  VCVTTQ_M_F32_F16 = 803,
  VCVTMQ_M_S = 804,
  VCVTMQ_M_U = 805,
  VCVTNQ_M_S = 806,
  VCVTPQ_M_S = 807,
  VCVTPQ_M_U = 808,
  VCVTQ_M_N_FROM_F_S = 809,
  VCVTNQ_M_U = 810,
  VREV16Q_M_S = 811,
  VREV16Q_M_U = 812,
  VREV32Q_M = 813,
  VCVTQ_M_FROM_F_U = 814,
  VCVTQ_M_FROM_F_S = 815,
  VRMLALDAVHQ_P_U = 816,
  VADDLVAQ_P_U = 817,
  VCVTQ_M_N_FROM_F_U = 818,
  VQSHLUQ_M_N_S = 819,
  VABAVQ_P_S = 820,
  VABAVQ_P_U = 821,
  VSHLQ_M_S = 822,
  VSHLQ_M_U = 823,
  VSRIQ_M_N_S = 824,
  VSRIQ_M_N_U = 825,
  VSUBQ_M_U = 826,
  VSUBQ_M_S = 827,
  VCVTQ_M_N_TO_F_U = 828,
  VCVTQ_M_N_TO_F_S = 829,
  VQADDQ_M_U = 830,
  VQADDQ_M_S = 831,
  VRSHRQ_M_N_S = 832,
  VSUBQ_M_N_S = 833,
  VSUBQ_M_N_U = 834,
  VBRSRQ_M_N_S = 835,
  VSUBQ_M_N_F = 836,
  VBICQ_M_F = 837,
  VHADDQ_M_U = 838,
  VBICQ_M_U = 839,
  VBICQ_M_S = 840,
  VMULQ_M_N_U = 841,
  VHADDQ_M_S = 842,
  VORNQ_M_F = 843,
  VMLAQ_M_N_S = 844,
  VQSUBQ_M_U = 845,
  VQSUBQ_M_S = 846,
  VMLAQ_M_N_U = 847,
  VQSUBQ_M_N_U = 848,
  VQSUBQ_M_N_S = 849,
  VMULLTQ_INT_M_S = 850,
  VMULLTQ_INT_M_U = 851,
  VMULQ_M_N_S = 852,
  VMULQ_M_N_F = 853,
  VMLASQ_M_N_U = 854,
  VMLASQ_M_N_S = 855,
  VMAXQ_M_U = 856,
  VQRDMLAHQ_M_N_U = 857,
  VCADDQ_ROT270_M_F = 858,
  VCADDQ_ROT270_M = 859,
  VQRSHLQ_M_S = 860,
  VMULQ_M_F = 861,
  VRHADDQ_M_U = 862,
  VSHRQ_M_N_U = 863,
  VRHADDQ_M_S = 864,
  VMULQ_M_S = 865,
  VMULQ_M_U = 866,
  VQDMLASHQ_M_N_S = 867,
  VQRDMLASHQ_M_N_S = 868,
  VRSHLQ_M_S = 869,
  VRSHLQ_M_U = 870,
  VRSHRQ_M_N_U = 871,
  VADDQ_M_N_F = 872,
  VADDQ_M_N_S = 873,
  VADDQ_M_N_U = 874,
  VQRDMLASHQ_M_N_U = 875,
  VMAXQ_M_S = 876,
  VQRDMLAHQ_M_N_S = 877,
  VORRQ_M_S = 878,
  VORRQ_M_U = 879,
  VORRQ_M_F = 880,
  VQRSHLQ_M_U = 881,
  VRMULHQ_M_U = 882,
  VRMULHQ_M_S = 883,
  VMINQ_M_S = 884,
  VMINQ_M_U = 885,
  VANDQ_M_F = 886,
  VANDQ_M_U = 887,
  VANDQ_M_S = 888,
  VHSUBQ_M_N_S = 889,
  VHSUBQ_M_N_U = 890,
  VMULHQ_M_S = 891,
  VMULHQ_M_U = 892,
  VMULLBQ_INT_M_U = 893,
  VMULLBQ_INT_M_S = 894,
  VCADDQ_ROT90_M_F = 895,
  VSHRQ_M_N_S = 896,
  VADDQ_M_U = 897,
  VSLIQ_M_N_U = 898,
  VQADDQ_M_N_S = 899,
  VBRSRQ_M_N_F = 900,
  VABDQ_M_F = 901,
  VBRSRQ_M_N_U = 902,
  VEORQ_M_F = 903,
  VSHLQ_M_N_S = 904,
  VQDMLAHQ_M_N_U = 905,
  VQDMLAHQ_M_N_S = 906,
  VSHLQ_M_N_U = 907,
  VMLADAVAQ_P_U = 908,
  VMLADAVAQ_P_S = 909,
  VSLIQ_M_N_S = 910,
  VQSHLQ_M_U = 911,
  VQSHLQ_M_S = 912,
  VCADDQ_ROT90_M = 913,
  VORNQ_M_U = 914,
  VORNQ_M_S = 915,
  VQSHLQ_M_N_S = 916,
  VQSHLQ_M_N_U = 917,
  VADDQ_M_S = 918,
  VHADDQ_M_N_S = 919,
  VADDQ_M_F = 920,
  VQADDQ_M_N_U = 921,
  VEORQ_M_S = 922,
  VEORQ_M_U = 923,
  VHSUBQ_M_S = 924,
  VHSUBQ_M_U = 925,
  VHADDQ_M_N_U = 926,
  VHCADDQ_ROT90_M_S = 927,
  VQRDMLSDHQ_M_S = 928,
  VQRDMLSDHXQ_M_S = 929,
  VQRDMLADHXQ_M_S = 930,
  VQDMULHQ_M_S = 931,
  VMLADAVAXQ_P_S = 932,
  VQDMLADHXQ_M_S = 933,
  VQRDMULHQ_M_S = 934,
  VMLSDAVAXQ_P_S = 935,
  VQDMULHQ_M_N_S = 936,
  VHCADDQ_ROT270_M_S = 937,
  VQDMLSDHQ_M_S = 938,
  VQDMLSDHXQ_M_S = 939,
  VMLSDAVAQ_P_S = 940,
  VQRDMLADHQ_M_S = 941,
  VQDMLADHQ_M_S = 942,
  VMLALDAVAQ_P_U = 943,
  VMLALDAVAQ_P_S = 944,
  VQRSHRNBQ_M_N_U = 945,
  VQRSHRNBQ_M_N_S = 946,
  VQRSHRNTQ_M_N_S = 947,
  VQSHRNBQ_M_N_U = 948,
  VQSHRNBQ_M_N_S = 949,
  VQSHRNTQ_M_N_S = 950,
  VRSHRNBQ_M_N_U = 951,
  VRSHRNBQ_M_N_S = 952,
  VRSHRNTQ_M_N_U = 953,
  VSHLLBQ_M_N_U = 954,
  VSHLLBQ_M_N_S = 955,
  VSHLLTQ_M_N_U = 956,
  VSHLLTQ_M_N_S = 957,
  VSHRNBQ_M_N_S = 958,
  VSHRNBQ_M_N_U = 959,
  VSHRNTQ_M_N_S = 960,
  VSHRNTQ_M_N_U = 961,
  VMLALDAVAXQ_P_S = 962,
  VQRSHRNTQ_M_N_U = 963,
  VQSHRNTQ_M_N_U = 964,
  VRSHRNTQ_M_N_S = 965,
  VQRDMULHQ_M_N_S = 966,
  VRMLALDAVHAQ_P_S = 967,
  VMLSLDAVAQ_P_S = 968,
  VMLSLDAVAXQ_P_S = 969,
  VMULLBQ_POLY_M_P = 970,
  VMULLTQ_POLY_M_P = 971,
  VQDMULLBQ_M_N_S = 972,
  VQDMULLBQ_M_S = 973,
  VQDMULLTQ_M_N_S = 974,
  VQDMULLTQ_M_S = 975,
  VQRSHRUNBQ_M_N_S = 976,
  VQSHRUNBQ_M_N_S = 977,
  VQSHRUNTQ_M_N_S = 978,
  VRMLALDAVHAQ_P_U = 979,
  VRMLALDAVHAXQ_P_S = 980,
  VRMLSLDAVHAQ_P_S = 981,
  VRMLSLDAVHAXQ_P_S = 982,
  VQRSHRUNTQ_M_N_S = 983,
  VCMLAQ_M_F = 984,
  VCMLAQ_ROT180_M_F = 985,
  VCMLAQ_ROT270_M_F = 986,
  VCMLAQ_ROT90_M_F = 987,
  VCMULQ_M_F = 988,
  VCMULQ_ROT180_M_F = 989,
  VCMULQ_ROT270_M_F = 990,
  VCMULQ_ROT90_M_F = 991,
  VFMAQ_M_F = 992,
  VFMAQ_M_N_F = 993,
  VFMASQ_M_N_F = 994,
  VFMSQ_M_F = 995,
  VMAXNMQ_M_F = 996,
  VMINNMQ_M_F = 997,
  VSUBQ_M_F = 998,
  VSTRWQSB_S = 999,
  VSTRWQSB_U = 1000,
  VSTRBQSO_S = 1001,
  VSTRBQSO_U = 1002,
  VSTRBQ_S = 1003,
  VSTRBQ_U = 1004,
  VLDRBQGO_S = 1005,
  VLDRBQGO_U = 1006,
  VLDRBQ_S = 1007,
  VLDRBQ_U = 1008,
  VLDRWQGB_S = 1009,
  VLDRWQGB_U = 1010,
  VLD1Q_F = 1011,
  VLD1Q_S = 1012,
  VLD1Q_U = 1013,
  VLDRHQ_F = 1014,
  VLDRHQGO_S = 1015,
  VLDRHQGO_U = 1016,
  VLDRHQGSO_S = 1017,
  VLDRHQGSO_U = 1018,
  VLDRHQ_S = 1019,
  VLDRHQ_U = 1020,
  VLDRWQ_F = 1021,
  VLDRWQ_S = 1022,
  VLDRWQ_U = 1023,
  VLDRDQGB_S = 1024,
  VLDRDQGB_U = 1025,
  VLDRDQGO_S = 1026,
  VLDRDQGO_U = 1027,
  VLDRDQGSO_S = 1028,
  VLDRDQGSO_U = 1029,
  VLDRHQGO_F = 1030,
  VLDRHQGSO_F = 1031,
  VLDRWQGB_F = 1032,
  VLDRWQGO_F = 1033,
  VLDRWQGO_S = 1034,
  VLDRWQGO_U = 1035,
  VLDRWQGSO_F = 1036,
  VLDRWQGSO_S = 1037,
  VLDRWQGSO_U = 1038,
  VSTRHQ_F = 1039,
  VST1Q_S = 1040,
  VST1Q_U = 1041,
  VSTRHQSO_S = 1042,
  VSTRHQ_U = 1043,
  VSTRWQ_S = 1044,
  VSTRWQ_U = 1045,
  VSTRWQ_F = 1046,
  VST1Q_F = 1047,
  VSTRDQSB_S = 1048,
  VSTRDQSB_U = 1049,
  VSTRDQSO_S = 1050,
  VSTRDQSO_U = 1051,
  VSTRDQSSO_S = 1052,
  VSTRDQSSO_U = 1053,
  VSTRWQSO_S = 1054,
  VSTRWQSO_U = 1055,
  VSTRWQSSO_S = 1056,
  VSTRWQSSO_U = 1057,
  VSTRHQSO_F = 1058,
  VSTRHQSSO_F = 1059,
  VSTRWQSB_F = 1060,
  VSTRWQSO_F = 1061,
  VSTRWQSSO_F = 1062,
  VDDUPQ = 1063,
  VDDUPQ_M = 1064,
  VDWDUPQ = 1065,
  VDWDUPQ_M = 1066,
  VIDUPQ = 1067,
  VIDUPQ_M = 1068,
  VIWDUPQ = 1069,
  VIWDUPQ_M = 1070,
  VSTRWQSBWB_S = 1071,
  VSTRWQSBWB_U = 1072,
  VLDRWQGBWB_S = 1073,
  VLDRWQGBWB_U = 1074,
  VSTRWQSBWB_F = 1075,
  VLDRWQGBWB_F = 1076,
  VSTRDQSBWB_S = 1077,
  VSTRDQSBWB_U = 1078,
  VLDRDQGBWB_S = 1079,
  VLDRDQGBWB_U = 1080,
  VADCQ_U = 1081,
  VADCQ_M_U = 1082,
  VADCQ_S = 1083,
  VADCQ_M_S = 1084,
  VSBCIQ_U = 1085,
  VSBCIQ_S = 1086,
  VSBCIQ_M_U = 1087,
  VSBCIQ_M_S = 1088,
  VSBCQ_U = 1089,
  VSBCQ_S = 1090,
  VSBCQ_M_U = 1091,
  VSBCQ_M_S = 1092,
  VADCIQ_U = 1093,
  VADCIQ_M_U = 1094,
  VADCIQ_S = 1095,
  VADCIQ_M_S = 1096,
  VLD2Q = 1097,
  VLD4Q = 1098,
  VST2Q = 1099,
  VSHLCQ_M_U = 1100,
  VSHLCQ_M_S = 1101,
  VSTRHQSO_U = 1102,
  VSTRHQSSO_S = 1103,
  VSTRHQSSO_U = 1104,
  VSTRHQ_S = 1105,
  SRSHRL = 1106,
  SRSHR = 1107,
  URSHR = 1108,
  URSHRL = 1109,
  SQRSHR = 1110,
  UQRSHL = 1111,
  UQRSHLL_64 = 1112,
  UQRSHLL_48 = 1113,
  SQRSHRL_64 = 1114,
  SQRSHRL_48 = 1115,
  REINTERPRET = 1116
};

extern const char *const unspec_strings[];

enum unspecv {
  VUNSPEC_BLOCKAGE = 0,
  VUNSPEC_EPILOGUE = 1,
  VUNSPEC_THUMB1_INTERWORK = 2,
  VUNSPEC_ALIGN = 3,
  VUNSPEC_POOL_END = 4,
  VUNSPEC_POOL_1 = 5,
  VUNSPEC_POOL_2 = 6,
  VUNSPEC_POOL_4 = 7,
  VUNSPEC_POOL_8 = 8,
  VUNSPEC_POOL_16 = 9,
  VUNSPEC_TMRC = 10,
  VUNSPEC_TMCR = 11,
  VUNSPEC_ALIGN8 = 12,
  VUNSPEC_WCMP_EQ = 13,
  VUNSPEC_WCMP_GTU = 14,
  VUNSPEC_WCMP_GT = 15,
  VUNSPEC_EH_RETURN = 16,
  VUNSPEC_ATOMIC_CAS = 17,
  VUNSPEC_ATOMIC_XCHG = 18,
  VUNSPEC_ATOMIC_OP = 19,
  VUNSPEC_LL = 20,
  VUNSPEC_LDRD_ATOMIC = 21,
  VUNSPEC_SC = 22,
  VUNSPEC_LAX = 23,
  VUNSPEC_SLX = 24,
  VUNSPEC_LDA = 25,
  VUNSPEC_LDR = 26,
  VUNSPEC_STL = 27,
  VUNSPEC_STR = 28,
  VUNSPEC_GET_FPSCR = 29,
  VUNSPEC_SET_FPSCR = 30,
  VUNSPEC_SET_FPSCR_NZCVQC = 31,
  VUNSPEC_PROBE_STACK_RANGE = 32,
  VUNSPEC_CDP = 33,
  VUNSPEC_CDP2 = 34,
  VUNSPEC_LDC = 35,
  VUNSPEC_LDC2 = 36,
  VUNSPEC_LDCL = 37,
  VUNSPEC_LDC2L = 38,
  VUNSPEC_STC = 39,
  VUNSPEC_STC2 = 40,
  VUNSPEC_STCL = 41,
  VUNSPEC_STC2L = 42,
  VUNSPEC_MCR = 43,
  VUNSPEC_MCR2 = 44,
  VUNSPEC_MRC = 45,
  VUNSPEC_MRC2 = 46,
  VUNSPEC_MCRR = 47,
  VUNSPEC_MCRR2 = 48,
  VUNSPEC_MRRC = 49,
  VUNSPEC_MRRC2 = 50,
  VUNSPEC_SPECULATION_BARRIER = 51,
  VUNSPEC_APSR_WRITE = 52,
  VUNSPEC_VSTR_VLDR = 53,
  VUNSPEC_CLRM_APSR = 54,
  VUNSPEC_VSCCLRM_VPR = 55,
  VUNSPEC_VLSTM = 56,
  VUNSPEC_VLLDM = 57,
  VUNSPEC_PACBTI_NOP = 58,
  VUNSPEC_AUT_NOP = 59,
  VUNSPEC_BTI_NOP = 60,
  DLSTP8 = 61,
  DLSTP16 = 62,
  DLSTP32 = 63,
  DLSTP64 = 64
};

extern const char *const unspecv_strings[];
# 22 "/tool/lib/gcc/arm-none-eabi/14.2.1/plugin/include/tm.h" 2
# 1 "/tool/lib/gcc/arm-none-eabi/14.2.1/plugin/include/config/vxworks-dummy.h" 1
# 23 "/tool/lib/gcc/arm-none-eabi/14.2.1/plugin/include/tm.h" 2
# 1 "/tool/lib/gcc/arm-none-eabi/14.2.1/plugin/include/config/elfos.h" 1
# 24 "/tool/lib/gcc/arm-none-eabi/14.2.1/plugin/include/tm.h" 2
# 1 "/tool/lib/gcc/arm-none-eabi/14.2.1/plugin/include/config/arm/unknown-elf.h" 1
# 25 "/tool/lib/gcc/arm-none-eabi/14.2.1/plugin/include/tm.h" 2
# 1 "/tool/lib/gcc/arm-none-eabi/14.2.1/plugin/include/config/arm/elf.h" 1
# 26 "/tool/lib/gcc/arm-none-eabi/14.2.1/plugin/include/tm.h" 2
# 1 "/tool/lib/gcc/arm-none-eabi/14.2.1/plugin/include/config/arm/bpabi.h" 1
# 27 "/tool/lib/gcc/arm-none-eabi/14.2.1/plugin/include/tm.h" 2
# 1 "/tool/lib/gcc/arm-none-eabi/14.2.1/plugin/include/config/newlib-stdint.h" 1
# 28 "/tool/lib/gcc/arm-none-eabi/14.2.1/plugin/include/tm.h" 2
# 1 "/tool/lib/gcc/arm-none-eabi/14.2.1/plugin/include/config/arm/aout.h" 1
# 29 "/tool/lib/gcc/arm-none-eabi/14.2.1/plugin/include/tm.h" 2
# 1 "/tool/lib/gcc/arm-none-eabi/14.2.1/plugin/include/config/arm/arm.h" 1
# 38 "/tool/lib/gcc/arm-none-eabi/14.2.1/plugin/include/config/arm/arm.h"
# 1 "/tool/lib/gcc/arm-none-eabi/14.2.1/plugin/include/insn-modes.h" 1






enum machine_mode
{
  E_VOIDmode,






  E_BLKmode,






  E_CCmode,






  E_CC_NZmode,






  E_CC_Zmode,






  E_CC_NVmode,






  E_CC_SWPmode,






  E_CC_RSBmode,






  E_CCFPmode,






  E_CCFPEmode,






  E_CC_DNEmode,






  E_CC_DEQmode,






  E_CC_DLEmode,






  E_CC_DLTmode,






  E_CC_DGEmode,






  E_CC_DGTmode,






  E_CC_DLEUmode,






  E_CC_DLTUmode,






  E_CC_DGEUmode,






  E_CC_DGTUmode,






  E_CC_Cmode,






  E_CC_Bmode,






  E_CC_Nmode,






  E_CC_Vmode,






  E_CC_ADCmode,






  E_BImode,






  E_B2Imode,






  E_B4Imode,






  E_QImode,






  E_HImode,






  E_SImode,






  E_DImode,






  E_TImode,






  E_EImode,






  E_OImode,






  E_CImode,






  E_XImode,






  E_QQmode,






  E_HQmode,






  E_SQmode,






  E_DQmode,






  E_TQmode,






  E_UQQmode,






  E_UHQmode,






  E_USQmode,






  E_UDQmode,






  E_UTQmode,






  E_HAmode,






  E_SAmode,






  E_DAmode,






  E_TAmode,






  E_UHAmode,






  E_USAmode,






  E_UDAmode,






  E_UTAmode,






  E_HFmode,






  E_BFmode,






  E_SFmode,






  E_DFmode,






  E_SDmode,






  E_DDmode,






  E_TDmode,






  E_CQImode,






  E_CHImode,






  E_CSImode,






  E_CDImode,






  E_CTImode,






  E_CEImode,






  E_COImode,






  E_CCImode,






  E_CXImode,






  E_BCmode,






  E_HCmode,






  E_SCmode,






  E_DCmode,






  E_V16BImode,






  E_V8BImode,






  E_V4BImode,






  E_V2QImode,






  E_V4QImode,






  E_V2HImode,






  E_V8QImode,






  E_V4HImode,






  E_V2SImode,






  E_V16QImode,






  E_V8HImode,






  E_V4SImode,






  E_V2DImode,






  E_V4QQmode,






  E_V2HQmode,






  E_V4UQQmode,






  E_V2UHQmode,






  E_V2HAmode,






  E_V2UHAmode,






  E_V2HFmode,






  E_V2BFmode,






  E_V4HFmode,






  E_V4BFmode,






  E_V2SFmode,






  E_V8HFmode,






  E_V8BFmode,






  E_V4SFmode,






  E_V2DFmode,






  MAX_MACHINE_MODE,

  MIN_MODE_RANDOM = E_VOIDmode,
  MAX_MODE_RANDOM = E_BLKmode,

  MIN_MODE_CC = E_CCmode,
  MAX_MODE_CC = E_CC_ADCmode,

  MIN_MODE_BOOL = E_BImode,
  MAX_MODE_BOOL = E_B4Imode,

  MIN_MODE_INT = E_QImode,
  MAX_MODE_INT = E_XImode,

  MIN_MODE_PARTIAL_INT = E_VOIDmode,
  MAX_MODE_PARTIAL_INT = E_VOIDmode,

  MIN_MODE_FRACT = E_QQmode,
  MAX_MODE_FRACT = E_TQmode,

  MIN_MODE_UFRACT = E_UQQmode,
  MAX_MODE_UFRACT = E_UTQmode,

  MIN_MODE_ACCUM = E_HAmode,
  MAX_MODE_ACCUM = E_TAmode,

  MIN_MODE_UACCUM = E_UHAmode,
  MAX_MODE_UACCUM = E_UTAmode,

  MIN_MODE_FLOAT = E_HFmode,
  MAX_MODE_FLOAT = E_DFmode,

  MIN_MODE_DECIMAL_FLOAT = E_SDmode,
  MAX_MODE_DECIMAL_FLOAT = E_TDmode,

  MIN_MODE_COMPLEX_INT = E_CQImode,
  MAX_MODE_COMPLEX_INT = E_CXImode,

  MIN_MODE_COMPLEX_FLOAT = E_BCmode,
  MAX_MODE_COMPLEX_FLOAT = E_DCmode,

  MIN_MODE_VECTOR_BOOL = E_V16BImode,
  MAX_MODE_VECTOR_BOOL = E_V4BImode,

  MIN_MODE_VECTOR_INT = E_V2QImode,
  MAX_MODE_VECTOR_INT = E_V2DImode,

  MIN_MODE_VECTOR_FRACT = E_V4QQmode,
  MAX_MODE_VECTOR_FRACT = E_V2HQmode,

  MIN_MODE_VECTOR_UFRACT = E_V4UQQmode,
  MAX_MODE_VECTOR_UFRACT = E_V2UHQmode,

  MIN_MODE_VECTOR_ACCUM = E_V2HAmode,
  MAX_MODE_VECTOR_ACCUM = E_V2HAmode,

  MIN_MODE_VECTOR_UACCUM = E_V2UHAmode,
  MAX_MODE_VECTOR_UACCUM = E_V2UHAmode,

  MIN_MODE_VECTOR_FLOAT = E_V2HFmode,
  MAX_MODE_VECTOR_FLOAT = E_V2DFmode,

  MIN_MODE_OPAQUE = E_VOIDmode,
  MAX_MODE_OPAQUE = E_VOIDmode,

  NUM_MACHINE_MODES = MAX_MACHINE_MODE
};
# 39 "/tool/lib/gcc/arm-none-eabi/14.2.1/plugin/include/config/arm/arm.h" 2



# 1 "/tool/lib/gcc/arm-none-eabi/14.2.1/plugin/include/config/vxworks-dummy.h" 1
# 43 "/tool/lib/gcc/arm-none-eabi/14.2.1/plugin/include/config/arm/arm.h" 2


extern char arm_arch_name[];




# 1 "/tool/lib/gcc/arm-none-eabi/14.2.1/plugin/include/config/arm/arm-opts.h" 1
# 51 "/tool/lib/gcc/arm-none-eabi/14.2.1/plugin/include/config/arm/arm.h" 2


extern enum processor_type arm_tune;

typedef enum arm_cond_code
{
  ARM_EQ = 0, ARM_NE, ARM_CS, ARM_CC, ARM_MI, ARM_PL, ARM_VS, ARM_VC,
  ARM_HI, ARM_LS, ARM_GE, ARM_LT, ARM_GT, ARM_LE, ARM_AL, ARM_NV
}
arm_cc;

extern arm_cc arm_current_cc;
# 71 "/tool/lib/gcc/arm-none-eabi/14.2.1/plugin/include/config/arm/arm.h"
extern int arm_target_label;
extern int arm_ccfsm_state;
extern struct _dont_use_rtx_here_ * arm_target_insn;

extern void (*arm_lang_output_object_attributes_hook)(void);



extern union _dont_use_tree_here_ * arm_fp16_type_node;



extern union _dont_use_tree_here_ * arm_bf16_type_node;
extern union _dont_use_tree_here_ * arm_bf16_ptr_type_node;
# 405 "/tool/lib/gcc/arm-none-eabi/14.2.1/plugin/include/config/arm/arm.h"
extern const struct arm_fpu_desc
{
  const char *name;
  enum isa_feature isa_bits[isa_num_bits];
} all_fpus[];


extern int arm_fpu_attr;
# 431 "/tool/lib/gcc/arm-none-eabi/14.2.1/plugin/include/config/arm/arm.h"
enum base_architecture
{
  BASE_ARCH_0 = 0,
  BASE_ARCH_2 = 2,
  BASE_ARCH_3 = 3,
  BASE_ARCH_3M = 3,
  BASE_ARCH_4 = 4,
  BASE_ARCH_4T = 4,
  BASE_ARCH_5T = 5,
  BASE_ARCH_5TE = 5,
  BASE_ARCH_5TEJ = 5,
  BASE_ARCH_6 = 6,
  BASE_ARCH_6J = 6,
  BASE_ARCH_6KZ = 6,
  BASE_ARCH_6K = 6,
  BASE_ARCH_6T2 = 6,
  BASE_ARCH_6M = 6,
  BASE_ARCH_6Z = 6,
  BASE_ARCH_7 = 7,
  BASE_ARCH_7A = 7,
  BASE_ARCH_7R = 7,
  BASE_ARCH_7M = 7,
  BASE_ARCH_7EM = 7,
  BASE_ARCH_8A = 8,
  BASE_ARCH_8M_BASE = 8,
  BASE_ARCH_8M_MAIN = 8,
  BASE_ARCH_8R = 8,
  BASE_ARCH_9A = 9
};


extern enum base_architecture arm_base_arch;


extern int arm_arch4;


extern int arm_arch4t;


extern int arm_arch5t;


extern int arm_arch5te;


extern int arm_arch6;


extern int arm_arch6k;


extern int arm_arch6m;


extern int arm_arch7;


extern int arm_arch_notm;


extern int arm_arch7em;


extern int arm_arch8;


extern int arm_arch8_1;


extern int arm_arch8_2;


extern int arm_arch8_3;


extern int arm_arch8_4;



extern int arm_arch8m_main;



extern int arm_arch8_1m_main;



extern int arm_fp16_inst;


extern int arm_ld_sched;


extern int arm_tune_strongarm;


extern int arm_arch_iwmmxt;


extern int arm_arch_iwmmxt2;


extern int arm_arch_xscale;


extern int arm_tune_xscale;


extern int arm_tune_wbuf;


extern int arm_tune_cortex_a9;






extern int arm_cpp_interwork;


extern int arm_arch_thumb1;


extern int arm_arch_thumb2;


extern int arm_arch_arm_hwdiv;


extern int arm_arch_thumb_hwdiv;


extern int arm_arch_no_volatile_ce;







extern int arm_arch_crc;


extern int arm_arch_cmse;


extern int arm_arch_i8mm;


extern int arm_arch_bf16;


extern int arm_arch_cde;
extern int arm_arch_cde_coproc;
extern const int arm_arch_cde_coproc_bits[];
# 1213 "/tool/lib/gcc/arm-none-eabi/14.2.1/plugin/include/config/arm/arm.h"
extern int arm_regs_in_sequence[];
# 1289 "/tool/lib/gcc/arm-none-eabi/14.2.1/plugin/include/config/arm/arm.h"
enum reg_class
{
  NO_REGS,
  LO_REGS,
  STACK_REG,
  BASE_REGS,
  HI_REGS,
  CALLER_SAVE_REGS,
  EVEN_REG,
  GENERAL_REGS,
  CORE_REGS,
  VFP_D0_D7_REGS,
  VFP_LO_REGS,
  VFP_HI_REGS,
  VFP_REGS,
  IWMMXT_REGS,
  IWMMXT_GR_REGS,
  CC_REG,
  VFPCC_REG,
  SFP_REG,
  AFP_REG,
  VPR_REG,
  PAC_REG,
  GENERAL_AND_VPR_REGS,
  ALL_REGS,
  LIM_REG_CLASSES
};
# 1386 "/tool/lib/gcc/arm-none-eabi/14.2.1/plugin/include/config/arm/arm.h"
enum vfp_sysregs_encoding {
  FPSCR_ENUM, FPSCR_nzcvqc_ENUM, VPR_ENUM, P0_ENUM, FPCXTNS_ENUM, FPCXTS_ENUM,
  NB_FP_SYSREGS
};

extern const char *fp_sysreg_names[NB_FP_SYSREGS];
# 1583 "/tool/lib/gcc/arm-none-eabi/14.2.1/plugin/include/config/arm/arm.h"
typedef struct arm_stack_offsets
{
  int saved_args;
  int frame;
  int saved_regs;
  int soft_frame;
  int locals_base;
  int outgoing_args;
  unsigned int saved_regs_mask;
}
arm_stack_offsets;
# 1650 "/tool/lib/gcc/arm-none-eabi/14.2.1/plugin/include/config/arm/arm.h"
extern struct _dont_use_rtx_here_ * thumb_call_via_label[14];






enum arm_pcs
{
  ARM_PCS_AAPCS,
  ARM_PCS_AAPCS_VFP,
  ARM_PCS_AAPCS_IWMMXT,

  ARM_PCS_AAPCS_LOCAL,
  ARM_PCS_ATPCS,
  ARM_PCS_APCS,
  ARM_PCS_UNKNOWN
};


extern enum arm_pcs arm_pcs_default;
# 1855 "/tool/lib/gcc/arm-none-eabi/14.2.1/plugin/include/config/arm/arm.h"
enum arm_auto_incmodes
  {
    ARM_POST_INC,
    ARM_PRE_INC,
    ARM_POST_DEC,
    ARM_PRE_DEC
  };
# 2196 "/tool/lib/gcc/arm-none-eabi/14.2.1/plugin/include/config/arm/arm.h"
extern unsigned arm_pic_register;
# 2228 "/tool/lib/gcc/arm-none-eabi/14.2.1/plugin/include/config/arm/arm.h"
extern int making_const_table;
# 2476 "/tool/lib/gcc/arm-none-eabi/14.2.1/plugin/include/config/arm/arm.h"
extern const char *arm_rewrite_mcpu (int argc, const char **argv);
extern const char *arm_rewrite_march (int argc, const char **argv);
extern const char *arm_asm_auto_mfpu (int argc, const char **argv);
# 2491 "/tool/lib/gcc/arm-none-eabi/14.2.1/plugin/include/config/arm/arm.h"
extern const char *arm_target_mode (int argc, const char **argv);






extern const char *host_detect_local_cpu (int argc, const char **argv);
# 2511 "/tool/lib/gcc/arm-none-eabi/14.2.1/plugin/include/config/arm/arm.h"
const char *arm_canon_arch_option (int argc, const char **argv);
const char *arm_canon_arch_multilib_option (int argc, const char **argv);







const char *arm_be8_option (int argc, const char **argv);
# 30 "/tool/lib/gcc/arm-none-eabi/14.2.1/plugin/include/tm.h" 2
# 1 "/tool/lib/gcc/arm-none-eabi/14.2.1/plugin/include/config/arm/arm-mlib.h" 1
# 31 "/tool/lib/gcc/arm-none-eabi/14.2.1/plugin/include/tm.h" 2
# 1 "/tool/lib/gcc/arm-none-eabi/14.2.1/plugin/include/config/initfini-array.h" 1
# 32 "/tool/lib/gcc/arm-none-eabi/14.2.1/plugin/include/tm.h" 2





# 1 "/tool/lib/gcc/arm-none-eabi/14.2.1/plugin/include/insn-modes.h" 1
# 38 "/tool/lib/gcc/arm-none-eabi/14.2.1/plugin/include/tm.h" 2

# 1 "/tool/lib/gcc/arm-none-eabi/14.2.1/plugin/include/defaults.h" 1
# 40 "/tool/lib/gcc/arm-none-eabi/14.2.1/plugin/include/tm.h" 2
# 64 "/previous/source/libgcc/crtstuff.c" 2
# 1 "/out/libgcc_tm.h" 1



# 1 "/source/libgcc/config/arm/bpabi-lib.h" 1
# 5 "/out/libgcc_tm.h" 2
# 65 "/previous/source/libgcc/crtstuff.c" 2
# 1 "/source/libgcc/unwind-dw2-fde.h" 1
# 30 "/source/libgcc/unwind-dw2-fde.h"
#pragma GCC visibility push(default)


struct fde_vector
{
  const void *orig_data;
  size_t count;
  const struct dwarf_fde *array[];
};

struct object
{
  void *pc_begin;
  void *tbase;
  void *dbase;
  union {
    const struct dwarf_fde *single;
    struct dwarf_fde **array;
    struct fde_vector *sort;
  } u;

  union {
    struct {
      unsigned long sorted : 1;
      unsigned long from_array : 1;
      unsigned long mixed_encoding : 1;
      unsigned long encoding : 8;


      unsigned long count : 21;
    } b;
    size_t i;
  } s;





  struct object *next;
};





struct old_object
{
  void *pc_begin;
  void *pc_end;
  struct dwarf_fde *fde_begin;
  struct dwarf_fde **fde_array;
  size_t count;
  struct old_object *next;
};

struct dwarf_eh_bases
{
  void *tbase;
  void *dbase;
  void *func;
};


extern void __register_frame_info_bases (const void *, struct object *,
      void *, void *);
extern void __register_frame_info (const void *, struct object *);
extern void __register_frame (void *);
extern void __register_frame_info_table_bases (void *, struct object *,
            void *, void *);
extern void __register_frame_info_table (void *, struct object *);
extern void __register_frame_table (void *);
extern void *__deregister_frame_info (const void *);
extern void *__deregister_frame_info_bases (const void *);
extern void __deregister_frame (void *);


typedef int sword __attribute__ ((mode (SI)));
typedef unsigned int uword __attribute__ ((mode (SI)));
typedef unsigned int uaddr __attribute__ ((mode (pointer)));
typedef int saddr __attribute__ ((mode (pointer)));
typedef unsigned char ubyte;
# 134 "/source/libgcc/unwind-dw2-fde.h"
struct dwarf_cie
{
  uword length;
  sword CIE_id;
  ubyte version;
  unsigned char augmentation[];
} __attribute__ ((packed, aligned (__alignof__ (void *))));


struct dwarf_fde
{
  uword length;
  sword CIE_delta;
  unsigned char pc_begin[];
} __attribute__ ((packed, aligned (__alignof__ (void *))));

typedef struct dwarf_fde fde;



static inline const struct dwarf_cie *
get_cie (const struct dwarf_fde *f)
{
  return (const void *)&f->CIE_delta - f->CIE_delta;
}

static inline const fde *
next_fde (const fde *f)
{
  return (const fde *) ((const char *) f + f->length + sizeof (f->length));
}

extern const fde * _Unwind_Find_FDE (void *, struct dwarf_eh_bases *);

static inline int
last_fde (const struct object *obj __attribute__ ((__unused__)), const fde *f)
{



  return f->length == 0;

}


#pragma GCC visibility pop
# 66 "/previous/source/libgcc/crtstuff.c" 2
# 182 "/previous/source/libgcc/crtstuff.c"
extern void __register_frame_info (const void *, struct object *)
      __attribute__ ((weak));
extern void __register_frame_info_bases (const void *, struct object *,
      void *, void *)
      __attribute__ ((weak));
extern void *__deregister_frame_info (const void *)
         __attribute__ ((weak));
extern void *__deregister_frame_info_bases (const void *)
         __attribute__ ((weak));
extern void __do_global_ctors_1 (void);


extern void _ITM_registerTMCloneTable (void *, size_t) __attribute__ ((weak));
extern void _ITM_deregisterTMCloneTable (void *) __attribute__ ((weak));




typedef void (*func_ptr) (void);
# 613 "/previous/source/libgcc/crtstuff.c"
;
# 629 "/previous/source/libgcc/crtstuff.c"
;
# 657 "/previous/source/libgcc/crtstuff.c"
typedef int int32;







static const int32 __FRAME_END__[]
     __attribute__ ((used, section(".eh_frame"),
       aligned(__alignof__(int32))))
     = { 0 };






func_ptr __TMC_END__[]
  __attribute__((used, section(".tm_clone_table"),
   aligned(__alignof__(void *))))

  __attribute__((__visibility__ ("hidden"))) = { };
