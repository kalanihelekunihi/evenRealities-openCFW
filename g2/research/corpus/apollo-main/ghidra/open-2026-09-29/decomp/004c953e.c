
undefined4 FUN_004c953e(void)

{
  undefined4 uVar1;
  int iVar2;
  undefined4 unaff_r7;
  
  uVar1 = osThreadGetId();
  osThreadSetPriority(uVar1,8);
  FUN_0054171c();
  uart_instance_init();
  iVar2 = productModeGet();
  if (iVar2 == 1) {
    FUN_0043d0c8(3);
  }
  (*(code *)*DAT_004c9c70)();
  (*(code *)*DAT_004c9c74)();
  (*(code *)*DAT_004c9c78)();
  (*(code *)*DAT_004c9c7c)();
  (*(code *)*DAT_004c9c80)();
  (*(code *)*DAT_004c9c84)();
  (*(code *)*DAT_004c9c88)();
  (*(code *)*DAT_004c9c8c)();
  (*(code *)*DAT_004c9c90)();
  (*(code *)*DAT_004c9c94)();
  uVar1 = osThreadGetId();
  osThreadSetPriority(uVar1,0x18);
  return unaff_r7;
}

