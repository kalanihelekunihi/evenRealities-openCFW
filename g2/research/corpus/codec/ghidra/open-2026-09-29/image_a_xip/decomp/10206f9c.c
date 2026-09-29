
void LvpQueueInit(undefined4 *param_1,undefined4 param_2,int param_3,int param_4)

{
  param_1[4] = param_4;
  param_1[2] = param_2;
  param_1[3] = param_4 * (param_3 / param_4);
  *param_1 = 0;
  param_1[1] = 0;
  return;
}

