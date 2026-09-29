
void FUN_0041fa98(void)

{
  char *pcVar1;
  int iVar2;
  
  pcVar1 = DAT_0041fad0;
  if (*DAT_0041fad0 == '\x01') {
    iVar2 = stage_one_entry();
    if (iVar2 != 0) {
      do {
                    /* WARNING: Do nothing block with infinite loop */
      } while( true );
    }
    iVar2 = stage_two_status();
    if (iVar2 != 0) {
      do {
                    /* WARNING: Do nothing block with infinite loop */
      } while( true );
    }
    FUN_0041583c(0);
    FUN_0041d92c(0x1c,*DAT_0041fad8);
    *pcVar1 = '\0';
  }
  return;
}

