
undefined4 hciCoreTxAclStart(int *param_1,uint param_2,int param_3)

{
  uint uVar1;
  int iVar2;
  undefined4 uVar3;
  
  uVar1 = HciGetBufSize();
  if ((uVar1 & 0xffff) < (param_2 & 0xffff)) {
    *(short *)((int)param_1 + 0x12) = (short)param_2 - (short)uVar1;
    param_1[1] = (uVar1 & 0xffff) + param_3;
    *param_1 = param_3;
    *(undefined1 *)((int)param_1 + 0x16) = 1;
    *(char *)(param_3 + 2) = (char)uVar1;
    *(char *)(param_3 + 3) = (char)(uVar1 >> 8);
    iVar2 = hciCoreSendAclData(param_1,param_3);
    if (iVar2 == 1) {
      uVar3 = 1;
    }
    else {
      *param_1 = 0;
      *(undefined1 *)((int)param_1 + 0x16) = 0;
      *(char *)(param_3 + 2) = (char)param_2;
      *(char *)(param_3 + 3) = (char)(param_2 >> 8);
      uVar3 = 0;
    }
  }
  else {
    uVar3 = hciCoreSendAclData(param_1,param_3);
  }
  return uVar3;
}

