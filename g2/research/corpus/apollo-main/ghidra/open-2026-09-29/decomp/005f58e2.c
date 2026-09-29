
undefined4 Ins_SxVTL(int param_1,ushort param_2,ushort param_3,undefined4 param_4)

{
  undefined4 uVar1;
  int iVar2;
  int *piVar3;
  int iVar4;
  int iVar5;
  uint uVar6;
  int *piVar7;
  
  uVar6 = (uint)*(byte *)(param_1 + 0x174);
  if ((param_2 < *(ushort *)(param_1 + 0x74)) && (param_3 < *(ushort *)(param_1 + 0x50))) {
    piVar3 = (int *)(*(int *)(param_1 + 0x58) + (uint)param_3 * 8);
    piVar7 = (int *)(*(int *)(param_1 + 0x7c) + (uint)param_2 * 8);
    iVar4 = *piVar3 - *piVar7;
    iVar2 = piVar3[1] - piVar7[1];
    if (iVar2 == 0 && iVar4 == 0) {
      iVar4 = 0x4000;
      uVar6 = 0;
    }
    iVar5 = iVar4;
    if ((int)(uVar6 << 0x1f) < 0) {
      iVar5 = -iVar2;
      iVar2 = iVar4;
    }
    Normalize(iVar5,iVar2,param_4);
    uVar1 = 0;
  }
  else {
    if (*(char *)(param_1 + 0x235) != '\0') {
      *(undefined4 *)(param_1 + 0xc) = 0x86;
    }
    uVar1 = 1;
  }
  return uVar1;
}

