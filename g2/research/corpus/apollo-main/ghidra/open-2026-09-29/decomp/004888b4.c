
int FUN_004888b4(int param_1,int param_2,int param_3,int param_4,int param_5)

{
  int iVar1;
  
  if (((((param_3 < param_2) || (iVar1 = param_5, param_1 < param_3)) &&
       ((param_3 < param_2 || (iVar1 = param_4, param_2 < param_1)))) &&
      ((param_2 < param_3 || (iVar1 = param_5, param_3 < param_1)))) &&
     ((param_2 < param_3 || (iVar1 = param_4, param_1 < param_2)))) {
    iVar1 = param_4 + ((param_5 - param_4) * (param_1 - param_2)) / (param_3 - param_2);
  }
  return iVar1;
}

