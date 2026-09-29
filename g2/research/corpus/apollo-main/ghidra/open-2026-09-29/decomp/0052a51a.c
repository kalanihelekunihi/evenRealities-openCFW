
undefined4 WsfTimerNextExpiration(undefined1 *param_1)

{
  int *piVar1;
  undefined4 uVar2;
  
  WsfTaskLock();
  piVar1 = DAT_0052a614;
  if (*DAT_0052a614 == 0) {
    *param_1 = 0;
    uVar2 = 0;
  }
  else {
    *param_1 = 1;
    uVar2 = *(undefined4 *)(*piVar1 + 4);
  }
  WsfTaskUnlock();
  return uVar2;
}

