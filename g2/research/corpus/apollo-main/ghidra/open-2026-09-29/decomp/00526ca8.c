
undefined4 FT_Select_Size(int param_1,int param_2)

{
  int iVar1;
  undefined4 uVar2;
  
  uVar2 = 0;
  if ((param_1 == 0) || (-1 < (int)((uint)*(byte *)(param_1 + 8) << 0x1e))) {
    uVar2 = 0x23;
  }
  else if ((param_2 < 0) || (*(int *)(param_1 + 0x1c) <= param_2)) {
    uVar2 = 6;
  }
  else {
    iVar1 = *(int *)(*(int *)(param_1 + 0x60) + 0xc);
    if (*(int *)(iVar1 + 0x5c) == 0) {
      FT_Select_Metrics();
    }
    else {
      uVar2 = (**(code **)(iVar1 + 0x5c))(*(undefined4 *)(param_1 + 0x58));
    }
  }
  return uVar2;
}

