
void FUN_00473b54(void)

{
  int iVar1;
  undefined4 in_r3;
  undefined4 auStack_30 [9];
  undefined4 uStack_c;
  
  uStack_c = in_r3;
  FUN_0043c0e4(auStack_30,0x24,0);
  auStack_30[0] = 6;
  iVar1 = osMessageQueuePut(*(undefined4 *)(DAT_004742f8 + 0xc),auStack_30,0,1000);
  if (iVar1 != 0) {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      FUN_0043d574(2,PTR_s_task_displaydrvmgr_0047430c,DAT_00474308,DAT_0047449c,0xb5,DAT_00474498);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x8000000,DAT_004744a0);
    }
  }
  return;
}

