clear all

T_sim = 1e-6;
T_sample = 2e-4;
t_enable = 0.06;
t_sim = 1;
t_data_in = 5;

s_b = 10e3;
v_b = 400;
v_dc = 700;
f_b = 50;
w_b = 2*pi*f_b;

r_g = 0.3;
l_g = 3.5e-3;
r_1 = 0.2;
l_1 = 4e-3;
r_2 = 0.2;
l_2 = 4e-3;

l_f = 2e-3;
r_f = 0.05;

% Current Control
kp_i = 8;
ki_i = 800;

% PLL
kp_pll_f = 10;%110;
ki_pll_f = 200;%5000;
kp_pll = 10;
ki_pll = 200;

% Current ref
i_qref0 = 2.0;
i_dref1 = 0.0;
i_dref2 = 0.0;

params = [w_b, l_f, kp_i, ki_i, kp_pll_f, ki_pll_f, kp_pll, ki_pll];