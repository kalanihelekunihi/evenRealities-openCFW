
undefined4 LvpAppEventTick(void)

{
  int *piVar1;
  int iVar2;
  uint uVar3;
  undefined4 uStack_10;
  undefined4 uStack_c;
  
  uStack_10 = 0;
  uStack_c = 0;
  iVar2 = LvpQueueGet(uRam10208d90,&uStack_10);
  piVar1 = piRam10208d94;
  if (((iVar2 != 0) && (*piRam10208d94 != 0)) && (uVar3 = *(uint *)(*piRam10208d94 + 8), uVar3 != 0)
     ) {
    (*(code *)(uVar3 & 0xfffffffe))(&uStack_10);
  }
  if ((*piVar1 != 0) && (uVar3 = *(uint *)(*piVar1 + 0xc), uVar3 != 0)) {
    (*(code *)(uVar3 & 0xfffffffe))();
  }
  gx8002_uart_async_tick();
  gx8002_watchdog_ping();
  return 0;
}

