
void am_devices_mspi_jbd4010_setBrightness(undefined *param_1,int param_2,undefined *param_3)

{
  char cVar1;
  int iVar2;
  undefined *puVar3;
  undefined *local_30;
  int local_2c;
  undefined *local_28;
  undefined *local_24;
  int local_20;
  undefined *local_1c;
  
  cVar1 = FUN_0045a568();
  iVar2 = FUN_0043d0ce();
  if (iVar2 << 0x1e < 0) {
    if (cVar1 == '\x01') {
      local_28 = &DAT_00593080;
    }
    else if (cVar1 == '\x02') {
      local_28 = &DAT_00593084;
    }
    else {
      local_28 = &LAB_00593088;
    }
    local_2c = DAT_005938e8;
    local_30 = (undefined *)0x23c;
    local_24 = param_1;
    local_20 = param_2;
    local_1c = param_3;
    FUN_0043d574(3,DAT_00593320,DAT_0059331c,DAT_005938ec);
  }
  iVar2 = FUN_0043d0ce();
  if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
    if (cVar1 == '\x01') {
      puVar3 = &DAT_00593080;
    }
    else if (cVar1 == '\x02') {
      puVar3 = &DAT_00593084;
    }
    else {
      puVar3 = &LAB_00593088;
    }
    local_30 = param_1;
    local_2c = param_2;
    local_28 = param_3;
    compress_log_output(0xd000000,DAT_005938f0,DAT_005938f0,puVar3);
  }
  FUN_0043c0e4(&local_28,0x14,0);
  jbd4010_write_command(6,&local_28,0);
  jbd4010_write_command(0xa9,&local_28,0);
  local_30 = (undefined *)(param_2 >> 8);
  local_2c = param_2;
  jbd4010_write_command(0x36,&local_30,2);
  local_30 = param_3;
  jbd4010_write_command(0x46,&local_30,1);
  local_28 = (undefined *)0x4;
  jbd4010_write_command(0x31,&local_28,1);
  jbd4010_write_command(0xa3,&local_28,0);
  jbd4010_write_command(0x97,&local_28,0);
  FUN_004910f4(1);
  return;
}

