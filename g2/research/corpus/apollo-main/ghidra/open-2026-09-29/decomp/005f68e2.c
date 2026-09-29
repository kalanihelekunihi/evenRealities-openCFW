
undefined8 Ins_MDRP(int param_1,uint *param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  undefined4 uVar2;
  int iVar3;
  int *piVar4;
  int *piVar5;
  uint uVar6;
  int iVar7;
  undefined4 local_20;
  undefined4 local_1c;
  
  iVar7 = *(int *)(param_1 + 0x138);
  uVar6 = *param_2;
  local_20 = param_3;
  local_1c = param_4;
  if (((uVar6 & 0xffff) < (uint)*(ushort *)(param_1 + 0x50)) &&
     (*(ushort *)(param_1 + 0x120) < *(ushort *)(param_1 + 0x2c))) {
    if ((*(short *)(param_1 + 0x15c) == 0) || (*(short *)(param_1 + 0x15e) == 0)) {
      piVar4 = (int *)(*(int *)(param_1 + 0x54) + (uVar6 & 0xffff) * 8);
      piVar5 = (int *)(*(int *)(param_1 + 0x30) + (uint)*(ushort *)(param_1 + 0x120) * 8);
      iVar1 = (**(code **)(param_1 + 0x244))(param_1,*piVar4 - *piVar5,piVar4[1] - piVar5[1]);
    }
    else {
      piVar4 = (int *)(*(int *)(param_1 + 0x5c) + (uVar6 & 0xffff) * 8);
      piVar5 = (int *)(*(int *)(param_1 + 0x38) + (uint)*(ushort *)(param_1 + 0x120) * 8);
      if (*(int *)(param_1 + 0xe0) == *(int *)(param_1 + 0xe4)) {
        uVar2 = (**(code **)(param_1 + 0x244))(param_1,*piVar4 - *piVar5,piVar4[1] - piVar5[1]);
        iVar1 = FT_MulFix(uVar2,*(undefined4 *)(param_1 + 0xe0));
      }
      else {
        local_20 = FT_MulFix(*piVar4 - *piVar5,*(undefined4 *)(param_1 + 0xe0));
        local_1c = FT_MulFix(piVar4[1] - piVar5[1],*(undefined4 *)(param_1 + 0xe4));
        iVar1 = (**(code **)(param_1 + 0x244))(param_1,local_20,local_1c);
      }
    }
    if (((0 < *(int *)(param_1 + 0x148)) &&
        (iVar1 < *(int *)(param_1 + 0x148) + *(int *)(param_1 + 0x14c))) &&
       (*(int *)(param_1 + 0x14c) - *(int *)(param_1 + 0x148) < iVar1)) {
      if (iVar1 < 0) {
        iVar1 = -*(int *)(param_1 + 0x14c);
      }
      else {
        iVar1 = *(int *)(param_1 + 0x14c);
      }
    }
    if ((int)((uint)*(byte *)(param_1 + 0x174) << 0x1d) < 0) {
      iVar3 = (**(code **)(param_1 + 0x23c))
                        (param_1,iVar1,
                         *(undefined4 *)(param_1 + (*(byte *)(param_1 + 0x174) & 3) * 4 + 0x10c));
    }
    else {
      iVar3 = Round_None(param_1,iVar1,
                         *(undefined4 *)(param_1 + (*(byte *)(param_1 + 0x174) & 3) * 4 + 0x10c));
    }
    if ((int)((uint)*(byte *)(param_1 + 0x174) << 0x1c) < 0) {
      if (iVar1 < 0) {
        if (-iVar7 < iVar3) {
          iVar3 = -iVar7;
        }
      }
      else if (iVar3 < iVar7) {
        iVar3 = iVar7;
      }
    }
    iVar7 = (**(code **)(param_1 + 0x240))
                      (param_1,*(int *)(*(int *)(param_1 + 0x58) + (uVar6 & 0xffff) * 8) -
                               *(int *)(*(int *)(param_1 + 0x34) +
                                       (uint)*(ushort *)(param_1 + 0x120) * 8),
                       *(int *)(*(int *)(param_1 + 0x58) + (uVar6 & 0xffff) * 8 + 4) -
                       *(int *)(*(int *)(param_1 + 0x34) + (uint)*(ushort *)(param_1 + 0x120) * 8 +
                               4));
    (**(code **)(param_1 + 0x24c))(param_1,param_1 + 0x48,uVar6 & 0xffff,iVar3 - iVar7);
  }
  else if (*(char *)(param_1 + 0x235) != '\0') {
    *(undefined4 *)(param_1 + 0xc) = 0x86;
  }
  *(undefined2 *)(param_1 + 0x122) = *(undefined2 *)(param_1 + 0x120);
  *(short *)(param_1 + 0x124) = (short)uVar6;
  if ((int)((uint)*(byte *)(param_1 + 0x174) << 0x1b) < 0) {
    *(short *)(param_1 + 0x120) = (short)uVar6;
  }
  return CONCAT44(local_1c,local_20);
}

