
undefined8 FUN_005b3718(undefined1 param_1,undefined1 param_2,undefined4 param_3,undefined4 param_4)

{
  undefined *puVar1;
  int iVar2;
  byte bVar3;
  uint uVar4;
  
  bVar3 = 0;
  for (uVar4 = 0; puVar1 = PTR_DAT_005b3e30, uVar4 < 6; uVar4 = uVar4 + 1) {
    iVar2 = FUN_005b3680(PTR_DAT_005b3e30 + uVar4 * 4,param_1,param_2);
    if (iVar2 != 0) {
      FUN_005b36be(puVar1[uVar4 * 4 + 2],puVar1[uVar4 * 4 + 3]);
      bVar3 = 1;
    }
  }
  return CONCAT44(param_4,(uint)bVar3);
}

