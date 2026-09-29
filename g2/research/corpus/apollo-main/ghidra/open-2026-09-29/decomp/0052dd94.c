
undefined4 FUN_0052dd94(uint param_1,undefined4 *param_2,int *param_3,undefined4 *param_4)

{
  uint *puVar1;
  undefined4 uVar2;
  int iVar3;
  int iVar4;
  int iVar5;
  undefined4 local_34;
  undefined1 auStack_30 [12];
  undefined4 local_24;
  undefined4 local_20;
  undefined4 *puStack_1c;
  
  iVar5 = 0;
  while ((iVar5 == 0 && (*(char *)(DAT_0052e940 + 8) != '\0'))) {
    iVar5 = 1;
  }
  if (iVar5 == 1) {
    uVar2 = 1;
  }
  else if ((param_1 < 9) && (param_2 != (undefined4 *)0x0)) {
    puStack_1c = param_4;
    FUN_004c2b68(param_1,0);
    FUN_0052dc40();
    FUN_00439c04(auStack_30,DAT_0052e944,0x14);
    local_20 = param_2[1];
    local_24 = *param_2;
    iVar3 = FUN_0055c2bc(param_1,&local_34);
    if ((iVar3 == 0) &&
       (((iVar3 = FUN_0055c7e8(local_34,0,0), iVar3 == 0 &&
         (iVar3 = FUN_0055ca94(local_34,auStack_30), iVar3 == 0)) &&
        (iVar4 = FUN_0055c32e(local_34), iVar3 = DAT_0052e940, iVar4 == 0)))) {
      *(undefined1 *)(iVar5 * 0xc + DAT_0052e940 + 8) = 1;
      *(undefined1 *)(iVar5 * 0xc + iVar3 + 9) = 1;
      *(uint *)(iVar3 + iVar5 * 0xc) = param_1;
      *(undefined4 *)(iVar5 * 0xc + iVar3 + 4) = local_34;
      *param_4 = *(undefined4 *)(iVar5 * 0xc + iVar3 + 4);
      *param_3 = iVar3 + iVar5 * 0xc;
      FUN_0052e0a2(*param_3);
      iVar5 = FUN_0052e4b4(*param_3);
      FUN_004733ee(DAT_0052ea1c,iVar5);
      if ((iVar5 == 5) || (iVar5 == 0)) {
        if (iVar5 == 5) {
          FUN_004733ee(DAT_0052ea20);
        }
        FUN_0052f0f8(*param_3,7,iVar5 == 5);
      }
      puVar1 = DAT_0052ea24;
      iVar5 = FUN_0052eeea(*param_3,DAT_0052ea24);
      if ((iVar5 == 0) && (*puVar1 != 0xffffffff)) {
        FUN_004733ee(DAT_0052eae8,*puVar1 >> 0x18,(*puVar1 & 0xffffff) >> 0x10,
                     (*puVar1 & 0xffff) >> 8,(char)*puVar1);
      }
      FUN_0052edd8(0);
      uVar2 = 0;
    }
    else {
      uVar2 = 1;
    }
  }
  else {
    uVar2 = 1;
  }
  return uVar2;
}

