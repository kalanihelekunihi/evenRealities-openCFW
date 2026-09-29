
int FUN_004eb33c(int param_1,int param_2)

{
  int iVar1;
  undefined4 *puVar2;
  undefined4 local_28;
  undefined4 local_24;
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
  
  if (param_1 == 10) {
    if (*(char *)(DAT_004eb740 + 0x124) == '\0') {
      local_10 = 0;
      local_f = 10;
      local_e = 0;
      local_d = 0;
      local_c = 0;
      local_b = 0;
      param_1 = FUN_00464bb2(1,&local_10,6,0);
    }
    else {
      iVar1 = FUN_0043d0ce();
      if (iVar1 << 0x1e < 0) {
        local_24 = DAT_004ebdf0;
        local_28 = 0x362;
        FUN_0043d574(4,DAT_004ebf1c,DAT_004ebdf8,DAT_004ebdf4);
      }
      iVar1 = FUN_0043d0ce();
      if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
        compress_log_output(0x10000000,DAT_004ebf2c,DAT_004ebf2c);
      }
      param_1 = 0;
    }
  }
  else if (param_1 == 0x48) {
    if (*(char *)(DAT_004eb740 + 0x124) == '\0') {
      local_18 = 0;
      local_17 = 0x48;
      local_16 = 0;
      local_15 = 0;
      local_14 = 0;
      local_13 = 0;
      param_1 = FUN_00464bb2(1,&local_18,6,0);
    }
    else {
      param_1 = 0;
    }
  }
  else if (param_1 != 0x49) {
    if (param_1 == 0x45) {
      if (*(char *)(DAT_004eb740 + 0x124) == '\0') {
        puVar2 = *(undefined4 **)(param_2 + 0x10);
        local_20 = 0;
        local_1f = 0x45;
        local_1e = (undefined1)*puVar2;
        local_1d = (undefined1)((uint)*puVar2 >> 8);
        local_1c = (undefined1)puVar2[1];
        local_1b = (undefined1)((uint)puVar2[1] >> 8);
        param_1 = FUN_00464bb2(1,&local_20,6,0);
      }
      else {
        param_1 = 0;
      }
    }
    else if (param_1 == 0x44) {
      if (*(char *)(DAT_004eb740 + 0x124) == '\0') {
        puVar2 = *(undefined4 **)(param_2 + 0x10);
        local_28 = CONCAT13((char)((uint)*puVar2 >> 8),CONCAT12((char)*puVar2,0x4400));
        local_24._0_2_ = CONCAT11((char)((uint)puVar2[1] >> 8),(char)puVar2[1]);
        param_1 = FUN_00464bb2(1,&local_28,6,0);
      }
      else {
        param_1 = 0;
      }
    }
  }
  return param_1;
}

