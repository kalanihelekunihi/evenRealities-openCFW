
undefined8 tt_check_single_notdef(int param_1,int param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  uint uVar2;
  uint uVar3;
  byte bVar4;
  uint uVar5;
  uint uVar6;
  int local_28;
  undefined4 local_24;
  undefined4 uStack_20;
  
  bVar4 = 0;
  uVar6 = 0;
  uVar5 = 0;
  uVar3 = 0;
  local_28 = param_2;
  local_24 = param_3;
  uStack_20 = param_4;
  while ((uVar5 < *(uint *)(param_1 + 0x2d4) &&
         ((tt_face_get_location(param_1,uVar5,&local_28), uVar2 = uVar3, local_28 == 0 ||
          (uVar6 = uVar6 + 1, uVar2 = uVar5, uVar6 < 2))))) {
    uVar5 = uVar5 + 1;
    uVar3 = uVar2;
  }
  if (uVar6 == 1) {
    if (uVar3 == 0) {
      bVar4 = 1;
    }
    else {
      iVar1 = FT_Get_Next_Char(param_1,uVar3,&local_24,8);
      if (((iVar1 == 0) && ((char)local_24 == '.')) &&
         (iVar1 = FUN_0044b610(&local_24,DAT_005f94ec,8), iVar1 == 0)) {
        bVar4 = 1;
      }
    }
  }
  return CONCAT44(local_28,(uint)bVar4);
}

