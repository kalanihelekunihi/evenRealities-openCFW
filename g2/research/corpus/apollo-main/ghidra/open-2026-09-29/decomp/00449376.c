
undefined8 osDelay(int param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  undefined4 uVar2;
  
  iVar1 = IRQ_Context();
  if (iVar1 == 0) {
    uVar2 = 0;
    if (param_1 != 0) {
      FUN_00454b4c(param_1);
    }
  }
  else {
    uVar2 = 0xfffffffa;
  }
  return CONCAT44(param_4,uVar2);
}

