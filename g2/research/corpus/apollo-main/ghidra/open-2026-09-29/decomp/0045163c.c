
bool FUN_0045163c(int *param_1,int *param_2)

{
  int iVar1;
  int iVar2;
  int iVar3;
  
  iVar2 = (param_1[2] - *param_1) / 2;
  iVar3 = *param_2 - (iVar2 + *param_1);
  iVar1 = param_2[1] - (iVar2 + param_1[1]);
  return (uint)(iVar3 * iVar3 + iVar1 * iVar1) <= (uint)(iVar2 * iVar2);
}

