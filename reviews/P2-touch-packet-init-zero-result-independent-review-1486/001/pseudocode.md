# Packet initialization zero-result tail

Extend 1483 with controlled 51BC status zero as well as nonzero cases. If status zero and record mode is not 1, return 1. For record mode 1, call original 5528(mode,row byte +33,row halfword +14). That helper returns its third argument unless the second low two bits equal 2; then modes 1 or10 shift right2, others shift right1.

Pack (helper result - 1) shifted16 and masked0FFF0000, row byte +33 shifted28 masked30000000, row byte +56 shifted30, and constant3 into adjusted output word +20. Return zero. All shifts/addition use32-bit semantics. The 96 original-instruction fixtures check full48-byte outputs, helper boundary arguments, zero/nonzero result handling and restored frame. Original5528 executes;51BC remains controlled. Uniform fields and indexpair0 constrain scope. Physical meanings remain unresolved. No canonical admission or C implementation.
