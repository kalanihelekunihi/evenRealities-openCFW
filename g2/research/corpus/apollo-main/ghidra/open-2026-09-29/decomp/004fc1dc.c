
int FUN_004fc1dc(int param_1,int param_2)

{
  int iVar1;
  undefined4 *puVar2;
  undefined4 local_30;
  undefined4 local_2c;
  undefined1 local_28;
  undefined1 local_27;
  undefined1 local_26;
  undefined1 local_25;
  undefined1 local_24;
  undefined1 local_23;
  undefined1 local_20;
  undefined1 local_1f;
  undefined1 local_1e;
  undefined1 local_1d;
  undefined1 local_1c;
  undefined1 local_1b;
  undefined1 local_18;
  undefined1 local_17;
  undefined1 local_16;
  undefined1 local_15;
  undefined1 local_14;
  undefined1 local_13;
  undefined1 local_10;
  undefined1 local_f;
  undefined1 local_e;
  undefined1 local_d;
  undefined1 local_c;
  undefined1 local_b;
  
  if (*DAT_004fc5fc == 1) {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      local_2c = DAT_004fc600;
      local_30 = 0x397;
      FUN_0043d574(3,DAT_004fc60c,DAT_004fc608,DAT_004fc604);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0xc000000,DAT_004fc610,DAT_004fc610);
    }
    param_1 = 0;
  }
  else if (param_1 == 10) {
    local_10 = 0;
    local_f = 10;
    local_e = 0;
    local_d = 0;
    local_c = 0;
    local_b = 0;
    param_1 = FUN_00464bb2(1,&local_10,6,0);
  }
  else if (param_1 == 0x48) {
    local_18 = 0;
    local_17 = 0x48;
    local_16 = 0;
    local_15 = 0;
    local_14 = 0;
    local_13 = 0;
    param_1 = FUN_00464bb2(1,&local_18,6,0);
  }
  else if (param_1 == 0x49) {
    local_20 = 0;
    local_1f = 0x49;
    local_1e = 0;
    local_1d = 0;
    local_1c = 0;
    local_1b = 0;
    param_1 = FUN_00464bb2(1,&local_20,6,0);
  }
  else if (param_1 == 0x45) {
    puVar2 = *(undefined4 **)(param_2 + 0x10);
    local_28 = 0;
    local_27 = 0x45;
    local_26 = (undefined1)*puVar2;
    local_25 = (undefined1)((uint)*puVar2 >> 8);
    local_24 = (undefined1)puVar2[1];
    local_23 = (undefined1)((uint)puVar2[1] >> 8);
    param_1 = FUN_00464bb2(1,&local_28,6,0);
  }
  else if (param_1 == 0x44) {
    puVar2 = *(undefined4 **)(param_2 + 0x10);
    local_30 = CONCAT13((char)((uint)*puVar2 >> 8),CONCAT12((char)*puVar2,0x4400));
    local_2c._0_2_ = CONCAT11((char)((uint)puVar2[1] >> 8),(char)puVar2[1]);
    param_1 = FUN_00464bb2(1,&local_30,6,0);
  }
  return param_1;
}

