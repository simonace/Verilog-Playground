from collections import namedtuple
ChannelType = namedtuple("ChannelType", ["dir", "paddr", "size"])
channelDict = {"ch0"    :  ChannelType("r", "32'h12345000", 'v'),
               "ch1"    :  ChannelType("t", "32'h4000ac00", 1),
               "ch2"    :  ChannelType("r", "32'h50004400", 2),
               "ch3"    :  ChannelType("t", "32'h4abcd800", 3)
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
