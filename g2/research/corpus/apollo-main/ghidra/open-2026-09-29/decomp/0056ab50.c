
void hciEvtProcessLeDirectAdvReport(byte *param_1)

{
  undefined2 *puVar1;
  byte bVar2;
  
  bVar2 = *param_1;
  param_1 = param_1 + 1;
  if ((bVar2 < 0x10) && (puVar1 = (undefined2 *)WsfBufAlloc(0x1c), puVar1 != (undefined2 *)0x0)) {
    while (bVar2 != 0) {
      *(byte *)(puVar1 + 5) = *param_1;
      *(byte *)((int)puVar1 + 0xb) = param_1[1];
      FUN_004d293c(puVar1 + 6,param_1 + 2);
      *(byte *)(puVar1 + 9) = param_1[8];
      FUN_004d293c((int)puVar1 + 0x13,param_1 + 9);
      *(byte *)((int)puVar1 + 9) = param_1[0xf];
      param_1 = param_1 + 0x10;
      *(undefined1 *)(puVar1 + 4) = 0;
      *(undefined4 *)(puVar1 + 2) = 0;
      *puVar1 = 0;
      *(undefined1 *)(puVar1 + 1) = 6;
      *(undefined1 *)((int)puVar1 + 3) = 0;
      (**(code **)(DAT_0056b140 + 8))(puVar1);
      bVar2 = bVar2 - 1;
    }
    WsfBufFree(puVar1);
  }
  return;
}

