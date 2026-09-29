
void SVC_Settings_SyncVersionOnlySend(void)

{
  undefined4 uVar1;
  int iVar2;
  undefined4 in_r3;
  undefined1 local_3c [36];
  undefined1 auStack_18 [12];
  undefined4 uStack_c;
  
  uStack_c = in_r3;
  FUN_0043c0e4(local_3c,0x30,0);
  uVar1 = DAT_0046c400;
  local_3c[0] = 2;
  FUN_0044b5a0(auStack_18,DAT_0046c400,9);
  FUN_00465480(9,local_3c,0x30,0,5);
  iVar2 = FUN_0043d0ce();
  if (iVar2 << 0x1e < 0) {
    FUN_0043d574(4,DAT_0046bb74,DAT_0046bb70,DAT_0046c408,0xd9,DAT_0046c404,uVar1);
  }
  iVar2 = FUN_0043d0ce();
  if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
    compress_log_output(0x10400000,DAT_0046c638,DAT_0046c638,uVar1);
  }
  return;
}

