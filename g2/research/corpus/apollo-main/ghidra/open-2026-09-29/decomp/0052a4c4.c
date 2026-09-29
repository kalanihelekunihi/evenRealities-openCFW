
undefined4 WsfTimerStartMs(undefined4 param_1,uint param_2)

{
  undefined4 unaff_r7;
  
  wsfTimerInsert(param_1,param_2 / 10);
  return unaff_r7;
}

