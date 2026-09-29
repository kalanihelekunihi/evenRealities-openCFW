
void driver_a6ng_read_register(uint param_1,undefined4 param_2,undefined4 param_3,char param_4)

{
  byte bVar1;
  undefined1 auStack_30 [4];
  uint local_2c;
  undefined4 local_24;
  undefined4 local_1c;
  undefined4 local_18;
  
  bVar1 = 0x79;
  if (param_4 == '\x01') {
    bVar1 = 0x7b;
  }
  FUN_00439c04(auStack_30,DAT_005bc89c,0x1c);
  local_2c = param_1 & 0xff | (uint)bVar1 << 8;
  local_18 = *DAT_005bc87c;
  local_24 = param_3;
  local_1c = param_2;
  am_devices_mspi_read(auStack_30);
  return;
}

