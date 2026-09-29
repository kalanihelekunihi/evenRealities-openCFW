
uint touch_sub_2a70(int param_1,int param_2)

{
  uint uVar1;
  uint uVar2;
  
  uVar1 = (uint)(*(int *)(*(int *)(param_2 + 8) + 0x2c) * param_1) >> 0xe;
  uVar2 = uVar1;
  if ((uVar1 != 0) && (uVar2 = uVar1 - 1, 0xffff < uVar1 - 1)) {
    uVar2 = DAT_00005d8c;
  }
  return uVar2;
}

