
void wsfTimerRemove(undefined4 *param_1)

{
  undefined4 *puVar1;
  undefined4 *puVar2;
  undefined4 *puVar3;
  
  puVar1 = (undefined4 *)*DAT_0052a614;
  puVar3 = (undefined4 *)0x0;
  while ((puVar2 = puVar1, puVar2 != (undefined4 *)0x0 && (puVar2 != param_1))) {
    puVar3 = puVar2;
    puVar1 = (undefined4 *)*puVar2;
  }
  if (puVar2 != (undefined4 *)0x0) {
    WsfQueueRemove(DAT_0052a614,param_1,puVar3);
    *(undefined1 *)((int)param_1 + 0xd) = 0;
  }
  return;
}

