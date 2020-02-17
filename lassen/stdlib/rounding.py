from lassen import gen_pe, asm
from peak import Peak

#should probably be in isa or something
_MANTISSA_SIZE = 7
_EXPONENT_SIZE = 8
_EXPONENT_BIAS = (1 << (_EXPONENT_SIZE - 1)) - 1

def gen_round_to_zero_bounded(family):
    Data = family.BitVector[16]
    PE = gen_pe(family)
    class RoundToZeroBounded(Peak):
        def __init__(self):
            self.pe1 = PE()
            self.pe2 = PE()

        def __call__(self, in0: Data) -> Data:
            f2i = asm.fgetfint()
            i2f = asm.fcnvsint2f()
            pe1_out,_,_ = self.pe1(f2i, in0)
            pe2_out,_,_ = self.pe2(i2f, pe1_out)
            return pe2_out
    return RoundToZeroBounded

def gen_round_to_zero(family):
    Data = family.BitVector[16]
    PE = gen_pe(family)
    RoundToZeroBounded = gen_round_to_zero_bounded(family)
    class RoundToZero(Peak):
        def __init__(self):
            self.round_to_zero_bounded = RoundToZeroBounded()
            self.pe1 = PE()
            self.pe2 = PE()
            self.pe3 = PE()

        def __call__(self, in0: Data) -> Data:
            exp_mask = Data(((1 << _EXPONENT_SIZE) - 1) << _MANTISSA_SIZE)
            mask_exponent = asm.and_(rb_mode=asm.Mode.CONST, rb_const=exp_mask)
            exp, _, _ = self.pe1(mask_exponent, in0)

            cutoff = Data((_EXPONENT_BIAS + _MANTISSA_SIZE) << _MANTISSA_SIZE)
            cmp_exp = asm.ult(rb_mode=asm.Mode.CONST, rb_const=cutoff)
            _, has_frac_bits, _ = self.pe2(cmp_exp, exp)

            r2z = Data(self.round_to_zero_bounded(in0))
            sel = asm.sel()
            out, _, _ = self.pe3(sel, r2z, in0, has_frac_bits)
            return out

    return RoundToZero
