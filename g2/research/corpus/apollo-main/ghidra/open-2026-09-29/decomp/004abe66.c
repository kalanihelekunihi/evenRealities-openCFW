
void productModeUpdate(undefined1 param_1)

{
  undefined1 *puVar1;
  undefined2 uVar2;
  
  set_product_mode(param_1);
  puVar1 = DAT_004abea0;
  *DAT_004abea0 = 1;
  uVar2 = FUN_0049acd4(puVar1,2,0);
  *(undefined2 *)(puVar1 + 2) = uVar2;
  SVC_NvdbWrite(DAT_004abeb8,puVar1,4);
  return;
}

