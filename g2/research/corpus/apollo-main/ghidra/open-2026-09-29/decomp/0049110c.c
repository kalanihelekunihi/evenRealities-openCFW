
void FUN_0049110c(void)

{
  int iVar1;
  code *pcStack_1c;
  undefined4 uStack_18;
  undefined2 uStack_14;
  undefined4 uStack_10;
  undefined4 uStack_c;
  
  do {
    do {
      do {
        iVar1 = osMessageQueueGet(*DAT_00491618,&pcStack_1c,0,0xffffffff);
      } while (iVar1 != 0);
    } while (pcStack_1c == (code *)0x0);
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      FUN_0043d574(4,DAT_00491628,DAT_00491624,DAT_00491620,0x3a,DAT_0049161c,uStack_18);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x10400000,DAT_0049162c,DAT_0049162c,uStack_18);
    }
    (*pcStack_1c)(uStack_18,uStack_10,uStack_c,uStack_14);
  } while( true );
}

