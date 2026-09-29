
ushort hciTrSendAclData(undefined4 param_1,int param_2)

{
  uint uVar1;
  ushort uVar2;
  
  uVar2 = (ushort)*(byte *)(param_2 + 3) * 0x100 + (ushort)*(byte *)(param_2 + 2) + 4;
  uVar1 = hciDrvWrite(2,uVar2);
  if (uVar1 != uVar2) {
    uVar2 = 0;
  }
  return uVar2;
}

