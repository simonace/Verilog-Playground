module tb;

initial begin
  $fsdbDumpfile("synch_fifo.fsdb");
  $fsdbDumpvars(0,tb);
end

reg     clk_tb;
reg     rstn_tb;
reg     wr_en_tb;
reg     rd_en_tb;
wire  [3:0] wr_ptr_tb;
wire  [3:0] rd_ptr_tb;
wire  [3:0] existed_entries_tb;
wire  [3:0] available_entries_tb;
wire    full_tb;
wire    empty_tb;

synch_fifo dut (
  .clk    (clk_tb),
  .rstn   (rstn_tb),
  .wr_en  (wr_en_tb),
  .rd_en  (rd_en_tb),
  .wr_ptr (wr_ptr_tb),
  .rd_ptr (rd_ptr_tb),
  .existed_entries  (existed_entries_tb),
  .available_entries(available_entries_tb),
  .full   (full_tb),
  .empty  (empty_tb)
);

initial begin
  clk_tb <= 1'b0;
  rstn_tb <= 1'b1;
  wr_en_tb <= 1'b0;
  rd_en_tb <= 1'b0;
  #1000;
  rstn_tb <= 1'b0;
  #1000;
  rstn_tb <= 1'b1;
  #400;
  wr_en_tb <= 1'b1;
  rd_en_tb <= 1'b0;
  #2800; // 14 cycles wr_en
  wr_en_tb <= 1'b1;
  rd_en_tb <= 1'b1;
  #1000; // 5 cycles wr_en rd_en
  wr_en_tb <= 1'b1;
  rd_en_tb <= 1'b0;
  #2000; // 10 cycles wr_en
  wr_en_tb <= 1'b0;
  rd_en_tb <= 1'b1;
  #4000; // 20 cycles rd_en
  wr_en_tb <= 1'b0;
  rd_en_tb <= 1'b0;
  #1000;
  $finish;
end

always #100 clk_tb <= ~clk_tb;

endmodule
