
int FUN_0047021c(undefined2 param_1,uint param_2,char param_3,undefined4 param_4,uint param_5)

{
  int *piVar1;
  int iVar2;
  uint local_34;
  undefined1 local_2f;
  undefined1 local_2e;
  bool local_2d;
  uint local_2c;
  undefined1 local_28;
  undefined2 local_26;
  undefined1 local_24;
  undefined1 local_23;
  undefined4 local_20;
  
  piVar1 = DAT_004708a4;
  if (*DAT_004708a4 == 0) {
    iVar2 = 2;
  }
  else {
    FUN_0048949c(&local_34,0x18);
    if (param_2 < 0x2000000) {
      if (param_5 < 0x101) {
        local_2e = 1;
        local_2c = param_2;
        if (param_3 == '\0') {
          local_2c = 0;
        }
        local_2d = param_3 != '\0';
        local_28 = 1;
        local_24 = 0;
        local_34 = param_5;
        local_2f = 0;
        local_23 = 0;
        local_26 = param_1;
        local_20 = param_4;
        iVar2 = FUN_004c2098(*piVar1,&local_34,DAT_00470a84);
        if (iVar2 != 0) {
          FUN_004733ee(DAT_00470a8c,param_1,param_2,param_5,iVar2);
        }
      }
      else {
        iVar2 = 5;
      }
    }
    else {
      iVar2 = 5;
    }
  }
  return iVar2;
}

