
undefined4 touch_sub_29ac(int param_1,int param_2)

{
  undefined4 uVar1;
  int *piVar2;
  uint local_c;
  
  piVar2 = (int *)(*(int *)(param_2 + 0xc) + param_1 * 0x90);
  local_c = 0;
  if ((int)((uint)*(byte *)(*piVar2 + 0x23) << 0x1c) < 0) {
    uVar1 = touch_sub_48c0(&local_c,param_1,(short)piVar2[0x20],0,param_2);
    if (0xffff < local_c) {
      local_c = DAT_00005cf4;
    }
    *(short *)(*piVar2 + 4) = (short)local_c;
  }
  else {
    uVar1 = 0;
  }
  return uVar1;
}

