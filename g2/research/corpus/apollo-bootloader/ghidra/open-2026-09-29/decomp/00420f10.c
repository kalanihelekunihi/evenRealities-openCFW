
undefined8 FUN_00420f10(void)

{
  undefined4 uVar1;
  int iVar2;
  undefined4 unaff_r5;
  undefined4 unaff_r6;
  
  iVar2 = FUN_00420e08(DAT_004210b4);
  uVar1 = DAT_004210b8;
  if (iVar2 == 0) {
    FUN_0041ff34(0);
    iVar2 = am_hal_mspi_control(*DAT_00421010,0x18,&stack0xfffffff8);
    uVar1 = DAT_004210c0;
    if (iVar2 != 0) {
      unaff_r5 = 0x5c7;
      elog_output(2,DAT_00421034,DAT_00421030,DAT_004210bc);
      unaff_r6 = uVar1;
    }
  }
  else {
    unaff_r5 = 0x5c0;
    elog_output(2,DAT_00421034,DAT_00421030,DAT_004210bc);
    unaff_r6 = uVar1;
  }
  return CONCAT44(unaff_r6,unaff_r5);
}

