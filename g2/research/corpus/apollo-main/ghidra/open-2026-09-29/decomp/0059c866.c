
undefined4 mspi_transfer_callback(undefined4 *param_1,undefined4 param_2)

{
  undefined4 unaff_r7;
  
  *param_1 = param_2;
  osSemaphoreRelease(*DAT_0059d164);
  return unaff_r7;
}

