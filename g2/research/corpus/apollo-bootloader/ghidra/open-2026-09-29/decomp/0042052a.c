
undefined8 FUN_0042052a(void)

{
  undefined4 uVar1;
  int iVar2;
  undefined4 unaff_r6;
  undefined4 uVar3;
  
  iVar2 = FUN_0042069e(0x66,0,0,0,0);
  uVar1 = DAT_00420c54;
  if (iVar2 != 0) {
    elog_output(1,DAT_00420adc,DAT_00420978,DAT_00420c58,0x2c4);
    unaff_r6 = uVar1;
  }
  FUN_0041f9d8(1);
  uVar3 = 0;
  iVar2 = FUN_0042069e(0x99,0,0,0);
  uVar1 = DAT_00420dfc;
  if (iVar2 != 0) {
    uVar3 = 0x2c9;
    elog_output(1,DAT_00420adc,DAT_00420978,DAT_00420c58);
    unaff_r6 = uVar1;
  }
  FUN_0041f9d8(0x32);
  return CONCAT44(unaff_r6,uVar3);
}

