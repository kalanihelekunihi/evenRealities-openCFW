
void FUN_0053d0b6(uint *param_1,int param_2)

{
  char cVar1;
  undefined4 uVar2;
  undefined4 uVar3;
  int iVar4;
  undefined4 local_44;
  undefined4 local_40;
  undefined1 auStack_34 [8];
  int local_2c;
  int local_28;
  undefined1 auStack_24 [8];
  int local_1c;
  
  FUN_0048949c(auStack_34,0x10);
  local_2c = (param_1[1] & 0xffff) - 1;
  local_28 = (param_1[1] >> 0x10) - 1;
  if (param_2 == 0) {
    FUN_00439c04(&local_44,auStack_34,0x10);
  }
  else {
    iVar4 = FUN_00450bcc(&local_44,param_2,auStack_34);
    if (iVar4 == 0) {
      return;
    }
  }
  cVar1 = FUN_004b092a(param_1,param_2,1);
  if (cVar1 == '\x01') {
    FUN_004b06c0(0,1,0,0xffffffff,0xffffffff,0);
    FUN_00522a16(0);
    uVar2 = FUN_004515a4(&local_44);
    uVar3 = FUN_00451598(&local_44);
    FUN_00522ae0(local_44,local_40,uVar3,uVar2);
    if ((*param_1 & 0xffff) >> 8 == 0x14) {
      FUN_004b1298(1,param_1[4] + (param_1[1] >> 0x10) * (param_1[1] & 0xffff) * 2,
                   param_1[1] & 0xffff,param_1[1] >> 0x10,8,(param_1[2] & 0xffff) / 2,0);
      FUN_004b06c0(0,1,1,0xffffffff,0xffffffff,0);
      uVar2 = FUN_004515a4(&local_44);
      uVar3 = FUN_00451598(&local_44);
      FUN_00522ae0(local_44,local_40,uVar3,uVar2);
    }
    else if ((((*param_1 & 0xffff) >> 8) - 7 < 4) && (param_2 == 0)) {
      if ((*param_1 & 0xffff) >> 8 == 7) {
        iVar4 = 2;
      }
      else if ((*param_1 & 0xffff) >> 8 == 8) {
        iVar4 = 4;
      }
      else if ((*param_1 & 0xffff) >> 8 == 9) {
        iVar4 = 0x10;
      }
      else if ((*param_1 & 0xffff) >> 8 == 10) {
        iVar4 = 0x100;
      }
      else {
        iVar4 = 0;
      }
      FUN_004b1298(1,param_1[4],iVar4,1,1,0xffffffff,0);
      FUN_0048949c(auStack_24,0x10);
      local_1c = iVar4 + -1;
      FUN_004b077e(0,auStack_24,0);
      FUN_004b06c0(0,1,1,0xffffffff,0xffffffff,0);
      FUN_00522ae0(0,0,iVar4,1);
    }
    FUN_004b0c8a(1);
  }
  return;
}

