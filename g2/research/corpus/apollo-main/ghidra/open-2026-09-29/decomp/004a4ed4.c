
undefined4 semantic_emit_imu_event(undefined4 param_1,undefined4 param_2)

{
  undefined2 uVar1;
  int iVar2;
  
  uVar1 = hub_role_get();
  iVar2 = SVC_Settings_InputEventCheck();
  if (iVar2 != 0) {
    FUN_00465748(uVar1,param_1,param_2,0);
  }
  return 0;
}

