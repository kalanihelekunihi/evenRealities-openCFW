
undefined4 FT_Stream_Close(int param_1)

{
  undefined4 unaff_r7;
  
  if ((param_1 != 0) && (*(int *)(param_1 + 0x18) != 0)) {
    (**(code **)(param_1 + 0x18))();
  }
  return unaff_r7;
}

