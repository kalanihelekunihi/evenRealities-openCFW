
void FUN_0044e884(undefined4 param_1,int param_2,int param_3,uint param_4)

{
  char cVar1;
  undefined4 uVar2;
  int iVar3;
  undefined4 local_78;
  undefined1 *local_74;
  undefined1 *local_64;
  undefined4 local_58;
  undefined4 local_48;
  uint uStack_18;
  
  if (param_3 != 0 || param_2 != 0) {
    uStack_18 = param_4;
    if ((param_4 & 0xff) == 0) {
      FUN_00450500(param_1,&LAB_0044f3d4_1);
      FUN_00450500(param_1,&LAB_0044f3b8_1);
      cVar1 = FUN_00451670(param_1,0xc,0);
      if ((cVar1 == '\x01') && (cVar1 = FUN_0044ea98(param_1,param_2,param_3), cVar1 == '\x01')) {
        FUN_00451670(param_1,0xe,0);
      }
    }
    else {
      uVar2 = FUN_0044dc0a(param_1);
      FUN_004503d6(&local_78);
      local_64 = &LAB_0044f3f0_1;
      local_78 = param_1;
      if (param_2 != 0) {
        iVar3 = FUN_0044fa7e(uVar2);
        local_48 = FUN_004505a2(iVar3 >> 1,200,400);
        iVar3 = FUN_0044e486(param_1);
        FUN_004506ce(&local_78,-iVar3,param_2 - iVar3);
        local_74 = &LAB_0044f3b8_1;
        local_58 = DAT_0044eb24;
        cVar1 = FUN_00451670(param_1,0xc,&local_78);
        if (cVar1 != '\x01') {
          return;
        }
        FUN_00450408(&local_78);
      }
      if (param_3 != 0) {
        iVar3 = FUN_0044faa8(uVar2);
        local_48 = FUN_004505a2(iVar3 >> 1,200,400);
        iVar3 = FUN_0044e498(param_1);
        FUN_004506ce(&local_78,-iVar3,param_3 - iVar3);
        local_74 = &LAB_0044f3d4_1;
        local_58 = DAT_0044eb24;
        cVar1 = FUN_00451670(param_1,0xc,&local_78);
        if (cVar1 == '\x01') {
          FUN_00450408(&local_78);
        }
      }
    }
  }
  return;
}

