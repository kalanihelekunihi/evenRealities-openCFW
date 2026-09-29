
undefined4 osSemaphoreGetCount(int param_1)

{
  undefined4 uVar1;
  int iVar2;
  
  if (param_1 == 0) {
    uVar1 = 0;
  }
  else {
    iVar2 = IRQ_Context();
    if (iVar2 == 0) {
      uVar1 = FUN_00441e66(param_1);
    }
    else {
      uVar1 = FUN_00441e8a(param_1);
    }
  }
  return uVar1;
}

