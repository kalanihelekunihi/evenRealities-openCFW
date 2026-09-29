
undefined4 dmSlaveAdvStopOnDisconnect(int param_1)

{
  undefined4 unaff_r7;
  
  if (*(char *)(param_1 + 3) == '\0') {
    GattValueUpdate(*DAT_0046e094);
  }
  return unaff_r7;
}

