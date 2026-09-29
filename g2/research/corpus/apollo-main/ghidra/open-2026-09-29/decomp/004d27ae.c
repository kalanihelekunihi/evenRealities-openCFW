
undefined4 dmPrivMsgHandler(int param_1)

{
  undefined4 unaff_r7;
  
  (**(code **)(DAT_004d2928 + (*(byte *)(param_1 + 2) & 7) * 4))();
  return unaff_r7;
}

