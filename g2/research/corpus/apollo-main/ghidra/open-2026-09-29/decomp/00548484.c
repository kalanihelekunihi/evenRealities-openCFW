
void FUN_00548484(void)

{
  undefined4 *puVar1;
  undefined4 *puVar2;
  int iVar3;
  undefined4 in_r3;
  undefined4 uStack_70;
  undefined *puStack_6c;
  undefined4 uStack_60;
  undefined *puStack_50;
  undefined4 uStack_40;
  undefined4 uStack_10;
  
  uStack_10 = in_r3;
  iVar3 = FUN_0043d0ce();
  if (iVar3 << 0x1e < 0) {
    puStack_6c = (undefined *)DAT_00548f28;
    uStack_70 = 0x5d4;
    FUN_0043d574(4,DAT_00548b50,DAT_00548b4c,DAT_00548f2c);
  }
  iVar3 = FUN_0043d0ce();
  if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
    compress_log_output(0x10000000,DAT_00548f30,DAT_00548f30);
  }
  puVar2 = DAT_00548558;
  FUN_0043ded4(*DAT_00548558,1);
  puVar1 = DAT_00548554;
  FUN_0043dfa4(*DAT_00548554,1);
  FUN_00441488(*puVar1,0,0);
  FUN_00440656(*puVar1);
  FUN_00440656(*puVar2);
  FUN_004503d6(&uStack_70);
  uStack_70 = *puVar1;
  puStack_6c = PTR_FUN_00547abc_1_00548598;
  FUN_004506ce(&uStack_70,0,0xff);
  uStack_40 = 100;
  puStack_50 = PTR_LAB_00450688_1_0054859c;
  uStack_60 = DAT_00548f34;
  FUN_00450408(&uStack_70);
  return;
}

