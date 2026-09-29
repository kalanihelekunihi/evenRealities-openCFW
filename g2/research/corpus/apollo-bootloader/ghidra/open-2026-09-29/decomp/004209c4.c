
undefined8 FUN_004209c4(void)

{
  int iVar1;
  undefined4 in_r3;
  undefined4 uVar2;
  
  uVar2 = 0;
  iVar1 = FUN_0042069e(4,0,0,0,0,in_r3);
  if (iVar1 != 0) {
    uVar2 = 0x3fe;
    elog_output(2,DAT_00420adc,DAT_00421030,PTR_s_mx25u25643g_enable_write_disable_00421038,0x3fe,
                DAT_00420dfc);
  }
  return CONCAT44(uVar2,iVar1);
}

