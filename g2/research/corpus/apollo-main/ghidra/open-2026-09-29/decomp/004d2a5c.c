
undefined4 DmHandler(undefined4 param_1,int param_2)

{
  undefined4 unaff_r7;
  
  if ((param_2 != 0) && (*(char *)(DAT_004d2ae8 + 0x10) == '\0')) {
    (**(code **)(*(int *)(DAT_004d2aec + ((int)(uint)*(byte *)(param_2 + 2) >> 3) * 4) + 8))();
  }
  return unaff_r7;
}

