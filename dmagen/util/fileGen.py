from . import rtlWriter

class FixedOrderArbiter(object):
    def __init__(self, channelNum):
        self.channelNum = channelNum
        self.moduleName = "fixed_order_arbiter_" + str(self.channelNum) + "_channels"
        self.portList = [("clk", 'i', 'w', 1),
                         ("rstn", 'i', 'w', 1),
                         ("req", 'i', 'w', self.channelNum),
                         ("channel_available", 'i', 'w', self.channelNum),
                         ("channel_not_trans", 'i', 'w', self.channelNum),
                         ("allow_accept_req", 'i', 'w', self.channelNum),
                         ("start", 'o', 'w', self.channelNum)
                         ]
                         

    def createRtl(self):
        f = open(self.moduleName + ".v", "w+")
        rtlWriter.writeHeaderInfoComment(f, self.moduleName)
        f.write('\n'*2)
        rtlWriter.writeModulePortList(f, self.moduleName, self.portList)
        f.write('\n'*2)
        rtlWriter.writeRegWireLine(f, ("req_pending", 'r', self.channelNum))
        for i in range(self.channelNum-1):
            rtlWriter.writeRegWireLine(f, ("has_pend_0_to_"+str(i), 'w', 1))
        for i in range(self.channelNum-1):
            rtlWriter.writeRegWireLine(f, ("no_pend_0_to_"+str(i), 'w', 1))
        rtlWriter.writeRegWireLine(f, ("no_pend_all", 'w', 1))
        for i in range(self.channelNum-1):
            rtlWriter.writeRegWireLine(f, ("has_req_0_to_"+str(i), 'w', 1))
        for i in range(self.channelNum-1):
            rtlWriter.writeRegWireLine(f, ("no_req_0_to_"+str(i), 'w', 1))
        rtlWriter.writeRegWireLine(f, ("next_pending", 'w', self.channelNum))
        rtlWriter.writeRegWireLine(f, ("start_from_pend", 'w', self.channelNum))
        rtlWriter.writeRegWireLine(f, ("start_from_req", 'w', self.channelNum))
        rtlWriter.writeRegWireLine(f, ("no_busy_channel", 'w', 1))
        f.write('\n'*2)
        for i in range(self.channelNum-1):
            if i == 0:
                rtlWriter.writeAssign(f, "has_pend_0_to_0", ["req_pending[0]"])
            else:
                t = ["has_pend_0_to_"+str(i-1),'|',"req_pending["+ str(i)+"]"]
                rtlWriter.writeAssign(f, "has_pend_0_to_"+str(i), t)
            rtlWriter.writeAssign(f, "no_pend_0_to_"+str(i), ["~has_pend_0_to_"+str(i)])
        rtlWriter.writeAssign(f, "no_pend_all", ["no_pend_0_to_"+str(self.channelNum-2), "&",
                                                 "~req_pending["+str(self.channelNum-1)+"]"])
        for i in range(self.channelNum-1):
            if i == 0:
                rtlWriter.writeAssign(f, "has_req_0_to_0", ["req[0]"])
            else:
                t = ["has_req_0_to_"+str(i-1),'|',"req["+ str(i)+"]"]
                rtlWriter.writeAssign(f, "has_req_0_to_"+str(i), t)
            rtlWriter.writeAssign(f, "no_req_0_to_"+str(i), ["~has_req_0_to_"+str(i)])
        for i in range(self.channelNum):
            t = ["no_pend_all", "&", "req["+str(i)+"]"] + (["&", "no_req_0_to_"+str(i-1)] if i>0 else [])
            rtlWriter.writeAssign(f, "start_from_req["+str(i)+"]", t)
        for i in range(self.channelNum):
            t = ["req_pending["+str(i)+"]"] + (["&", "no_pend_0_to_"+str(i-1)] if i>0 else [])
            rtlWriter.writeAssign(f, "start_from_pend["+str(i)+"]", t)
        rtlWriter.writeAssign(f, "no_busy_channel", ["&channel_not_trans["+str(self.channelNum-1)+":0]"])
        rtlWriter.writeAssign(f, "start", ["(start_from_pend", "|", "start_from_req)", "&",
                                           "{"+str(self.channelNum)+"{no_busy_channel}}", "&",
                                           "channel_available"])
        rtlWriter.writeAssign(f, "next_pending", ["(~start)", "&", "allow_accept_req", "&",
                                                  "(req_pending", "|", "req)", "&",
                                                  "channel_available"])
        f.write('\n'*2)
        sList = [rtlWriter.IfStruct("~rstn", [rtlWriter.AssignStruct("req_pending", [str(self.channelNum) + "'h0"])]),
                 rtlWriter.ElseStruct([rtlWriter.AssignStruct("req_pending", ["next_pending"])])]
        rtlWriter.writeFlop(f, "clk", "rstn", sList, "req_pending")
        f.write("endmodule")
        
        f.close()

