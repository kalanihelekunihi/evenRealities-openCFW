
void jbd4010_write_command
               (undefined1 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  undefined1 auStack_30 [9];
  undefined1 local_27;
  undefined4 local_24;
  undefined4 local_1c;
  undefined4 local_18;
  undefined4 uStack_14;
  
  uStack_14 = param_4;
  FUN_00439c04(auStack_30,DAT_00593288,0x1c);
  local_18 = *DAT_005932f8;
  local_27 = param_1;
  local_24 = param_3;
  local_1c = param_2;
  am_devices_mspi_write(auStack_30);
  return;
}

