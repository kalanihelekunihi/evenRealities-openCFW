
undefined4
dmPrivAesActResAddrAesCmpl(int param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  int iVar2;
  
  iVar1 = DAT_004d2920;
  iVar2 = FUN_004751c8(DAT_004d2920,*(undefined4 *)(param_1 + 4),3);
  if (iVar2 == 0) {
    *(undefined1 *)(param_1 + 3) = 0;
  }
  else {
    *(undefined1 *)(param_1 + 3) = 5;
  }
  *(byte *)(iVar1 + 3) = *(byte *)(iVar1 + 3) & 0xfe;
  *(undefined1 *)(param_1 + 2) = 0x37;
  (**(code **)(DAT_004d2924 + 8))(param_1);
  return param_4;
}

