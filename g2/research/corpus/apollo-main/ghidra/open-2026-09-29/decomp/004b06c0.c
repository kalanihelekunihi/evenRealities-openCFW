
void FUN_004b06c0(int param_1,int param_2,char param_3,char param_4,char param_5,char param_6)

{
  if (param_1 == 0) {
    param_1 = FUN_004c791a();
  }
  if ((((param_6 != '\0') || (param_2 != *(int *)(param_1 + 0x50))) ||
      (param_3 != *(char *)(param_1 + 0x54))) ||
     ((param_4 != *(char *)(param_1 + 0x55) || (param_5 != *(char *)(param_1 + 0x56))))) {
    FUN_00513924(param_2,(int)param_3,(int)param_4,(int)param_5);
    *(int *)(param_1 + 0x50) = param_2;
    *(char *)(param_1 + 0x54) = param_3;
    *(char *)(param_1 + 0x55) = param_4;
    *(char *)(param_1 + 0x56) = param_5;
  }
  return;
}

