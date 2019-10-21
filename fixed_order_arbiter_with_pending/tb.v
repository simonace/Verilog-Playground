module tb;

initial begin
  $fsdbDumpfile("fixed_order_arbiter_with_pending.fsdb");
  $fsdbDumpvars(0,tb);
end

reg           clk_tb;
reg           rstn_tb;
reg   [3:0]   req_tb;
reg           enable_tb;
wire  [3:0]   grant_tb;

fixed_order_arbiter_with_pending dut(
  .clk    (clk_tb),
  .rstn   (rstn_tb),
  .req    (req_tb),
  .enable (enable_tb),
  .grant  (grant_tb)
);

initial begin
  clk_tb <= 1'b0;
  rstn_tb <= 1'b1;
  req_tb <= 4'b0000;
  enable_tb <= 1'b1;
  #1000;
  rstn_tb <= 1'b0;
  #1000;
  rstn_tb <= 1'b1;
  #200;
  req_tb <= 4'b1011;
  #200;
  req_tb <= 4'b0101;
  #200;
  req_tb <= 4'b1000;
  #200;
  req_tb <= 4'b0000;
  enable_tb <= 1'b0;
  #800;
  req_tb <= 4'b1000;
  #200;
  req_tb <= 4'b0010;
  #200;
  req_tb <= 4'b1010;
  #200;
  req_tb <= 4'b1000;
  #1000;
  $finish;
end

always #100 clk_tb <= ~clk_tb;

endmodule
