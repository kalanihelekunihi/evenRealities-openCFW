# Configuration table selection at 52BC

The 172-byte body [52BC,5368) is followed by four literal pointers. Copy 84 authenticated table bytes from the first literal to output +144 through descriptor word +36. If context bytes +90, +91 or +92 equal exactly 1, replace respective 28-byte rows at output +144, +172 or +200 from the three other literal tables. Context byte +117 equal 5 ORs 256 into output word +188, after second-row replacement and before third-row replacement.

No calls occur. R0 retains the incoming descriptor unless the third replacement executes; then it retains the fourth copied word of that table. The 81 fixtures check all output bytes, literal-backed tables, exact-equality conditions, returned register and frame restoration. Table field meanings and global ownership remain unresolved. No canonical admission or C implementation.