class ChannelFsm(object):
    def __init__(self):
        self.moduleName = "dma_channel_fsm"
        self.portList = [("clk", 'i', 'w', 1),
                         ("rstn", 'i', 'w', 1),
                         ("start", 'i', 'w', 1),
                         ("HREADY", 'i', 'w', 1),
                         ("rd_addr", 'i', 'w', 32),
                         ("wr_addr", 'i', 'w', 32),
                         ("hsize", 'i', 'w', 3),
                         ("trans_valid", 'o', 'w', 1),
                         ("trans_hsize", 'o', 'w', 3),
                         ("trans_haddr", 'o', 'w', 32),
                         ("trans_hwrite", 'o', 'w', 1),
                         ("channel_not_trans", 'o', 'w', 1),
                         ("allow_accept_req", 'o', 'w', 1),
                         ("transfer_finish", 'o', 'w', 1)
                         ]

    def createRtl(self):
        f = open(self.moduleName + ".v", "w+")
        rtlWriter.writeHeaderInfoComment(f, self.moduleName)
        f.write('\n'*2)
        rtlWriter.writeModulePortList(f, self.moduleName, self.portList)
        f.write('\n'*2)
        rtlWriter.writeLocalParam(f, "STATE_IDLE", "4'b0001")
        rtlWriter.writeLocalParam(f, "STATE_READ", "4'b0010")
        rtlWriter.writeLocalParam(f, "STATE_WRITE", "4'b0100")
        rtlWriter.writeLocalParam(f, "STATE_TAIL", "4'b1000")
        f.write('\n')
        rtlWriter.writeRegWireLine(f, ("current_state", 'r', 4))
        rtlWriter.writeRegWireLine(f, ("next_state", 'r', 4))
        f.write('\n'*2)
        rtlWriter.writeAssign(f, "trans_valid", ["current_state[1]", "|", "current_state[2]"])
        rtlWriter.writeAssign(f, "trans_size", ["hsize"])
        rtlWriter.writeAssign(f, "trans_haddr", ["current_state[1]", "?", "rd_addr", ":", "(current_state[2]", "?", "wr_addr", ":", "32'h0)"])
        rtlWriter.writeAssign(f, "trans_hwrite", ["current_state[2]"])
        rtlWriter.writeAssign(f, "channel_not_trans", ["current_state[0]", "|", "current_state[3]"])
        rtlWriter.writeAssign(f, "allow_accept_req", ["current_state[0]"])
        f.write('\n')
        caseDict = {"STATE_IDLE": [rtlWriter.IfStruct("start & HREADY", [rtlWriter.AssignStruct("next_state", ["STATE_READ"], False)])],
                    "STATE_READ": [rtlWriter.IfStruct("HREADY", [rtlWriter.AssignStruct("next_state", ["STATE_WRITE"], False)])],
                    "STATE_WRITE": [rtlWriter.IfStruct("HREADY", [rtlWriter.AssignStruct("next_state", ["STATE_TAIL"], False)])],
                    "STATE_TAIL": [rtlWriter.IfStruct("HREADY", [rtlWriter.AssignStruct("next_state", ["STATE_IDLE"], False)])]
                    }
        sNextStateList = [rtlWriter.AssignStruct("next_state", ["current_state"], False), rtlWriter.CaseStruct("current_state", caseDict)]
        rtlWriter.writeFlop(f, "", "", sNextStateList, "next_state")
        f.write('\n')
        sList = [rtlWriter.IfStruct("~rstn", [rtlWriter.AssignStruct("current_state", ["STATE_IDLE"])]),
                 rtlWriter.ElseStruct([rtlWriter.AssignStruct("current_state", ["next_state"])])]
        rtlWriter.writeFlop(f, "clk", "rstn", sList, "req_pending")
        f.write('\n')
        f.write("endmodule")
        f.close()

