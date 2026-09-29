
undefined8 osMutexDelete(uint param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  undefined4 uVar2;
  
  iVar1 = IRQ_Context();
  if (iVar1 == 0) {
    if ((param_1 & 0xfffffffe) == 0) {
      uVar2 = 0xfffffffc;
    }
    else {
      uVar2 = 0;
      vQueueDelete(param_1 & 0xfffffffe);
    }
  }
  else {
    uVar2 = 0xfffffffa;
  }
  return CONCAT44(param_4,uVar2);
}

