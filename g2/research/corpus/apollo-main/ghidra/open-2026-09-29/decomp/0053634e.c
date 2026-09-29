
undefined4 FUN_0053634e(undefined1 *param_1,byte param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  char cVar2;
  byte bVar3;
  byte bVar4;
  uint uVar5;
  
  iVar1 = DAT_005363e8;
  bVar4 = *(char *)(DAT_005363e8 + 0x3a) << 3;
  bVar3 = param_2;
  while( true ) {
    uVar5 = (param_2 + 7) / 8;
    if (bVar3 == 0) break;
    *param_1 = *(undefined1 *)(iVar1 + (uint)bVar4);
    param_1 = param_1 + 1;
    if (bVar4 == 0x1f) {
      bVar4 = 0;
      bVar3 = bVar3 - 1;
    }
    else {
      bVar4 = bVar4 + 1;
      bVar3 = bVar3 - 1;
    }
  }
  while( true ) {
    if ((char)uVar5 == '\0') break;
    HciLeRandCmd();
    if (*(byte *)(iVar1 + 0x3a) < 3) {
      cVar2 = *(char *)(iVar1 + 0x3a) + '\x01';
    }
    else {
      cVar2 = '\0';
    }
    *(char *)(iVar1 + 0x3a) = cVar2;
    uVar5 = uVar5 - 1;
  }
  return param_4;
}

