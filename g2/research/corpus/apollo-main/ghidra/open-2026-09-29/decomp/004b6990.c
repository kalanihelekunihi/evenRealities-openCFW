
void dmConn2HciHandler(undefined2 *param_1)

{
  char cVar1;
  int iVar2;
  
  iVar2 = dmConnCcbByHandle(*param_1);
  if (iVar2 != 0) {
    cVar1 = *(char *)(param_1 + 1);
    if (cVar1 == '\a') {
      dmConn2ActRssiRead(iVar2,param_1);
    }
    else if (cVar1 == '\n') {
      dmConn2ActReadRemoteVerInfoCmpl(iVar2,param_1);
    }
    else if (cVar1 == '\v') {
      dmConn2ActReadRemoteFeaturesCmpl(iVar2,param_1);
    }
    else if (cVar1 == '#') {
      dmConn2ActRemoteConnParamReq(iVar2,param_1);
    }
    else if (cVar1 == '$') {
      dmConn2ActDataLenChange(iVar2,param_1);
    }
    else if (cVar1 == '\'') {
      dmConn2ActWriteAuthToCmpl(iVar2,param_1);
    }
    else if (cVar1 == '(') {
      dmConn2ActAuthToExpired(iVar2,param_1);
    }
    else if (cVar1 == 'G') {
      dmConn2ActReqPeerSca(iVar2,param_1);
    }
  }
  return;
}

