
void FUN_0057f530(undefined4 param_1,int param_2,int param_3,int *param_4)

{
  if (param_3 == 0) {
    *param_4 = param_2 + *param_4;
    param_4[3] = param_4[3] + 1;
  }
  else {
    param_4[1] = param_2 + param_4[1];
  }
  param_4[2] = param_4[2] + 1;
  return;
}

