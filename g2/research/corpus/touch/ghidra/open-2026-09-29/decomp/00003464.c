
undefined4 touch_runtime_0164_reset_entry(void)

{
  undefined4 uVar1;
  int iVar2;
  
  iVar2 = iRam000034c4;
  if (iRam000034c4 == 0) {
    iVar2 = iRam000034b8;
  }
  touch_runtime_0158_stack_limit();
  memset(iRam000034c8,0,iRam000034cc - iRam000034c8);
  if (pcRam000034bc != (code *)0x0) {
    (*pcRam000034bc)();
  }
  if (pcRam000034c0 != (code *)0x0) {
    (*pcRam000034c0)();
  }
  uVar1 = 0;
  if (iRam000034d0 != 0) {
    uVar1 = uRam000034d4;
  }
  __libc_init_array(uVar1);
  touch_product_09b4_run(0,0);
  exit_wrapper();
  *(undefined4 *)(iVar2 + -4) = 0x34b7;
  *(undefined4 *)(iVar2 + -8) = 0;
  iVar2 = DAT_00003514;
  if (*DAT_0000350c == '\0') {
    *(undefined4 *)(DAT_00003514 + 8) = DAT_00003510;
    iVar2 = touch_eeprom_5738_initialize_adapter(iVar2,DAT_00003518);
    if ((iVar2 == 0) || (iVar2 == DAT_0000351c)) {
      *DAT_0000350c = '\x01';
      uVar1 = 0;
    }
    else {
      uVar1 = 1;
    }
  }
  else {
    uVar1 = 0;
  }
  return uVar1;
}

