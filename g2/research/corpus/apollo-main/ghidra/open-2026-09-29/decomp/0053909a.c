
undefined8 FUN_0053909a(uint *param_1,char param_2,undefined4 param_3,undefined4 param_4)

{
  undefined4 uVar1;
  
  if ((param_1 == (uint *)0x0) || ((*param_1 & 0x1ffffff) != DAT_0053924c)) {
    uVar1 = 2;
  }
  else {
    FUN_00538d18(param_1);
    if ((param_2 == '\0') && (param_1[7] != param_1[8])) {
      uVar1 = 3;
    }
    else {
      *param_1 = *param_1 & 0xfeffffff;
      **(uint **)param_1[9] = **(uint **)param_1[9] & 0xfffffffe;
      **(uint **)(param_1[9] + 0x10) =
           **(uint **)(param_1[9] + 0x10) & ~*(uint *)(param_1[9] + 0x14);
      uVar1 = 0;
    }
  }
  return CONCAT44(param_4,uVar1);
}

