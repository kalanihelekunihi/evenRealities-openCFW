
undefined8 stage_one_wait_reg80(void)

{
  int iVar1;
  undefined4 unaff_r7;
  
  iVar1 = delay_status_change(1000,DAT_00423d9c,0x800000,0);
  return CONCAT44(unaff_r7,(uint)(iVar1 == 0));
}

