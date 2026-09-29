
undefined4 osTimerIsRunning(int param_1)

{
  int iVar1;
  undefined4 uVar2;
  
  iVar1 = IRQ_Context();
  if ((iVar1 == 0) && (param_1 != 0)) {
    uVar2 = FUN_0047eaf6(param_1);
  }
  else {
    uVar2 = 0;
  }
  return uVar2;
}

