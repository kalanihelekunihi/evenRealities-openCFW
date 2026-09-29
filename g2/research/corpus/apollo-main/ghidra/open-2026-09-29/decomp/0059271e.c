
void jbd4010_write_data_block
               (undefined4 param_1,undefined1 param_2,undefined1 param_3,undefined4 param_4,
               undefined4 param_5,undefined4 param_6)

{
  undefined1 local_38 [4];
  undefined4 local_34;
  undefined1 local_2f;
  undefined4 local_2c;
  undefined4 local_24;
  undefined4 local_20;
  undefined4 uStack_1c;
  
  uStack_1c = param_4;
  FUN_00439c04(local_38,DAT_00593308,0x1c);
  local_2c = param_6;
  local_24 = param_5;
  local_20 = *DAT_005932f8;
  local_38[0] = param_3;
  local_34 = param_4;
  local_2f = param_2;
  am_devices_mspi_qspi_write(local_38);
  return;
}

