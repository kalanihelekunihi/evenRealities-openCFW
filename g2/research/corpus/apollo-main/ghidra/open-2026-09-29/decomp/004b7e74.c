
void bleCommHandlerInit(undefined1 param_1)

{
  int iVar1;
  undefined1 *puVar2;
  
  iVar1 = DAT_004b81fc;
  *(undefined1 *)(DAT_004b81fc + 0x56) = param_1;
  *DAT_004b8728 = DAT_004b8724;
  *DAT_004b872c = DAT_004b81b4;
  puVar2 = DAT_004b8730;
  *DAT_004b8730 = 4;
  APP_SlaveHanderInit(param_1,iVar1,puVar2);
  FUN_00535488(param_1,iVar1,puVar2);
  APP_MasterHanderInit(param_1,iVar1,puVar2);
  bleSubsystemInit();
  return;
}

