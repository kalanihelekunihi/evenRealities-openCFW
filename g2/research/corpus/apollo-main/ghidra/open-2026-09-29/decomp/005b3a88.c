
void FUN_005b3a88(int param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  int iVar2;
  
  iVar1 = DAT_005b3e48;
  if (*(char *)(DAT_005b3e48 + 0x10) != '\0') goto LAB_005b3afa;
  if (((*DAT_005b3e34 != '\x04') || (DAT_005b3e34[0x96] != '\0')) || (DAT_005b3e34[0xa4] != '\x01'))
  goto LAB_005b3afa;
  iVar2 = FUN_0043d0ce();
  if (iVar2 << 0x1e < 0) {
    FUN_0043d574(3,DAT_005b3e18,DAT_005b3e14,DAT_005b3e9c,0x131,DAT_005b3e98);
  }
  iVar2 = FUN_0043d0ce();
  if (iVar2 << 0x1f < 0) {
LAB_005b3ae8:
    compress_log_output(0xc000000,DAT_005b3ea0,DAT_005b3ea0);
  }
  else {
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1d < 0) goto LAB_005b3ae8;
  }
  FUN_005b384c();
LAB_005b3afa:
  iVar2 = FUN_005b3a5a();
  if ((iVar2 != 0) && (iVar2 = FUN_005b3628(iVar1 + 0x10,param_1), iVar2 != 0)) {
    if (*(int *)(iVar1 + 0x18) == -1) {
      iVar2 = FUN_0043d0ce();
      if (iVar2 << 0x1e < 0) {
        FUN_0043d574(4,DAT_005b3e18,DAT_005b3e14,DAT_005b3e9c,0x13e,DAT_005b3ea4);
      }
      iVar2 = FUN_0043d0ce();
      if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
        compress_log_output(0x10000000,DAT_005b3ea8);
      }
      *(undefined4 *)(iVar1 + 0x18) = 0;
    }
    else {
      *(int *)(iVar1 + 0x18) = *(int *)(iVar1 + 0x18) + 1;
      iVar2 = FUN_0043d0ce();
      if (iVar2 << 0x1e < 0) {
        FUN_0043d574(4,DAT_005b3e18,DAT_005b3e14,DAT_005b3e9c,0x143,DAT_005b3eac,
                     *(undefined4 *)(iVar1 + 0x18),DAT_005b3e34[0x95],param_4);
      }
      iVar2 = FUN_0043d0ce();
      if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
        compress_log_output(0x10800000,DAT_005b3eb0,DAT_005b3eb0,*(undefined4 *)(iVar1 + 0x18),
                            DAT_005b3e34[0x95]);
      }
    }
    if (*(uint *)(iVar1 + 0x18) < (uint)(byte)DAT_005b3e34[0x95]) {
      FUN_005b02e4(9,(uint)(byte)DAT_005b3e34[0x95] - *(int *)(iVar1 + 0x18));
      *(int *)(iVar1 + 0x14) = param_1 + 1000;
    }
    else {
      iVar2 = FUN_0043d0ce();
      if (iVar2 << 0x1e < 0) {
        FUN_0043d574(3,DAT_005b3e18,DAT_005b3e14,DAT_005b3e9c,0x147,DAT_005b3eb4);
      }
      iVar2 = FUN_0043d0ce();
      if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
        compress_log_output(0xc000000,DAT_005b3eb8,DAT_005b3eb8);
      }
      *(undefined4 *)(iVar1 + 0x18) = 0;
      *(undefined1 *)(iVar1 + 0x10) = 0;
      FUN_005b02e4(10,2);
    }
  }
  return;
}

