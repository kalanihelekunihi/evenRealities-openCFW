
undefined4 FUN_00590848(uint *param_1,uint *param_2,char param_3)

{
  int iVar1;
  undefined4 uVar2;
  uint uVar3;
  
  iVar1 = DAT_00590d34;
  uVar3 = param_1[1];
  if ((param_1 == (uint *)0x0) || ((*param_1 & 0x1ffffff) != DAT_00590a20)) {
    uVar2 = 2;
  }
  else {
    if (param_3 == '\0') {
      *param_2 = *(uint *)(DAT_00590d34 + uVar3 * 0x1000 + 0x304);
    }
    else {
      *param_2 = *(uint *)(DAT_00590d34 + uVar3 * 0x1000 + 0x304);
      *param_2 = *param_2 & *(uint *)(iVar1 + uVar3 * 0x1000 + 0x300);
    }
    uVar2 = 0;
  }
  return uVar2;
}

