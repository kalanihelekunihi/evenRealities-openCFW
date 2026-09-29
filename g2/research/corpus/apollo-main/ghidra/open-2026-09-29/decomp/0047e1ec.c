
undefined8 FUN_0047e1ec(void)

{
  int *piVar1;
  uint *puVar2;
  undefined4 uVar3;
  undefined4 in_r3;
  
  puVar2 = DAT_0047e2bc;
  piVar1 = DAT_0047e2b8;
  if (*DAT_0047e2b4 == '\0') {
    uVar3 = 0xfffffffe;
  }
  else {
    if (*DAT_0047e2b8 != 0) {
      if (0x20 < *DAT_0047e2bc) {
        FUN_0047e06a();
        *piVar1 = 0;
        *puVar2 = 0;
        uVar3 = 0;
        goto LAB_0047e21e;
      }
    }
    uVar3 = 0;
  }
LAB_0047e21e:
  return CONCAT44(in_r3,uVar3);
}

