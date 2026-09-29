
undefined4 dmPrivActSetAddrResEnable(int param_1)

{
  undefined4 unaff_r7;
  
  dmPrivSetAddrResEnable(*(undefined1 *)(param_1 + 4));
  return unaff_r7;
}

