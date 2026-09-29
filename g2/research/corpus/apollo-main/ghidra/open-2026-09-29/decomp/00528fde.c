
void FT_Vector_Unit(int *param_1)

{
  if (param_1 != (int *)0x0) {
    *param_1 = DAT_0052913c;
    param_1[1] = 0;
    ft_trig_pseudo_rotate(param_1);
    *param_1 = *param_1 + 0x80 >> 8;
    param_1[1] = param_1[1] + 0x80 >> 8;
  }
  return;
}

