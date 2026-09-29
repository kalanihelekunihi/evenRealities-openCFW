
undefined8 set_product_mode(uint param_1,undefined4 param_2,uint param_3,undefined4 param_4)

{
  int iVar1;
  uint uVar2;
  
  uVar2 = param_1;
  iVar1 = FUN_0043d0ce();
  if (iVar1 << 0x1e < 0) {
    param_3 = param_1 & 0xff;
    uVar2 = 0x40;
    param_2 = DAT_004abebc;
    FUN_0043d574(2,DAT_004abeb0,DAT_004abeac,DAT_004abec0,0x40,DAT_004abebc,param_3,param_4);
  }
  iVar1 = FUN_0043d0ce();
  if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
    compress_log_output(0x8400000,DAT_004abec4,DAT_004abec4,param_1 & 0xff,uVar2,param_2,param_3);
  }
  *(char *)(DAT_004abea0 + 1) = (char)param_1;
  return CONCAT44(param_2,uVar2);
}

