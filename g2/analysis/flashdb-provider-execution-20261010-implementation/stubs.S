.syntax unified
.thumb
.section .text
.global find_kv
.thumb_func
find_kv:
 bkpt #0
 bx lr
.global _fdb_flash_read
.thumb_func
_fdb_flash_read:
 bkpt #0
 bx lr
.global _fdb_flash_write
.thumb_func
_fdb_flash_write:
 bkpt #0
 bx lr
.global _fdb_write_status
.thumb_func
_fdb_write_status:
 bkpt #0
 bx lr
.global diagnostic
.thumb_func
diagnostic:
 bkpt #0
 bx lr
