
undefined4 Ins_SDPVTL(int param_1,uint *param_2,undefined4 param_3,undefined4 param_4)

{
  int *piVar1;
  int iVar2;
  int *piVar3;
  int iVar4;
  int iVar5;
  uint uVar6;
  uint uVar7;
  uint uVar8;
  
  uVar6 = (uint)*(byte *)(param_1 + 0x174);
  uVar7 = param_2[1];
  uVar8 = *param_2;
  if (((uVar8 & 0xffff) < (uint)*(ushort *)(param_1 + 0x50)) &&
     ((uVar7 & 0xffff) < (uint)*(ushort *)(param_1 + 0x74))) {
    piVar1 = (int *)(*(int *)(param_1 + 0x54) + (uVar8 & 0xffff) * 8);
    piVar3 = (int *)(*(int *)(param_1 + 0x78) + (uVar7 & 0xffff) * 8);
    iVar4 = *piVar1 - *piVar3;
    iVar2 = piVar1[1] - piVar3[1];
    if (iVar2 == 0 && iVar4 == 0) {
      iVar4 = 0x4000;
      uVar6 = 0;
    }
    iVar5 = iVar4;
    if ((int)(uVar6 << 0x1f) < 0) {
      iVar5 = -iVar2;
      iVar2 = iVar4;
    }
    Normalize(iVar5,iVar2,param_1 + 0x126);
    piVar1 = (int *)(*(int *)(param_1 + 0x58) + (uVar8 & 0xffff) * 8);
    piVar3 = (int *)(*(int *)(param_1 + 0x7c) + (uVar7 & 0xffff) * 8);
    iVar4 = *piVar1 - *piVar3;
    iVar2 = piVar1[1] - piVar3[1];
    if (iVar2 == 0 && iVar4 == 0) {
      iVar4 = 0x4000;
      uVar6 = 0;
    }
    iVar5 = iVar4;
    if ((int)(uVar6 << 0x1f) < 0) {
      iVar5 = -iVar2;
      iVar2 = iVar4;
    }
    Normalize(iVar5,iVar2,param_1 + 0x12a);
    Compute_Funcs(param_1);
  }
  else if (*(char *)(param_1 + 0x235) != '\0') {
    *(undefined4 *)(param_1 + 0xc) = 0x86;
  }
  return param_4;
}

