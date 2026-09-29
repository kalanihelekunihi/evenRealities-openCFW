
undefined8
navigation_record_third_field_lookup
          (int param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  int iVar2;
  undefined4 uVar3;
  uint uVar4;
  
  uVar3 = DAT_00588594;
  if (param_1 != 0) {
    for (uVar4 = 0; iVar1 = DAT_00588590, uVar4 < 0x59; uVar4 = uVar4 + 1) {
      iVar2 = FUN_0046cacc(*(undefined4 *)(DAT_00588590 + uVar4 * 0xc),param_1);
      if (iVar2 == 0) {
        uVar3 = *(undefined4 *)(iVar1 + uVar4 * 0xc + 8);
        goto LAB_0058858a;
      }
    }
    uVar3 = *(undefined4 *)(DAT_00588590 + 0x434);
  }
LAB_0058858a:
  return CONCAT44(param_4,uVar3);
}

