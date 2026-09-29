
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

undefined8 FUN_004f5e18(void)

{
  char cVar1;
  int iVar2;
  byte bVar3;
  undefined4 in_r3;
  
  iVar2 = DAT_004f6760;
  cVar1 = *_DAT_004f676c;
  if (cVar1 == '\x01') {
    bVar3 = FUN_004f5718();
  }
  else if (cVar1 == '\x02') {
    if (*(char *)(DAT_004f6760 + 0x2e4d) == '\x01') {
      bVar3 = FUN_004f5a1c();
    }
    else if (*(char *)(DAT_004f6760 + 0x2e4d) == '\x02') {
      bVar3 = FUN_004f5838();
    }
    else {
      bVar3 = FUN_004f5a1c();
    }
  }
  else if (cVar1 == '\x03') {
    bVar3 = FUN_004f5c4c();
  }
  else {
    bVar3 = 3;
  }
  *(char *)(iVar2 + 0x2e4c) = cVar1;
  return CONCAT44(in_r3,(uint)bVar3);
}

