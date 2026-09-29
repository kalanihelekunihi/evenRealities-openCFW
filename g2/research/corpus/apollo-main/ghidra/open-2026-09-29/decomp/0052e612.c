
undefined8 FUN_0052e612(undefined4 param_1,uint *param_2,undefined4 param_3,int param_4,int param_5)

{
  bool bVar1;
  int iVar2;
  
  if (((param_2 == (uint *)0x0) || (param_4 == 0)) || (param_5 == 0)) {
    iVar2 = 0xc;
  }
  else {
    iVar2 = FUN_0052e0d2(param_1,param_2);
    if (iVar2 == 0) {
      iVar2 = 0;
      while (bVar1 = false, -1 < *DAT_0052eba4 << 10) {
        if (iVar2 == DAT_0052f20c) {
          bVar1 = true;
          break;
        }
        FUN_00491102(1);
        iVar2 = iVar2 + 1;
      }
      if (bVar1) {
        iVar2 = 10;
      }
      else {
        do {
          iVar2 = FUN_0052e1ea(param_1,param_4,param_5);
          if (iVar2 != 0) break;
        } while (((*(uint *)(param_4 + 4) & 0xff) != (*param_2 >> 8 & 0xff)) ||
                ((*(uint *)(param_4 + 4) >> 8 & 0xff) != (*param_2 >> 0x10 & 0xff)));
      }
    }
  }
  return CONCAT44(param_4,iVar2);
}

