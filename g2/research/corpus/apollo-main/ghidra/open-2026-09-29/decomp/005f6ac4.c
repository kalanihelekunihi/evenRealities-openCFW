
void Ins_MIRP(int param_1,uint *param_2)

{
  int iVar1;
  uint uVar2;
  int iVar3;
  uint uVar4;
  undefined4 uVar5;
  undefined4 *puVar6;
  undefined4 *puVar7;
  uint uVar8;
  int iVar9;
  int iVar10;
  
  iVar10 = *(int *)(param_1 + 0x138);
  iVar9 = *(int *)(param_1 + 0x144);
  uVar8 = *param_2;
  uVar4 = param_2[1];
  if ((((uVar8 & 0xffff) < (uint)*(ushort *)(param_1 + 0x50)) &&
      (uVar4 + 1 < *(int *)(param_1 + 0x180) + 1U)) &&
     (*(ushort *)(param_1 + 0x120) < *(ushort *)(param_1 + 0x2c))) {
    if (uVar4 == 0xffffffff) {
      uVar4 = 0;
    }
    else {
      uVar4 = (**(code **)(param_1 + 600))(param_1,uVar4);
    }
    if ((int)(uVar4 - *(int *)(param_1 + 0x14c)) < 0) {
      iVar1 = *(int *)(param_1 + 0x14c) - uVar4;
    }
    else {
      iVar1 = uVar4 - *(int *)(param_1 + 0x14c);
    }
    if (iVar1 < *(int *)(param_1 + 0x148)) {
      if ((int)uVar4 < 0) {
        uVar4 = -*(int *)(param_1 + 0x14c);
      }
      else {
        uVar4 = *(uint *)(param_1 + 0x14c);
      }
    }
    if (*(short *)(param_1 + 0x15e) == 0) {
      iVar1 = TT_MulFix14(uVar4,(int)*(short *)(param_1 + 0x12e));
      *(int *)(*(int *)(param_1 + 0x54) + (uVar8 & 0xffff) * 8) =
           iVar1 + *(int *)(*(int *)(param_1 + 0x30) + (uint)*(ushort *)(param_1 + 0x120) * 8);
      iVar1 = TT_MulFix14(uVar4,(int)*(short *)(param_1 + 0x130));
      *(int *)(*(int *)(param_1 + 0x54) + (uVar8 & 0xffff) * 8 + 4) =
           iVar1 + *(int *)(*(int *)(param_1 + 0x30) + (uint)*(ushort *)(param_1 + 0x120) * 8 + 4);
      puVar6 = (undefined4 *)(*(int *)(param_1 + 0x54) + (uVar8 & 0xffff) * 8);
      uVar5 = puVar6[1];
      puVar7 = (undefined4 *)(*(int *)(param_1 + 0x58) + (uVar8 & 0xffff) * 8);
      *puVar7 = *puVar6;
      puVar7[1] = uVar5;
    }
    uVar2 = (**(code **)(param_1 + 0x244))
                      (param_1,*(int *)(*(int *)(param_1 + 0x54) + (uVar8 & 0xffff) * 8) -
                               *(int *)(*(int *)(param_1 + 0x30) +
                                       (uint)*(ushort *)(param_1 + 0x120) * 8),
                       *(int *)(*(int *)(param_1 + 0x54) + (uVar8 & 0xffff) * 8 + 4) -
                       *(int *)(*(int *)(param_1 + 0x30) + (uint)*(ushort *)(param_1 + 0x120) * 8 +
                               4));
    iVar1 = (**(code **)(param_1 + 0x240))
                      (param_1,*(int *)(*(int *)(param_1 + 0x58) + (uVar8 & 0xffff) * 8) -
                               *(int *)(*(int *)(param_1 + 0x34) +
                                       (uint)*(ushort *)(param_1 + 0x120) * 8),
                       *(int *)(*(int *)(param_1 + 0x58) + (uVar8 & 0xffff) * 8 + 4) -
                       *(int *)(*(int *)(param_1 + 0x34) + (uint)*(ushort *)(param_1 + 0x120) * 8 +
                               4));
    if ((*(char *)(param_1 + 0x140) != '\0') && ((int)(uVar4 ^ uVar2) < 0)) {
      uVar4 = -uVar4;
    }
    if ((int)((uint)*(byte *)(param_1 + 0x174) << 0x1d) < 0) {
      if (*(short *)(param_1 + 0x15c) == *(short *)(param_1 + 0x15e)) {
        iVar3 = uVar4 - uVar2;
        if (iVar3 < 0) {
          iVar3 = -iVar3;
        }
        if (iVar9 < iVar3) {
          uVar4 = uVar2;
        }
      }
      iVar9 = (**(code **)(param_1 + 0x23c))
                        (param_1,uVar4,
                         *(undefined4 *)(param_1 + (*(byte *)(param_1 + 0x174) & 3) * 4 + 0x10c));
    }
    else {
      iVar9 = Round_None(param_1,uVar4,
                         *(undefined4 *)(param_1 + (*(byte *)(param_1 + 0x174) & 3) * 4 + 0x10c));
    }
    if ((int)((uint)*(byte *)(param_1 + 0x174) << 0x1c) < 0) {
      if ((int)uVar2 < 0) {
        if (-iVar10 < iVar9) {
          iVar9 = -iVar10;
        }
      }
      else if (iVar9 < iVar10) {
        iVar9 = iVar10;
      }
    }
    (**(code **)(param_1 + 0x24c))(param_1,param_1 + 0x48,uVar8 & 0xffff,iVar9 - iVar1);
  }
  else if (*(char *)(param_1 + 0x235) != '\0') {
    *(undefined4 *)(param_1 + 0xc) = 0x86;
  }
  *(undefined2 *)(param_1 + 0x122) = *(undefined2 *)(param_1 + 0x120);
  if ((int)((uint)*(byte *)(param_1 + 0x174) << 0x1b) < 0) {
    *(short *)(param_1 + 0x120) = (short)uVar8;
  }
  *(short *)(param_1 + 0x124) = (short)uVar8;
  return;
}

