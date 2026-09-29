
undefined8 FUN_0049eb1e(byte param_1,undefined4 param_2,undefined4 param_3,uint param_4)

{
  int iVar1;
  uint uVar2;
  
  iVar1 = FUN_0043d0ce();
  if (iVar1 << 0x1e < 0) {
    param_4 = (uint)param_1;
    param_2 = 0x42;
    param_3 = DAT_0049efb0;
    FUN_0043d574(3,DAT_0049efbc,DAT_0049efb8,DAT_0049efb4,0x42,DAT_0049efb0,param_4);
  }
  iVar1 = FUN_0043d0ce();
  if (-1 < iVar1 << 0x1f) {
    iVar1 = FUN_0043d0ce();
    if (-1 < iVar1 << 0x1d) goto LAB_0049eb6e;
  }
  compress_log_output(0xc400000,DAT_0049efc0,DAT_0049efc0,param_1,param_2,param_3,param_4);
LAB_0049eb6e:
  uVar2 = FUN_0049ead8();
  if (param_1 != uVar2) {
    iVar1 = settings_get_config();
    *(byte *)(iVar1 + 0x14) = param_1;
    FUN_0049ebb6(*DAT_0049efc4 & 0xff);
  }
  return CONCAT44(param_3,param_2);
}

