
void nvdbBuzzerUpdate(undefined4 param_1,undefined1 param_2)

{
  undefined1 *puVar1;
  undefined2 uVar2;
  
  puVar1 = DAT_0058fa90;
  *(undefined4 *)(DAT_0058fa90 + 4) = param_1;
  puVar1[8] = param_2;
  *puVar1 = 2;
  uVar2 = FUN_0049acd4(puVar1,10,0);
  *(undefined2 *)(puVar1 + 10) = uVar2;
  SVC_NvdbWrite(DAT_0058faa8,puVar1,0xc);
  return;
}

