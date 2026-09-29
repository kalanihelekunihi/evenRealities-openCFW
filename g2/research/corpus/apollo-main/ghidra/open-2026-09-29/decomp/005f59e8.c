
undefined4 Ins_SFVTPV(int param_1)

{
  undefined4 unaff_r7;
  
  *(undefined4 *)(param_1 + 0x12e) = *(undefined4 *)(param_1 + 0x12a);
  Compute_Funcs();
  return unaff_r7;
}

