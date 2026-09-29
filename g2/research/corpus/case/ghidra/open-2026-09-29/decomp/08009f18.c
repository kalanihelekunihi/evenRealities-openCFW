
undefined4
calibrated_sensor_value_convert
          (undefined4 *param_1,undefined4 param_2,undefined4 param_3,uint param_4)

{
  int iVar1;
  undefined4 uVar2;
  int iVar3;
  uint local_18;
  uint local_14;
  
  local_18 = 0;
  local_14 = param_4 & 0xffffff00;
  iVar1 = case_invoke_mode_one(0xab,&local_14);
  if ((iVar1 != 0) || (iVar1 = case_read_stable_u16(0xe,&local_18), iVar1 != 0)) {
    return 0xffffffff;
  }
  iVar1 = case_sign_extend_u16(local_18 & 0xffff);
  if ((byte)local_14 >> 6 == 0) {
    uVar2 = DAT_08009f7c;
    iVar3 = DAT_08009f78;
    if ((byte)local_14 == 0) goto LAB_08009f6c;
  }
  else {
    iVar3 = 0x640;
  }
  uVar2 = FUN_0800018c(iVar3 * iVar1,DAT_08009f74);
LAB_08009f6c:
  *param_1 = uVar2;
  return 0;
}

