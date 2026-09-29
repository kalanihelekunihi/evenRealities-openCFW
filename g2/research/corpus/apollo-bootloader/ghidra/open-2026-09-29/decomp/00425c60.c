
undefined4 blocking_transfer_call(void)

{
  undefined4 uVar1;
  
  uVar1 = mspi_cq_pause();
  return uVar1;
}

