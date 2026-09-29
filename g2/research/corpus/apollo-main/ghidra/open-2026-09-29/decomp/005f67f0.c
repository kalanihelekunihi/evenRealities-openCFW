
void Ins_MIAP(int param_1,uint *param_2)

{
  int iVar1;
  undefined4 uVar2;
  int iVar3;
  int iVar4;
  undefined4 *puVar5;
  undefined4 *puVar6;
  uint uVar7;
  int iVar8;
  
  iVar8 = *(int *)(param_1 + 0x144);
  uVar7 = *param_2;
  if (((uVar7 & 0xffff) < (uint)*(ushort *)(param_1 + 0x2c)) &&
     (param_2[1] < *(uint *)(param_1 + 0x180))) {
    iVar1 = (**(code **)(param_1 + 600))(param_1,param_2[1]);
    if (*(short *)(param_1 + 0x15c) == 0) {
      uVar2 = TT_MulFix14(iVar1,(int)*(short *)(param_1 + 0x12e));
      *(undefined4 *)(*(int *)(param_1 + 0x30) + (uVar7 & 0xffff) * 8) = uVar2;
      uVar2 = TT_MulFix14(iVar1,(int)*(short *)(param_1 + 0x130));
      *(undefined4 *)(*(int *)(param_1 + 0x30) + (uVar7 & 0xffff) * 8 + 4) = uVar2;
      puVar5 = (undefined4 *)(*(int *)(param_1 + 0x30) + (uVar7 & 0xffff) * 8);
      uVar2 = puVar5[1];
      puVar6 = (undefined4 *)(*(int *)(param_1 + 0x34) + (uVar7 & 0xffff) * 8);
      *puVar6 = *puVar5;
      puVar6[1] = uVar2;
    }
    iVar3 = (**(code **)(param_1 + 0x240))
                      (param_1,*(undefined4 *)(*(int *)(param_1 + 0x34) + (uVar7 & 0xffff) * 8),
                       *(undefined4 *)(*(int *)(param_1 + 0x34) + (uVar7 & 0xffff) * 8 + 4));
    if ((int)((uint)*(byte *)(param_1 + 0x174) << 0x1f) < 0) {
      iVar4 = iVar1 - iVar3;
      if (iVar4 < 0) {
        iVar4 = -iVar4;
      }
      if (iVar8 < iVar4) {
        iVar1 = iVar3;
      }
      iVar1 = (**(code **)(param_1 + 0x23c))(param_1,iVar1,*(undefined4 *)(param_1 + 0x10c));
    }
    (**(code **)(param_1 + 0x24c))(param_1,param_1 + 0x24,uVar7 & 0xffff,iVar1 - iVar3);
  }
  else if (*(char *)(param_1 + 0x235) != '\0') {
    *(undefined4 *)(param_1 + 0xc) = 0x86;
  }
  *(short *)(param_1 + 0x120) = (short)uVar7;
  *(short *)(param_1 + 0x122) = (short)uVar7;
  return;
}

