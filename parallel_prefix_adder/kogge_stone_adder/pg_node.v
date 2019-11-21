module pg_node(
  input   wire    pi1,
  input   wire    pi2, //lower
  input   wire    gi1,
  input   wire    gi2, //lower
  output  wire    po,
  output  wire    go
);

assign po = pi1 & pi2;
assign go = gi1 | (pi1 & gi2);

endmodule
