
void FUN_00482ff2(undefined4 param_1,int *param_2)

{
  int iVar1;
  
  iVar1 = *param_2;
  if ((*(int *)*param_2 != 0) && (*(int *)(*param_2 + 0x20) << 0xb < 0)) {
    *param_2 = *(int *)*param_2;
    FUN_00482ff2(param_1,param_2);
  }
  *param_2 = iVar1;
  FUN_00482fce(param_1,param_2);
  return;
}

