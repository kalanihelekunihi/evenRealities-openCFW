
void NVIC_SystemReset(void)

{
  DataSynchronizationBarrier(0xf);
  *(undefined4 *)(DAT_00007e28 + 0xc) = DAT_00007e2c;
  DataSynchronizationBarrier(0xf);
  do {
                    /* WARNING: Do nothing block with infinite loop */
  } while( true );
}

