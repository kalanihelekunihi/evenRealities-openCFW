
void FUN_004c5916(ushort param_1,undefined4 param_2,byte param_3,uint param_4)

{
  int iVar1;
  undefined4 local_30;
  uint local_2c;
  undefined4 local_28;
  undefined4 local_24;
  uint local_20;
  uint local_1c;
  uint uStack_18;
  
  uStack_18 = param_4;
  iVar1 = FUN_0043d0ce();
  if (iVar1 << 0x1e < 0) {
    local_1c = param_4 & 0xff;
    local_20 = (uint)param_3;
    local_28 = (uint)param_1;
    local_2c = DAT_004c6178;
    local_30 = 0x61;
    local_24 = param_2;
    FUN_0043d574(4,DAT_004c6184,DAT_004c6180,DAT_004c617c);
  }
  iVar1 = FUN_0043d0ce();
  if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
    local_28 = param_4 & 0xff;
    local_2c = (uint)param_3;
    local_30 = param_2;
    compress_log_output(0x11000000,DAT_004c6188,DAT_004c6188,param_1);
  }
  local_30 = CONCAT22(local_30._2_2_,param_1);
  local_28._0_2_ = CONCAT11((char)param_4,param_3);
  local_2c = param_2;
  FUN_00464d1c(0x108,&local_30,0xc,0);
  return;
}

