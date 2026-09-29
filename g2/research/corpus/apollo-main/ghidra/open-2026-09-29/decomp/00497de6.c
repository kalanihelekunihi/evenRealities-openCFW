
undefined8 service_even_ai_fn_00497de6(void)

{
  uint uVar1;
  undefined4 uVar2;
  undefined4 unaff_r7;
  
  uVar1 = osKernelGetTickCount();
  if ((uVar1 < *DAT_004985ac) || (uVar1 - *DAT_004985ac < 300)) {
    uVar2 = 1;
  }
  else {
    uVar2 = 0;
  }
  return CONCAT44(unaff_r7,uVar2);
}

