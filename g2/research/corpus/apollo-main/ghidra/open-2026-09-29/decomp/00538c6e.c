
undefined4 WsfQueuePush(int *param_1,int *param_2,undefined4 param_3,undefined4 param_4)

{
  WsfCsEnter();
  *param_2 = *param_1;
  if (*param_1 == 0) {
    param_1[1] = (int)param_2;
  }
  *param_1 = (int)param_2;
  WsfCsExit();
  return param_4;
}

