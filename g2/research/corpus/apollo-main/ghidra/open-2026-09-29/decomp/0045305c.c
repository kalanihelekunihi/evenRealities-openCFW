
void FUN_0045305c(char *param_1,int param_2)

{
  undefined4 uVar1;
  
  param_1[0xb] = param_1[0xb] | 2;
  if (*(char **)(DAT_004530f8 + 0x50) == param_1) {
    *(undefined4 *)(DAT_004530f8 + 0x54) = 0;
  }
  if ((*param_1 == '\x01') || (*param_1 == '\x02')) {
    if ((param_2 == 0) || (*(int *)(param_1 + 0x74) == param_2)) {
      param_1[0x74] = '\0';
      param_1[0x75] = '\0';
      param_1[0x76] = '\0';
      param_1[0x77] = '\0';
    }
    if (*(int *)(param_1 + 0x68) != 0) {
      uVar1 = *(undefined4 *)(param_1 + 0x68);
      param_1[0x68] = '\0';
      param_1[0x69] = '\0';
      param_1[0x6a] = '\0';
      param_1[0x6b] = '\0';
      FUN_00451670(uVar1,0x17,param_1);
      FUN_00453002(param_1,0x17,uVar1);
    }
    if ((param_2 == 0) || (*(int *)(param_1 + 0x6c) == param_2)) {
      param_1[0x6c] = '\0';
      param_1[0x6d] = '\0';
      param_1[0x6e] = '\0';
      param_1[0x6f] = '\0';
    }
    if (*(int *)(param_1 + 0x70) != 0) {
      uVar1 = *(undefined4 *)(param_1 + 0x70);
      param_1[0x70] = '\0';
      param_1[0x71] = '\0';
      param_1[0x72] = '\0';
      param_1[0x73] = '\0';
      FUN_00451670(uVar1,0x17,param_1);
      FUN_00453002(param_1,0x17,uVar1);
    }
    if ((param_2 == 0) || (*(int *)(param_1 + 0x78) == param_2)) {
      param_1[0x78] = '\0';
      param_1[0x79] = '\0';
      param_1[0x7a] = '\0';
      param_1[0x7b] = '\0';
    }
  }
  return;
}

