
/* WARNING: Removing unreachable block (ram,0x0048eece) */
/* WARNING: Removing unreachable block (ram,0x0048eef4) */
/* WARNING: Removing unreachable block (ram,0x0048eed6) */
/* WARNING: Removing unreachable block (ram,0x0048ef04) */
/* WARNING: Removing unreachable block (ram,0x0048eedc) */
/* WARNING: Removing unreachable block (ram,0x0048ef1c) */
/* WARNING: Removing unreachable block (ram,0x0048eee2) */
/* WARNING: Removing unreachable block (ram,0x0048ef3a) */
/* WARNING: Removing unreachable block (ram,0x0048ef42) */
/* WARNING: Removing unreachable block (ram,0x0048ef5e) */
/* WARNING: Removing unreachable block (ram,0x0048ef66) */
/* WARNING: Removing unreachable block (ram,0x0048ef6e) */
/* WARNING: Removing unreachable block (ram,0x0048ef7c) */
/* WARNING: Removing unreachable block (ram,0x0048eeea) */
/* WARNING: Removing unreachable block (ram,0x0048ef34) */
/* WARNING: Removing unreachable block (ram,0x0048eef2) */
/* WARNING: Removing unreachable block (ram,0x0048ef9e) */

undefined8 _thread_pb_msg_handler(void)

{
  int iVar1;
  undefined4 unaff_r5;
  undefined4 unaff_r6;
  
  do {
    iVar1 = osMessageQueueGet(*(undefined4 *)(DAT_0048f324 + 0xc),&stack0xfffffff8,0,0);
  } while (iVar1 == 0);
  return CONCAT44(unaff_r6,unaff_r5);
}

