
undefined4 dmPrivSetAddrResEnable(undefined1 param_1)

{
  undefined4 unaff_r7;
  
  *(undefined1 *)(DAT_004d2920 + 9) = param_1;
  HciLeSetAddrResolutionEnable(param_1);
  return unaff_r7;
}

