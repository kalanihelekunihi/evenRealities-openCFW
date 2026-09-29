
undefined8 WsfTimerServiceExpired(void)

{
  undefined4 in_r3;
  int iVar1;
  
  WsfTaskLock();
  iVar1 = *DAT_0052a614;
  if ((iVar1 == 0) || (*(int *)(iVar1 + 4) != 0)) {
    WsfTaskUnlock();
    iVar1 = 0;
  }
  else {
    WsfQueueRemove(DAT_0052a614,iVar1,0);
    *(undefined1 *)(iVar1 + 0xd) = 0;
    WsfTaskUnlock();
  }
  return CONCAT44(in_r3,iVar1);
}

