
undefined4 pt_protocol_dispatch(char *param_1,char param_2,char *param_3,byte *param_4)

{
  char cVar1;
  int iVar2;
  undefined4 uVar3;
  code *pcVar4;
  uint local_120;
  undefined4 local_11c;
  undefined4 local_118;
  char local_110 [256];
  
  if ((((param_1 == (char *)0x0) || (param_2 == '\0')) || (param_3 == (char *)0x0)) ||
     (param_4 == (byte *)0x0)) {
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      local_118 = DAT_0056fda8;
      local_11c = DAT_0056fdac;
      local_120 = 399;
      FUN_0043d574(1,DAT_0056fbe8,DAT_0056fbe4);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x4400000,DAT_0056fdb0,DAT_0056fdb0,DAT_0056fda8);
    }
    uVar3 = 0xffffffff;
  }
  else {
    cVar1 = *param_1;
    pcVar4 = DAT_0056ffb0;
    if (((((((cVar1 != '\x01') && (pcVar4 = DAT_0056ffb4, cVar1 != '\x05')) &&
           ((pcVar4 = DAT_00570170, cVar1 != '\x06' &&
            (((pcVar4 = DAT_0056ffb8, cVar1 != '\a' && (pcVar4 = DAT_0056ffbc, cVar1 != '\b')) &&
             (pcVar4 = DAT_0056ffc0, cVar1 != '\v')))))) &&
          ((pcVar4 = DAT_00570120, cVar1 != '\x11' && (pcVar4 = DAT_00570124, cVar1 != '\x13')))) &&
         (((pcVar4 = DAT_00570128, cVar1 != '\x17' &&
           (((pcVar4 = DAT_0057012c, cVar1 != '\x18' && (pcVar4 = DAT_00570130, cVar1 != '\x19')) &&
            ((pcVar4 = DAT_00570134, cVar1 != '\x1a' &&
             (((pcVar4 = DAT_00570138, cVar1 != '\x1b' && (pcVar4 = DAT_00570174, cVar1 != '\x1c'))
              && (pcVar4 = DAT_0057013c, cVar1 != ' ')))))))) &&
          (((pcVar4 = DAT_00570178, cVar1 != '\"' && (pcVar4 = DAT_00570140, cVar1 != '$')) &&
           (pcVar4 = DAT_00570144, cVar1 != '%')))))) &&
        (((((pcVar4 = DAT_00570148, cVar1 != '&' && (pcVar4 = DAT_0057014c, cVar1 != ')')) &&
           ((pcVar4 = DAT_00570150, cVar1 != '*' &&
            (((((pcVar4 = DAT_0057017c, cVar1 != '-' && (pcVar4 = DAT_00570180, cVar1 != '.')) &&
               (pcVar4 = DAT_00570154, cVar1 != '0')) &&
              ((pcVar4 = DAT_00570158, cVar1 != '1' && (pcVar4 = DAT_0057015c, cVar1 != '5')))) &&
             (pcVar4 = DAT_00570160, cVar1 != '8')))))) &&
          (((pcVar4 = DAT_00570194, cVar1 != '9' && (pcVar4 = DAT_00570164, cVar1 != ':')) &&
           ((pcVar4 = DAT_00570198, cVar1 != '=' &&
            (((pcVar4 = DAT_00570184, cVar1 != '>' && (pcVar4 = DAT_00570168, cVar1 != 'B')) &&
             (pcVar4 = DAT_0057016c, cVar1 != 'C')))))))) &&
         ((((((pcVar4 = DAT_00570188, cVar1 != 'D' && (pcVar4 = DAT_0057018c, cVar1 != 'E')) &&
             ((pcVar4 = DAT_00570190, cVar1 != 'F' &&
              ((pcVar4 = DAT_0057019c, cVar1 != 'G' && (pcVar4 = DAT_005701a0, cVar1 != 'H')))))) &&
            (pcVar4 = DAT_005701a4, cVar1 != 'I')) &&
           (((((pcVar4 = DAT_005701a8, cVar1 != 'R' && (pcVar4 = DAT_005701ac, cVar1 != 'S')) &&
              (pcVar4 = DAT_005701b0, cVar1 != 'T')) &&
             ((pcVar4 = DAT_005701b4, cVar1 != 'U' && (pcVar4 = DAT_005701b8, cVar1 != 'W')))) &&
            (((pcVar4 = DAT_005701bc, cVar1 != 'X' &&
              ((pcVar4 = DAT_005701c0, cVar1 != 'Y' && (pcVar4 = DAT_005701c4, cVar1 != 'Z')))) &&
             (pcVar4 = DAT_005701c8, cVar1 != '[')))))) &&
          (((((((pcVar4 = DAT_005701d0, cVar1 != '`' && (pcVar4 = DAT_005701d4, cVar1 != 'a')) &&
               (pcVar4 = DAT_005701d8, cVar1 != 'b')) &&
              ((pcVar4 = DAT_005701dc, cVar1 != 'c' && (pcVar4 = DAT_005701e0, cVar1 != 'd')))) &&
             ((pcVar4 = DAT_005701e4, cVar1 != 'e' &&
              ((pcVar4 = DAT_005701e8, cVar1 != 'f' && (pcVar4 = DAT_005701ec, cVar1 != 'g')))))) &&
            (pcVar4 = DAT_005701f0, cVar1 != 'i')) &&
           (((pcVar4 = DAT_005701f4, cVar1 != 'j' && (pcVar4 = DAT_005701f8, cVar1 != 'k')) &&
            (pcVar4 = DAT_005701fc, cVar1 != 'l')))))))))) &&
       ((((pcVar4 = DAT_00570200, cVar1 != 'm' && (pcVar4 = DAT_00570204, cVar1 != 'n')) &&
         ((pcVar4 = DAT_00570208, cVar1 != 't' &&
          ((pcVar4 = DAT_0057020c, cVar1 != 'u' && (pcVar4 = DAT_00570430, cVar1 != 'w')))))) &&
        (pcVar4 = DAT_005701cc, cVar1 != -0xd)))) {
      pcVar4 = (code *)0x0;
    }
    if (pcVar4 == (code *)0x0) {
      *param_3 = cVar1;
      param_3[1] = '\x01';
      param_3[2] = '\x03';
      param_3[3] = '\x01';
      param_3[4] = '\x02';
      *param_4 = 5;
    }
    else {
      (*pcVar4)(param_1,param_2,param_3,param_4);
    }
    FUN_0043c0e4(&local_11c,10,0);
    local_120 = local_120 & 0xffffff00;
    iVar2 = pt_response_prefix(&local_11c,*param_4,&local_120);
    if (iVar2 == 0) {
      if ((uint)*param_4 + (local_120 & 0xff) < 0x101) {
        FUN_0043c0e4(local_110,0x100,0);
        for (iVar2 = 0; iVar2 < (int)(uint)*param_4; iVar2 = iVar2 + 1) {
          local_110[iVar2] = param_3[iVar2];
        }
        for (iVar2 = 0; iVar2 < (int)(local_120 & 0xff); iVar2 = iVar2 + 1) {
          param_3[iVar2] = *(char *)((int)&local_11c + iVar2);
        }
        for (iVar2 = 0; iVar2 < (int)(uint)*param_4; iVar2 = iVar2 + 1) {
          param_3[iVar2 + (local_120 & 0xff)] = local_110[iVar2];
        }
        *param_4 = (char)local_120 + *param_4;
        iVar2 = pt_response_checksum(param_3,param_4);
        if (iVar2 == 0) {
          uVar3 = 0;
        }
        else {
          uVar3 = 0xfffffffc;
        }
      }
      else {
        uVar3 = 0xfffffffd;
      }
    }
    else {
      uVar3 = 0xfffffffe;
    }
  }
  return uVar3;
}

