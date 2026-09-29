
void FT_Add64(uint *param_1,int *param_2,uint *param_3)

{
  int iVar1;
  int iVar2;
  uint uVar3;
  uint uVar4;
  uint uVar5;
  
  uVar3 = *param_1;
  iVar2 = *param_2;
  uVar4 = *param_1;
  uVar5 = param_1[1];
  iVar1 = param_2[1];
  *param_3 = iVar2 + uVar3;
  param_3[1] = iVar1 + uVar5 + (uint)(iVar2 + uVar3 < uVar4);
  return;
}

