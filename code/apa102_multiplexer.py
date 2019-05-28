from myhdl import block, always, intbv, Signal, always_comb


def create_multiplex(stripes=12, leds=192):
    MAX_BITS = (1 + stripes * leds + 1) * 32

    @block
    def multiplex(clk, i_clock, i_data, o_clocks, o_datas):
        assert i_clock._nrbits == 1, 'Width of i_clock must be 1 bit.'
        assert i_data._nrbits == 1, 'Width of i_data must be 1 bit.'
        assert o_clocks._nrbits == stripes, 'Width of clocks must be %i bit.' % stripes
        assert o_datas._nrbits == stripes, 'Width of clocks must be %i bit.' % stripes

        state = Signal(intbv(0, min=0, max=1 + MAX_BITS))
        zero_counter = Signal(intbv(0, min=0, max=32))

        @always(clk)
        def handle():
            if i_clock.negedge:
                state.next = (state + 1) % MAX_BITS
            # use to sync stuff
            if i_clock.posedge:
                if i_data == 1:
                    zero_counter.next = (zero_counter + 1) % 32
                    if zero_counter + 1 == 32:
                        state.next = 32
            if state < 32 or (MAX_BITS - 32) <= state:
                # write signals to all stripes
                for stripe in range(stripes):
                    o_clocks.next[stripe] = i_clock
                    o_datas.next[stripe] = i_data
                pass
            else:
                # write signal to single stripe ( = (state - 32) // (leds * 32) )
                o_clocks.next = 0
                o_datas.next = 0
                o_clocks.next[((state - 32) // (leds * 32))] = i_clock
                o_datas.next[((state - 32) // (leds * 32))] = i_data

        return handle

    return multiplex
