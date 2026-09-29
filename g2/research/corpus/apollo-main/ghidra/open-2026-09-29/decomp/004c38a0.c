
int FUN_004c38a0(int param_1,uint *param_2,undefined4 param_3,undefined4 param_4)

{
  bool bVar1;
  int iVar2;
  int iVar3;
  uint local_28;
  uint local_24;
  uint uStack_20;
  uint uStack_1c;
  undefined4 uStack_18;
  
  iVar3 = 0;
  local_24 = *DAT_004c43e0;
  uStack_20 = DAT_004c43e0[1];
  uStack_1c = DAT_004c43e0[2];
  if ((param_1 == 0) || (param_1 == DAT_004c43e4)) {
    uStack_18 = param_4;
    if (param_1 != 0) {
      if (*(int *)(DAT_004c43e8 + 0xc) == 0) {
        return 7;
      }
      if (param_2 == (uint *)0x0) {
        iVar3 = FUN_004d3914(*(undefined4 *)(DAT_004c43e8 + 0xc),param_1,&local_28);
        local_24 = local_24 & 0xfff000ff | (local_28 & 0xfff) << 8;
        param_2 = &local_24;
      }
    }
    if (iVar3 == 0) {
      local_28 = FUN_00473940();
      iVar2 = FUN_004c37ca(4);
      if (iVar2 == 0) {
        if (param_1 != *DAT_004c445c) {
          FUN_004d3944();
          *DAT_004c4464 = 0;
          *DAT_004c4468 = 0;
        }
      }
      else {
        iVar3 = 3;
        if (((param_1 == 0) || (param_1 == DAT_004c43e4)) &&
           ((*DAT_004c445c == 0 || (*DAT_004c445c == DAT_004c43e4)))) {
          if (param_1 == 0) {
            iVar3 = FUN_004d3944();
          }
          else {
            iVar3 = FUN_004d3938(*param_2);
            if (iVar3 != 0) {
              FUN_004d3938(*DAT_004c4460);
            }
          }
        }
      }
      if (iVar3 == 0) {
        if (param_1 != 0) {
          FUN_00439be4(DAT_004c4460,param_2,0xc);
        }
        *DAT_004c445c = param_1;
        *DAT_004c44a0 = 1;
      }
      bVar1 = (bool)isCurrentModePrivileged();
      if (bVar1) {
        enableIRQinterrupts((local_28 & 1) == 1);
      }
    }
  }
  else {
    iVar3 = 5;
  }
  return iVar3;
}

