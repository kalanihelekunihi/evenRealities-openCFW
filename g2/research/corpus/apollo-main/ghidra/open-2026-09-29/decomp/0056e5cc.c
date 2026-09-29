
undefined4 smpStartRspTimer(int param_1)

{
  undefined4 unaff_r7;
  
  *(undefined1 *)(param_1 + 10) = 0xf;
  *(undefined1 *)(param_1 + 0xb) = 0xe1;
  WsfTimerStartSec(param_1,0x1e);
  return unaff_r7;
}

