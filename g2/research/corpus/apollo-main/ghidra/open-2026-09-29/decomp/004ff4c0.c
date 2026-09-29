
undefined8
FUN_004ff4c0(float param_1,float param_2,float param_3,uint param_4,int param_5,uint param_6,
            undefined4 param_7)

{
  bool bVar1;
  undefined4 uVar2;
  int iVar3;
  int iVar4;
  int iVar5;
  uint uVar6;
  uint uVar7;
  uint uVar8;
  uint uVar9;
  float fVar10;
  float fVar11;
  int local_48;
  undefined4 local_44;
  uint local_40;
  
  if (((param_1 <= 0.0) || ((int)((uint)(param_2 < 0.0) << 0x1f) < 0)) ||
     ((int)((uint)(param_1 < param_2) << 0x1f) < 0)) {
    uVar2 = 0;
  }
  else if (param_4 < 9) {
    osKernelGetTickCount();
    iVar4 = FUN_004ff214(param_4);
    FUN_0043c0e4(iVar4,0x1ff8,0);
    iVar5 = FUN_004ff31c(param_1,param_2,param_5,param_6);
    iVar3 = DAT_004ff8c0;
    if (iVar5 == 0) {
      iVar3 = FUN_0043d0ce();
      if (iVar3 << 0x1e < 0) {
        local_44 = DAT_004ff8b0;
        local_48 = 0x69c;
        local_40 = param_4;
        FUN_0043d574(1,DAT_004ff8a8,DAT_004ff8a4,DAT_004ff8a0);
      }
      iVar3 = FUN_0043d0ce();
      if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
        compress_log_output(0x4400000,DAT_004ff8b4,DAT_004ff8b4,param_4);
      }
      uVar2 = 0;
    }
    else if ((param_6 == 0) || (param_5 == 0)) {
      iVar3 = FUN_0043d0ce();
      if (iVar3 << 0x1e < 0) {
        local_44 = DAT_004ff8b8;
        local_48 = 0x6a3;
        FUN_0043d574(2,DAT_004ff8a8,DAT_004ff8a4,DAT_004ff8a0);
      }
      iVar3 = FUN_0043d0ce();
      if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
        compress_log_output(0x8000000,DAT_004ff8bc,DAT_004ff8bc);
      }
      uVar2 = 0;
    }
    else {
      fVar10 = param_3;
      if ((int)((uint)(param_2 < param_3) << 0x1f) < 0) {
        fVar10 = param_2;
      }
      *(float *)(DAT_004ff8c0 + param_4 * 4) = fVar10;
      iVar5 = DAT_004ff8c4;
      if ((int)((uint)(param_1 < param_3) << 0x1f) < 0) {
        param_1 = param_3;
      }
      if (-1 < (int)((uint)(param_2 < param_3) << 0x1f)) {
        param_2 = param_3;
      }
      *(float *)(DAT_004ff8c4 + param_4 * 4) = DAT_004ff850 / (param_1 - param_2);
      fVar10 = *(float *)(iVar3 + param_4 * 4);
      fVar11 = *(float *)(iVar5 + param_4 * 4);
      uVar9 = (uint)((param_3 - fVar10) * fVar11);
      if (0x3d < (uVar9 & 0xff)) {
        uVar9 = 0x3d;
      }
      for (iVar3 = 0; iVar3 < 0x84; iVar3 = iVar3 + 1) {
        if ((iVar3 % 8 != 6) && (iVar3 % 8 != 7)) {
          *(undefined1 *)(iVar4 + (0x3d - (uVar9 & 0xff)) * 0x84 + iVar3) = 0xff;
        }
      }
      if (param_6 < 0xb9) {
        uVar9 = param_6;
        if (0x83 < param_6) {
          uVar9 = 0x84;
        }
      }
      else {
        uVar9 = 0x84;
      }
      bVar1 = true;
      uVar7 = 0;
      for (iVar3 = 0; iVar3 < (int)uVar9; iVar3 = iVar3 + 1) {
        uVar2 = FUN_004ff2b8(iVar3,param_5,param_6,uVar9);
        uVar6 = FUN_004ff280(uVar2,fVar10,fVar11);
        if (bVar1) {
          uVar7 = (0x3d - (uVar6 & 0xff)) * 0x84 + iVar3;
          if (uVar7 < 0x1ff8) {
            *(undefined1 *)(iVar4 + uVar7) = 0xff;
          }
          bVar1 = false;
        }
        else if ((uVar6 & 0xff) < (uVar7 & 0xff)) {
          for (iVar5 = 0; iVar5 <= (int)(uVar7 - uVar6 & 0xff); iVar5 = iVar5 + 1) {
            uVar8 = ((0x3d - (uVar6 & 0xff)) - iVar5) * 0x84 + iVar3;
            if (uVar8 < 0x1ff8) {
              *(undefined1 *)(iVar4 + uVar8) = 0xff;
            }
          }
        }
        else if ((uVar7 & 0xff) < (uVar6 & 0xff)) {
          for (iVar5 = 0; iVar5 <= (int)(uVar6 - uVar7 & 0xff); iVar5 = iVar5 + 1) {
            uVar8 = (iVar5 + (0x3d - (uVar6 & 0xff))) * 0x84 + iVar3;
            if (uVar8 < 0x1ff8) {
              *(undefined1 *)(iVar4 + uVar8) = 0xff;
            }
          }
        }
        else {
          uVar7 = (0x3d - (uVar6 & 0xff)) * 0x84 + iVar3;
          if (uVar7 < 0x1ff8) {
            *(undefined1 *)(iVar4 + uVar7) = 0xff;
          }
        }
        uVar7 = uVar6;
      }
      osKernelGetTickCount(uVar7);
      local_44 = 0x1ff8;
      local_48 = iVar4;
      FUN_00475014(&local_48,1);
      uVar2 = 1;
    }
  }
  else {
    iVar3 = FUN_0043d0ce();
    if (iVar3 << 0x1e < 0) {
      local_44 = DAT_004ff89c;
      local_48 = 0x690;
      local_40 = param_4;
      FUN_0043d574(1,DAT_004ff8a8,DAT_004ff8a4,DAT_004ff8a0);
    }
    iVar3 = FUN_0043d0ce();
    if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
      compress_log_output(0x4400000,DAT_004ff8ac,DAT_004ff8ac,param_4);
    }
    uVar2 = 0;
  }
  return CONCAT44(param_7,uVar2);
}

