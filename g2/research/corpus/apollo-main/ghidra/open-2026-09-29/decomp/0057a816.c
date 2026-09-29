
undefined8 DRV_Gx8002_Reboot(char param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  undefined4 local_10;
  undefined4 local_c;
  
  DRV_Gx8002_PowerOff();
  osDelay(100);
  DRV_Gx8002_PowerOn();
  if (param_1 == '\0') {
    osDelay(0x5dc);
  }
  iVar1 = FUN_0043d0ce();
  local_10 = param_3;
  local_c = param_4;
  if (iVar1 << 0x1e < 0) {
    local_c = DAT_0057a8f4;
    local_10 = 0xb9;
    FUN_0043d574(3,DAT_0057a898,DAT_0057a894,DAT_0057a8f8);
  }
  iVar1 = FUN_0043d0ce();
  if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
    compress_log_output(0xc000000,DAT_0057a8fc,DAT_0057a8fc);
  }
  return CONCAT44(local_c,local_10);
}

