
undefined4 FUN_005925e0(uint *param_1,uint *param_2,char param_3)

{
  int iVar1;
  undefined4 uVar2;
  uint uVar3;
  
  iVar1 = DAT_00592640;
  if ((param_1 == (uint *)0x0) || ((*param_1 & 0x1ffffff) != DAT_00592650)) {
    uVar2 = 2;
  }
  else {
    uVar3 = param_1[2];
    if (param_3 == '\0') {
      *param_2 = *(uint *)(DAT_00592640 + uVar3 * 0x1000 + 0x104);
    }
    else {
      *param_2 = *(uint *)(DAT_00592640 + uVar3 * 0x1000 + 0x104);
      *param_2 = *param_2 & *(uint *)(iVar1 + uVar3 * 0x1000 + 0x100);
    }
    uVar2 = 0;
  }
  return uVar2;
}

