
undefined4 L2cSlaveHandler(undefined4 param_1,int param_2)

{
  undefined4 unaff_r7;
  
  if ((param_2 != 0) && (*(char *)(param_2 + 2) == '\x01')) {
    l2cSlaveReqTimeout();
  }
  return unaff_r7;
}

