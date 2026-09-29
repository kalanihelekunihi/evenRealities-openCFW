
void FUN_0044d16e(int *param_1)

{
  if (*(int *)(*param_1 + 8) != 0) {
    (**(code **)(*param_1 + 8))(*param_1,param_1);
  }
  if (*(int *)*param_1 != 0) {
    *param_1 = *(int *)*param_1;
    FUN_0044d16e(param_1);
  }
  return;
}

