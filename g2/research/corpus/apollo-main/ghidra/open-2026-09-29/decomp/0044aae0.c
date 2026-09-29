
undefined8 FUN_0044aae0(void)

{
  int iVar1;
  undefined4 uVar2;
  undefined4 unaff_r7;
  
  iVar1 = xTaskGetSchedulerState();
  uVar2 = DAT_0044ab10;
  if (iVar1 != 1) {
    xTaskGetCurrentTaskHandle();
    uVar2 = FUN_00454f16();
  }
  return CONCAT44(unaff_r7,uVar2);
}

