
undefined4
hciEvtProcessLePerAdvReport(byte *param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  undefined2 *puVar1;
  
  if ((param_1[6] < 0xf8) &&
     (puVar1 = (undefined2 *)WsfBufAlloc(param_1[6] + 0x10), puVar1 != (undefined2 *)0x0)) {
    puVar1[2] = (ushort)param_1[1] * 0x100 + (ushort)*param_1;
    *(byte *)(puVar1 + 3) = param_1[2];
    *(byte *)((int)puVar1 + 7) = param_1[3];
    *(byte *)(puVar1 + 4) = param_1[4];
    *(byte *)((int)puVar1 + 9) = param_1[5];
    puVar1[5] = (ushort)param_1[6];
    *(undefined2 **)(puVar1 + 6) = puVar1 + 8;
    FUN_00439be4(*(undefined4 *)(puVar1 + 6),param_1 + 7,puVar1[5]);
    *puVar1 = 0;
    *(undefined1 *)(puVar1 + 1) = 0x31;
    *(undefined1 *)((int)puVar1 + 3) = *(undefined1 *)((int)puVar1 + 9);
    (**(code **)(DAT_0056b140 + 8))(puVar1);
    WsfBufFree(puVar1);
  }
  return param_4;
}

