
undefined8 FUN_004bacf0(byte param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  uint uVar1;
  int iVar2;
  char cVar3;
  byte bVar4;
  
  bVar4 = 0;
  iVar2 = DAT_004bb3ac;
  for (cVar3 = '\x03'; cVar3 != '\0'; cVar3 = cVar3 + -1) {
    if (*(char *)(iVar2 + 4) != '\0') {
      uVar1 = DmConnRole(*(undefined1 *)(iVar2 + 4));
      if (uVar1 == param_1) {
        bVar4 = bVar4 + 1;
      }
    }
    iVar2 = iVar2 + 0x30;
  }
  return CONCAT44(param_4,(uint)bVar4);
}

