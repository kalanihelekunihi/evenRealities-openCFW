
bool hciTrSendCmd(int param_1)

{
  uint uVar1;
  ushort uVar2;
  
  uVar2 = *(byte *)(param_1 + 2) + 3;
  uVar1 = hciDrvWrite(1,uVar2);
  return uVar1 == uVar2;
}

