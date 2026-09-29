
undefined4 dmAdvMsgHandler(int param_1)

{
  undefined4 unaff_r7;
  
  (**(code **)(PTR_PTR_004bac94 + (*(byte *)(param_1 + 2) & 7) * 4))();
  return unaff_r7;
}

