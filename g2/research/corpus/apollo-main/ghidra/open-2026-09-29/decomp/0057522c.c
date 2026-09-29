
undefined8 pt_cmd_49_handler(int param_1,uint param_2,undefined1 *param_3,undefined1 *param_4)

{
  char *pcVar1;
  undefined1 uVar2;
  int iVar3;
  undefined4 uVar4;
  uint local_20;
  undefined4 local_1c;
  undefined1 *local_18;
  
  local_20 = param_2;
  local_1c = param_3;
  local_18 = param_4;
  iVar3 = FUN_0043d0ce();
  if (iVar3 << 0x1e < 0) {
    local_1c = DAT_00575ae8;
    local_20 = 0xba5;
    FUN_0043d574(3,DAT_00575414,DAT_00575410,DAT_00575aec);
  }
  iVar3 = FUN_0043d0ce();
  if (-1 < iVar3 << 0x1f) {
    iVar3 = FUN_0043d0ce();
    if (-1 < iVar3 << 0x1d) goto LAB_00575276;
  }
  compress_log_output(0xc000000,DAT_00575af0,DAT_00575af0);
LAB_00575276:
  pcVar1 = DAT_00575af4;
  if ((((param_3 == (undefined1 *)0x0) || (param_4 == (undefined1 *)0x0)) || (param_1 == 0)) ||
     ((param_2 & 0xff) < 4)) {
    iVar3 = FUN_0043d0ce();
    if (iVar3 << 0x1e < 0) {
      local_18 = DAT_00575aec;
      local_1c = DAT_00575418;
      local_20 = 0xba8;
      FUN_0043d574(1,DAT_00575414,DAT_00575410);
    }
    iVar3 = FUN_0043d0ce();
    if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
      compress_log_output(0x4400000,DAT_0057541c,DAT_0057541c,DAT_00575aec);
    }
    uVar4 = 0xffffffff;
  }
  else {
    *DAT_00575af4 = '\0';
    local_20 = *DAT_00575e7c;
    local_1c = (undefined1 *)DAT_00575e7c[1];
    local_18 = (undefined1 *)DAT_00575e7c[2];
    uVar2 = FUN_0045a568();
    local_1c = (undefined1 *)CONCAT31(local_1c._1_3_,uVar2);
    iVar3 = FUN_0045a568();
    if (iVar3 == 1) {
      uVar2 = 2;
    }
    else {
      uVar2 = 1;
    }
    local_1c._0_2_ = CONCAT11(uVar2,(undefined1)local_1c);
    FUN_004651e0(0x102,&local_20,0xc,0);
    *param_3 = 0x49;
    param_3[1] = 1;
    param_3[2] = 3;
    param_3[3] = 1;
    osDelay(0x14);
    if (*pcVar1 == '\0') {
      param_3[4] = 1;
    }
    else {
      param_3[4] = 0;
    }
    *param_4 = 5;
    uVar4 = 0;
  }
  return CONCAT44(local_20,uVar4);
}

