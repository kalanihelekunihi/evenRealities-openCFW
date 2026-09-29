
undefined4 FUN_00480ed8(uint param_1,uint *param_2,int *param_3)

{
  *param_2 = param_1 >> 5;
  *param_3 = 1 << (param_1 & 0x1f);
  return 0;
}

