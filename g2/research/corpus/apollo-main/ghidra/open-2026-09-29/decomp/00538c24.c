
undefined4 WsfQueueEnq(int *param_1,undefined4 *param_2,undefined4 param_3,undefined4 param_4)

{
  *param_2 = 0;
  WsfCsEnter();
  if (*param_1 == 0) {
    *param_1 = (int)param_2;
    param_1[1] = (int)param_2;
  }
  else {
    *(undefined4 **)param_1[1] = param_2;
    param_1[1] = (int)param_2;
  }
  WsfCsExit();
  return param_4;
}

