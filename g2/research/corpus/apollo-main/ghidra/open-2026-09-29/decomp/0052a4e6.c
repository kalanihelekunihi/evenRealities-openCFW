
undefined4 WsfTimerUpdate(uint param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  undefined4 *puVar1;
  
  WsfTaskLock();
  for (puVar1 = (undefined4 *)*DAT_0052a614; puVar1 != (undefined4 *)0x0;
      puVar1 = (undefined4 *)*puVar1) {
    if (param_1 < (uint)puVar1[1]) {
      puVar1[1] = puVar1[1] - param_1;
    }
    else {
      puVar1[1] = 0;
      WsfTaskSetReady(*(undefined1 *)(puVar1 + 3),2);
    }
  }
  WsfTaskUnlock();
  return param_4;
}

