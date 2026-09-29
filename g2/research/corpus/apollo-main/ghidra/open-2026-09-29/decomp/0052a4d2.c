
void WsfTimerStop(undefined4 param_1)

{
  WsfTaskLock();
  wsfTimerRemove(param_1);
  WsfTaskUnlock();
  return;
}

