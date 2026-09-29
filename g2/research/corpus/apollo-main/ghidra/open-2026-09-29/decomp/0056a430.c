
undefined4
hciEvtProcessLeExtAdvReport(byte *param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  byte bVar1;
  byte bVar2;
  undefined2 *puVar3;
  byte bVar4;
  byte bVar5;
  byte *pbVar6;
  
  if (*param_1 < 0x10) {
    pbVar6 = param_1 + 1;
    bVar2 = 0;
    bVar4 = *param_1;
    while( true ) {
      bVar5 = bVar4 - 1;
      if (bVar4 == 0) break;
      bVar1 = pbVar6[0x17];
      pbVar6 = pbVar6 + bVar1 + 0x18;
      bVar4 = bVar5;
      if (bVar2 < bVar1) {
        bVar2 = bVar1;
      }
    }
    puVar3 = (undefined2 *)WsfBufAlloc(bVar2 + 0x24);
    if (puVar3 != (undefined2 *)0x0) {
      pbVar6 = param_1 + 1;
      bVar2 = *param_1;
      while (bVar2 != 0) {
        puVar3[2] = (ushort)pbVar6[1] * 0x100 + (ushort)*pbVar6;
        *(byte *)(puVar3 + 3) = pbVar6[2];
        FUN_004d293c((int)puVar3 + 7,pbVar6 + 3);
        *(byte *)((int)puVar3 + 0xd) = pbVar6[9];
        *(byte *)(puVar3 + 7) = pbVar6[10];
        *(byte *)((int)puVar3 + 0xf) = pbVar6[0xb];
        *(byte *)(puVar3 + 8) = pbVar6[0xc];
        *(byte *)((int)puVar3 + 0x11) = pbVar6[0xd];
        puVar3[9] = (ushort)pbVar6[0xf] * 0x100 + (ushort)pbVar6[0xe];
        *(byte *)(puVar3 + 10) = pbVar6[0x10];
        FUN_004d293c((int)puVar3 + 0x15,pbVar6 + 0x11);
        puVar3[0xe] = (ushort)pbVar6[0x17];
        if (0xe5 < (ushort)puVar3[0xe]) break;
        *(undefined2 **)(puVar3 + 0x10) = puVar3 + 0x12;
        FUN_00439be4(*(undefined4 *)(puVar3 + 0x10),pbVar6 + 0x18,puVar3[0xe]);
        pbVar6 = pbVar6 + 0x18 + (ushort)puVar3[0xe];
        *puVar3 = 0;
        *(undefined1 *)(puVar3 + 1) = 0x2c;
        *(undefined1 *)((int)puVar3 + 3) = 0;
        (**(code **)(DAT_0056b140 + 8))(puVar3);
        bVar2 = bVar2 - 1;
      }
      WsfBufFree(puVar3);
    }
  }
  return param_4;
}

