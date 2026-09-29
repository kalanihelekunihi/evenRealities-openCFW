
int touch_config_load_from_eeprom(void)

{
  undefined4 *puVar1;
  int iVar2;
  
  puVar1 = DAT_00003a6c;
  *DAT_00003a6c = DAT_00003a70;
  iVar2 = touch_config_read_adapter(0,puVar1,8);
  if (iVar2 == 0) {
    logger_stub(DAT_00003a78,*(undefined2 *)(DAT_00003a6c + 1),
                *(undefined2 *)((int)DAT_00003a6c + 6),DAT_00003a74);
  }
  else {
    logger_stub(DAT_00003a7c,iVar2,DAT_00003a74);
  }
  return iVar2;
}

