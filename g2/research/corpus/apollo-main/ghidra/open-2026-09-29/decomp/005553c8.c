
void FUN_005553c8(void)

{
  int iVar1;
  int iVar2;
  undefined4 in_r3;
  undefined4 local_1c;
  undefined4 local_18;
  undefined4 local_14;
  undefined4 uStack_10;
  
  uStack_10 = in_r3;
  iVar1 = FUN_0045a568();
  iVar2 = DAT_00555754;
  if ((iVar1 == 1) && (*(int *)(DAT_00555754 + 0x3c) == 0)) {
    FUN_0043c0e4(&local_1c,0xc,0);
    local_1c = *(undefined4 *)(iVar2 + 0x30);
    local_18 = *(undefined4 *)(iVar2 + 0x34);
    local_14 = *(undefined4 *)(iVar2 + 0x28);
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      FUN_0043d574(3,DAT_005558cc,DAT_005558c8,DAT_0055600c,0x415,DAT_00555d14,local_1c,local_18,
                   local_14);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0xcc00000,DAT_00556124,DAT_00556124,local_1c,local_18,local_14);
    }
    APP_PbTxEncodeScrollSync(&local_1c);
  }
  return;
}

