
undefined8 FUN_0052a284(undefined4 param_1,int param_2,uint param_3,int param_4,code *param_5)

{
  int iVar1;
  int iVar2;
  
  while (param_3 != 0) {
    iVar2 = param_2 + param_4 * (param_3 >> 1);
    iVar1 = (*param_5)(param_1,iVar2);
    if (iVar1 < 1) {
      if (-1 < iVar1) goto LAB_0052a2d2;
      param_3 = param_3 >> 1;
    }
    else {
      param_3 = (param_3 >> 1) - (param_3 & 1 ^ 1);
      param_2 = iVar2 + param_4;
    }
  }
  iVar2 = 0;
LAB_0052a2d2:
  return CONCAT44(param_4,iVar2);
}

