
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

undefined4
gx_xip_init(undefined4 param_1,int param_2,uint param_3,uint param_4,uint param_5,undefined4 param_6
           ,int param_7,int param_8,uint param_9)

{
  int iVar1;
  int iVar2;
  
  param_5 = param_5 >> 1;
  param_9 = param_9 >> 1;
  iVar1 = 0;
  if (param_2 != 0) {
    if (param_2 == 4) {
      iVar1 = 1;
    }
    else if (param_2 == 8) {
      iVar1 = 2;
    }
    else {
      if (param_2 != 0x10) {
        _DAT_a2000008 = 0;
        return 0xffffffff;
      }
      iVar1 = 3;
    }
  }
  if (param_3 >> 1 == 0) {
    iVar2 = 0;
    if (param_5 != 0) {
      if (param_5 != param_9) {
        _DAT_a2000008 = 0;
        return 0xffffffff;
      }
      iVar2 = 1;
    }
  }
  else {
    if (param_3 >> 1 != param_9) {
      _DAT_a2000008 = 0;
      return 0xffffffff;
    }
    if (param_5 != param_9) {
      _DAT_a2000008 = 0;
      return 0xffffffff;
    }
    iVar2 = 2;
  }
  if ((param_4 & 3) != 0) {
    _DAT_a2000008 = 0;
    return 0xffffffff;
  }
  _DAT_a2000108 =
       iVar2 << 2 | iVar1 << 9 | param_8 << 0xd | 0xc00000U | (param_4 >> 2) << 4 | param_9;
  if (param_7 == 1) {
    _DAT_a2000108 = _DAT_a2000108 | 0x8001000;
  }
  uRam00000090 = 0;
  _DAT_a2000008 = 1;
  _DAT_a2000100 = param_1;
  _DAT_a2000104 = param_1;
  _DAT_a200010c = 1;
  _DAT_a2000114 = 0xff;
  return 0;
}

