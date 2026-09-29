
undefined4 FUN_00592584(uint *param_1,uint param_2)

{
  undefined4 uVar1;
  
  if ((param_1 == (uint *)0x0) || ((*param_1 & 0x1ffffff) != DAT_00592650)) {
    uVar1 = 2;
  }
  else {
    *(uint *)(DAT_00592640 + param_1[2] * 0x1000 + 0x100) =
         *(uint *)(DAT_00592640 + param_1[2] * 0x1000 + 0x100) & ~param_2;
    uVar1 = 0;
  }
  return uVar1;
}

