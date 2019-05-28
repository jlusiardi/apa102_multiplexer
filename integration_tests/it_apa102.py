from integration_tests.tools import run_integration
from myhdl import Signal, always, block, intbv, always_comb
from code.apa102_multiplexer import create_multiplex

clock_rate = 50000000
frame_rate = 60


@block
def module(clock, clk_in, ce_in, miso_in, mosi_in, clocks, datas):
    mp = create_multiplex(12, 192)(clock, clk_in, mosi_in, clocks, datas)

    return mp


def create_entity():
    """Convert inc block to Verilog or VHDL."""
    clock = Signal(bool(0))
    reset = Signal(bool(0))  # this is the button
    led_d2 = Signal(bool(0))
    led_d4 = Signal(bool(0))
    led_d5 = Signal(bool(0))

    clk_in = Signal(bool(0))
    miso_in = Signal(bool(0))
    mosi_in = Signal(bool(0))
    ce_in = Signal(bool(0))

    datas = Signal(intbv(0, _nrbits=12))
    clocks = Signal(intbv(0, _nrbits=12))

    return module(clock, clk_in, ce_in, miso_in, mosi_in, clocks, datas)


run_integration(__file__, create_entity())
