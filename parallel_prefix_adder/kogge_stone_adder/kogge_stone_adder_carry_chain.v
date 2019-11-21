module kogge_stone_adder_carry_chain(
  input   wire    [7:0]   a,
  input   wire    [7:0]   b,
  input   wire            c0,
  output  wire    [7:0]   c_o
);

wire  [7:0]   p;
wire  [7:0]   g;
wire          p10;
wire          g10;
wire          p21;
wire          g21;
wire          p32;
wire          g32;
wire          p43;
wire          g43;
wire          p54;
wire          g54;
wire          p65;
wire          g65;
wire          p76;
wire          g76;
wire          p20;
wire          g20;
wire          p30;
wire          g30;
wire          p41;
wire          g41;
wire          p52;
wire          g52;
wire          p63;
wire          g63;
wire          p74;
wire          g74;
wire          p40;
wire          g40;
wire          p50;
wire          g50;
wire          p60;
wire          g60;
wire          p70;
wire          g70;

assign p = a ^ b;
assign g = a & b;

pg_node u_pg10(
  .pi1  (p[1]),
  .pi2  (p[0]),
  .gi1  (g[1]),
  .gi2  (g[0]),
  .po   (p10),
  .go   (g10)
);

pg_node u_pg21(
  .pi1  (p[2]),
  .pi2  (p[1]),
  .gi1  (g[2]),
  .gi2  (g[1]),
  .po   (p21),
  .go   (g21)
);

pg_node u_pg32(
  .pi1  (p[3]),
  .pi2  (p[2]),
  .gi1  (g[3]),
  .gi2  (g[2]),
  .po   (p32),
  .go   (g32)
);

pg_node u_pg43(
  .pi1  (p[4]),
  .pi2  (p[3]),
  .gi1  (g[4]),
  .gi2  (g[3]),
  .po   (p43),
  .go   (g43)
);

pg_node u_pg54(
  .pi1  (p[5]),
  .pi2  (p[4]),
  .gi1  (g[5]),
  .gi2  (g[4]),
  .po   (p54),
  .go   (g54)
);

pg_node u_pg65(
  .pi1  (p[6]),
  .pi2  (p[5]),
  .gi1  (g[6]),
  .gi2  (g[5]),
  .po   (p65),
  .go   (g65)
);

pg_node u_pg76(
  .pi1  (p[7]),
  .pi2  (p[6]),
  .gi1  (g[7]),
  .gi2  (g[6]),
  .po   (p76),
  .go   (g76)
);

pg_node u_pg20(
  .pi1  (p21),
  .pi2  (p[0]),
  .gi1  (g21),
  .gi2  (g[0]),
  .po   (p20),
  .go   (g20)
);

pg_node u_pg30(
  .pi1  (p32),
  .pi2  (p10),
  .gi1  (g32),
  .gi2  (g10),
  .po   (p30),
  .go   (g30)
);

pg_node u_pg41(
  .pi1  (p43),
  .pi2  (p21),
  .gi1  (g43),
  .gi2  (g21),
  .po   (p41),
  .go   (g41)
);

pg_node u_pg52(
  .pi1  (p54),
  .pi2  (p32),
  .gi1  (g54),
  .gi2  (g32),
  .po   (p52),
  .go   (g52)
);

pg_node u_pg63(
  .pi1  (p65),
  .pi2  (p43),
  .gi1  (g65),
  .gi2  (g43),
  .po   (p63),
  .go   (g63)
);

pg_node u_pg74(
  .pi1  (p76),
  .pi2  (p54),
  .gi1  (g76),
  .gi2  (g54),
  .po   (p74),
  .go   (g74)
);

pg_node u_pg40(
  .pi1  (p41),
  .pi2  (p[0]),
  .gi1  (g41),
  .gi2  (g[0]),
  .po   (p40),
  .go   (g40)
);

pg_node u_pg50(
  .pi1  (p52),
  .pi2  (p10),
  .gi1  (g52),
  .gi2  (g10),
  .po   (p50),
  .go   (g50)
);

pg_node u_pg60(
  .pi1  (p63),
  .pi2  (p20),
  .gi1  (g63),
  .gi2  (g20),
  .po   (p60),
  .go   (g60)
);

pg_node u_pg70(
  .pi1  (p74),
  .pi2  (p30),
  .gi1  (g74),
  .gi2  (g30),
  .po   (p70),
  .go   (g70)
);

assign c_o[0] = g[0] | (p[0] & c0);
assign c_o[1] = g10 | (p10 & c0);
assign c_o[2] = g20 | (p20 & c0);
assign c_o[3] = g30 | (p30 & c0);
assign c_o[4] = g40 | (p40 & c0);
assign c_o[5] = g50 | (p50 & c0);
assign c_o[6] = g60 | (p60 & c0);
assign c_o[7] = g70 | (p70 & c0);

endmodule
