
void FUN_004fa72c(int param_1,int param_2)

{
  ushort uVar1;
  ushort uVar2;
  int *piVar3;
  ushort *puVar4;
  int *piVar5;
  int iVar6;
  int iVar7;
  ushort uVar8;
  int iVar9;
  int iVar10;
  uint uVar11;
  
  piVar3 = DAT_004fac60;
  if ((*DAT_004fac60 != 0) &&
     (iVar6 = FUN_0043e2ea(*DAT_004fac60), puVar4 = DAT_004fac4c, iVar6 != 0)) {
    uVar2 = DAT_004fac4c[0x1724];
    uVar8 = 0;
    if (0x28 < (uint)DAT_004fac4c[0x1724] + (uint)*DAT_004fac4c) {
      uVar8 = (DAT_004fac4c[0x1724] + *DAT_004fac4c) - 0x28;
    }
    iVar6 = FUN_0043d0ce();
    if (iVar6 << 0x1e < 0) {
      FUN_0043d574(4,DAT_004fab14,DAT_004fb07c,DAT_004fb0fc,0x112d,DAT_004fb0f8,*puVar4,uVar2,uVar8)
      ;
    }
    iVar6 = FUN_0043d0ce();
    if ((iVar6 << 0x1f < 0) || (iVar6 = FUN_0043d0ce(), iVar6 << 0x1d < 0)) {
      compress_log_output(0x10c00000,DAT_004fb100,DAT_004fb100,*puVar4,uVar2,uVar8);
    }
    iVar6 = 0;
    iVar9 = 0;
    if (uVar8 != 0) {
      uVar1 = uVar8;
      if (*puVar4 < uVar8) {
        uVar1 = *puVar4;
      }
      uVar11 = (uint)uVar1;
      for (iVar10 = 0; iVar10 < (int)(uVar11 & 0xffff); iVar10 = iVar10 + 1) {
        if (*(int *)(DAT_004faa38 + iVar10 * 0x10) != 0) {
          iVar7 = FUN_0043fdda(*(undefined4 *)(DAT_004faa38 + iVar10 * 0x10));
          iVar6 = iVar7 + 4 + iVar6;
        }
      }
      iVar10 = FUN_0043d0ce();
      if (iVar10 << 0x1e < 0) {
        FUN_0043d574(4,DAT_004fab14,DAT_004fb07c,DAT_004fb0fc,0x1141,DAT_004fb104,iVar6);
      }
      iVar10 = FUN_0043d0ce();
      if ((iVar10 << 0x1f < 0) || (iVar10 = FUN_0043d0ce(), iVar10 << 0x1d < 0)) {
        compress_log_output(0x10400000,DAT_004fb108,DAT_004fb108,iVar6);
      }
    }
    piVar5 = DAT_004fb0e4;
    if (param_2 < 0) {
      if (((param_2 == -1) && (*DAT_004fb0e4 != 0)) &&
         (iVar10 = FUN_0043e0e0(*DAT_004fb0e4,1), iVar10 == 0)) {
        iVar10 = FUN_0043fce0(*piVar5);
        iVar9 = iVar10 - param_1;
        iVar7 = FUN_0043d0ce();
        if (iVar7 << 0x1e < 0) {
          FUN_0043d574(4,DAT_004fab14,DAT_004fb07c,DAT_004fb0fc,0x1152,DAT_004fb114,iVar9,iVar10,
                       param_1);
        }
        iVar7 = FUN_0043d0ce();
        if ((iVar7 << 0x1f < 0) || (iVar7 = FUN_0043d0ce(), iVar7 << 0x1d < 0)) {
          compress_log_output(0x10c00000,DAT_004fb118,DAT_004fb118,iVar9,iVar10,param_1);
        }
      }
    }
    else if (*(int *)(DAT_004faa38 + param_2 * 0x10) != 0) {
      iVar10 = FUN_0043fce0(*(undefined4 *)(DAT_004faa38 + param_2 * 0x10));
      iVar9 = iVar10 - param_1;
      iVar7 = FUN_0043d0ce();
      if (iVar7 << 0x1e < 0) {
        FUN_0043d574(4,DAT_004fab14,DAT_004fb07c,DAT_004fb0fc,0x114a,DAT_004fb10c,param_2,iVar9,
                     iVar10,param_1);
      }
      iVar7 = FUN_0043d0ce();
      if ((iVar7 << 0x1f < 0) || (iVar7 = FUN_0043d0ce(), iVar7 << 0x1d < 0)) {
        compress_log_output(0x11000000,DAT_004fb110,DAT_004fb110,param_2,iVar9,iVar10,param_1);
      }
    }
    FUN_004f92f0();
    FUN_004f5596();
    FUN_004f9484();
    FUN_0043f66c(*piVar3);
    FUN_004f9d84(param_2,uVar8,uVar2);
    FUN_004fa058(param_1,param_2,iVar9,3,iVar6,uVar2);
    if ((*DAT_004fb0e4 == 0) || (iVar6 = FUN_0043e0e0(*DAT_004fb0e4,1), iVar6 != 0)) {
      piVar3 = DAT_004faa2c;
      if ((-1 < *DAT_004faa2c) && (*DAT_004faa2c < (int)(uint)*puVar4)) {
        FUN_004f70a4(*DAT_004faa2c);
        FUN_004f9afc(*piVar3);
      }
    }
    else {
      FUN_004f80a0(0,3,uVar2);
    }
    iVar6 = FUN_0043d0ce();
    if (iVar6 << 0x1e < 0) {
      FUN_0043d574(4,DAT_004fab14,DAT_004fb07c,DAT_004fb0fc,0x117a,DAT_004fb11c);
    }
    iVar6 = FUN_0043d0ce();
    if ((iVar6 << 0x1f < 0) || (iVar6 = FUN_0043d0ce(), iVar6 << 0x1d < 0)) {
      compress_log_output(0x10000000,DAT_004fb120,DAT_004fb120);
    }
  }
  return;
}

