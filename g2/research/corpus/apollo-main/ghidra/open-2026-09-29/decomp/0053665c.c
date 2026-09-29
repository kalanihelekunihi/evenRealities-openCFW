
bool FUN_0053665c(undefined4 param_1,undefined4 param_2,undefined2 param_3,undefined1 param_4,
                 undefined2 param_5,undefined1 param_6)

{
  int iVar1;
  undefined2 *puVar2;
  
  puVar2 = (undefined2 *)WsfMsgAlloc(100);
  if (puVar2 != (undefined2 *)0x0) {
    *(undefined2 **)(puVar2 + 0x18) = puVar2 + 0x1c;
    *(undefined1 *)(puVar2 + 0x1a) = 1;
    iVar1 = DAT_005366d4;
    *(undefined1 *)((int)puVar2 + 3) = *(undefined1 *)(DAT_005366d4 + 0x38);
    *(char *)(iVar1 + 0x38) = *(char *)(iVar1 + 0x38) + '\x01';
    *puVar2 = param_5;
    *(undefined1 *)(puVar2 + 1) = param_6;
    *(undefined4 *)(puVar2 + 0x1c) = param_2;
    puVar2[0x2f] = param_3;
    puVar2[0x2e] = 0;
    *(undefined1 *)(puVar2 + 0x30) = param_4;
    *(undefined1 *)((int)puVar2 + 0x61) = 0;
    FUN_00542a44(puVar2 + 0x1e,param_1);
    FUN_0053653a(puVar2);
  }
  return puVar2 != (undefined2 *)0x0;
}

