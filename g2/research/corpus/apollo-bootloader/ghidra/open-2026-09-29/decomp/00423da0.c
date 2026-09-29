
undefined8 stage_one_wait_index(int param_1)

{
  int iVar1;
  undefined4 unaff_r7;
  
  iVar1 = delay_status_change(1000,param_1 * 4 + -0x20000000,3,1);
  return CONCAT44(unaff_r7,(uint)(iVar1 == 0));
}

