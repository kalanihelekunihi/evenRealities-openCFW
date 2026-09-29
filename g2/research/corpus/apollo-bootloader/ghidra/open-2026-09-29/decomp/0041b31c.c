
void FUN_0041b31c(void)

{
  bool bVar1;
  undefined4 *puVar2;
  undefined4 *puVar3;
  undefined4 uVar4;
  undefined4 unaff_r4;
  undefined4 unaff_r5;
  undefined4 unaff_r6;
  undefined4 unaff_r7;
  undefined4 unaff_r8;
  undefined4 unaff_r9;
  undefined4 unaff_r10;
  undefined4 unaff_r11;
  uint unaff_lr;
  undefined4 unaff_s16;
  undefined4 unaff_s17;
  undefined4 unaff_s18;
  undefined4 unaff_s19;
  undefined4 unaff_s20;
  undefined4 unaff_s21;
  undefined4 unaff_s22;
  undefined4 unaff_s23;
  undefined4 unaff_s24;
  undefined4 unaff_s25;
  undefined4 unaff_s26;
  undefined4 unaff_s27;
  undefined4 unaff_s28;
  undefined4 unaff_s29;
  undefined4 unaff_s30;
  undefined4 unaff_s31;
  
  puVar2 = (undefined4 *)getProcessStackPointer();
  puVar3 = puVar2;
  if ((unaff_lr & 0x10) == 0) {
    puVar3 = puVar2 + -0x10;
    *puVar3 = unaff_s16;
    puVar2[-0xf] = unaff_s17;
    puVar2[-0xe] = unaff_s18;
    puVar2[-0xd] = unaff_s19;
    puVar2[-0xc] = unaff_s20;
    puVar2[-0xb] = unaff_s21;
    puVar2[-10] = unaff_s22;
    puVar2[-9] = unaff_s23;
    puVar2[-8] = unaff_s24;
    puVar2[-7] = unaff_s25;
    puVar2[-6] = unaff_s26;
    puVar2[-5] = unaff_s27;
    puVar2[-4] = unaff_s28;
    puVar2[-3] = unaff_s29;
    puVar2[-2] = unaff_s30;
    puVar2[-1] = unaff_s31;
  }
  uVar4 = getProcessStackPointerLimit();
  puVar3[-1] = unaff_r11;
  puVar3[-2] = unaff_r10;
  puVar3[-3] = unaff_r9;
  puVar3[-4] = unaff_r8;
  puVar3[-5] = unaff_r7;
  puVar3[-6] = unaff_r6;
  puVar3[-7] = unaff_r5;
  puVar3[-8] = unaff_r4;
  puVar3[-9] = unaff_lr;
  puVar3[-10] = uVar4;
  *(undefined4 **)*DAT_0041b388 = puVar3 + -10;
  bVar1 = (bool)isCurrentModePrivileged();
  if (bVar1) {
    setBasePriority(0x30);
  }
  DataSynchronizationBarrier(0xf);
  InstructionSynchronizationBarrier(0xf);
  FUN_00418570(0x30);
  bVar1 = (bool)isCurrentModePrivileged();
  if (bVar1) {
    setBasePriority(0);
  }
  puVar3 = *(undefined4 **)*DAT_0041b388;
  puVar2 = puVar3 + 10;
  if (((uint)puVar3[1] & 0x10) == 0) {
    puVar2 = puVar3 + 0x1a;
  }
  setProcStackPointerLimit(*puVar3);
  bVar1 = (bool)isCurrentModePrivileged();
  if (bVar1) {
    setProcessStackPointer(puVar2);
  }
                    /* WARNING: Could not recover jumptable at 0x0041b372. Too many branches */
                    /* WARNING: Treating indirect jump as call */
  (*(code *)puVar3[1])(puVar2,(int *)*DAT_0041b388,*puVar3);
  return;
}

