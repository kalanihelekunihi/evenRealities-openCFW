
void FUN_0041a700(void)

{
  DataSynchronizationBarrier(0xf);
  *DAT_0041b04c = *DAT_0041b04c & 0x700 | DAT_0041b050;
  DataSynchronizationBarrier(0xf);
  do {
                    /* WARNING: Do nothing block with infinite loop */
  } while( true );
}

