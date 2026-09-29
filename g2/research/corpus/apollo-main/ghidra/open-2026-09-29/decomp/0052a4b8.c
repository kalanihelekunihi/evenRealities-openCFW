
undefined4 WsfTimerStartSec(undefined4 param_1,int param_2)

{
  undefined4 unaff_r7;
  
  wsfTimerInsert(param_1,param_2 * 100);
  return unaff_r7;
}

