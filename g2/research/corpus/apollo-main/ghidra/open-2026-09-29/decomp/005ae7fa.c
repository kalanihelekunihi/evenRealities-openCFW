
undefined4 cff_done_blend(int param_1)

{
  undefined4 unaff_r7;
  
  if (*(int *)(param_1 + 0x224) != 0) {
    (**(code **)(*(int *)(param_1 + 0x224) + 0x24))();
  }
  return unaff_r7;
}

