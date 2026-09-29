
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

uint mode_apply_42ff00(byte param_1,char param_2,undefined4 param_3,uint param_4)

{
  bool bVar1;
  uint uStack_10;
  
  uStack_10 = param_4;
  if (param_1 == 1) {
    boolean_route_status_4303bc(0x81,param_2 == '\x01');
  }
  else if (param_1 == 2) {
    boolean_route_status_4303bc(0x7d,param_2 == '\x01');
  }
  else if (param_1 == 3) {
    boolean_route_status_4303bc(0x80,param_2 == '\x01');
  }
  else if (param_1 == 4) {
    boolean_route_status_4303bc(0x8e,param_2 == '\x01');
  }
  else {
    if ((param_1 != 6) && (param_1 != 7)) {
      if (param_1 == 8) {
        boolean_route_status_4303bc(0x92,param_2 == '\x01');
        return param_4;
      }
      if (param_1 != 9) {
        return param_4;
      }
    }
    uStack_10 = critical_save();
    if (param_2 == '\x01') {
      *_DAT_00430204 = 1 << (uint)param_1 | *_DAT_00430204;
    }
    else if (param_2 == '\0') {
      *_DAT_00430204 = *_DAT_00430204 & ~(1 << (uint)param_1);
    }
    if (*_DAT_00430204 == 0) {
      boolean_route_status_4303bc(0x86,0);
    }
    else {
      boolean_route_status_4303bc(0x86,1);
    }
    bVar1 = (bool)isCurrentModePrivileged();
    if (bVar1) {
      enableIRQinterrupts((uStack_10 & 1) == 1);
    }
  }
  return uStack_10;
}

