
void driver_a6ng_write_register
               (undefined1 param_1,undefined1 param_2,char param_3,undefined4 param_4)

{
  uint uVar1;
  undefined4 uVar2;
  undefined4 local_30;
  undefined1 auStack_2c [24];
  undefined4 local_14;
  undefined4 uStack_10;
  
  local_30 = *DAT_005bc890;
  if (param_3 == '\x01') {
    uVar1 = (uint)local_30 >> 8;
    local_30 = CONCAT31((int3)uVar1,0x7a);
  }
  uVar2 = local_30;
  local_30._3_1_ = SUB41(uVar2,3);
  local_30._0_3_ = CONCAT12(param_2,CONCAT11(param_1,(undefined1)local_30));
  uStack_10 = param_4;
  FUN_00439be4(DAT_005bc894,&local_30,3);
  FUN_00439c04(auStack_2c,DAT_005bc898,0x1c);
  local_14 = *DAT_005bc87c;
  am_devices_mspi_write(auStack_2c);
  return;
}

