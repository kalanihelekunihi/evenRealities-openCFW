
undefined4 FUN_00569716(int param_1,byte param_2,int param_3)

{
  undefined4 unaff_r7;
  
  if ((((param_1 != 0) && (param_3 != 0)) && ((param_2 == 0 || (param_2 == 1)))) &&
     (param_1 = param_1 + (uint)param_2 * 0x20, *(char *)(param_1 + 0x50) != '\0')) {
    FUN_00568728(param_1 + 0x34,param_3);
  }
  return unaff_r7;
}

