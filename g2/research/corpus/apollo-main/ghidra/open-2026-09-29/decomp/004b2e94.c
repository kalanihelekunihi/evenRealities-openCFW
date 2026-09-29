
undefined4 dmDevMsgHandler(int param_1)

{
  undefined4 unaff_r7;
  
  (**(code **)(DAT_004b3074 + (*(byte *)(param_1 + 2) & 7) * 4))();
  return unaff_r7;
}

