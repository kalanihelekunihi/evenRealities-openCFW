
undefined4 FUN_0050a9c2(void)

{
  int iVar1;
  int *piVar2;
  int *piVar3;
  int iVar4;
  undefined4 in_r3;
  int iVar5;
  
  piVar3 = DAT_0050b164;
  if (*DAT_0050b164 != 0) {
    for (iVar5 = 0; iVar1 = DAT_0050b14c, iVar5 < 4; iVar5 = iVar5 + 1) {
      if ((*(int *)(iVar5 * 0x30 + DAT_0050b14c + 4) != 0) &&
         (iVar4 = FUN_0043e2ea(*(undefined4 *)(iVar5 * 0x30 + DAT_0050b14c + 4)), iVar4 != 0)) {
        FUN_00450500(*(undefined4 *)(iVar1 + iVar5 * 0x30 + 4),DAT_0050b150);
      }
    }
    FUN_00450500(DAT_0050b14c,DAT_0050b154);
    *DAT_0050b158 = 0;
    *DAT_0050b15c = 0;
    *DAT_0050af9c = 0;
    piVar2 = DAT_0050b160;
    if (*DAT_0050b160 != 0) {
      ui_common_api_fn_00509c96(*DAT_0050b160);
      *piVar2 = 0;
    }
    iVar5 = FUN_0044ddea(*piVar3);
    while (iVar5 = iVar5 + -1, -1 < iVar5) {
      iVar4 = FUN_0044dce2(*piVar3,iVar5);
      if (iVar4 != 0) {
        FUN_0044d7b8();
      }
    }
    for (iVar5 = 0; iVar5 < 4; iVar5 = iVar5 + 1) {
      *(undefined4 *)(iVar1 + iVar5 * 0x30) = 0;
      *(undefined4 *)(iVar5 * 0x30 + iVar1 + 4) = 0;
      *(undefined4 *)(iVar5 * 0x30 + iVar1 + 8) = 0;
      *(undefined4 *)(iVar5 * 0x30 + iVar1 + 0xc) = 0;
      *(undefined4 *)(iVar5 * 0x30 + iVar1 + 0x10) = 0;
      *(undefined4 *)(iVar5 * 0x30 + iVar1 + 0x14) = 0;
      *(undefined4 *)(iVar5 * 0x30 + iVar1 + 0x18) = 0;
      *(undefined1 *)(iVar5 * 0x30 + iVar1 + 0x29) = 0;
    }
    *DAT_0050b044 = 0;
    if (*(int *)(DAT_0050aaf8 + *DAT_0050aaf4 * 8 + 4) != 0) {
      FUN_0044d878(*(undefined4 *)(DAT_0050aaf8 + *DAT_0050aaf4 * 8 + 4));
    }
    FUN_0050a094();
  }
  return in_r3;
}

