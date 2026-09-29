
void FUN_10003f1c(int *param_1,int *param_2,int param_3,int param_4,byte param_5)

{
  uint uVar1;
  int iVar2;
  int *piVar3;
  int iVar4;
  int iVar5;
  int iVar6;
  int iVar7;
  int iVar8;
  int *local_40;
  ushort auStack_34 [4];
  
  auStack_34[0] = 0xfff;
  auStack_34[1] = 0xf001;
  uVar1 = param_1[3];
  auStack_34[2] = 0;
  auStack_34[3] = 0;
  iVar5 = (uint)param_5 * (uint)auStack_34[(uVar1 & 0x3ff) >> 9];
  iVar4 = (uint)param_5 * (uint)auStack_34[(uVar1 & 0xff) >> 7];
  if (param_3 < 2) {
    iVar4 = 0;
    iVar5 = iVar4;
    local_40 = param_2;
  }
  else {
    iVar6 = 0;
    iVar7 = 0;
    iVar8 = 0;
    piVar3 = param_2;
    while( true ) {
      *piVar3 = *param_1 + iVar7;
      iVar2 = param_1[1];
      piVar3[3] = uVar1;
      piVar3[1] = iVar2 + iVar6;
      piVar3[4] = 0xfff;
      iVar8 = iVar8 + 1;
      iVar2 = FUN_100029c0(piVar3 + 6);
      piVar3[2] = iVar2;
      iVar7 = iVar7 + iVar5;
      iVar6 = iVar6 + iVar4;
      if (iVar8 == param_3 + -1) break;
      uVar1 = param_1[3];
      piVar3 = piVar3 + 6;
    }
    local_40 = param_2 + param_3 * 6 + -6;
    iVar4 = iVar4 * iVar8;
    uVar1 = param_1[3];
    iVar5 = iVar5 * iVar8;
  }
  iVar6 = *param_1;
  iVar7 = param_1[1];
  local_40[3] = uVar1 & 0xe7ffffff;
  param_4 = param_4 % 0xfff;
  if (param_4 == 0) {
    param_4 = 0xfff;
  }
  *local_40 = iVar5 + iVar6;
  local_40[1] = iVar7 + iVar4;
  local_40[4] = param_4;
  local_40[2] = 0;
  return;
}

