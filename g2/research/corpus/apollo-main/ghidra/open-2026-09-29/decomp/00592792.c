
void jbd4010_read_die_response
               (undefined1 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  undefined1 auStack_30 [4];
  undefined4 local_2c;
  undefined1 local_27;
  undefined4 local_24;
  undefined4 local_1c;
  undefined4 local_18;
  
  FUN_00439c04(auStack_30,DAT_00593310,0x1c);
  local_18 = *DAT_005932f8;
  local_2c = param_4;
  local_27 = param_1;
  local_24 = param_3;
  local_1c = param_2;
  am_devices_mspi_read(auStack_30);
  return;
}

