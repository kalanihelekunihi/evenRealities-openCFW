
undefined4 hciEvtCmdStatusFailure(char param_1,short param_2,undefined4 param_3,undefined4 param_4)

{
  undefined2 *puVar1;
  code *pcVar2;
  
  if ((param_2 == 0x2026) && (param_1 == '\x12')) {
    pcVar2 = *(code **)(DAT_0056b140 + 0xc);
    puVar1 = (undefined2 *)WsfBufAlloc(4);
    if (puVar1 != (undefined2 *)0x0) {
      *puVar1 = 0;
      *(undefined1 *)(puVar1 + 1) = 0x26;
      *(undefined1 *)((int)puVar1 + 3) = 0x12;
      (*pcVar2)(puVar1);
      WsfBufFree(puVar1);
    }
  }
  return param_4;
}