class DmaRegFile(object):
    def __init__(self, channelDict):
        self.channelDict = channelDict
        self.channelNum = len(self.channelDict)
        self.moduleName = "dma_reg_" + str(self.channelNum) + "_channels"
        self._makeLists()

    def _makeLists(self):
        self.portList = [("PCLK", 'i', 'w', 1),
                         ("PRESETn", 'i', 'w', 1),
                         ("PSEL", 'i', 'w', 1),
                         ("PENABLE", 'i', 'w', 1),
                         ("PWRITE", 'i', 'w', 1),
                         ("PADDR", 'i', 'w', 10),
                         ("PWDATA", 'i', 'w', 32),
                         ("PRDATA", 'o', 'r', 32)
                         ]
        sizeList = []
        dirList = []
        self.vsizeList = []
        self.fsizeList = []
        self.channelNameList = []
        for chName, chType in self.channelDict.items():
            self.channelNameList.append(chName)
            if chType.size == 'v':
                sizeList.append((chName+"_size", 'i', 'w', 2))
                self.vsizeList.append(chName)
            elif chType.size == 1:
                sizeList.append((chName+"_size is fixed as byte", 'c', 'c', 1))
                self.fsizeList.append((chName, "4'b0001"))
            elif chType.size == 2:
                sizeList.append((chName+"_size is fixed as half-word", 'c', 'c', 1))
                self.fsizeList.append((chName, "4'b0010"))
            elif chType.size == 3:
                sizeList.append((chName+"_size is fixed as word", 'c', 'c', 1))
                self.fsizeList.append((chName, "4'b0100"))

            if chType.dir == 't':
                dirList.append((chName+" is TX channel", 'c', 'c', 1))
                dirList.append((chName+"_rd_addr", 'o', 'r', 32))
            elif chType.dir == 'r':
                dirList.append((chName+" is RX channel", 'c', 'c', 1))
                dirList.append((chName+"_wr_addr", 'o', 'r', 32))

        self.portList = self.portList + sizeList + dirList + [("transfer_finish", 'i', 'w', self.channelNum),
                                                              ("channel_available", 'o', 'w', self.channelNum)
                                                              ]

    def createRtl(self):
        f = open(self.moduleName + ".v", "w+")
        rtlWriter.writeHeaderInfoComment(f, self.moduleName)
        f.write('\n'*2)
        rtlWriter.writeModulePortList(f, self.moduleName, self.portList)
        f.write('\n'*2)
        for t in self.fsizeList:
            rtlWriter.writeLocalParam(f, t[0]+"_byte_size", t[1])
        f.write('\n'*2)
        for n in self.vsizeList:
            rtlWriter.writeRegWireLine(f, (n+"_byte_size", 'w', 4))
        f.write('\n')
        rtlWriter.writeRegWireLine(f, ("w_en", 'w', 1))
        rtlWriter.writeRegWireLine(f, ("r_en", 'w', 1))
        for n in self.channelNameList:
            rtlWriter.writeRegWireLine(f, (n+"_channel_addr_match", 'w', 1))
        rtlWriter.writeRegWireLine(f, ("CONTROL_addr_match", 'w', 1))
        rtlWriter.writeRegWireLine(f, ("POINTER_addr_match", 'w', 1))
        rtlWriter.writeRegWireLine(f, ("COUNTER_addr_match", 'w', 1))
        rtlWriter.writeRegWireLine(f, ("NEXT_POINTER_addr_match", 'w', 1))
        rtlWriter.writeRegWireLine(f, ("NEXT_COUNTER_addr_match", 'w', 1))
        for n in self.channelNameList:
            f.write("// " + n + "_channel regs\n")
            rtlWriter.writeRegWireLine(f, (n+"_channel_en", 'r', 1))
            rtlWriter.writeRegWireLine(f, (n+"_channel_cnt", 'r', 16))
            rtlWriter.writeRegWireLine(f, (n+"_channel_next_cnt", 'r', 16))
            rtlWriter.writeRegWireLine(f, (n+"_channel_pnt", 'r', 32))
            rtlWriter.writeRegWireLine(f, (n+"_channel_next_pnt", 'r', 32))
            rtlWriter.writeRegWireLine(f, (n+"_channel_cnt_will_empty", 'w', 1))
            rtlWriter.writeRegWireLine(f, (n+"_channel_cnt_zero", 'w', 1))
            rtlWriter.writeRegWireLine(f, (n+"_channel_next_cnt_zero", 'w', 1))
            rtlWriter.writeRegWireLine(f, (n+"_channel_is_last_trans", 'w', 1))
        rtlWriter.writeAssign(f, "w_en", ["PWRITE", "&", "PSEL", "&", "PENABLE"])
        rtlWriter.writeAssign(f, "r_en", ["(~PWRITE)", "&", "PSEL", "&", "PENABLE"])
        rtlWriter.writeAssign(f, "CONTROL_addr_match", ["PADDR[4:2]", "==", "3'b000"])
        rtlWriter.writeAssign(f, "POINTER_addr_match", ["PADDR[4:2]", "==", "3'b010"])
        rtlWriter.writeAssign(f, "COUNTER_addr_match", ["PADDR[4:2]", "==", "3'b011"])
        rtlWriter.writeAssign(f, "NEXT_POINTER_addr_match", ["PADDR[4:2]", "==", "3'b100"])
        rtlWriter.writeAssign(f, "NEXT_COUNTER_addr_match", ["PADDR[4:2]", "==", "3'b101"])
        for i in range(len(self.channelNameList)):
            b=bin(i)[2:]
            bb="5'b" + '0'*(5-len(b)) + b
            rtlWriter.writeAssign(f, self.channelNameList[i]+"_channel_addr_match", ["PADDR[9:5]", "==", bb])
        for n in self.vsizeList:
            rtlWriter.writeAssign(f, n+"_byte_size", ["4'b0001", "<<", n+"_size"])
        for i in range(len(self.channelNameList)):
            n = self.channelNameList[i]
            rtlWriter.writeAssign(f, n+"_channel_cnt_zero", ["~(|"+n+"_channel_cnt[15:0]"])
            rtlWriter.writeAssign(f, n+"_channel_next_cnt_zero", ["~(|"+n+"_channel_next_cnt[15:0]"])
            rtlWriter.writeAssign(f, n+"_channel_cnt_will_empty", ["("+n+"_channel_cnt", "<=", n+"_byte_size)", "&", "(~"+n+"_channel_cnt_zero)"])
            rtlWriter.writeAssign(f, n+"_channel_is_last_trans", [n+"_channel_cnt_will_empty", "&", n+"_channel_next_cnt_zero", "&",
                                                                  "transfer_finish["+str(i)+"]"])
            rtlWriter.writeAssign(f, "channel_available["+str(i)+"]", ["~("+n+"_channel_cnt_zero", "|", n+"_channel_is_last_trans)", "&",
                                                                       n+"_channel_en"])
        f.write('\n'*2)
        prdataCaseDict = {}
        for i in range(len(self.channelNameList)):
            b=bin(i)[2:]
            bb= '0'*(5-len(b)) + b
            prdataCaseDict["8'b"+ bb + "000"] = [rtlWriter.AssignStruct("PRDATA", ["{31'h0,", self.channelNameList[i]+"_channel_en}"], False)]
            prdataCaseDict["8'b"+ bb + "010"] = [rtlWriter.AssignStruct("PRDATA", [self.channelNameList[i]+"_channel_pnt"], False)]
            prdataCaseDict["8'b"+ bb + "011"] = [rtlWriter.AssignStruct("PRDATA", ["{16'h0,", self.channelNameList[i]+"_channel_cnt}"], False)]
            prdataCaseDict["8'b"+ bb + "100"] = [rtlWriter.AssignStruct("PRDATA", [self.channelNameList[i]+"_channel_next_pnt"], False)]
            prdataCaseDict["8'b"+ bb + "101"] = [rtlWriter.AssignStruct("PRDATA", ["{16'h0,", self.channelNameList[i]+"_channel_next_cnt}"], False)]
        prdataCaseDict["default"] = [rtlWriter.AssignStruct("PRDATA", ["32'h0"], False)] 
        prdataList = [rtlWriter.IfStruct("r_en", [rtlWriter.CaseStruct("PADDR[9:2]", prdataCaseDict)]),
                      rtlWriter.ElseStruct([rtlWriter.AssignStruct("PRDATA", ["32'h0"], False)])
                      ]
        rtlWriter.writeFlop(f, "", "", prdataList, "PRDATA")
        f.write('\n'*2)
        for i in range(len(self.channelNameList)):
            f.write("// " + self.channelNameList[i] + " regfiles\n")
            enList = [rtlWriter.IfStruct("~PRESETn", [rtlWriter.AssignStruct(self.channelNameList[i]+"_channel_en", ["1'b0"])]),
                      rtlWriter.ElifStruct("w_en & "+self.channelNameList[i]+"_channel_addr_match & CONTROL_addr_match",
                                          [rtlWriter.AssignStruct(self.channelNameList[i]+"_channel_en", ["PWDATA[0]"])])]
            rtlWriter.writeFlop(f, "PCLK", "PRESETn", enList, self.channelNameList[i]+" Channel CONTROL register")

            pntList = [rtlWriter.IfStruct("~PRESETn", [rtlWriter.AssignStruct(self.channelNameList[i]+"_channel_pnt", ["32'h0"])]),
                       rtlWriter.ElifStruct("transfer_finish["+str(i)+"]", [rtlWriter.IfStruct(self.channelNameList[i] + "_channel_cnt_will_empty",
                                                                                              [rtlWriter.AssignStruct(self.channelNameList[i]+"_channel_pnt",[self.channelNameList[i]+"_channel_next_pnt"])]),
                                                                           rtlWriter.ElseStruct([rtlWriter.AssignStruct(self.channelNameList[i]+"_channel_pnt",[self.channelNameList[i]+"_channel_pnt",
                                                                                                                                                                "+",self.channelNameList[i]+"_byte_size"])])
                                                                           ]
                                           ),
                       rtlWriter.ElifStruct("w_en & "+self.channelNameList[i]+"_channel_addr_match & POINTER_addr_match",
                                            [rtlWriter.AssignStruct(self.channelNameList[i]+"_channel_pnt", ["PWDATA[31:0]"])])
                       ]
            rtlWriter.writeFlop(f, "PCLK", "PRESETn", pntList, self.channelNameList[i]+" Channel POINTER register")
            
            cntList = [rtlWriter.IfStruct("~PRESETn", [rtlWriter.AssignStruct(self.channelNameList[i]+"_channel_cnt", ["16'h0"])]),
                       rtlWriter.ElifStruct("transfer_finish["+str(i)+"]", [rtlWriter.IfStruct(self.channelNameList[i] + "_channel_cnt_will_empty",
                                                                                              [rtlWriter.AssignStruct(self.channelNameList[i]+"_channel_cnt",[self.channelNameList[i]+"_channel_next_cnt"])]),
                                                                           rtlWriter.ElseStruct([rtlWriter.AssignStruct(self.channelNameList[i]+"_channel_cnt",[self.channelNameList[i]+"_channel_cnt",
                                                                                                                                                                "-",self.channelNameList[i]+"_byte_size"])])
                                                                           ]
                                           ),
                       rtlWriter.ElifStruct("w_en & "+self.channelNameList[i]+"_channel_addr_match & COUNTER_addr_match",
                                            [rtlWriter.AssignStruct(self.channelNameList[i]+"_channel_cnt", ["PWDATA[15:0]"])])
                       ]
            rtlWriter.writeFlop(f, "PCLK", "PRESETn", cntList, self.channelNameList[i]+" Channel COUNTER register")
            
            nPntList = [rtlWriter.IfStruct("~PRESETn", [rtlWriter.AssignStruct(self.channelNameList[i]+"_channel_next_pnt", ["32'h0"])]),
                        rtlWriter.ElifStruct("transfer_finish["+str(i)+"] & "+self.channelNameList[i]+"_channel_cnt_will_empty", [rtlWriter.AssignStruct(self.channelNameList[i]+"_channel_next_pnt", ["32'h0"])]),
                        rtlWriter.ElifStruct("w_en & "+self.channelNameList[i]+"_channel_addr_match & NEXT_POINTER_addr_match",
                                            [rtlWriter.AssignStruct(self.channelNameList[i]+"_channel_next_pnt", ["PWDATA[31:0]"])])
                        ]
            rtlWriter.writeFlop(f, "PCLK", "PRESETn", nPntList, self.channelNameList[i]+" Channel NEXT_POINTER register")

            nCntList = [rtlWriter.IfStruct("~PRESETn", [rtlWriter.AssignStruct(self.channelNameList[i]+"_channel_next_cnt", ["16'h0"])]),
                        rtlWriter.ElifStruct("transfer_finish["+str(i)+"] & "+self.channelNameList[i]+"_channel_cnt_will_empty", [rtlWriter.AssignStruct(self.channelNameList[i]+"_channel_next_cnt", ["16'h0"])]),
                        rtlWriter.ElifStruct("w_en & "+self.channelNameList[i]+"_channel_addr_match & NEXT_COUNTER_addr_match",
                                            [rtlWriter.AssignStruct(self.channelNameList[i]+"_channel_next_cnt", ["PWDATA[15:0]"])])
                        ]
            rtlWriter.writeFlop(f, "PCLK", "PRESETn", nCntList, self.channelNameList[i]+" Channel NEXT_COUNTER register")

            

            f.write('\n')
        f.write('\n')
        f.write("endmodule")
        f.close()
        
