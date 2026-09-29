
undefined4 dmHciEvtCback(int param_1)

{
  undefined4 unaff_r7;
  
  if ((*(char *)(DAT_004d2ae8 + 0x10) == '\0') || (*(char *)(param_1 + 2) == '\0')) {
    (**(code **)(*(int *)(DAT_004d2aec +
                         (uint)*(byte *)(DAT_004d2af0 + (uint)*(byte *)(param_1 + 2)) * 4) + 4))();
  }
  return unaff_r7;
}

