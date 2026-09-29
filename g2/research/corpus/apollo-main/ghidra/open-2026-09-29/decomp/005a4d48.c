
int FUN_005a4d48(void)

{
  undefined4 *puVar1;
  byte bVar2;
  int iVar3;
  undefined4 local_20;
  undefined4 local_1c;
  undefined4 local_18;
  undefined4 local_14;
  undefined4 local_10;
  
  puVar1 = DAT_005a4eec;
  if (*DAT_005a4ee8 << 0x1c < 0) {
    bVar2 = (byte)((uint)(*DAT_005a4e98 << 4) >> 0x1f) ^ 1;
  }
  else {
    bVar2 = 0;
  }
  if (bVar2 == 0) {
    iVar3 = FUN_004d3f3c(1,0x25c,0x14,DAT_005a4eec + 1);
    if ((iVar3 == 0) && (iVar3 = FUN_004d3f3c(1,0x270,5,&local_20), iVar3 == 0)) {
      puVar1[0x15] = local_20;
      puVar1[0x16] = local_1c;
      puVar1[0x17] = local_18;
      puVar1[0x18] = local_14;
      puVar1[0x19] = local_10;
      iVar3 = FUN_004d3f3c(1,0x278,1,&local_20);
      if (iVar3 == 0) {
        puVar1[0x1a] = local_20;
        *puVar1 = DAT_005a4e8c;
        FUN_004801fc();
      }
    }
  }
  else {
    iVar3 = 7;
  }
  return iVar3;
}

