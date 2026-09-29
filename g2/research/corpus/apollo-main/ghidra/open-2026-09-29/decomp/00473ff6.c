
void FUN_00473ff6(undefined4 param_1)

{
  int iVar1;
  undefined4 local_30 [7];
  undefined4 local_14;
  
  FUN_0043c0e4(local_30,0x24,0);
  local_30[0] = 4;
  local_14 = param_1;
  iVar1 = osMessageQueuePut(*(undefined4 *)(DAT_004742f8 + 0xc),local_30,0,1000);
  if (iVar1 != 0) {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      FUN_0043d574(2,PTR_s_task_displaydrvmgr_0047430c,DAT_00474308,DAT_004744f4,0x150,DAT_004744f0)
      ;
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x8000000,DAT_004744f8);
    }
  }
  return;
}

