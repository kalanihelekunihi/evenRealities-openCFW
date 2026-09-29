
void vTaskSwitchContext(void)

{
  undefined4 *puVar1;
  int iVar2;
  int iVar3;
  int iVar4;
  
  puVar1 = DAT_0800c3f0;
  if (DAT_0800c3f0[0xc] != 0) {
    DAT_0800c3f0[7] = 1;
    return;
  }
  DAT_0800c3f0[7] = 0;
  iVar2 = puVar1[4];
  iVar3 = *(int *)(DAT_0800c3f4 + iVar2 * 0x14);
  while( true ) {
    if (iVar3 != 0) {
      iVar3 = iVar2 * 0x14 + DAT_0800c3f4;
      iVar4 = *(int *)(*(int *)(iVar3 + 4) + 4);
      *(int *)(iVar3 + 4) = iVar4;
      if (iVar4 == iVar3 + 8) {
        *(undefined4 *)(iVar3 + 4) = *(undefined4 *)(iVar4 + 4);
      }
      *puVar1 = *(undefined4 *)(*(int *)(iVar3 + 4) + 0xc);
      puVar1[4] = iVar2;
      return;
    }
    if (iVar2 == 0) break;
    iVar2 = iVar2 + -1;
    iVar3 = *(int *)(DAT_0800c3f4 + iVar2 * 0x14);
  }
  disableIRQinterrupts();
  do {
                    /* WARNING: Do nothing block with infinite loop */
  } while( true );
}

