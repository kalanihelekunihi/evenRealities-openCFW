
void case_clock_descriptor(undefined4 *param_1,uint *param_2)

{
  int iVar1;
  
  *param_1 = 7;
  iVar1 = DAT_0800546c;
  param_1[1] = *(uint *)(DAT_0800546c + 8) & 7;
  param_1[2] = *(uint *)(iVar1 + 8) & 0xf00;
  param_1[3] = *(uint *)(iVar1 + 8) & 0x7000;
  *param_2 = *DAT_08005470 & 7;
  return;
}

