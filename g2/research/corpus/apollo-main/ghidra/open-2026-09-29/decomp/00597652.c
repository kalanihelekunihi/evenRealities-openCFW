
undefined4 td_record_timer_clear(void)

{
  int iVar1;
  undefined4 unaff_r7;
  
  iVar1 = td_current_record();
  if (iVar1 != 0) {
    *(undefined4 *)(iVar1 + 0x88) = 0;
  }
  return unaff_r7;
}

