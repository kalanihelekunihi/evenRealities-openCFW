
void attention_release_timeout_rearm(void)

{
  int iVar1;
  
  iVar1 = DAT_00003b18;
  *(undefined4 *)(DAT_00003b18 + 0x44) = 2;
  Cy_SysLib_Delay(200);
  *(undefined4 *)(iVar1 + 0x40) = 2;
  logger_stub(DAT_00003b20,DAT_00003b1c);
  return;
}

