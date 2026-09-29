
bool central_master_link_matches_target_004a2864(int param_1)

{
  int iVar1;
  bool bVar2;
  
  if (*DAT_004a3120 == '\x02') {
    if (*DAT_004a3124 == '\0') {
      bVar2 = false;
    }
    else if ((*DAT_004a3134 == 0) || (*(char *)(*DAT_004a3134 + 0x55) == '\0')) {
      bVar2 = false;
    }
    else if (param_1 == 0) {
      bVar2 = true;
    }
    else {
      iVar1 = DmConnPeerAddr(*(undefined1 *)(*DAT_004a3134 + 0x55));
      if (iVar1 == 0) {
        bVar2 = false;
      }
      else {
        iVar1 = FUN_004751c8(iVar1,param_1,6);
        bVar2 = iVar1 == 0;
      }
    }
  }
  else {
    bVar2 = false;
  }
  return bVar2;
}

