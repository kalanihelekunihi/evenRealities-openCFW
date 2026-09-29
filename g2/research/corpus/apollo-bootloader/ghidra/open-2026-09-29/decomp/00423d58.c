
undefined8 stage_one_status(void)

{
  int iVar1;
  undefined4 uVar2;
  undefined4 unaff_r7;
  
  iVar1 = stage_one_wait_zero();
  if ((iVar1 == 0) || (iVar1 = stage_one_wait_reg80(), iVar1 == 0)) {
    uVar2 = 4;
  }
  else {
    delay_us(500);
    uVar2 = 0;
  }
  return CONCAT44(unaff_r7,uVar2);
}

