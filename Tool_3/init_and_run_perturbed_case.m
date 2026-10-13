clear all
close all
clc

% Simulation parameters
T_sim = 1e-6;
T_sample = 2e-4;
t_enable = 0.06;
t_sim = 20;
t_data_in = 5;

% System parameters
f_pwm = 1e4;
T_pwm = 1/f_pwm;

s_b = 1.5e3;
v_b = 380;
i_b = s_b/(sqrt(3)*v_b);
f_b = 50;
w_b = 2*pi*f_b;
z_b = v_b^2/s_b;
l_b = z_b/w_b;
c_b = 1/(z_b*w_b);
v_dc = 800;

L_f1 = 0.08*l_b;
r_f1 = 0.1*L_f1*w_b;
L_f2 = 0.05*l_b;
r_f2 = 0.1*L_f2*w_b;
C_f = 0.08*c_b;

R_1 = 2*z_b;
R_2 = 0.015*z_b;
R_3 = 0.015*z_b;
L_2 = 0.15*l_b;
L_3 = 0.15*l_b;
C_2 = 0.05*c_b;
C_3 = 10*c_b;

% Excitation
N_s = t_sim/T_sample;

rbs_signals = idinput([N_s,4],'rbs',[],[-0.1,0.1]); %Random binary signals for perturbation

rbs_qg = [(0:T_sample:t_sim-T_sample)', rbs_signals(:,1)];
rbs_dg = [(0:T_sample:t_sim-T_sample)', rbs_signals(:,2)];
rbs_qc = [(0:T_sample:t_sim-T_sample)', rbs_signals(:,3)];
rbs_dc = [(0:T_sample:t_sim-T_sample)', rbs_signals(:,4)];

%noise = 1e-9;

% PLL
e_max = 340;
w_n = w_b;
dmp = 1.0;
tau_pll = 2*dmp/w_n;
K_pll = 2*dmp*w_n/e_max;

% Current Control
tau_i = L_f1/r_f1;
tau_d = 1e-3;
K_i = L_f1/tau_d;

params = [w_b, L_f1, L_f2, tau_pll, K_pll, tau_i, K_i];

disp('Config done -> starting Grid base simulation')

ext = 0;
aux = sim('grid_foll_grid.slx');
V_base_qg = simout.Data(1,:).';
V_base_dg = simout.Data(2,:).';
I_base_qg = simout.Data(3,:).';
I_base_dg = simout.Data(4,:).';

disp('Grid base simulation done -> starting Grid perturbated simulation')

ext = 1;
aux = sim('grid_foll_grid.slx');
V_p_qg = simout.Data(1,:).';
V_p_dg = simout.Data(2,:).';
I_p_qg = simout.Data(3,:).';
I_p_dg = simout.Data(4,:).';

disp('Grid perturbated simulation done -> preparing data for identification')

DV_qg = V_p_qg - V_base_qg;
DV_dg = V_p_dg - V_base_dg;
DI_qg = I_p_qg - I_base_qg;
DI_dg = I_p_dg - I_base_dg;

outputs_g = [DI_qg, DI_dg];
inputs_g  = [DV_qg, DV_dg];

disp('Grid data done -> starting VSC base simulation')

ext = 0;
aux = sim('grid_foll_vsc.slx');
V_base_qc = simout.Data(1,:).';
V_base_dc = simout.Data(2,:).';
I_base_qc = simout.Data(3,:).';
I_base_dc = simout.Data(4,:).';

disp('VSC base simulation done -> starting VSC perturbated simulation')

ext = 1;
aux = sim('grid_foll_vsc.slx');
V_p_qc = simout.Data(1,:).';
V_p_dc = simout.Data(2,:).';
I_p_qc = simout.Data(3,:).';
I_p_dc = simout.Data(4,:).';

disp('VSC perturbated simulation done -> preparing data for identification')

DV_qc = V_p_qc - V_base_qc;
DV_dc = V_p_dc - V_base_dc;
DI_qc = I_p_qc - I_base_qc;
DI_dc = I_p_dc - I_base_dc;

outputs_c = [DI_qc, DI_dc];
inputs_c  = [DV_qc, DV_dc];