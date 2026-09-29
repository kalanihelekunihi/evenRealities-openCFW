
undefined4
SmpHandlerInit(undefined1 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  byte bVar1;
  int iVar2;
  
  iVar2 = DAT_00537ebc;
  *(undefined1 *)(DAT_00537ebc + 0xec) = param_1;
  SmpDbInit();
  for (bVar1 = 0; bVar1 < 3; bVar1 = bVar1 + 1) {
    *(undefined1 *)(iVar2 + 0xc) = param_1;
    *(ushort *)(iVar2 + 8) = bVar1 + 1;
    *(undefined1 *)(iVar2 + 0x1c) = param_1;
    *(ushort *)(iVar2 + 0x18) = bVar1 + 1;
    iVar2 = iVar2 + 0x4c;
  }
  L2cRegister(6,PTR_smpL2cDataCback_1_00537ed8,PTR_smpL2cCtrlCback_1_00537ed4);
  DmConnRegister(1,PTR_smpDmConnCback_1_00537edc);
  return param_4;
}

