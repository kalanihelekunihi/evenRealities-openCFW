
void DmSmpEncryptReq(undefined1 param_1,undefined1 param_2,undefined4 param_3)

{
  int iVar1;
  
  iVar1 = dmConnCcbById(param_1);
  if (iVar1 != 0) {
    *(undefined1 *)(iVar1 + 0x18) = param_2;
    *(undefined1 *)(iVar1 + 0x12) = 0;
    HciLeStartEncryptionCmd(*(undefined2 *)(iVar1 + 0xc),DAT_0055bc54,0,param_3);
  }
  return;
}

