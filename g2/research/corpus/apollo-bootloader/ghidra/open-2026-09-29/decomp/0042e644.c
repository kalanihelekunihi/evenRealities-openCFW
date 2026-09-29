
void event_callback_loop_42e644(void)

{
  int iVar1;
  undefined4 uStack_c;
  code *pcStack_8;
  
  do {
    while (iVar1 = FUN_00416920(*DAT_0042e838,&uStack_c,0,0xffffffff), iVar1 != 0) {
      elog_output(1,DAT_0042e84c,DAT_0042e848,DAT_0042e878,0x8c,DAT_0042e874,iVar1);
    }
    (*pcStack_8)(uStack_c);
  } while( true );
}

