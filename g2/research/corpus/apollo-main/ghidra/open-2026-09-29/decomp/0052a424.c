
void wsfTimerInsert(int param_1,undefined4 param_2)

{
  undefined4 *puVar1;
  undefined4 *puVar2;
  undefined4 *puVar3;
  
  WsfTaskLock();
  if (*(char *)(param_1 + 0xd) != '\0') {
    wsfTimerRemove(param_1);
  }
  *(undefined1 *)(param_1 + 0xd) = 1;
  *(undefined4 *)(param_1 + 4) = param_2;
  puVar1 = (undefined4 *)*DAT_0052a614;
  puVar3 = (undefined4 *)0x0;
  while ((puVar2 = puVar1, puVar2 != (undefined4 *)0x0 &&
         ((uint)puVar2[1] <= *(uint *)(param_1 + 4)))) {
    puVar3 = puVar2;
    puVar1 = (undefined4 *)*puVar2;
  }
  WsfQueueInsert(DAT_0052a614,param_1,puVar3);
  WsfTaskUnlock();
  return;
}

