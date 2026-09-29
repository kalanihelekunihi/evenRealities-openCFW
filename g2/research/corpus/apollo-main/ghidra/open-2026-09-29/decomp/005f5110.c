
undefined4 Ins_WCVTF(int param_1,uint *param_2,undefined4 param_3,undefined4 param_4)

{
  undefined4 uVar1;
  uint uVar2;
  
  uVar2 = *param_2;
  if (uVar2 < *(uint *)(param_1 + 0x180)) {
    uVar1 = FT_MulFix(param_2[1],*(undefined4 *)(param_1 + 0x108));
    *(undefined4 *)(*(int *)(param_1 + 0x184) + uVar2 * 4) = uVar1;
  }
  else if (*(char *)(param_1 + 0x235) != '\0') {
    *(undefined4 *)(param_1 + 0xc) = 0x86;
  }
  return param_4;
}

