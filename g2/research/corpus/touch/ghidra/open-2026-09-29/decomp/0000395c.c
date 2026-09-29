
void touch_config_065c_bootstrap(void)

{
  int *piVar1;
  int iVar2;
  
  iVar2 = touch_storage_01d8_initialize();
  if (iVar2 == 0) {
    iVar2 = touch_storage_0220_read(0,DAT_000039f8,8);
    if ((iVar2 == 0) && (*DAT_000039f8 == DAT_000039fc)) {
      if (*(short *)((int)DAT_000039f8 + 6) == 0) {
        *(undefined2 *)((int)DAT_000039f8 + 6) = 1000;
      }
      logger_stub(DAT_00003a18,(short)DAT_000039f8[1],*(undefined2 *)((int)DAT_000039f8 + 6),
                  DAT_00003a00);
    }
    else {
      logger_stub(DAT_00003a04,DAT_00003a00);
      iVar2 = touch_storage_02b0_context_operation();
      if (iVar2 == 0) {
        Cy_SysLib_Delay(10);
        piVar1 = DAT_000039f8;
        *DAT_000039f8 = DAT_000039fc;
        *(undefined2 *)(piVar1 + 1) = 0;
        *(undefined2 *)((int)piVar1 + 6) = 1000;
        iVar2 = touch_config_read_adapter(0,piVar1,8);
        if (iVar2 == 0) {
          logger_stub(DAT_00003a08,DAT_00003a00);
        }
        else {
          logger_stub(DAT_00003a14,iVar2,DAT_00003a00);
        }
      }
      else {
        logger_stub(DAT_00003a10,iVar2,DAT_00003a00);
      }
    }
  }
  else {
    logger_stub(DAT_00003a0c,iVar2,DAT_00003a00);
  }
  return;
}

