
void FUN_00555200(char param_1)

{
  int iVar1;
  int iVar2;
  int iVar3;
  int iVar4;
  uint uVar5;
  
  iVar1 = DAT_00555754;
  iVar2 = DAT_005553c4;
  if (*(int *)(DAT_00555754 + 0x3c) == 0) {
    if (*(int *)(DAT_00555754 + 0x18) == 0) {
      iVar2 = FUN_0043d0ce();
      if (iVar2 << 0x1e < 0) {
        FUN_0043d574(1,DAT_005558cc,DAT_005558c8,DAT_00555cfc,0x3cd,DAT_00555d04);
      }
      iVar2 = FUN_0043d0ce();
      if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
        compress_log_output(0x4000000,DAT_00555d08);
      }
    }
    else {
      iVar3 = FUN_0044e498();
      if ((param_1 != '\0') || ((iVar3 != *(int *)(iVar1 + 0x38) && (iVar3 % 0x1c == 0)))) {
        uVar5 = iVar3 / 0x118;
        if (3 < uVar5) {
          uVar5 = 3;
        }
        *(uint *)(iVar1 + 0x30) = uVar5 + *(int *)(iVar1 + 0x2c);
        *(uint *)(iVar1 + 0x34) = (DAT_00555d0c * uVar5 + iVar3) / 0x1c;
        iVar4 = FUN_0043d0ce();
        if (iVar4 << 0x1e < 0) {
          FUN_0043d574(4,DAT_005558cc,DAT_005558c8,DAT_00555cfc,0x3e4,DAT_00555d10,uVar5,
                       *(undefined4 *)(iVar1 + 0x30),*(undefined4 *)(iVar1 + 0x34),iVar3);
        }
        iVar4 = FUN_0043d0ce();
        if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
          compress_log_output(0x11000000,DAT_005560c8,DAT_005560c8,uVar5,
                              *(undefined4 *)(iVar1 + 0x30),*(undefined4 *)(iVar1 + 0x34),iVar3);
        }
        *(int *)(iVar1 + 0x38) = iVar3;
        FUN_00554d58(*(undefined4 *)(iVar1 + 0x1c),*(undefined4 *)(iVar1 + 0x30),
                     *(undefined4 *)(iVar1 + 0x34));
        if ((4 < *(uint *)(iVar2 + 0xc)) && (param_1 != '\0')) {
          if ((*(uint *)(iVar1 + 0x30) < *(int *)(iVar1 + 0x2c) + 1U) &&
             ((*(int *)(iVar1 + 0x30) != 0 && (*(int *)(iVar1 + 0x3c) == 0)))) {
            FUN_00589b68(0xe,*(uint *)(iVar1 + 0x30) & 0xffff | *(int *)(iVar1 + 0x34) << 0x10);
          }
          else if ((*(int *)(iVar1 + 0x2c) + 1U < *(uint *)(iVar1 + 0x30)) &&
                  ((*(int *)(iVar1 + 0x2c) + 4U < *(uint *)(iVar2 + 0xc) &&
                   (*(int *)(iVar1 + 0x3c) == 0)))) {
            FUN_00589b68(0xf,*(uint *)(iVar1 + 0x30) & 0xffff | *(int *)(iVar1 + 0x34) << 0x10);
          }
        }
      }
    }
  }
  else {
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      FUN_0043d574(2,DAT_005558cc,DAT_005558c8,DAT_00555cfc,0x3c7,DAT_00555cf8);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x8000000,DAT_00555d00,DAT_00555d00);
    }
  }
  return;
}

