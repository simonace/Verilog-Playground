from collections import namedtuple
ChannelType = namedtuple("ChannelType", ["dir", "paddr", "size"])
channelDict = {"ch0"       :  ChannelType(["r", "t"], ["32'h49002000", "32'h49002004"], 1),
               "ch1"       :  ChannelType(["t"], ["32'h4900f000"], 1),
               "ch2"       :  ChannelType(["r", "r", "r"], ["32'h49004000", "32'h49004000", "32'h49004000"], 1),
               "ch3"       :  ChannelType(["t", "t", "t", "t", "r"], ["32'h49004004", "32'h49004000", "32'h49004000", "32'h49004000", "32'h49004004"], 1),
               "ch4"       :  ChannelType(["r"], ["32'h4900a008"], 'v')
               }

WITH_NEXT_CNT_PNT_REG = True


import util
if __name__ == "__main__":
    channelNum = len(channelDict)
    arb = util.fileGen.FixedOrderArbiter(channelNum)
    arb.createRtl()
    fsm = util.fileGen.ChannelFsm()
    fsm.createRtl()
    reg = util.fileGen.DmaRegFile(channelDict)
    reg.createRtl(WITH_NEXT_CNT_PNT_REG)
    topFile = util.fileGen.TopFile(channelDict)
    topFile.createRtl()
    ahbFile = util.fileGen.AhbReadWrite()
    ahbFile.createRtl()
