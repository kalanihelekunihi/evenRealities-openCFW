
undefined8 FUN_004b3606(ushort *param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  int iVar2;
  undefined4 uVar3;
  int iVar4;
  
  iVar2 = DAT_004b3c8c;
  iVar1 = DAT_004b3c90 + (uint)*param_1 * 0x30;
  if (*(char *)(DAT_004b3c8c + 0x74) == '\0') {
    FUN_00479418();
    uVar3 = FUN_0047a630(0);
    *(undefined4 *)(iVar2 + 0x70) = uVar3;
    while (*(int *)(iVar2 + 0x70) != 0) {
      iVar4 = FUN_0047ae78(*(undefined4 *)(iVar2 + 0x70),4,0);
      if (iVar4 != 0) {
        uVar3 = DmConnPeerAddr(*(undefined1 *)(iVar1 + -0x2c));
        DmPrivResolveAddr(uVar3,iVar4,*param_1);
        *(undefined1 *)(iVar2 + 0x74) = 1;
        break;
      }
      uVar3 = FUN_0047a630(*(undefined4 *)(iVar2 + 0x70));
      *(undefined4 *)(iVar2 + 0x70) = uVar3;
    }
  }
  else {
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      param_2 = 0x166;
      param_3 = DAT_004b3c94;
      FUN_0043d574(2,DAT_004b3ca0,DAT_004b3c9c,DAT_004b3c98,0x166,DAT_004b3c94,param_4);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x8000000,DAT_004b4238,DAT_004b4238);
    }
  }
  return CONCAT44(param_3,param_2);
}

