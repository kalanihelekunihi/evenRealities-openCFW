
longlong Normalize(undefined2 *param_1,int param_2,undefined2 *param_3)

{
  undefined2 *local_10;
  int local_c;
  
  local_10 = param_3;
  if (param_2 != 0 || param_1 != (undefined2 *)0x0) {
    local_10 = param_1;
    local_c = param_2;
    FT_Vector_NormLen(&local_10);
    *param_3 = (short)((int)local_10 / 4);
    param_3[1] = (short)(local_c / 4);
  }
  return ZEXT48(local_10) << 0x20;
}

