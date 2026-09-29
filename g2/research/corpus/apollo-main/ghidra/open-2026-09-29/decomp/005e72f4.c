
undefined4 FUN_005e72f4(int param_1)

{
  undefined4 uVar1;
  int iVar2;
  
  if (*(int *)(param_1 + 0x29c) == 0) {
    uVar1 = 0;
  }
  else {
    iVar2 = osKernelGetTickCount();
    if ((uint)(iVar2 - *(int *)(param_1 + 0x29c)) < 5000) {
      uVar1 = 1;
    }
    else {
      *(undefined4 *)(param_1 + 0x29c) = 0;
      uVar1 = 0;
    }
  }
  return uVar1;
}

