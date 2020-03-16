module fixed_order_arbiter_with_pending_4_channels (
    input   wire            clk     ,
    input   wire            rstn    ,
    input   wire    [3:0]   req     ,
    input   wire    [3:0]   enable  ,
    input   wire    [3:0]   accept_req,
    output  wire    [3:0]   grant   
);


reg     [3:0]   req_pending ;
wire            has_pend_0_to_0;
wire            has_pend_0_to_1;
wire            has_pend_0_to_2;
wire            no_pend_0_to_0;
wire            no_pend_0_to_1;
wire            no_pend_0_to_2;
wire            no_pend_all ;
wire            has_req_0_to_0;
wire            has_req_0_to_1;
wire            has_req_0_to_2;
wire            no_req_0_to_0;
wire            no_req_0_to_1;
wire            no_req_0_to_2;
wire    [3:0]   next_pending;
wire    [3:0]   pending_grant;
wire    [3:0]   direct_grant;
wire            allow_grant ;


assign has_pend_0_to_0      = req_pending[0];
assign no_pend_0_to_0       = ~has_pend_0_to_0;
assign has_pend_0_to_1      = has_pend_0_to_0 | req_pending[1];
assign no_pend_0_to_1       = ~has_pend_0_to_1;
assign has_pend_0_to_2      = has_pend_0_to_1 | req_pending[2];
assign no_pend_0_to_2       = ~has_pend_0_to_2;
assign no_pend_all          = no_pend_0_to_2 & ~req_pending[3];
assign has_req_0_to_0       = req[0];
assign no_req_0_to_0        = ~has_req_0_to_0;
assign has_req_0_to_1       = has_req_0_to_0 | req[1];
assign no_req_0_to_1        = ~has_req_0_to_1;
assign has_req_0_to_2       = has_req_0_to_1 | req[2];
assign no_req_0_to_2        = ~has_req_0_to_2;
assign direct_grant[0]      = no_pend_all & req[0];
assign direct_grant[1]      = no_pend_all & no_req_0_to_0 & req[1];
assign direct_grant[2]      = no_pend_all & no_req_0_to_1 & req[2];
assign direct_grant[3]      = no_pend_all & no_req_0_to_2 & req[3];
assign pending_grant[0]     = req_pending[0];
assign pending_grant[1]     = no_pend_all & no_pend_0_to_0 & req_pending[1];
assign pending_grant[2]     = no_pend_all & no_pend_0_to_1 & req_pending[2];
assign pending_grant[3]     = no_pend_all & no_pend_0_to_2 & req_pending[3];
assign allow_grant          = &enable[3:0];
assign grant                = (pending_grant | direct_grant) & {4{allow_grant}};
assign next_pending         = (~grant) & ( req_pending | req) & accept_req;

always @(posedge clk or negedge rstn) begin
    if (~rstn) begin
        req_pending <= 4`b0;
    end
    else begin
        req_pending <= next_pending;
    end
end

endmodule