
undefined4
dmPrivAesActGenAddrAesCmpl(int param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  
  FUN_00439be4(param_1 + 4,*(undefined4 *)(param_1 + 4),3);
  iVar1 = DAT_004d2920;
  FUN_00439be4(param_1 + 7,DAT_004d2920 + 10,3);
  *(byte *)(iVar1 + 3) = *(byte *)(iVar1 + 3) & 0xfd;
  *(undefined1 *)(param_1 + 2) = 0x38;
  *(undefined1 *)(param_1 + 3) = 0;
  (**(code **)(DAT_004d2924 + 8))(param_1);
  return param_4;
}

