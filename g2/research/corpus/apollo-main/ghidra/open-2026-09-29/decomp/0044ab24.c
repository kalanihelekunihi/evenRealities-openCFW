
void FUN_0044ab24(void)

{
  DataSynchronizationBarrier(0xf);
  *DAT_0044b4f4 = *DAT_0044b4f4 & 0x700 | DAT_0044b4f8;
  DataSynchronizationBarrier(0xf);
  do {
                    /* WARNING: Do nothing block with infinite loop */
  } while( true );
}

