
undefined8 FUN_004145fc(int param_1,undefined4 *param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  undefined4 uVar2;
  
  iVar1 = FUN_00410b1c(param_1 + 0x18,param_2);
  if (iVar1 == 0) {
    if (param_2[2] == param_2[3]) {
      *param_2 = *(undefined4 *)(param_1 + 0x18);
      param_2[1] = *(undefined4 *)(param_1 + 0x1c);
      param_2[2] = 0;
      param_2[3] = param_2[3] << 1;
    }
    param_2[2] = param_2[2] + 1;
    uVar2 = 0;
  }
  else {
    FUN_00415fae(DAT_0041510c,DAT_004150fc,0x1171,&DAT_0041464c);
    uVar2 = 0xffffffac;
  }
  return CONCAT44(param_4,uVar2);
}

