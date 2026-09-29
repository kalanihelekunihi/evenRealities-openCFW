
int spotmgr_init_42abbc(void)

{
  undefined4 *puVar1;
  byte bVar2;
  int iVar3;
  undefined4 local_20;
  undefined4 local_1c;
  undefined4 local_18;
  undefined4 local_14;
  undefined4 local_10;
  
  puVar1 = DAT_0042ac50;
  if (*DAT_0042ad38 << 0x1c < 0) {
    bVar2 = (byte)((uint)(*DAT_0042acec << 4) >> 0x1f) ^ 1;
  }
  else {
    bVar2 = 0;
  }
  if (bVar2 == 0) {
    iVar3 = FUN_00421548(1,0x25c,0x14,DAT_0042ac50 + 1);
    if ((iVar3 == 0) && (iVar3 = FUN_00421548(1,0x270,5,&local_20), iVar3 == 0)) {
      puVar1[0x15] = local_20;
      puVar1[0x16] = local_1c;
      puVar1[0x17] = local_18;
      puVar1[0x18] = local_14;
      puVar1[0x19] = local_10;
      iVar3 = FUN_00421548(1,0x278,1,&local_20);
      if (iVar3 == 0) {
        puVar1[0x1a] = local_20;
        *puVar1 = DAT_0042ace4;
        FUN_0041cc04();
      }
    }
  }
  else {
    iVar3 = 7;
  }
  return iVar3;
}

