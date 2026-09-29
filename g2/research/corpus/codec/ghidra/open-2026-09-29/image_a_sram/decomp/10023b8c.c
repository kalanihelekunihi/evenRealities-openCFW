
void sflash_addr2cmd_isra_0(int *param_1,uint param_2,int param_3)

{
  *(char *)(param_3 + 1) = (char)(param_2 >> ((*param_1 + 0x1fffffff) * 8 & 0x3fU));
  *(char *)(param_3 + 2) = (char)(param_2 >> ((*param_1 + 0x1ffffffe) * 8 & 0x3fU));
  *(char *)(param_3 + 3) = (char)(param_2 >> ((*param_1 + 0x1ffffffd) * 8 & 0x3fU));
  *(char *)(param_3 + 4) = (char)(param_2 >> ((*param_1 + 0x1ffffffc) * 8 & 0x3fU));
  return;
}

