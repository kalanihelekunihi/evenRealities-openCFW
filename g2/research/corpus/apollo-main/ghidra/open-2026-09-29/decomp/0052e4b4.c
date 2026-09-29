
int FUN_0052e4b4(int param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  bool bVar1;
  int *piVar2;
  int iVar3;
  int iVar4;
  undefined4 local_30;
  undefined4 local_2c;
  undefined1 local_28;
  undefined4 local_1c;
  undefined4 uStack_18;
  
  local_1c = 0;
  bVar1 = false;
  uStack_18 = param_4;
  FUN_0048949c(&local_2c,0x10);
  local_30 = *DAT_0052f090;
  if (param_1 == 0) {
    iVar3 = 0xc;
  }
  else {
    FUN_0052e49a(1);
    FUN_00480fd6(0x5d,0);
    FUN_004910f4(1);
    FUN_00480fd6(0x5d,1);
    iVar3 = 0;
    while (piVar2 = DAT_0052eba4, *DAT_0052eba4 << 10 < 0) {
      if (iVar3 == 30000) {
        bVar1 = true;
        break;
      }
      FUN_00491102(1);
      iVar3 = iVar3 + 1;
    }
    if (bVar1) {
      iVar3 = 4;
    }
    else {
      iVar3 = 0;
      while (-1 < *piVar2 << 10) {
        if (iVar3 == 30000) {
          bVar1 = true;
          break;
        }
        FUN_00491102(1);
        iVar3 = iVar3 + 1;
      }
      FUN_0052e49a(0);
      if (bVar1) {
        iVar3 = 5;
      }
      else {
        iVar3 = FUN_0052e1ea(param_1,&local_2c,&local_1c);
        if (iVar3 == 0) {
          iVar4 = FUN_004751c8(&local_2c,&local_30,4);
          if (iVar4 == 0) {
            FUN_004733ee(DAT_0052f0e0);
          }
          else {
            iVar3 = 5;
            *DAT_0052eaec = local_2c;
            FUN_004733ee(DAT_0052f0e4,0x452);
            FUN_004733ee(DAT_0052f0e8,local_2c & 0xff,local_2c._1_1_,local_2c._2_1_,local_2c >> 0x18
                         ,local_28);
          }
        }
      }
    }
  }
  return iVar3;
}

