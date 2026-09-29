
undefined8 FUN_004e0cce(undefined4 param_1)

{
  int iVar1;
  undefined4 uVar2;
  undefined4 unaff_r5;
  
  if (((*DAT_004e1454 == 0) || (*(int *)(*DAT_004e1454 + 4) == 0)) || (*(int *)*DAT_004e1454 == 0))
  {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      unaff_r5 = 0x65;
      FUN_0043d574(1,DAT_004e1464,DAT_004e1460,DAT_004e145c,0x65,DAT_004e1458);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x4000000,DAT_004e1468,DAT_004e1468);
    }
    uVar2 = 0;
  }
  else {
    uVar2 = FUN_00493fa8(*DAT_004e1454,param_1);
  }
  return CONCAT44(unaff_r5,uVar2);
}

