
undefined4 osThreadYield(void)

{
  int iVar1;
  undefined4 uVar2;
  
  iVar1 = IRQ_Context();
  if (iVar1 == 0) {
    uVar2 = 0;
    FUN_004420bc();
  }
  else {
    uVar2 = 0xfffffffa;
  }
  return uVar2;
}

