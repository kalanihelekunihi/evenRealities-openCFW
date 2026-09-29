
undefined8 threadBleWsfTakeTxReady(undefined2 param_1)

{
  int iVar1;
  undefined4 uVar2;
  undefined4 unaff_r7;
  
  if (*(int *)(DAT_004d0cdc + 0x14) == 0) {
    uVar2 = 0;
  }
  else {
    iVar1 = osSemaphoreAcquire(*(undefined4 *)(DAT_004d0cdc + 0x14),param_1);
    if (iVar1 == 0) {
      uVar2 = 1;
    }
    else if (iVar1 == -2) {
      uVar2 = 0;
    }
    else {
      uVar2 = 0;
    }
  }
  return CONCAT44(unaff_r7,uVar2);
}

