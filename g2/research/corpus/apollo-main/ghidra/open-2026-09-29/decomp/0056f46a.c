
undefined4 pt_response_checksum(int param_1,byte *param_2)

{
  byte bVar1;
  undefined4 uVar2;
  char cVar3;
  int iVar4;
  
  if ((param_1 == 0) || (param_2 == (byte *)0x0)) {
    uVar2 = 0xffffffff;
  }
  else {
    cVar3 = '\0';
    bVar1 = *param_2;
    for (iVar4 = 0; iVar4 < (int)(uint)bVar1; iVar4 = iVar4 + 1) {
      cVar3 = cVar3 + *(char *)(param_1 + iVar4);
    }
    *(char *)(param_1 + (uint)bVar1) = cVar3;
    *param_2 = bVar1 + 1;
    uVar2 = 0;
  }
  return uVar2;
}

