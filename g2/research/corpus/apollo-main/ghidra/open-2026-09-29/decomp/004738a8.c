
undefined8 FUN_004738a8(undefined4 param_1,undefined4 param_2,undefined *param_3,undefined4 param_4)

{
  int *piVar1;
  int iVar2;
  undefined4 local_10;
  
  piVar1 = DAT_0047390c;
  iVar2 = FUN_00441636(1,0,3);
  *piVar1 = iVar2;
  local_10 = param_3;
  if (*piVar1 == 0) {
    local_10 = PTR_s_display_buffer_lock_mutex_create_00473920;
    FUN_0044d25c(3,DAT_004738f0,0x140,PTR_s_display_buffer_lock_init_00473924);
  }
  FUN_004417ee(*piVar1,0,0,0);
  return CONCAT44(param_4,local_10);
}

