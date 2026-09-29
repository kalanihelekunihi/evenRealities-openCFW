
void FUN_004fa404(int param_1,int param_2)

{
  ushort uVar1;
  int *piVar2;
  ushort *puVar3;
  int *piVar4;
  int iVar5;
  int iVar6;
  int iVar7;
  short sVar8;
  int iVar9;
  uint uVar10;
  
  piVar2 = DAT_004fac60;
  if ((*DAT_004fac60 != 0) &&
     (iVar5 = FUN_0043e2ea(*DAT_004fac60), puVar3 = DAT_004fac4c, iVar5 != 0)) {
    uVar1 = DAT_004fac4c[0x1724];
    sVar8 = 0;
    if (0x28 < (uint)DAT_004fac4c[0x1724] + (uint)*DAT_004fac4c) {
      sVar8 = DAT_004fac4c[0x1724] + *DAT_004fac4c + -0x28;
    }
    iVar5 = FUN_0043d0ce();
    if (iVar5 << 0x1e < 0) {
      FUN_0043d574(4,DAT_004fa710,DAT_004fb07c,DAT_004faf90,0x10cf,DAT_004faf8c,*puVar3,uVar1,sVar8)
      ;
    }
    iVar5 = FUN_0043d0ce();
    if ((iVar5 << 0x1f < 0) || (iVar5 = FUN_0043d0ce(), iVar5 << 0x1d < 0)) {
      compress_log_output(0x10c00000,DAT_004faf94,DAT_004faf94,*puVar3,uVar1,sVar8);
    }
    iVar5 = 0;
    iVar9 = 0;
    if (sVar8 != 0) {
      for (uVar10 = (uint)(ushort)(*puVar3 - sVar8); (int)uVar10 < (int)(uint)*puVar3;
          uVar10 = uVar10 + 1) {
        if (*(int *)(DAT_004faa38 + uVar10 * 0x10) != 0) {
          iVar6 = FUN_0043fdda(*(undefined4 *)(DAT_004faa38 + uVar10 * 0x10));
          iVar5 = iVar6 + 4 + iVar5;
        }
      }
      iVar6 = FUN_0043d0ce();
      if (iVar6 << 0x1e < 0) {
        FUN_0043d574(4,DAT_004fa710,DAT_004fb07c,DAT_004faf90,0x10e1,DAT_004faf98,iVar5);
      }
      iVar6 = FUN_0043d0ce();
      if ((iVar6 << 0x1f < 0) || (iVar6 = FUN_0043d0ce(), iVar6 << 0x1d < 0)) {
        compress_log_output(0x10400000,DAT_004fb080,DAT_004fb080,iVar5);
      }
    }
    piVar4 = DAT_004fb0e4;
    if ((param_2 < 0) || ((int)(uint)*puVar3 <= param_2)) {
      if ((param_2 == -2) &&
         ((*DAT_004fb0e4 != 0 && (iVar6 = FUN_0043e0e0(*DAT_004fb0e4,1), iVar6 == 0)))) {
        iVar6 = FUN_0043fdda(*piVar4);
        iVar9 = iVar6 + 4;
        iVar7 = FUN_0043d0ce();
        if (iVar7 << 0x1e < 0) {
          FUN_0043d574(4,DAT_004fa710,DAT_004fb07c,DAT_004faf90,0x10f9,DAT_004fb0e8,iVar9,iVar6,
                       param_1);
        }
        iVar7 = FUN_0043d0ce();
        if ((iVar7 << 0x1f < 0) || (iVar7 = FUN_0043d0ce(), iVar7 << 0x1d < 0)) {
          compress_log_output(0x10c00000,DAT_004fb0ec,DAT_004fb0ec,iVar9,iVar6,param_1);
        }
      }
    }
    else if (*(int *)(DAT_004faa38 + param_2 * 0x10) != 0) {
      iVar6 = FUN_0043fce0(*(undefined4 *)(DAT_004faa38 + param_2 * 0x10));
      iVar9 = iVar6 - param_1;
      iVar7 = FUN_0043d0ce();
      if (iVar7 << 0x1e < 0) {
        FUN_0043d574(4,DAT_004fa710,DAT_004fb07c,DAT_004faf90,0x10ea,DAT_004fb084,param_2,iVar9,
                     iVar6,param_1);
      }
      iVar7 = FUN_0043d0ce();
      if ((iVar7 << 0x1f < 0) || (iVar7 = FUN_0043d0ce(), iVar7 << 0x1d < 0)) {
        compress_log_output(0x11000000,DAT_004fb088,DAT_004fb088,param_2,iVar9,iVar6,param_1);
      }
    }
    FUN_004f92f0();
    FUN_004f5596();
    FUN_004f9484();
    FUN_0043f66c(*piVar2);
    FUN_004f9bf8(param_2,sVar8,uVar1);
    FUN_004fa058(param_1,param_2,iVar9,2,iVar5,uVar1);
    if ((*DAT_004fb0e4 == 0) || (iVar5 = FUN_0043e0e0(*DAT_004fb0e4,1), iVar5 != 0)) {
      piVar2 = DAT_004faa2c;
      if ((-1 < *DAT_004faa2c) && (*DAT_004faa2c < (int)(uint)*puVar3)) {
        FUN_004f70a4(*DAT_004faa2c);
        FUN_004f9afc(*piVar2);
      }
    }
    else {
      FUN_004f80a0(1,2,uVar1);
    }
    iVar5 = FUN_0043d0ce();
    if (iVar5 << 0x1e < 0) {
      FUN_0043d574(4,DAT_004fa710,DAT_004fb07c,DAT_004faf90,0x111a,DAT_004fb0f0);
    }
    iVar5 = FUN_0043d0ce();
    if ((iVar5 << 0x1f < 0) || (iVar5 = FUN_0043d0ce(), iVar5 << 0x1d < 0)) {
      compress_log_output(0x10000000,DAT_004fb0f4,DAT_004fb0f4);
    }
  }
  return;
}

