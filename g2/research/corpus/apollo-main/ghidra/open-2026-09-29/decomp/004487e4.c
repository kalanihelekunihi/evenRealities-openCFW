
undefined8 OTA_SetInterface(uint param_1,undefined4 param_2,undefined *param_3,undefined4 param_4)

{
  int iVar1;
  undefined *puVar2;
  uint uVar3;
  
  *DAT_00448868 = (char)param_1;
  uVar3 = param_1;
  iVar1 = FUN_0043d0ce();
  if (iVar1 << 0x1e < 0) {
    param_3 = DAT_004488d4;
    if ((param_1 & 0xff) != 1) {
      param_3 = &DAT_0044884c;
    }
    uVar3 = 0x7c6;
    param_2 = DAT_004488d8;
    FUN_0043d574(4,DAT_004488e4,DAT_004488e0,DAT_004488dc,0x7c6,DAT_004488d8,param_3,param_4);
  }
  iVar1 = FUN_0043d0ce();
  if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
    puVar2 = DAT_004488d4;
    if ((param_1 & 0xff) != 1) {
      puVar2 = &DAT_0044884c;
    }
    compress_log_output(0x10400000,DAT_004488e8,DAT_004488e8,puVar2,uVar3,param_2,param_3);
  }
  return CONCAT44(param_2,uVar3);
}

