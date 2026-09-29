
undefined4 FUN_00473bc4(byte param_1)

{
  int iVar1;
  undefined4 uVar2;
  undefined4 local_30 [7];
  uint local_14;
  
  FUN_0043c0e4(local_30,0x24,0);
  local_30[0] = 8;
  local_14 = (uint)param_1;
  iVar1 = osMessageQueuePut(*(undefined4 *)(DAT_004742f8 + 0xc),local_30,0,1000);
  if (iVar1 == 0) {
    uVar2 = 0;
  }
  else {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      FUN_0043d574(2,PTR_s_task_displaydrvmgr_0047430c,DAT_00474308,DAT_004744a4,0xc1,DAT_00474498);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x8000000,DAT_004744a0);
    }
    uVar2 = 0xffffffff;
  }
  return uVar2;
}

