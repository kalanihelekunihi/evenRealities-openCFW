
undefined2 case_trimmed_average8(void)

{
  undefined2 uVar1;
  uint uVar2;
  uint uVar3;
  uint uVar4;
  byte bVar5;
  int iVar6;
  
  FUN_080047d4(DAT_08002f24);
  case_wait_peripheral(DAT_08002f24,10);
  iVar6 = 0;
  uVar4 = 0xffffffff;
  uVar3 = 0;
  bVar5 = 0;
  do {
    uVar2 = case_handle_word16(DAT_08002f24);
    if (uVar3 < uVar2) {
      uVar3 = uVar2;
    }
    if (uVar2 < uVar4) {
      uVar4 = uVar2;
    }
    bVar5 = bVar5 + 1;
    iVar6 = iVar6 + uVar2;
  } while (bVar5 < 8);
  case_guarded_two_stage(DAT_08002f24);
  uVar1 = __aeabi_uidiv((iVar6 - uVar3) - uVar4,6);
  return uVar1;
}

