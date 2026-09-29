
undefined * FUN_00471164(void)

{
  uint uVar1;
  undefined *puVar2;
  
  uVar1 = *DAT_00471ac4;
  puVar2 = DAT_00471ac8;
  if (uVar1 != 0) {
    if (uVar1 == 2) {
      puVar2 = &DAT_0047131c;
    }
    else if (uVar1 < 2) {
      puVar2 = &DAT_00471318;
    }
    else if (uVar1 == 4) {
      puVar2 = &DAT_00471324;
    }
    else if (uVar1 < 4) {
      puVar2 = &DAT_00471320;
    }
    else {
      puVar2 = DAT_00471acc;
      if (uVar1 != 6) {
        if (uVar1 < 6) {
          puVar2 = &DAT_00471328;
        }
        else {
          puVar2 = PTR_s_zh_HK_00471ad0;
          if (uVar1 != 7) {
            puVar2 = DAT_00471ac8;
          }
        }
      }
    }
  }
  return puVar2;
}

