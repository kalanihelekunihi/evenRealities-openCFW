
int FUN_0041c320(void)

{
  undefined4 *puVar1;
  byte bVar2;
  int iVar3;
  undefined4 in_r3;
  undefined4 local_40;
  undefined4 local_3c;
  undefined4 local_38;
  undefined4 local_34;
  undefined4 local_30;
  undefined4 local_2c;
  undefined4 local_28;
  undefined4 local_24;
  undefined4 local_20;
  undefined4 local_1c;
  undefined4 local_18;
  undefined4 local_14;
  undefined4 uStack_10;
  
  if (*DAT_0041cb18 << 0x1c < 0) {
    bVar2 = (byte)((uint)(*DAT_0041c4ac << 4) >> 0x1f) ^ 1;
  }
  else {
    bVar2 = 1;
  }
  if (bVar2 == 0) {
    uStack_10 = in_r3;
    iVar3 = FUN_00421548(5,0x480,2,&local_40);
    puVar1 = DAT_0041cb1c;
    if (iVar3 == 0) {
      DAT_0041cb1c[1] = local_40;
      puVar1[2] = local_3c;
      iVar3 = FUN_00421548(1,0x204,1,&local_40);
      if (iVar3 == 0) {
        puVar1[3] = local_40;
        iVar3 = FUN_00421548(1,0x206,1,&local_40);
        if (iVar3 == 0) {
          puVar1[4] = local_40;
          iVar3 = FUN_00421548(3,0x208,8,&local_40);
          if (iVar3 == 0) {
            puVar1[5] = local_40;
            puVar1[6] = local_3c;
            puVar1[7] = local_38;
            puVar1[8] = local_34;
            puVar1[9] = local_30;
            puVar1[10] = local_2c;
            puVar1[0xb] = local_28;
            puVar1[0xc] = local_24;
            iVar3 = FUN_00421548(1,0x210,1,&local_40);
            if (iVar3 == 0) {
              puVar1[0xd] = local_40;
              iVar3 = FUN_00421548(1,0x240,3,&local_40);
              if (iVar3 == 0) {
                puVar1[0xe] = local_40;
                puVar1[0xf] = local_3c;
                puVar1[0x10] = local_38;
                iVar3 = FUN_00421548(1,0x24a,2,&local_40);
                if (iVar3 == 0) {
                  puVar1[0x12] = local_40;
                  puVar1[0x13] = local_3c;
                  iVar3 = FUN_00421548(1,0x250,0xc,&local_40);
                  if (iVar3 == 0) {
                    puVar1[0x14] = local_40;
                    puVar1[0x15] = local_3c;
                    puVar1[0x16] = local_38;
                    puVar1[0x17] = local_34;
                    puVar1[0x18] = local_30;
                    puVar1[0x19] = local_2c;
                    puVar1[0x1a] = local_28;
                    puVar1[0x1b] = local_24;
                    puVar1[0x1c] = local_20;
                    puVar1[0x1d] = local_1c;
                    puVar1[0x1e] = local_18;
                    puVar1[0x1f] = local_14;
                    iVar3 = FUN_00421548(1,0x245,1,&local_40);
                    if (iVar3 == 0) {
                      puVar1[0x11] = local_40;
                      *puVar1 = DAT_0041cb20;
                    }
                  }
                }
              }
            }
          }
        }
      }
    }
  }
  else {
    iVar3 = 7;
  }
  return iVar3;
}

