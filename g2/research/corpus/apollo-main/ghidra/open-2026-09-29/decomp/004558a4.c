
undefined4 xTaskGetSchedulerState(void)

{
  undefined4 uVar1;
  
  if (*DAT_00456064 == 0) {
    uVar1 = 1;
  }
  else if (*DAT_00456068 == 0) {
    uVar1 = 2;
  }
  else {
    uVar1 = 0;
  }
  return uVar1;
}

