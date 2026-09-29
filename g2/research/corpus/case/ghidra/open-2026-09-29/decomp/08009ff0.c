
undefined4 sensor_default_value_read(undefined4 *param_1)

{
  int iVar1;
  
  iVar1 = case_invoke_mode_one(6);
  if (iVar1 != 0) {
    return 0xffffffff;
  }
  *param_1 = 0xfffffe70;
  return 0;
}

