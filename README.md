IEEE 13-Bus Feeder Solar PV Penetration & Volt-VAR Smart Inverter Mitigation
Project Overview & Objectives
High-penetration solar photovoltaics (PV) attached to radial distribution networks can induce local voltage rise and reverse power flow during peak irradiance hours. This project models an IEEE 13-Bus distribution feeder to simulate the dynamic impacts of distributed solar generation and demonstrate dynamic voltage mitigation using smart inverter technology.
Feeder Modeling: Built a standard 115 kV / 4.16 kV radial distribution circuit featuring power transformers, lines, and lumped customer loads.
High Solar Penetration Impact: Integrated a 2.5 MW 3-phase PV system at edge Bus 675. Time-series daily simulations showed afternoon power injection pushing voltage at the point of common coupling (PCC) up to 1.040 p.u..
Volt-VAR Mitigation: Configured an IEEE 1547-compliant Volt-VAR control strategy using OpenDSS smart inverter capabilities (InvControl). By dynamically absorbing reactive power (-kVAR) during midday peak generation, the smart inverter suppressed peak voltages down to 1.0176 p.u., maintaining strict compliance with ANSI C84.1 statutory limits (0.95 - 1.05 p.u.).
System Topology & Setup Instructions
Plaintext
[115 kV Source] ---> (Substation Transformer 115/4.16 kV) ---> [Bus 650] 
                                                                 |
                                                             [Bus 632]
                                                                 |
                                                             [Bus 671]
                                                                 |
                                                       [Bus 675 + 2.5 MW PV]

Technical Requirements & Prerequisites
Ensure you have Python 3.10+ installed along with the required dependencies:
opendssdirect.py (EPRI OpenDSS direct-memory interface)
matplotlib (Plotting and graphical visualization)
Bash
pip install opendssdirect.py matplotlib

Execution
Run the complete multi-phase simulation script from your terminal or VS Code environment:
Bash
python P1_Final.py

Key Results & Visual Assets
Comparative Performance Analysis
Simulation Phase
Peak Bus 675 Voltage
Volt-VAR Control
ANSI C84.1 Compliance Status
Phase 1: Baseline
0.9727 p.u.
Disabled
Compliant
Phase 2: Unmitigated PV
1.0400 p.u.
Disabled
High Voltage Rise
Phase 3: Volt-VAR Mitigated
1.0176 p.u.
Active (IEEE 1547)
Fully Compliant (0.95 - 1.05 p.u.)

24-Hour Voltage Profile (Bus 675)

The plot highlights the full 24-hour time-series trajectory:
Unmitigated Injection (Red Dashed Line): During maximum solar irradiance (Hours 8–12), generation exceeds local demand, driving voltages up toward the statutory limit.
Smart Inverter Mitigation (Green Solid Line): The IEEE 1547 Volt-VAR control curve kicks in as voltage passes 1.00 p.u., absorbing reactive power (-kVAR) to pull the peak back down by over 0.022 p.u..

