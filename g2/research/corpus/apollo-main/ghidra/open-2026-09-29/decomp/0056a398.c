
undefined4
hciEvtProcessLeAdvReport(byte *param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  undefined2 *puVar1;
  byte bVar2;
  
  bVar2 = *param_1;
  if ((bVar2 < 0x10) && (puVar1 = (undefined2 *)WsfBufAlloc(0x3b), puVar1 != (undefined2 *)0x0)) {
    while( true ) {
      if (bVar2 == 0) break;
      *(byte *)(puVar1 + 5) = param_1[1];
      *(byte *)((int)puVar1 + 0xb) = param_1[2];
      FUN_004d293c(puVar1 + 6,param_1 + 3);
      *(byte *)(puVar1 + 4) = param_1[9];
      if (0x1f < *(byte *)(puVar1 + 4)) break;
      *(undefined2 **)(puVar1 + 2) = puVar1 + 0xe;
      FUN_00439be4(*(undefined4 *)(puVar1 + 2),param_1 + 10,*(undefined1 *)(puVar1 + 4));
      param_1 = param_1 + 10 + *(byte *)(puVar1 + 4);
      *(byte *)((int)puVar1 + 9) = *param_1;
      *(undefined1 *)(puVar1 + 9) = 0;
      FUN_0043c0e4((int)puVar1 + 0x13,6,0);
      *puVar1 = 0;
      *(undefined1 *)(puVar1 + 1) = 6;
      *(undefined1 *)((int)puVar1 + 3) = 0;
      (**(code **)(DAT_0056b140 + 8))(puVar1);
      bVar2 = bVar2 - 1;
    }
    WsfBufFree(puVar1);
  }
  return param_4;
}

