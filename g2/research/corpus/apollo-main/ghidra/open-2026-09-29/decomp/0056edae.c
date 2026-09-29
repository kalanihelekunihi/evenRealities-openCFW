
void smpActMaxAttempts(int param_1)

{
  undefined4 uVar1;
  
  smpActPairingCancel(param_1);
  uVar1 = SmpDbMaxAttemptReached(*(undefined1 *)(param_1 + 0x3d));
  *(undefined1 *)(param_1 + 0x1a) = 0x10;
  WsfTimerStartMs(param_1 + 0x10,uVar1);
  *(undefined1 *)(param_1 + 0x42) = 0;
  return;
}

