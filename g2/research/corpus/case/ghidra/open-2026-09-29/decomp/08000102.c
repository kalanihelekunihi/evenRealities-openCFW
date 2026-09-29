
int xPortPendSVHandler(void)

{
  bool bVar1;
  undefined4 *puVar2;
  int iVar3;
  undefined4 unaff_r4;
  undefined4 unaff_r5;
  undefined4 unaff_r6;
  undefined4 unaff_r7;
  undefined4 unaff_r8;
  undefined4 unaff_r9;
  undefined4 unaff_r10;
  undefined4 unaff_r11;
  
  puVar2 = DAT_08000140;
  iVar3 = getProcessStackPointer();
  *(undefined4 **)*DAT_08000140 = (undefined4 *)(iVar3 + -0x20);
  *(undefined4 *)(iVar3 + -0x20) = unaff_r4;
  *(undefined4 *)(iVar3 + -0x1c) = unaff_r5;
  *(undefined4 *)(iVar3 + -0x18) = unaff_r6;
  *(undefined4 *)(iVar3 + -0x14) = unaff_r7;
  *(undefined4 *)(iVar3 + -0x10) = unaff_r8;
  *(undefined4 *)(iVar3 + -0xc) = unaff_r9;
  *(undefined4 *)(iVar3 + -8) = unaff_r10;
  *(undefined4 *)(iVar3 + -4) = unaff_r11;
  disableIRQinterrupts();
  vTaskSwitchContext(iVar3);
  enableIRQinterrupts();
  bVar1 = (bool)isCurrentModePrivileged();
  if (bVar1) {
    setProcessStackPointer(*(int *)*puVar2 + 0x20);
  }
  return *(int *)*puVar2 + 0x10;
}

