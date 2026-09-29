
longlong cff_get_kerning(int param_1,undefined4 param_2,undefined4 param_3,undefined4 *param_4)

{
  undefined4 uVar1;
  int iVar2;
  
  iVar2 = *(int *)(param_1 + 0x21c);
  *param_4 = 0;
  param_4[1] = 0;
  if (iVar2 != 0) {
    uVar1 = (**(code **)(iVar2 + 0x54))();
    *param_4 = uVar1;
  }
  return ZEXT48(param_4) << 0x20;
}

