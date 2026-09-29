
uint FUN_004239c2(int param_1,uint param_2,uint param_3,int param_4,code *param_5)

{
  int iVar1;
  uint uVar2;
  int iVar3;
  int iVar4;
  uint uVar5;
  int iVar6;
  
  uVar2 = param_2;
  iVar6 = param_1 + param_4 * param_2;
  while( true ) {
    iVar4 = uVar2 * 2;
    uVar5 = iVar4 + 2;
    iVar3 = param_1 + param_4 * uVar5;
    if (param_3 < uVar5) break;
    if ((uVar5 == param_3) || (iVar1 = (*param_5)(iVar3,iVar3 - param_4), uVar2 = uVar5, iVar1 < 0))
    {
      uVar2 = iVar4 + 1;
      iVar3 = iVar3 - param_4;
    }
    FUN_00423864(iVar6,iVar3,param_4);
    iVar6 = iVar3;
  }
  while( true ) {
    if (uVar2 <= param_2) {
      return param_2;
    }
    uVar2 = uVar2 - 1 >> 1;
    iVar4 = param_1 + param_4 * uVar2;
    iVar3 = (*param_5)(iVar6,iVar4);
    if (iVar3 < 1) break;
    FUN_00423864(iVar4,iVar6,param_4);
    iVar6 = iVar4;
  }
  return param_2;
}

