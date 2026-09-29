
undefined8 FT_Vector_Rotate(int *param_1,int param_2,int param_3,int param_4)

{
  int iVar1;
  uint uVar2;
  int iVar3;
  int local_18;
  int local_14;
  
  iVar1 = param_3;
  local_14 = param_4;
  if ((param_1 != (int *)0x0) && (iVar1 = param_3, param_2 != 0)) {
    local_18 = *param_1;
    local_14 = param_1[1];
    if ((local_18 != 0) || (iVar1 = 0, local_14 != 0)) {
      uVar2 = ft_trig_prenorm(&local_18);
      ft_trig_pseudo_rotate(&local_18,param_2);
      local_18 = ft_trig_downscale(local_18);
      local_14 = ft_trig_downscale(local_14);
      iVar1 = local_18;
      if ((int)uVar2 < 1) {
        *param_1 = local_18 << (-uVar2 & 0xff);
        param_1[1] = local_14 << (-uVar2 & 0xff);
      }
      else {
        iVar3 = 1 << (uVar2 + 0xff & 0xff);
        *param_1 = iVar3 + local_18 + (local_18 >> 0x1f) >> (uVar2 & 0xff);
        param_1[1] = iVar3 + local_14 + (local_14 >> 0x1f) >> (uVar2 & 0xff);
      }
    }
  }
  local_18 = iVar1;
  return CONCAT44(local_14,local_18);
}

