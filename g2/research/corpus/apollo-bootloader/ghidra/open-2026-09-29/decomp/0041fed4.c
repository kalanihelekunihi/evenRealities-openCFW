
undefined8 FUN_0041fed4(void)

{
  undefined4 uVar1;
  int iVar2;
  undefined4 unaff_r5;
  undefined4 unaff_r6;
  
  if ((*DAT_0042087c != 0) &&
     (iVar2 = FUN_00416710(*DAT_0042087c), uVar1 = DAT_00420980, iVar2 != 0)) {
    unaff_r5 = 0xcc;
    elog_output(1,DAT_00420adc,DAT_00420978,DAT_004209c0);
    unaff_r6 = uVar1;
  }
  return CONCAT44(unaff_r6,unaff_r5);
}

