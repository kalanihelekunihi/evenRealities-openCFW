
undefined8
free_touch_firmware_memory
          (undefined4 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int *piVar1;
  int iVar2;
  undefined4 local_10;
  undefined4 local_c;
  
  piVar1 = DAT_0056108c;
  local_10 = param_3;
  local_c = param_4;
  if (*DAT_0056108c != 0) {
    file_heap_free(*DAT_0056108c);
    *piVar1 = 0;
    *DAT_00561090 = 0;
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      local_c = DAT_00561094;
      local_10 = 0x2b3;
      FUN_0043d574(4,DAT_005608c8,DAT_005608c4,DAT_00561098);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x10000000,DAT_0056109c,DAT_0056109c);
    }
  }
  return CONCAT44(local_c,local_10);
}

