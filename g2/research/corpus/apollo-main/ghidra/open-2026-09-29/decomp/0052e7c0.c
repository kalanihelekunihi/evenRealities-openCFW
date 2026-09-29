
undefined8 FUN_0052e7c0(undefined4 param_1)

{
  int iVar1;
  byte bVar2;
  undefined4 uVar3;
  int iVar4;
  int local_20;
  int local_1c;
  uint local_18;
  
  local_1c = 0;
  local_18 = 0;
  local_20 = 0;
  FUN_0052e788(&local_18,&local_20);
  bVar2 = 0;
  do {
    if (local_18 <= bVar2) {
LAB_0052e848:
      uVar3 = 1;
LAB_0052e84a:
      return CONCAT44(local_20,uVar3);
    }
    uVar3 = **(undefined4 **)(local_20 + (uint)bVar2 * 4);
    iVar4 = *(int *)(*(int *)(local_20 + (uint)bVar2 * 4) + 4);
    iVar1 = *(int *)(*(int *)(local_20 + (uint)bVar2 * 4) + 8);
    iVar1 = FUN_0052e6ac(param_1,iVar1,iVar4 + iVar1,&local_1c);
    if (iVar1 != 0) {
      FUN_004733ee(DAT_0052f218,iVar1);
      goto LAB_0052e848;
    }
    iVar1 = FUN_004d34f8(uVar3,iVar4,0);
    if (local_1c != iVar1) {
      FUN_004733ee(DAT_0052f214,local_1c);
      uVar3 = 0;
      goto LAB_0052e84a;
    }
    bVar2 = bVar2 + 1;
  } while( true );
}

