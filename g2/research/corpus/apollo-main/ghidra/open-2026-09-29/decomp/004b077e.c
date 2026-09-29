
void FUN_004b077e(int param_1,int *param_2,char param_3)

{
  if (param_1 == 0) {
    param_1 = FUN_004c791a();
  }
  if ((((param_3 != '\0') || (*param_2 != *(int *)(param_1 + 0x74))) ||
      (param_2[1] != *(int *)(param_1 + 0x78))) ||
     ((param_2[2] != *(int *)(param_1 + 0x7c) || (param_2[3] != *(int *)(param_1 + 0x80))))) {
    FUN_004b1488(*param_2,param_2[1],(param_2[2] - *param_2) + 1,(param_2[3] - param_2[1]) + 1);
    FUN_00439c04(param_1 + 0x74,param_2,0x10);
  }
  return;
}

