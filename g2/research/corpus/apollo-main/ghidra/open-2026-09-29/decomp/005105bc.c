
void CALLBACK_MGR_Notify(int *param_1,undefined4 param_2,undefined4 param_3)

{
  if (((param_1 != (int *)0x0) && (*param_1 != 0)) && ((char)param_1[1] != '\0')) {
    for (param_1 = (int *)*param_1; param_1 != (int *)0x0; param_1 = (int *)param_1[1]) {
      if (*param_1 != 0) {
        (*(code *)*param_1)(param_2,param_3);
      }
    }
  }
  return;
}

