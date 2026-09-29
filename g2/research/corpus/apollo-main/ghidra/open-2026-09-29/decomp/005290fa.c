
undefined4 FT_Vector_From_Polar(undefined4 *param_1,undefined4 param_2,undefined4 param_3)

{
  undefined4 unaff_r7;
  
  if (param_1 != (undefined4 *)0x0) {
    *param_1 = param_2;
    param_1[1] = 0;
    FT_Vector_Rotate(param_1,param_3);
  }
  return unaff_r7;
}

