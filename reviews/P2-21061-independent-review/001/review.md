# P2-21061 independent review

Status: partial / unaccepted. No source or gate changes.

Fresh replay passed and exact data JSON matched. The pool is 16 bytes at 0x47F944..0x47F954: four aligned words and 5 mapped PC-load consumers across maps 21428/21430/21432/21434. Consumer literal targets were retained from the decoded records. Adjacent padding at 0x47F942..0x47F944 is excluded; pointed-object ownership and additional consumers are unresolved.
