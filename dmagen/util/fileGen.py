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
        rtlWriter.writeRegWireLine(f, ("allow_accept_req_d", 'r', 1))
        f.write('\n'*2)
        rtlWriter.writeAssign(f, "trans_valid", ["current_state[1]", "|", "current_state[2]"])
        rtlWriter.writeAssign(f, "trans_hsize", ["hsize"])
        rtlWriter.writeAssign(f, "trans_haddr", ["current_state[1]", "?", "rd_addr", ":", "(current_state[2]", "?", "wr_addr", ":", "32'h0)"])
        rtlWriter.writeAssign(f, "trans_hwrite", ["current_state[2]"])
        rtlWriter.writeAssign(f, "channel_not_trans", ["current_state[0]", "|", "current_state[3]"])
        rtlWriter.writeAssign(f, "allow_accept_req", ["current_state[0]"])
        rtlWriter.writeAssign(f, "transfer_finish", ["~allow_accept_req_d", "&", "allow_accept_req"])
        f.write('\n')
        caseDict = {"STATE_IDLE": [rtlWriter.IfStruct("start", [rtlWriter.AssignStruct("next_state", ["STATE_READ"], False)])],
                    "STATE_READ": [rtlWriter.IfStruct("HREADY", [rtlWriter.AssignStruct("next_state", ["STATE_WRITE"], False)])],
                    "STATE_WRITE": [rtlWriter.IfStruct("HREADY", [rtlWriter.AssignStruct("next_state", ["STATE_TAIL"], False)])],
                    "STATE_TAIL": [rtlWriter.IfStruct("HREADY", [rtlWriter.AssignStruct("next_state", ["STATE_IDLE"], False)])]
                    }
        sNextStateList = [rtlWriter.AssignStruct("next_state", ["current_state"], False), rtlWriter.CaseStruct("current_state", caseDict)]
        rtlWriter.writeFlop(f, "", "", sNextStateList, "next_state")
        f.write('\n')
        sList = [rtlWriter.IfStruct("~rstn", [rtlWriter.AssignStruct("current_state", ["STATE_IDLE"]),
                                              rtlWriter.AssignStruct("allow_accept_req_d", ["1'b1"])]),
                 rtlWriter.ElseStruct([rtlWriter.AssignStruct("current_state", ["next_state"]),
                                       rtlWriter.AssignStruct("allow_accept_req_d", ["allow_accept_req"])])]
        rtlWriter.writeFlop(f, "clk", "rstn", sList)
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
        selList = []
        self.channelNameList = []
        cntZeroList = []
        enableList = []
        sizeList = []
        for chName, chType in self.channelDict.items():
            self.channelNameList.append(chName)
            self.portList.append((chName+"_pointer", 'o', 'w', 32))
            sizeList.append((chName+"_size", 'i', 'w', 2))
            cntZeroList.append((chName+"_channel_cnt_zero",'o', 'w', 1))
            enableList.append((chName+"_channel_en", 'o', 'r', 1))

            if len(chType.dir)>1:
                selList.append((chName+"_sel", 'o', 'r', 3))

        self.portList = self.portList + sizeList + selList + cntZeroList + enableList + [("transfer_finish", 'i', 'w', self.channelNum),
                                                                                         ("channel_available", 'o', 'w', self.channelNum)
                                                                                         ]

    def createRtl(self, withNextCntPntReg):
        f = open(self.moduleName + ".v", "w+")
        rtlWriter.writeHeaderInfoComment(f, self.moduleName)
        f.write('\n'*2)
        rtlWriter.writeModulePortList(f, self.moduleName, self.portList)
        f.write('\n'*2)
        rtlWriter.writeRegWireLine(f, ("w_en", 'w', 1))
        rtlWriter.writeRegWireLine(f, ("r_en", 'w', 1))
        for n in self.channelNameList:
            rtlWriter.writeRegWireLine(f, (n+"_channel_addr_match", 'w', 1))
        rtlWriter.writeRegWireLine(f, ("CONTROL_addr_match", 'w', 1))
        rtlWriter.writeRegWireLine(f, ("POINTER_addr_match", 'w', 1))
        rtlWriter.writeRegWireLine(f, ("COUNTER_addr_match", 'w', 1))
        if withNextCntPntReg:
            rtlWriter.writeRegWireLine(f, ("NEXT_POINTER_addr_match", 'w', 1))
            rtlWriter.writeRegWireLine(f, ("NEXT_COUNTER_addr_match", 'w', 1))
        for n in self.channelNameList:
            f.write("// " + n + "_channel regs\n")
            rtlWriter.writeRegWireLine(f, (n+"_channel_cnt", 'r', 16))
            rtlWriter.writeRegWireLine(f, (n+"_channel_pnt", 'r', 32))
            if withNextCntPntReg:
                rtlWriter.writeRegWireLine(f, (n+"_channel_next_cnt", 'r', 16))
                rtlWriter.writeRegWireLine(f, (n+"_channel_next_pnt", 'r', 32))
            rtlWriter.writeRegWireLine(f, (n+"_channel_cnt_will_empty", 'w', 1))
            if withNextCntPntReg:
                rtlWriter.writeRegWireLine(f, (n+"_channel_next_cnt_zero", 'w', 1))
            rtlWriter.writeRegWireLine(f, (n+"_channel_is_last_trans", 'w', 1))
            rtlWriter.writeRegWireLine(f, (n+"_byte_size", 'w', 4))
        rtlWriter.writeAssign(f, "w_en", ["PWRITE", "&", "PSEL", "&", "PENABLE"])
        rtlWriter.writeAssign(f, "r_en", ["(~PWRITE)", "&", "PSEL", "&", "PENABLE"])
        rtlWriter.writeAssign(f, "CONTROL_addr_match", ["PADDR[4:2]", "==", "3'b000"])
        rtlWriter.writeAssign(f, "POINTER_addr_match", ["PADDR[4:2]", "==", "3'b010"])
        rtlWriter.writeAssign(f, "COUNTER_addr_match", ["PADDR[4:2]", "==", "3'b011"])
        if withNextCntPntReg:
            rtlWriter.writeAssign(f, "NEXT_POINTER_addr_match", ["PADDR[4:2]", "==", "3'b100"])
            rtlWriter.writeAssign(f, "NEXT_COUNTER_addr_match", ["PADDR[4:2]", "==", "3'b101"])
        for i in range(len(self.channelNameList)):
            b=bin(i)[2:]
            bb="5'b" + '0'*(5-len(b)) + b
            rtlWriter.writeAssign(f, self.channelNameList[i]+"_channel_addr_match", ["PADDR[9:5]", "==", bb])
        for n in self.channelNameList:
            rtlWriter.writeAssign(f, n+"_byte_size", ["4'b0001", "<<", n+"_size"])
        for i in range(len(self.channelNameList)):
            n = self.channelNameList[i]
            rtlWriter.writeAssign(f, n+"_channel_cnt_zero", ["~(|"+n+"_channel_cnt[15:0])"])
            if withNextCntPntReg:
                rtlWriter.writeAssign(f, n+"_channel_next_cnt_zero", ["~(|"+n+"_channel_next_cnt[15:0])"])
            rtlWriter.writeAssign(f, n+"_channel_cnt_will_empty", ["("+n+"_channel_cnt", "<=", n+"_byte_size)", "&", "(~"+n+"_channel_cnt_zero)"])
            if withNextCntPntReg:
                rtlWriter.writeAssign(f, n+"_channel_is_last_trans", [n+"_channel_cnt_will_empty", "&", n+"_channel_next_cnt_zero", "&",
                                                                      "transfer_finish["+str(i)+"]"])
            else:
                rtlWriter.writeAssign(f, n+"_channel_is_last_trans", [n+"_channel_cnt_will_empty", "&","transfer_finish["+str(i)+"]"])
            rtlWriter.writeAssign(f, "channel_available["+str(i)+"]", ["~("+n+"_channel_cnt_zero", "|", n+"_channel_is_last_trans)", "&",
                                                                       n+"_channel_en"])
            rtlWriter.writeAssign(f, n+"_pointer", [n+"_channel_pnt"])
        f.write('\n'*2)
        prdataCaseDict = {}
        for i in range(len(self.channelNameList)):
            chName = self.channelNameList[i]
            b=bin(i)[2:]
            bb= '0'*(5-len(b)) + b
            selReg = chName+"_sel" if len(self.channelDict[chName].dir)>1 else "3'b000"
            prdataCaseDict["8'b"+ bb + "000"] = [rtlWriter.AssignStruct("PRDATA", ["{28'h0,", selReg+",", chName+"_channel_en}"], False)]
            prdataCaseDict["8'b"+ bb + "010"] = [rtlWriter.AssignStruct("PRDATA", [chName+"_channel_pnt"], False)]
            prdataCaseDict["8'b"+ bb + "011"] = [rtlWriter.AssignStruct("PRDATA", ["{16'h0,", chName+"_channel_cnt}"], False)]
            if withNextCntPntReg:
                prdataCaseDict["8'b"+ bb + "100"] = [rtlWriter.AssignStruct("PRDATA", [chName+"_channel_next_pnt"], False)]
                prdataCaseDict["8'b"+ bb + "101"] = [rtlWriter.AssignStruct("PRDATA", ["{16'h0,", chName+"_channel_next_cnt}"], False)]
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
            if len(self.channelDict[self.channelNameList[i]].dir)>1:
                selRegList = [rtlWriter.IfStruct("~PRESETn", [rtlWriter.AssignStruct(self.channelNameList[i]+"_sel", ["3'b000"])]),
                              rtlWriter.ElifStruct("w_en & "+self.channelNameList[i]+"_channel_addr_match & CONTROL_addr_match",
                                                   [rtlWriter.AssignStruct(self.channelNameList[i]+"_sel", ["PWDATA[3:1]"])])]
                rtlWriter.writeFlop(f, "PCLK", "PRESETn", selRegList)

            pntList = [rtlWriter.IfStruct("~PRESETn", [rtlWriter.AssignStruct(self.channelNameList[i]+"_channel_pnt", ["32'h0"])]),
                       rtlWriter.ElifStruct("transfer_finish["+str(i)+"]", [rtlWriter.IfStruct(self.channelNameList[i] + "_channel_cnt_will_empty",
                                                                                              [rtlWriter.AssignStruct(self.channelNameList[i]+"_channel_pnt",[self.channelNameList[i]+"_channel_next_pnt" if withNextCntPntReg
                                                                                                                                                              else "32'h0"])]),
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
                                                                                              [rtlWriter.AssignStruct(self.channelNameList[i]+"_channel_cnt",[self.channelNameList[i]+"_channel_next_cnt" if withNextCntPntReg
                                                                                                                                                              else "32'h0"])]),
                                                                           rtlWriter.ElseStruct([rtlWriter.AssignStruct(self.channelNameList[i]+"_channel_cnt",[self.channelNameList[i]+"_channel_cnt",
                                                                                                                                                                "-",self.channelNameList[i]+"_byte_size"])])
                                                                           ]
                                           ),
                       rtlWriter.ElifStruct("w_en & "+self.channelNameList[i]+"_channel_addr_match & COUNTER_addr_match",
                                            [rtlWriter.AssignStruct(self.channelNameList[i]+"_channel_cnt", ["PWDATA[15:0]"])])
                       ]
            rtlWriter.writeFlop(f, "PCLK", "PRESETn", cntList, self.channelNameList[i]+" Channel COUNTER register")
            if withNextCntPntReg:
                nPntList = [rtlWriter.IfStruct("~PRESETn", [rtlWriter.AssignStruct(self.channelNameList[i]+"_channel_next_pnt", ["32'h0"])]),
                            rtlWriter.ElifStruct("transfer_finish["+str(i)+"] & "+self.channelNameList[i]+"_channel_cnt_will_empty", [rtlWriter.AssignStruct(self.channelNameList[i]+"_channel_next_pnt", ["32'h0"])]),
                            rtlWriter.ElifStruct("w_en & "+self.channelNameList[i]+"_channel_addr_match & NEXT_POINTER_addr_match",
                                                 [rtlWriter.AssignStruct(self.channelNameList[i]+"_channel_next_pnt", ["PWDATA[31:0]"])])]
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

