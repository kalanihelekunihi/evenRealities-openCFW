
void WsfQueueRemove(int *param_1,int *param_2,int *param_3)

{
  WsfCsEnter();
  if (param_2 == (int *)*param_1) {
    *param_1 = *param_2;
  }
  else if (param_3 != (int *)0x0) {
    *param_3 = *param_2;
  }
  if (param_2 == (int *)param_1[1]) {
    param_1[1] = (int)param_3;
  }
  WsfCsExit();
  return;
}

