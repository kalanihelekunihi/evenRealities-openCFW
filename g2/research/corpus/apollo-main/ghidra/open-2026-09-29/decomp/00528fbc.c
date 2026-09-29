
undefined8 FT_Atan2(int param_1,int param_2)

{
  int unaff_r5;
  
  if (param_2 == 0 && param_1 == 0) {
    param_2 = 0;
    param_1 = unaff_r5;
  }
  else {
    ft_trig_prenorm(&stack0xfffffff0);
    ft_trig_pseudo_polarize(&stack0xfffffff0);
  }
  return CONCAT44(param_1,param_2);
}

