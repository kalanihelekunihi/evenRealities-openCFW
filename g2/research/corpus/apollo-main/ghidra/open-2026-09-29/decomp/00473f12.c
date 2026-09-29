
void FUN_00473f12(void)

{
  int iVar1;
  undefined4 in_r3;
  undefined4 local_30 [9];
  undefined4 uStack_c;
  
  uStack_c = in_r3;
  FUN_0043c0e4(local_30,0x24,0);
  local_30[0] = 0;
  iVar1 = osMessageQueuePut(*(undefined4 *)(DAT_004742f8 + 0xc),local_30,0,1000);
  if (iVar1 != 0) {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      FUN_0043d574(2,PTR_s_task_displaydrvmgr_0047430c,DAT_00474308,DAT_004744dc,0x13b,DAT_004744d8)
      ;
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x8000000,DAT_004744e0);
    }
  }
  return;
}

