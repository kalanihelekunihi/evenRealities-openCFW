
undefined4 FUN_004b3a86(int param_1,int *param_2)

{
  undefined4 unaff_r7;
  
  if ((*(char *)((int)param_2 + 7) != '\0') && (*param_2 != 0)) {
    *(byte *)((int)param_2 + 0xb) = *(byte *)((int)param_2 + 0xb) | *(byte *)(param_1 + 0x1e);
    FUN_0047aed4(*param_2,param_1);
  }
  return unaff_r7;
}

