
undefined8 FT_Vector_Length(int *param_1,undefined4 param_2,int param_3)

{
  uint uVar1;
  int local_10;
  int local_c;
  
  if (param_1 == (int *)0x0) {
    local_c = 0;
    local_10 = param_3;
  }
  else {
    local_10 = *param_1;
    local_c = param_1[1];
    if (local_10 == 0) {
      if (local_c < 0) {
        local_c = -local_c;
      }
    }
    else if (local_c == 0) {
      local_c = local_10;
      if (local_10 < 0) {
        local_c = -local_10;
      }
    }
    else {
      uVar1 = ft_trig_prenorm(&local_10);
      ft_trig_pseudo_polarize(&local_10);
      local_10 = ft_trig_downscale(local_10);
      if ((int)uVar1 < 1) {
        local_c = local_10 << (-uVar1 & 0xff);
      }
      else {
        local_c = (1 << (uVar1 + 0xff & 0xff)) + local_10 >> (uVar1 & 0xff);
      }
    }
  }
  return CONCAT44(local_10,local_c);
}

