
int FUN_004f6880(int param_1,int param_2)

{
  int *piVar1;
  int iVar2;
  undefined4 *puVar3;
  undefined4 local_30;
  undefined4 local_2c;
  undefined4 local_28;
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
  
  piVar1 = DAT_004f6fb8;
  if (*DAT_004f6fb8 == 0) {
    if (param_1 == 10) {
      local_10 = 0;
      local_f = 10;
      local_e = 0;
      local_d = 0;
      local_c = 0;
      local_b = 0;
      param_2 = FUN_00464bb2(1,&local_10,6,0);
    }
    else if (param_1 == 0x48) {
      local_18 = 0;
      local_17 = 0x48;
      local_16 = 0;
      local_15 = 0;
      local_14 = 0;
      local_13 = 0;
      param_2 = FUN_00464bb2(1,&local_18,6,0);
    }
    else if (param_1 == 0x49) {
      local_20 = 0;
      local_1f = 0x49;
      local_1e = 0;
      local_1d = 0;
      local_1c = 0;
      local_1b = 0;
      param_2 = FUN_00464bb2(1,&local_20,6,0);
    }
    else if (param_1 == 0x45) {
      puVar3 = *(undefined4 **)(param_2 + 0x10);
      local_28 = CONCAT13((char)((uint)*puVar3 >> 8),CONCAT12((char)*puVar3,0x4500));
      local_24 = (undefined1)puVar3[1];
      local_23 = (undefined1)((uint)puVar3[1] >> 8);
      param_2 = FUN_00464bb2(1,&local_28,6,0);
    }
    else if (param_1 == 0x44) {
      puVar3 = *(undefined4 **)(param_2 + 0x10);
      local_30 = CONCAT13((char)((uint)*puVar3 >> 8),CONCAT12((char)*puVar3,0x4400));
      local_2c._0_2_ = CONCAT11((char)((uint)puVar3[1] >> 8),(char)puVar3[1]);
      param_2 = FUN_00464bb2(1,&local_30,6,0);
    }
  }
  else {
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      local_28 = *piVar1;
      local_2c = DAT_004f6fbc;
      local_30 = 0x58a;
      FUN_0043d574(3,DAT_004f6d3c,DAT_004f6d38,DAT_004f6fc0);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0xc400000,DAT_004f7160,DAT_004f7160,*piVar1);
    }
    param_2 = 0;
  }
  return param_2;
}

