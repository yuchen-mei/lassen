


from peak import Peak, family_closure, Const
from peak import family
from peak.family import AbstractFamily
from peak.family import MagmaFamily, SMTFamily
import magma
from hwtypes import SMTFPVector, FPVector, RoundingMode


DATAWIDTH = 16
def BFloat16_fc(family):
    if isinstance(family, MagmaFamily):
        BFloat16 =  magma.BFloat[16]
        BFloat16.reinterpret_from_bv = lambda bv: BFloat16(bv)
        BFloat16.reinterpret_as_bv = lambda f: magma.Bits[16](f)
        return BFloat16
    elif isinstance(family, SMTFamily):
        FPV = SMTFPVector
    else:
        FPV = FPVector
    BFloat16 = FPV[8, 7, RoundingMode.RNE, False]
    return BFloat16

@family_closure
def fp_addiexp_pipelined_fc(family: AbstractFamily):
    Data = family.BitVector[16]
    Data32 = family.Unsigned[32]
    SInt = family.Signed
    UInt = family.Unsigned[16]
    Bit = family.Bit

    BFloat16 = BFloat16_fc(family)
    FPExpBV = family.BitVector[8]
    FPFracBV = family.BitVector[7]
    BitVector = family.BitVector

    def bv2float(bv):
        return BFloat16.reinterpret_from_bv(bv)

    def float2bv(bvf):
        return BFloat16.reinterpret_as_bv(bvf)

    def fp_get_exp(val : Data):
        return val[7:15]

    def fp_get_frac(val : Data):
        return val[:7]

    def fp_is_zero(val : Data):
        return (fp_get_exp(val) == FPExpBV(0)) & (fp_get_frac(val) == FPFracBV(0))

    def fp_is_inf(val : Data):
        return (fp_get_exp(val) == FPExpBV(-1)) & (fp_get_frac(val) == FPFracBV(0))

    def fp_is_neg(val : Data):
        return Bit(val[-1])

    @family.assemble(locals(), globals())
    class fp_addiexp_pipelined(Peak):
        def __call__(self, in0 : Data, in1 : Data) -> Data:
            
            sign = BitVector[16]((in0 & 0x8000))
            exp = UInt(in0)[7:15]
            exp_check = exp.zext(1)
            exp = exp + UInt(in1)[0:8]
            exp_check = exp_check + UInt(in1)[0:9]
            # Augassign not supported by magma yet
            # exp += SInt[8](in1[0:8])
            # exp_check += SInt[9](in1[0:9])
            exp_shift = BitVector[16](exp)
            exp_shift = exp_shift << 7
            mant = BitVector[16]((in0 & 0x7F))
            res = (sign | exp_shift | mant)
            return res
    
    return fp_addiexp_pipelined
    