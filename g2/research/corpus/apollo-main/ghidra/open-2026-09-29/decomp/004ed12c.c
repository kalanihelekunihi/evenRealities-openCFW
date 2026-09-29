
void FUN_004ed12c(int param_1)

{
  ushort uVar1;
  int iVar2;
  undefined4 uVar3;
  int iVar4;
  int iVar5;
  uint uVar6;
  int iVar7;
  
  if (param_1 == 0) {
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      FUN_0043d574(1,DAT_004ed6e4,DAT_004ed728,DAT_004ed738,0x72c,DAT_004ed734);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x4000000,DAT_004ed73c,DAT_004ed73c);
    }
  }
  else {
    uVar1 = FUN_004e9fd6();
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      FUN_0043d574(3,DAT_004ed6e4,DAT_004ed728,DAT_004ed738,0x732,DAT_004ed740,uVar1);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0xc400000,DAT_004ed744,DAT_004ed744,uVar1);
    }
    uVar6 = (uVar1 + 2) / 3;
    if (uVar6 < 2) {
      *DAT_004ed748 = 0;
      *DAT_004ed730 = 0;
    }
    else {
      *DAT_004ed730 = 1;
      if (3 < uVar6) {
        uVar6 = 3;
      }
      *DAT_004ed748 = uVar6;
      iVar5 = uVar6 * 0xc + -8;
      iVar7 = (0xfe - iVar5) / 2 + 0x11;
      iVar2 = FUN_0043d0ce();
      if (iVar2 << 0x1e < 0) {
        FUN_0043d574(4,DAT_004ed6e4,DAT_004ed728,DAT_004ed738,0x759,DAT_004ed74c,uVar6,iVar5,iVar7,
                     0x22f);
      }
      iVar2 = FUN_0043d0ce();
      if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
        compress_log_output(0x11000000,DAT_004ed750,DAT_004ed750,uVar6,iVar5,iVar7,0x22f);
      }
      for (iVar2 = 0; iVar5 = DAT_004ed754, iVar2 < (int)uVar6; iVar2 = iVar2 + 1) {
        uVar3 = FUN_0043de82(param_1);
        *(undefined4 *)(iVar5 + iVar2 * 4) = uVar3;
        FUN_0043f4c0(*(undefined4 *)(iVar5 + iVar2 * 4),4,4);
        FUN_0043f09a(*(undefined4 *)(iVar5 + iVar2 * 4),0x22f,iVar2 * 0xc + iVar7);
        FUN_0044131c(*(undefined4 *)(iVar5 + iVar2 * 4),0,0);
        FUN_0044146a(*(undefined4 *)(iVar5 + iVar2 * 4),0,0);
        FUN_0044130c(*(undefined4 *)(iVar5 + iVar2 * 4),0,0);
        iVar4 = FUN_004ebf20();
        if (iVar2 == iVar4) {
          uVar3 = FUN_0044104c(0xffffff);
          FUN_0044127e(*(undefined4 *)(iVar5 + iVar2 * 4),uVar3,0);
          FUN_0044129e(*(undefined4 *)(iVar5 + iVar2 * 4),0xff,0);
        }
        else {
          uVar3 = FUN_0044104c(DAT_004ed6c0);
          FUN_0044127e(*(undefined4 *)(iVar5 + iVar2 * 4),uVar3,0);
          FUN_0044129e(*(undefined4 *)(iVar5 + iVar2 * 4),0x96,0);
        }
        FUN_0043dfa4(*(undefined4 *)(iVar5 + iVar2 * 4),2);
      }
    }
  }
  return;
}

