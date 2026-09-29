
int cff_parse_num(int param_1,int *param_2)

{
  int iVar1;
  
  if (*(char *)*param_2 == '\x1e') {
    iVar1 = cff_parse_real(*param_2,*(undefined4 *)(param_1 + 8),0,0);
    iVar1 = iVar1 >> 0x10;
  }
  else if (*(char *)*param_2 == -1) {
    iVar1 = (int)(short)(((uint)*(byte *)(*param_2 + 2) << 8 | (uint)*(byte *)(*param_2 + 1) << 0x10
                         | (uint)*(byte *)(*param_2 + 3)) + 0x80 >> 8);
  }
  else {
    iVar1 = cff_parse_integer(*param_2,*(undefined4 *)(param_1 + 8));
  }
  return iVar1;
}

