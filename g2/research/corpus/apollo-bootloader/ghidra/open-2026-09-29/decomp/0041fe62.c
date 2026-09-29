
undefined8 FUN_0041fe62(undefined4 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int *piVar1;
  int iVar2;
  undefined4 local_10;
  undefined4 local_c;
  
  piVar1 = DAT_0042087c;
  local_10 = param_3;
  local_c = param_4;
  if (*DAT_0042087c == 0) {
    iVar2 = bl_runtime_flags_create(DAT_00420880);
    *piVar1 = iVar2;
    if (*piVar1 == 0) {
      local_c = DAT_00420884;
      local_10 = 0xba;
      elog_output(1,DAT_00420adc,DAT_00420978,DAT_00420888);
    }
  }
  return CONCAT44(local_c,local_10);
}

