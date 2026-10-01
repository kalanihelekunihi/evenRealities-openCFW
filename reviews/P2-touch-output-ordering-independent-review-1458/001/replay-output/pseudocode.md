# Output ordering at 50E4

The 158-byte code body [50E4,5182) is followed by alignment NOP and table pointer at 5184. Copy the authenticated 14-word table into a 56-byte stack buffer using original AA2C. Set context bytes +99 through +112 to 255, then set +104 to zero. Context mode +116 equal 1 assigns mapping byte +99 to 1; mode 2 assigns +100 to 1; other modes leave both 255. Assign +107 to 2 for modes 1/2, otherwise 1, and set count byte +98 to that value plus one.

For each of 14 mapping bytes that is not 255, copy the corresponding scratch table word into output +112 plus four times the mapping value. Return zero and restore the 80-byte frame. Fifteen original-instruction fixtures check entire context/output buffers, exact modes and original copy execution. Prior mapping bytes are overwritten before use. Physical meanings and global ownership remain unresolved. No canonical admission or C implementation.
