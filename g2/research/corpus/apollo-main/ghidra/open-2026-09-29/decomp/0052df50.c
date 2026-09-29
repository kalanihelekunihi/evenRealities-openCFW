
char FUN_0052df50(undefined4 *param_1)

{
  char cVar1;
  int iVar2;
  uint uVar3;
  char local_48;
  char local_47;
  undefined1 local_44;
  undefined1 local_43;
  undefined4 local_40;
  undefined4 local_3c;
  undefined4 local_30;
  undefined1 local_2c;
  undefined1 *local_28;
  undefined1 *local_24;
  undefined1 local_20;
  undefined1 local_1f;
  undefined4 local_1c;
  undefined4 local_18;
  
  *DAT_0052eaf4 = 1;
  local_44 = 0x42;
  local_43 = 0;
  FUN_00480fd6(0x95,0);
  uVar3 = 0;
  while ((uVar3 < 12000 && (-1 < *DAT_0052eba4 << 10))) {
    FUN_00491102(100);
    uVar3 = uVar3 + 1;
  }
  if (*DAT_0052eba4 << 10 < 0) {
    for (uVar3 = 0; uVar3 < 10; uVar3 = uVar3 + 1) {
      FUN_00480fd6(0x95,0);
      iVar2 = FUN_0052dd1c();
      if (iVar2 == 0) {
        FUN_0043c0e4(&local_40,0x30,0);
        local_1f = 0;
        local_1c = 0;
        local_18 = 0;
        local_2c = 2;
        local_3c = 0;
        local_30 = 2;
        local_28 = &local_44;
        local_40 = 0;
        local_20 = 0;
        local_24 = &local_48;
        cVar1 = FUN_0055cf40(param_1[1],&local_40);
        if (cVar1 != '\0') {
          FUN_004733ee(DAT_0052ec80,cVar1,*param_1);
          return '\0';
        }
        if ((local_48 == -0x40) && (local_47 != '\0')) {
          return local_47;
        }
        FUN_00480fd6(0x95,1);
      }
      else {
        FUN_0052dc98(local_44);
        local_47 = FUN_0052dcde();
        if (local_47 != '\0') {
          return local_47;
        }
      }
    }
  }
  else {
    local_47 = '\0';
  }
  return local_47;
}

