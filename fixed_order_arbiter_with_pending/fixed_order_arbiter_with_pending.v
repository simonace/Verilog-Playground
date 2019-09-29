module fixed_order_arbiter_with_pending(
  input   wire          clk,
  input   wire          rstn,
  input   wire  [3:0]   req,
  output  reg   [3:0]   grant
);

reg   [3:0]   req_pending;
wire          with_pending_0;
wire          with_pending_1;
wire          with_pending_2;
wire          no_pending;
wire          with_req_0;
wire          with_req_1;
wire          with_req_2;
wire  [3:0]   next_pending;
wire  [3:0]   next_grant;
wire  [3:0]   direct_grant;
wire  [3:0]   pending_grant;

assign with_pending_0 = req_pending[0];
assign with_pending_1 = with_pending_0 | req_pending[1];
assign with_pending_2 = with_pending_1 | req_pending[2];
assign no_pending = ~(with_pending_2 | req_pending[3]);
assign with_req_0 = req[0];
assign with_req_1 = with_req_0 | req[1];
assign with_req_2 = with_req_1 | req[2];
assign direct_grant[0] = no_pending & req[0];
assign direct_grant[1] = no_pending & (~with_req_0) & req[1];
assign direct_grant[2] = no_pending & (~with_req_1) & req[2];
assign direct_grant[3] = no_pending & (~with_req_2) & req[3];
assign pending_grant[0] = req_pending[0];
assign pending_grant[1] = req_pending[1] & ~(with_pending_0);
assign pending_grant[2] = req_pending[2] & ~(with_pending_1);
assign pending_grant[3] = req_pending[3] & ~(with_pending_2);
assign next_grant[3:0] = pending_grant[3:0] | direct_grant[3:0];
assign next_pending[3:0] = (~next_grant[3:0]) & (req_pending[3:0] | req[3:0]);

always @(posedge clk or negedge rstn) begin
  if (~rstn) begin
    req_pending[3:0] <= 4'b0;
  end
  else begin
    req_pending[3:0] <= next_pending[3:0];
  end
end

always @(posedge clk or negedge rstn) begin
  if (~rstn) begin
    grant[3:0] <= 4'b0;
  end
  else begin
    grant[3:0] <= next_grant[3:0];
  end
end

endmodule
