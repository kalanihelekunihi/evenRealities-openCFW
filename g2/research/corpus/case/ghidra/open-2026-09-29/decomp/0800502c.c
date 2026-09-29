
void NVIC_SystemReset(void)

{
  DataSynchronizationBarrier(0xf);
  *(undefined4 *)(DAT_08005044 + 0xc) = DAT_08005040;
  DataSynchronizationBarrier(0xf);
  do {
                    /* WARNING: Do nothing block with infinite loop */
  } while( true );
}

