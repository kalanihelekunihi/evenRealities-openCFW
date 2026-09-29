
undefined1 FUN_00482a6a(byte param_1)

{
  undefined1 uVar1;
  
  if (param_1 == 0xff) {
    uVar1 = 0x3f;
  }
  else if (param_1 == 0) {
    uVar1 = 0;
  }
  else if (param_1 < 0x8a) {
    uVar1 = *(undefined1 *)(DAT_00482afc + (uint)param_1);
  }
  else if ((*(int *)(DAT_00482ab8 + 0x30) == 0) ||
          (*(uint *)(DAT_00482ab8 + 0x28) <= (uint)(byte)(param_1 + 0x76))) {
    uVar1 = 0;
  }
  else {
    uVar1 = *(undefined1 *)(*(int *)(DAT_00482ab8 + 0x30) + (uint)(byte)(param_1 + 0x76));
  }
  return uVar1;
}

