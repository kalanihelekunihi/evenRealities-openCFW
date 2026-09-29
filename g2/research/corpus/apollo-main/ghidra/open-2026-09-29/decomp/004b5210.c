
undefined4 AttMsgFree(int param_1,char param_2)

{
  byte bVar1;
  undefined4 unaff_r7;
  
  if ((param_2 == '\x1b') || (param_2 == '\x1d')) {
    bVar1 = 0xb;
  }
  else {
    bVar1 = 0;
  }
  WsfMsgFree(param_1 - (uint)bVar1);
  return unaff_r7;
}

