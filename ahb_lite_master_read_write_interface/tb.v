module tb;

initial begin
  $fsdbDumpfile("ahb_lite_master_read_write_interface.fsdb");
  $fsdbDumpvars(0,tb);
end

reg           hclk_tb;
reg           hrstn_tb;
reg           hready_tb;
wire  [31:0]  haddr_tb;
wire          hwrite_tb;
wire  [2:0]   hsize_tb;
wire  [31:0]  hwdata_tb;
wire  [1:0]   htrans_tb;
reg           i_available_tb;
reg   [31:0]  i_haddr_tb;
reg           i_hwrite_tb;
reg   [2:0]   i_hsize_tb;
reg   [31:0]  i_hwdata_tb;
wire          hrdata_ready_tb;

ahb_lite_master_read_write_interface dut(
  // AHB interface
  .HCLK     (hclk_tb),
  .HRESETn  (hrstn_tb),
  .HREADY   (hready_tb),
  .HADDR    (haddr_tb),
  .HWRITE   (hwrite_tb),
  .HSIZE    (hsize_tb),
  .HWDATA   (hwdata_tb),
  .HTRANS   (htrans_tb),
  .instr_available  (i_available_tb),
  .instr_haddr      (i_haddr_tb),
  .instr_hwrite     (i_hwrite_tb),
  .instr_hsize      (i_hsize_tb),
  .instr_hwdata     (i_hwdata_tb),
  .hrdata_ready     (hrdata_ready_tb)
);

initial begin
  hclk_tb <= 1'b0;
  hrstn_tb <= 1'b1;
  i_available_tb <= 1'b0;
  hready_tb <= 1'b1;
  i_haddr_tb <= 32'h0;
  i_hwrite_tb <= 1'b0;
  i_hsize_tb <= 3'b0;
  i_hwdata_tb <= 32'h0;
  #1000;
  hrstn_tb <= 1'b0;
  #1000;
  hrstn_tb <= 1'b1;
  #200;
  hready_tb <= 1'b1;
  i_available_tb <= 1'b1;
  i_haddr_tb <= 32'habcdabcd;
  i_hwrite_tb <= 1'b0;
  i_hsize_tb <= 3'b001;
  i_hwdata_tb <= 32'h1234;
  #200;
  hready_tb <= 1'b1;
  i_available_tb <= 1'b1;
  i_haddr_tb <= 32'h12345678;
  i_hwrite_tb <= 1'b1;
  i_hsize_tb <= 3'b000;
  i_hwdata_tb <= 32'haa;
  #200;
  hready_tb <= 1'b1;
  i_available_tb <= 1'b1;
  i_haddr_tb <= 32'h5a5a5a5a;
  i_hwrite_tb <= 1'b1;
  i_hsize_tb <= 3'b001;
  i_hwdata_tb <= 32'haabb;
  #200;
  hready_tb <= 1'b0;
  i_available_tb <= 1'b1;
  i_haddr_tb <= 32'hfedccdef;
  i_hwrite_tb <= 1'b1;
  i_hsize_tb <= 3'b000;
  i_hwdata_tb <= 32'h55;
  #200;
  hready_tb <= 1'b1;
  i_available_tb <= 1'b1;
  i_haddr_tb <= 32'hfedccdef;
  i_hwrite_tb <= 1'b0;
  i_hsize_tb <= 3'b000;
  i_hwdata_tb <= 32'h55;
  #200;
  hready_tb <= 1'b1;
  i_available_tb <= 1'b0;
  i_haddr_tb <= 32'h0;
  i_hwrite_tb <= 1'b0;
  i_hsize_tb <= 3'b000;
  i_hwdata_tb <= 32'h0;
  #800;
  hready_tb <= 1'b1;
  i_available_tb <= 1'b1;
  i_haddr_tb <= 32'h4;
  i_hwrite_tb <= 1'b1;
  i_hsize_tb <= 3'b010;
  i_hwdata_tb <= 32'hffffffff;
  #200;
  hready_tb <= 1'b1;
  i_available_tb <= 1'b1;
  i_haddr_tb <= 32'h8;
  i_hwrite_tb <= 1'b1;
  i_hsize_tb <= 3'b010;
  i_hwdata_tb <= 32'heeeeeeee;
  #200;
  hready_tb <= 1'b1;
  i_available_tb <= 1'b1;
  i_haddr_tb <= 32'hc;
  i_hwrite_tb <= 1'b1;
  i_hsize_tb <= 3'b010;
  i_hwdata_tb <= 32'hdddddddd;
  #200;
  hready_tb <= 1'b1;
  i_available_tb <= 1'b1;
  i_haddr_tb <= 32'hc;
  i_hwrite_tb <= 1'b0;
  i_hsize_tb <= 3'b010;
  i_hwdata_tb <= 32'h0;
  #200;
  hready_tb <= 1'b1;
  i_available_tb <= 1'b1;
  i_haddr_tb <= 32'h8;
  i_hwrite_tb <= 1'b0;
  i_hsize_tb <= 3'b010;
  i_hwdata_tb <= 32'h0;
  #200;
  hready_tb <= 1'b1;
  i_available_tb <= 1'b1;
  i_haddr_tb <= 32'h4;
  i_hwrite_tb <= 1'b0;
  i_hsize_tb <= 3'b010;
  i_hwdata_tb <= 32'h0;
  #1000;
  $finish;
end

always #100 hclk_tb <= ~hclk_tb;

endmodule
