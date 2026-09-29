
int hw_state_compose_42bdf0(void)

{
  undefined4 *puVar1;
  byte bVar2;
  int iVar3;
  uint *puVar4;
  uint *puVar5;
  undefined4 in_r3;
  undefined4 local_20;
  undefined4 local_1c;
  undefined4 local_18;
  undefined4 local_14;
  undefined4 uStack_10;
  
  puVar1 = DAT_0042bfcc;
  if (*DAT_0042c02c << 0x1c < 0) {
    bVar2 = (byte)((uint)(*DAT_0042bfd8 << 4) >> 0x1f) ^ 1;
  }
  else {
    bVar2 = 0;
  }
  if (bVar2 == 0) {
    uStack_10 = in_r3;
    iVar3 = FUN_00421548(1,0x25c,0x10,DAT_0042bfcc + 1);
    if (iVar3 == 0) {
      puVar1[0x11] = puVar1[5];
      puVar1[0x12] = puVar1[6];
      puVar1[0x13] = puVar1[7];
      puVar1[0x14] = puVar1[8];
      puVar1[0x11] = puVar1[0x11] & 0xffffff80 | puVar1[0xd] & 0x7f;
      puVar1[0x12] = puVar1[0x12] & 0xffffff80 | puVar1[0xe] & 0x7f;
      puVar1[0x13] = puVar1[0x13] & 0xffffff80 | puVar1[0xf] & 0x7f;
      puVar1[0x14] = puVar1[0x14] & 0xffffff80 | puVar1[0x10] & 0x7f;
      iVar3 = FUN_00421548(1,0x270,4,&local_20);
      if (iVar3 == 0) {
        puVar1[0x15] = local_20;
        puVar1[0x16] = local_1c;
        puVar1[0x17] = local_18;
        puVar1[0x18] = local_14;
        iVar3 = FUN_00421548(1,0x278,1,&local_20);
        if (iVar3 == 0) {
          puVar1[0x1a] = local_20;
          puVar5 = puVar1 + 9;
          *puVar5 = *puVar5 & 0xf01fffff |
                    (((puVar1[0xe] & 0xfffffff) >> 0x15) + ((puVar1[0xd] & 0xfffffff) >> 0x15)) / 2
                    << 0x15;
          puVar4 = puVar1 + 10;
          *puVar4 = *puVar4 & 0xf01fffff | ((uint)puVar1[0xb] >> 0x15 & 0x7f) << 0x15;
          *puVar5 = *puVar5 & 0xefffffff | ((uint)puVar1[0xd] >> 0x1c & 1) << 0x1c;
          *puVar4 = *puVar4 & 0xefffffff | ((uint)puVar1[0xb] >> 0x1c & 1) << 0x1c;
          puVar4 = puVar1 + 0xd;
          *puVar4 = *puVar4 & 0xf01fffff | ((uint)puVar1[0xe] >> 0x15 & 0x7f) << 0x15;
          *puVar4 = *puVar4 & 0xefffffff | ((uint)puVar1[0xe] >> 0x1c & 1) << 0x1c;
          *puVar4 = *puVar4 & 0xffe1ffff | ((uint)puVar1[0xe] >> 0x11 & 0xf) << 0x11;
          *puVar4 = *puVar4 & 0xfffe007f | ((uint)puVar1[0xe] >> 7 & 0x3ff) << 7;
          puVar1[0x1a] = puVar1[0x1a] & 0xfc0fffff | 0x1f00000;
          *puVar1 = DAT_0042bfd0;
          FUN_0041cc04();
        }
      }
    }
  }
  else {
    iVar3 = 7;
  }
  return iVar3;
}

