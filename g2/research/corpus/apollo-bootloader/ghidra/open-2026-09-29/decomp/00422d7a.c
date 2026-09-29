
undefined4 FUN_00422d7a(int param_1,uint param_2)

{
  undefined4 uVar1;
  
  param_2 = param_2 | *(uint *)(DAT_00423440 + param_1 * 0x1000 + 0x3c);
  uVar1 = DAT_00423768;
  if ((((-1 < (int)(param_2 << 0x19)) && (uVar1 = DAT_0042376c, -1 < (int)(param_2 << 0x18))) &&
      (uVar1 = DAT_00423770, -1 < (int)(param_2 << 0x17))) &&
     (((uVar1 = DAT_00423774, -1 < (int)(param_2 << 0x16) &&
       (uVar1 = DAT_00423778, -1 < (int)(param_2 << 0x15))) &&
      (uVar1 = 0, (int)(param_2 << 0x13) < 0)))) {
    uVar1 = DAT_0042382c;
  }
  return uVar1;
}

