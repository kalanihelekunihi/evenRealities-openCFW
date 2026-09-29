
void FUN_0047dac0(void)

{
  undefined4 *puVar1;
  int *piVar2;
  undefined4 uVar3;
  
  piVar2 = DAT_0047dc38;
  puVar1 = DAT_0047dc30;
  if (*DAT_0047dc38 != 0) {
    *DAT_0047dc30 = DAT_0047dc34;
    puVar1[1] = 1;
    puVar1[2] = puVar1[2] + 1;
    puVar1[3] = *piVar2;
    puVar1[4] = 0;
    FUN_00439be4(puVar1 + 6,DAT_0047dc3c,*piVar2);
    *(undefined1 *)((int)puVar1 + *piVar2 + 0x18) = 0;
    uVar3 = FUN_0047d9fc(puVar1);
    puVar1[5] = uVar3;
  }
  return;
}

