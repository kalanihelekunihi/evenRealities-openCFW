
undefined4 scaled_sensor_value_read(uint *param_1)

{
  int iVar1;
  int local_10;
  
  local_10 = 0;
  iVar1 = case_read_stable_u16(2,&local_10);
  if (iVar1 != 0) {
    return 0xffffffff;
  }
  *param_1 = (uint)(local_10 * 5) >> 4;
  return 0;
}

