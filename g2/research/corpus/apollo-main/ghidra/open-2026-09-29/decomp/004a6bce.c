
void HUB_IMUCalibParaInit(void)

{
  int iVar1;
  undefined4 local_40;
  undefined4 uStack_3c;
  undefined4 uStack_38;
  undefined4 local_34;
  undefined4 uStack_30;
  undefined4 uStack_2c;
  float local_28;
  float local_24;
  float local_20;
  float local_1c;
  float local_18;
  float local_14;
  float local_10;
  float local_c;
  float local_8;
  
  local_34 = 0;
  uStack_30 = 0;
  uStack_2c = 0;
  local_40 = 0;
  uStack_3c = 0;
  uStack_38 = 0;
  FUN_0048949c(&local_28,0x24);
  nvdbSensorCaldataAgRead(&local_34,&local_40,&local_28);
  semantic_set_orientation_matrix(&local_34,&local_40,&local_28);
  iVar1 = FUN_0043d0ce();
  if (iVar1 << 0x1e < 0) {
    FUN_0043d574(3,DAT_004a6ee0,DAT_004a6edc,DAT_004a73a8,0x13b,DAT_004a73a4,(double)local_28,
                 (double)local_24,(double)local_20,(double)local_1c,(double)local_18,
                 (double)local_14,(double)local_10,(double)local_c,(double)local_8);
  }
  iVar1 = FUN_0043d0ce();
  if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
    compress_log_output(0xe400000,DAT_004a73ac,DAT_004a73ac);
  }
  return;
}

