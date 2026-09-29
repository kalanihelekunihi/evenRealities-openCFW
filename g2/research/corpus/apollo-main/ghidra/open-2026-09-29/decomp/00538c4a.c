
undefined8 WsfQueueDeq(int *param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int *piVar1;
  
  WsfCsEnter();
  piVar1 = (int *)*param_1;
  if (piVar1 != (int *)0x0) {
    *param_1 = *piVar1;
    if (*param_1 == 0) {
      param_1[1] = 0;
    }
  }
  WsfCsExit();
  return CONCAT44(param_4,piVar1);
}

