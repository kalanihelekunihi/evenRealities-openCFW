
/* WARNING: Removing unreachable block (ram,0x00475394) */
/* WARNING: Removing unreachable block (ram,0x004753ce) */
/* WARNING: Removing unreachable block (ram,0x004753e0) */
/* WARNING: Removing unreachable block (ram,0x004753dc) */
/* WARNING: Removing unreachable block (ram,0x004753e2) */
/* WARNING: Removing unreachable block (ram,0x0047539c) */
/* WARNING: Removing unreachable block (ram,0x00475400) */
/* WARNING: Removing unreachable block (ram,0x0047541a) */
/* WARNING: Removing unreachable block (ram,0x00475422) */
/* WARNING: Removing unreachable block (ram,0x0047543e) */
/* WARNING: Removing unreachable block (ram,0x00475446) */
/* WARNING: Removing unreachable block (ram,0x0047544e) */
/* WARNING: Removing unreachable block (ram,0x0047540a) */
/* WARNING: Removing unreachable block (ram,0x0047545c) */
/* WARNING: Removing unreachable block (ram,0x004753a0) */
/* WARNING: Removing unreachable block (ram,0x0047545e) */
/* WARNING: Removing unreachable block (ram,0x00475470) */
/* WARNING: Removing unreachable block (ram,0x0047546c) */
/* WARNING: Removing unreachable block (ram,0x00475472) */
/* WARNING: Removing unreachable block (ram,0x004753a4) */
/* WARNING: Removing unreachable block (ram,0x0047548c) */
/* WARNING: Removing unreachable block (ram,0x0047549e) */
/* WARNING: Removing unreachable block (ram,0x0047549a) */
/* WARNING: Removing unreachable block (ram,0x004754a0) */
/* WARNING: Removing unreachable block (ram,0x004753a8) */
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

undefined8 threadBleMsgTxQueueDrain(void)

{
  undefined4 unaff_r5;
  undefined4 unaff_r6;
  
  osMessageQueueGet(*(undefined4 *)(DAT_00475d70 + 0xc),&stack0xfffffff8,0,0);
  return CONCAT44(unaff_r6,unaff_r5);
}

