
undefined8 FUN_0041fe9c(void)

{
  undefined4 uVar1;
  int iVar2;
  undefined4 unaff_r5;
  undefined4 unaff_r6;
  
  if ((*DAT_0042087c != 0) &&
     (iVar2 = FUN_004166aa(*DAT_0042087c,0xffffffff), uVar1 = DAT_0042088c, iVar2 != 0)) {
    unaff_r5 = 0xc3;
    elog_output(1,DAT_00420adc,DAT_00420978,DAT_0042097c);
    unaff_r6 = uVar1;
  }
  return CONCAT44(unaff_r6,unaff_r5);
}

