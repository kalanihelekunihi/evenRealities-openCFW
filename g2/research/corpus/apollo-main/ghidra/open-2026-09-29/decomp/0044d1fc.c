
void FUN_0044d1fc(undefined4 param_1,int *param_2)

{
  int iVar1;
  
  if (*(int *)*param_2 != 0) {
    iVar1 = *param_2;
    *param_2 = *(int *)*param_2;
    FUN_0044d1fc(param_1,param_2);
    *param_2 = iVar1;
  }
  if (*(int *)(*param_2 + 4) != 0) {
    (**(code **)(*param_2 + 4))(param_1,param_2);
  }
  return;
}