class TopFile(object):
    def __init__(self, channelDict):
        self.channelDict = channelDict
        self.channelNum = len(self.channelDict)
        self.moduleName = "dma_" + str(self.channelNum) + "_channels"
        self.portList = [("APB interface", 'c', 'c', 1),
                         ("PCLK", 'i', 'w', 1),
                         ("PRESETn", 'i', 'w', 1),
                         ("PSEL", 'i', 'w', 1),
                         ("PENABLE", 'i', 'w', 1),
                         ("PWRITE", 'i', 'w', 1),
                         ("PADDR", 'i', 'w', 10),
                         ("PWDATA", 'i', 'w', 32),
                         ("PRDATA", 'o', 'w', 32),
                         ("AHB interface", 'c', 'c', 1),
                         ("HCLK", 'i', 'w', 1),
                         ("HRESETn", 'i', 'w', 1),
                         ("HREADY", 'i', 'w', 1),
                         ("HRDATA", 'i', 'w', 32),
                         ("HADDR", 'o', 'w', 32),
                         ("HWRITE", 'o', 'w', 1),
                         ("HSIZE", 'o', 'w', 3),
                         ("HWDATA", 'o', 'w', 32),
                         ("HTRANS", 'o', 'w', 2),
                         ("DMA interface", 'c', 'c', 1)
                         ]
        for n, t in self.channelDict.items():
            self.portList.append((n+"_req", 'i', 'w', len(t.dir)))
        self.fsizeList = []
        for n, t in self.channelDict.items():
            if len(t.size)==1:
                self.portList.append(("Channel " + n + " only has one function", 'c', 'c', 1))
                self.portList.append((n+"_size", 'i', 'w', 3))
            else:
                self.portList.append(("Channel " + n + " only has "+str(len(t.size)) + " functions", 'c', 'c', 1))
                for i in range(len(t.size)):
                    if t.size[i]=='v':
                        self.portList.append((n+"_" + str(i)+"_size", 'i', 'w', 3))
                    elif t.size[i]==1:
                        self.portList.append((n+"_" + str(i)+"_size is fixed as byte", 'c', 'c', 1))
                        self.fsizeList.append((n+"_" + str(i)+"_size", "3'b000"))
                    elif t.size[i]==2:
                        self.portList.append((n+"_" + str(i)+"_size is fixed as half-word", 'c', 'c', 1))
                        self.fsizeList.append((n+"_" + str(i)+"_size", "3'b001"))
                    elif t.size[i]==3:
                        self.portList.append((n+"_" + str(i)+"_size is fixed as word", 'c', 'c', 1))
                        self.fsizeList.append((n+"_" + str(i)+"_size", "3'b010"))
        for n, t in self.channelDict.items():
            self.portList.append((n+"_channel_en", 'o', 'w', len(t.dir)))
        for n in self.channelDict.keys():
            self.portList.append((n+"_channel_cnt_zero", 'o', 'w', 1))

    def createRtl(self):
        f = open(self.moduleName + ".v", "w+")
        rtlWriter.writeHeaderInfoComment(f, self.moduleName)
        self._channelDiscriptionComment(f)
        f.write('\n'*2)
        rtlWriter.writeModulePortList(f, self.moduleName, self.portList)
        f.write('\n'*2)
        for t in self.fsizeList:
            rtlWriter.writeLocalParam(f, t[0], t[1])
        f.write('\n')
        rtlWriter.writeRegWireLine(f, ("req", 'w', self.channelNum))
        for n, t in self.channelDict.items():
            f.write("// Channel "+n+" signals\n")
            rtlWriter.writeRegWireLine(f, (n+"_channel_en_all", 'w', 1))
            rtlWriter.writeRegWireLine(f, (n+"_trans_valid", 'w', 1))
            rtlWriter.writeRegWireLine(f, (n+"_trans_hsize", 'w', 3))
            rtlWriter.writeRegWireLine(f, (n+"_trans_haddr", 'w', 32))
            rtlWriter.writeRegWireLine(f, (n+"_trans_hwrite", 'w', 1))
            rtlWriter.writeRegWireLine(f, (n+"_wr_addr", 'w', 32))
            rtlWriter.writeRegWireLine(f, (n+"_rd_addr", 'w', 32))
            rtlWriter.writeRegWireLine(f, (n+"_pointer", 'w', 32))
            if len(t.dir)>1:
                rtlWriter.writeRegWireLine(f, (n+"_sel", 'w', 3))
                rtlWriter.writeRegWireLine(f, (n+"_size", 'w', 3))
            else:
                f.write("// Channel " + n + " only has one function\n")
                f.write("// No "+n+"_sel signal \n")
                f.write("// "+n+"_size is directly from port\n")
        f.write('\n')
        rtlWriter.writeRegWireLine(f, ("start", 'w', self.channelNum))
        rtlWriter.writeRegWireLine(f, ("channel_available", 'w', self.channelNum))
        rtlWriter.writeRegWireLine(f, ("channel_not_trans", 'w', self.channelNum))
        rtlWriter.writeRegWireLine(f, ("allow_accept_req", 'w', self.channelNum))
        rtlWriter.writeRegWireLine(f, ("transfer_finish", 'w', self.channelNum))
        rtlWriter.writeRegWireLine(f, ("trans_valid", 'w', 1))
        rtlWriter.writeRegWireLine(f, ("trans_hsize", 'r', 3))
        rtlWriter.writeRegWireLine(f, ("trans_haddr", 'r', 32))
        rtlWriter.writeRegWireLine(f, ("trans_hwrite", 'r', 1))
        f.write('\n'*2)
        caseDict = {}
        validList = []
        i = 0
        for n in self.channelDict.keys():
            caseDict[n+"_trans_valid"] = [rtlWriter.AssignStruct("trans_hsize", [n+"_trans_hsize"], False),
                                          rtlWriter.AssignStruct("trans_haddr", [n+"_trans_haddr"], False),
                                          rtlWriter.AssignStruct("trans_hwrite", [n+"_trans_hwrite"], False)]
            validList.append(n+"_trans_valid")
            if not i==self.channelNum-1:
                validList.append("|")
                if i%4==0 and i !=0:
                    validList.append('\n')
            i=i+1  
        muxList = [rtlWriter.AssignStruct("trans_hsize", ["3'b000"], False),
                   rtlWriter.AssignStruct("trans_haddr", ["32'h0"], False),
                   rtlWriter.AssignStruct("trans_hwrite", ["1'b0"], False),
                   rtlWriter.CaseStruct("1'b1", caseDict)]
        f.write('\n'*2)
        rtlWriter.writeFlop(f, "", "", muxList)
        f.write('\n')
        rtlWriter.writeAssign(f, "trans_valid", validList)
        f.write('\n')
        j=0
        for n, t in self.channelDict.items():
            if len(t.dir)>1:
                wrAddrList = []
                rdAddrList = []
                reqList = []
                sizeList = []
                for i in range(len(t.dir)):
                    b=bin(i)[2:]
                    bb="(" + n + "_sel == 3'b" + '0'*(3-len(b)) + b + ")"
                    rtlWriter.writeAssign(f, n+"_channel_en["+str(i)+"]", [bb, '&', n+"_channel_en_all"])
                    reqList = reqList + [bb, "?", n+"_req["+str(i)+"]", ":", '\n']
                    sizeList = sizeList + [bb, "?", n+'_'+str(i)+"_size", ":", '\n']
                    if t.dir[i] == 'r':
                        wrAddrList = wrAddrList + [bb, "?", n+"_pointer", ":", '\n']
                        rdAddrList = rdAddrList + [bb, "?", t.paddr[i], ":", '\n']
                    elif t.dir[i] == 't':
                        rdAddrList = rdAddrList + [bb, "?", n+"_pointer", ":", '\n']
                        wrAddrList = wrAddrList + [bb, "?", t.paddr[i], ":", '\n']
                reqList.append("1'b0")
                wrAddrList.append("32'h0")
                rdAddrList.append("32'h0")
                sizeList.append("3'b000")
                rtlWriter.writeAssign(f, "req["+str(j)+"]", reqList)
                rtlWriter.writeAssign(f, n+"_rd_addr", rdAddrList)
                rtlWriter.writeAssign(f, n+"_wr_addr", wrAddrList)
                rtlWriter.writeAssign(f, n+"_size", sizeList)
            else:
                rtlWriter.writeAssign(f, n+"_channel_en", [n+"_channel_en_all"])
                rtlWriter.writeAssign(f, "req["+str(j)+"]", [n+"_req"])
                if t.dir[0] == 'r':
                    rtlWriter.writeAssign(f, n+"_rd_addr", [t.paddr[0]])
                    rtlWriter.writeAssign(f, n+"_wr_addr", [n+"_pointer"])
                elif t.dir[0] == 't':
                    rtlWriter.writeAssign(f, n+"_rd_addr", [n+"_pointer"])
                    rtlWriter.writeAssign(f, n+"_wr_addr", [t.paddr[0]])
            j = j+1
            f.write('\n')            
        f.write('\n'*2)
        f.write("fixed_order_arbiter_" + str(self.channelNum) + "_channels u_arb(\n")
        rtlWriter.writeInstancePortLine(f, "clk", "HCLK")
        rtlWriter.writeInstancePortLine(f, "rstn", "HRESETn")
        rtlWriter.writeInstancePortLine(f, "req", "req")
        rtlWriter.writeInstancePortLine(f, "channel_available", "channel_available")
        rtlWriter.writeInstancePortLine(f, "channel_not_trans", "channel_not_trans")
        rtlWriter.writeInstancePortLine(f, "allow_accept_req", "allow_accept_req")
        rtlWriter.writeInstancePortLine(f, "start", "start", False)
        f.write(");\n")
        f.write('\n')
        f.write("ahb_lite_master_rw_interface u_rw_interface(\n")
        rtlWriter.writeInstancePortLine(f, "HCLK", "HCLK")
        rtlWriter.writeInstancePortLine(f, "HRESETn", "HRESETn")
        rtlWriter.writeInstancePortLine(f, "HREADY", "HREADY")
        rtlWriter.writeInstancePortLine(f, "HRDATA", "HRDATA")
        rtlWriter.writeInstancePortLine(f, "HADDR", "HADDR")
        rtlWriter.writeInstancePortLine(f, "HWRITE", "HWRITE")
        rtlWriter.writeInstancePortLine(f, "HSIZE", "HSIZE")
        rtlWriter.writeInstancePortLine(f, "HWDATA", "HWDATA")
        rtlWriter.writeInstancePortLine(f, "HTRANS", "HTRANS")
        rtlWriter.writeInstancePortLine(f, "trans_valid", "trans_valid")
        rtlWriter.writeInstancePortLine(f, "trans_hsize", "trans_hsize")
        rtlWriter.writeInstancePortLine(f, "trans_haddr", "trans_haddr")
        rtlWriter.writeInstancePortLine(f, "trans_hwrite", "trans_hwrite", False)
        f.write(");\n")
        f.write('\n')
        f.write("dma_reg_" + str(self.channelNum) + "_channels u_reg(\n")
        rtlWriter.writeInstancePortLine(f, "PCLK", "PCLK")
        rtlWriter.writeInstancePortLine(f, "PRESETn", "PRESETn")
        rtlWriter.writeInstancePortLine(f, "PSEL", "PSEL")
        rtlWriter.writeInstancePortLine(f, "PENABLE", "PENABLE")
        rtlWriter.writeInstancePortLine(f, "PWRITE", "PWRITE")
        rtlWriter.writeInstancePortLine(f, "PADDR", "PADDR")
        rtlWriter.writeInstancePortLine(f, "PWDATA", "PWDATA")
        rtlWriter.writeInstancePortLine(f, "PRDATA", "PRDATA")
        for n in self.channelDict.keys():
            rtlWriter.writeInstancePortLine(f, n+"_pointer", n+"_pointer")
        for n, t in self.channelDict.items():
            rtlWriter.writeInstancePortLine(f, n+"_size", n+"_size[1:0]")
        for n, t in self.channelDict.items():
            if len(t.dir)>1:
                rtlWriter.writeInstancePortLine(f, n+"_sel", n+"_sel")
        for n in self.channelDict.keys():
            rtlWriter.writeInstancePortLine(f, n+"_channel_cnt_zero", n+"_channel_cnt_zero")
        for n in self.channelDict.keys():
            rtlWriter.writeInstancePortLine(f, n+"_channel_en", n+"_channel_en_all")
        rtlWriter.writeInstancePortLine(f, "transfer_finish", "transfer_finish")
        rtlWriter.writeInstancePortLine(f, "channel_available", "channel_available", False)
        f.write(");\n")
        f.write('\n')
        i=0
        for n, t in self.channelDict.items():
            f.write("// Channel "+str(i)+":".ljust(12) + n.ljust(24) + '\n')
            f.write("dma_channel_fsm u_channel_" + n + "(\n")
            rtlWriter.writeInstancePortLine(f, "clk", "HCLK")
            rtlWriter.writeInstancePortLine(f, "rstn", "HRESETn")
            rtlWriter.writeInstancePortLine(f, "start", "start[" + str(i)+"]")
            rtlWriter.writeInstancePortLine(f, "HREADY", "HREADY")
            rtlWriter.writeInstancePortLine(f, "rd_addr", n+"_rd_addr")
            rtlWriter.writeInstancePortLine(f, "wr_addr", n+"_wr_addr")
            rtlWriter.writeInstancePortLine(f, "hsize", n+"_size")
            rtlWriter.writeInstancePortLine(f, "trans_valid", n+"_trans_valid")
            rtlWriter.writeInstancePortLine(f, "trans_hsize", n+"_trans_hsize")
            rtlWriter.writeInstancePortLine(f, "trans_haddr", n+"_trans_haddr")
            rtlWriter.writeInstancePortLine(f, "trans_hwrite", n+"_trans_hwrite")
            rtlWriter.writeInstancePortLine(f, "channel_not_trans", "channel_not_trans["+str(i)+"]")
            rtlWriter.writeInstancePortLine(f, "allow_accept_req", "allow_accept_req["+str(i)+"]")
            rtlWriter.writeInstancePortLine(f, "transfer_finish", "transfer_finish["+str(i)+"]", False)
            f.write(");\n")
            f.write('\n')
            i=i+1
        f.write('\n')
        f.write("endmodule")
        f.close()

    def _channelDiscriptionComment(self, f):
        f.write("//\n")
        f.write("//" + "-"*70 + '\n')
        f.write("//" + "DMA Channel Discription".center(70) + '\n')
        f.write("//" + "-"*70 + '\n')
        f.write("//|" + "Channel Nr.".center(12)+ "|" + "Channel Name".center(24) + "|" + "Direction".center(12) + "|" + "TX/RX Reg Addr".center(18)+'\n')
        f.write("//|" + '-'*12 + "|" + '-'*24 + "|" + '-'*12 + "|" + '-'*18 + '\n')
        i = 0
        for n, t in self.channelDict.items():
            f.write("//|" + str(i).center(12) + "|" + n.center(24) + "|" + '-'*31 + '\n')
            for i in range(len(t.dir)):
                f.write("//|" + '-'*37 + "|" + ("RX" if t.dir[i]=='r' else "TX").center(12) + "|" + t.paddr[i].center(18) + '\n')
            i = i+1
            f.write("//|" + '-'*37 + "|" + '-'*31 + '\n')
        f.write("//|" + '-'*12 + "|" + '-'*24 + "|" + '-'*12 + "|" + '-'*18 + '\n')

