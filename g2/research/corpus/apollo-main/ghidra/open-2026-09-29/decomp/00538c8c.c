
void WsfQueueInsert(int *param_1,undefined4 *param_2,undefined4 *param_3)

{
  WsfCsEnter();
  if ((*param_1 == 0) || (param_3 == (undefined4 *)param_1[1])) {
    WsfQueueEnq(param_1,param_2);
  }
  else if (param_3 == (undefined4 *)0x0) {
    WsfQueuePush(param_1,param_2);
  }
  else {
    *param_2 = *param_3;
    *param_3 = param_2;
  }
  WsfCsExit();
  return;
}

