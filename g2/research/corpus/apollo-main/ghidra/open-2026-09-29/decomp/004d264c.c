
undefined4
dmPrivActGenAddr(undefined2 *param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  int iVar2;
  undefined4 uStack_18;
  
  iVar1 = DAT_004d2920;
  if ((int)((uint)*(byte *)(DAT_004d2920 + 3) << 0x1e) < 0) {
    *(undefined1 *)((int)param_1 + 3) = 7;
    *(undefined1 *)(param_1 + 1) = 0x38;
    (**(code **)(DAT_004d2924 + 8))(param_1);
    uStack_18 = param_4;
  }
  else {
    iVar2 = DAT_004d2920 + 10;
    FUN_0053634e(iVar2,3);
    *(byte *)(iVar1 + 0xc) = *(byte *)(iVar1 + 0xc) & 0x3f | 0x40;
    FUN_0043c0e4(iVar1 + 0xd,0xd,0);
    *(byte *)(iVar1 + 3) = *(byte *)(iVar1 + 3) | 2;
    uStack_18 = 0x79;
    FUN_00536426(param_1 + 2,iVar2,*(undefined1 *)(DAT_004d2924 + 0xc),*param_1);
  }
  return uStack_18;
}

