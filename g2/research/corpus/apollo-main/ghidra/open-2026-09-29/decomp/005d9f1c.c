
void nvdbAdvMagicUpdate(undefined1 param_1)

{
  undefined1 *puVar1;
  undefined2 uVar2;
  
  puVar1 = DAT_005d9f40;
  DAT_005d9f40[1] = param_1;
  *puVar1 = 1;
  uVar2 = FUN_0049acd4(puVar1,2,0);
  *(undefined2 *)(puVar1 + 2) = uVar2;
  SVC_NvdbWrite(DAT_005d9f44,puVar1,4);
  return;
}