class AhbReadWrite(object):
    def __init__(self):
        self.moduleName = "ahb_lite_master_rw_interface"
        self.portList = [("HCLK", 'i', 'w', 1),
                         ("HRESETn", 'i', 'w', 1),
                         ("HREADY", 'i', 'w', 1),
                         ("HRDATA", 'i', 'w', 32),
                         ("HADDR", 'o', 'w', 32),
                         ("HWRITE", 'o', 'w', 1),
                         ("HSIZE", 'o', 'w', 3),
                         ("HWDATA", 'o', 'w', 32),
                         ("HTRANS", 'o', 'w', 2),
                         ("trans_valid", 'i', 'w', 1),
                         ("trans_hsize", 'i', 'w', 3),
                         ("trans_haddr", 'i', 'w', 32),
                         ("trans_hwrite", 'i', 'w', 1)
                         ]

    def createRtl(self):
        f = open(self.moduleName + ".v", "w+")
        rtlWriter.writeHeaderInfoComment(f, self.moduleName)
        f.write('\n'*2)
        rtlWriter.writeModulePortList(f, self.moduleName, self.portList)
        f.write('\n'*2)
        rtlWriter.writeRegWireLine(f, ("haddr_pipeline_1", 'r', 32))
        rtlWriter.writeRegWireLine(f, ("hwrite_pipeline_1", 'r', 1))
        rtlWriter.writeRegWireLine(f, ("hwrite_pipeline_2", 'r', 1))
        rtlWriter.writeRegWireLine(f, ("hsize_pipeline_1", 'r', 3))
        rtlWriter.writeRegWireLine(f, ("trans_valid_pipeline_1", 'r', 1))
        rtlWriter.writeRegWireLine(f, ("trans_valid_pipeline_2", 'r', 1))
        rtlWriter.writeRegWireLine(f, ("trans_data", 'r', 32))
        f.write('\n'*2)
        rtlWriter.writeAssign(f, "HTRANS", ["{trans_valid_pipeline_1,", "1'b0}"])
        rtlWriter.writeAssign(f, "HADDR", ["haddr_pipeline_1"])
        rtlWriter.writeAssign(f, "HSIZE", ["hsize_pipeline_1"])
        rtlWriter.writeAssign(f, "HWRITE", ["hwrite_pipeline_1"])
        rtlWriter.writeAssign(f, "HWDATA", ["trans_data"])
        f.write('\n')
        pipeList = [rtlWriter.IfStruct("~HRESETn", [rtlWriter.AssignStruct("trans_valid_pipeline_1", ["1'b0"]),
                                                    rtlWriter.AssignStruct("trans_valid_pipeline_2", ["1'b0"]),
                                                    rtlWriter.AssignStruct("haddr_pipeline_1", ["32'h0"]),
                                                    rtlWriter.AssignStruct("hwrite_pipeline_1", ["1'b0"]),
                                                    rtlWriter.AssignStruct("hwrite_pipeline_2", ["1'b0"]),
                                                    rtlWriter.AssignStruct("hsize_pipeline_1", ["3'b000"])
                                                    ]),
                    rtlWriter.ElifStruct("HREADY", [rtlWriter.AssignStruct("trans_valid_pipeline_1", ["trans_valid"]),
                                                    rtlWriter.AssignStruct("trans_valid_pipeline_2", ["trans_valid_pipeline_1"]),
                                                    rtlWriter.AssignStruct("haddr_pipeline_1", ["trans_haddr"]),
                                                    rtlWriter.AssignStruct("hwrite_pipeline_1", ["trans_hwrite"]),
                                                    rtlWriter.AssignStruct("hwrite_pipeline_2", ["hwrite_pipeline_1"]),
                                                    rtlWriter.AssignStruct("hsize_pipeline_1", ["trans_hsize"])
                                                    ])
                    ]
        rtlWriter.writeFlop(f, "HCLK", "HRESETn", pipeList)
        f.write('\n')
        transDataList = [rtlWriter.IfStruct("~HRESETn", [rtlWriter.AssignStruct("trans_data", ["32'h0"])]),
                         rtlWriter.ElifStruct("~hwrite_pipeline_2 & trans_valid_pipeline_2 & HREADY", [rtlWriter.AssignStruct("trans_data", ["HRDATA"])])]
        rtlWriter.writeFlop(f, "HCLK", "HRESETn", transDataList)
        f.write('\n'*2)
        f.write("endmodule")
        f.close()
        
        
            
        
        




