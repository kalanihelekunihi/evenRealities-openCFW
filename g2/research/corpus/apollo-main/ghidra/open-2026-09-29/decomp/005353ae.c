
undefined4 AttsAddGroup(int param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  undefined4 *puVar1;
  undefined4 *puVar2;
  undefined4 *puVar3;
  
  WsfTaskLock();
  puVar1 = *(undefined4 **)(DAT_00535448 + 600);
  puVar3 = (undefined4 *)0x0;
  while ((puVar2 = puVar1, puVar2 != (undefined4 *)0x0 &&
         (*(ushort *)(puVar2 + 4) <= *(ushort *)(param_1 + 0x10)))) {
    puVar3 = puVar2;
    puVar1 = (undefined4 *)*puVar2;
  }
  WsfQueueInsert(DAT_00535448 + 600,param_1,puVar3);
  attsCsfSetHashUpdateStatus(1);
  WsfTaskUnlock();
  return param_4;
}

