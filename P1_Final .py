import opendssdirect as dss
import matplotlib.pyplot as plt

# ---------------------------------------------------------
# STEP 1: INITIALIZE OPENDSS & SET UP SUBSTATION
# ---------------------------------------------------------
dss.Text.Command("Clear")

# Define primary circuit (115 kV Source)
dss.Text.Command("New Circuit.IEEE13Feeder phases=3 BasekV=115 pu=1.00 Bus1=SourceBus")

# Define Substation Transformer (115 kV Delta / 4.16 kV Wye, 5 MVA)
dss.Text.Command(  
    "New Transformer.Substation Phases=3 Windings=2 Xhl=8.0 "
    "wdg=1 bus=SourceBus conn=Delta kva=5000 kv=115 %r=0.5 "
    "wdg=2 bus=650 conn=Wye kva=5000 kv=4.16 %r=0.5"
)

# ---------------------------------------------------------
# STEP 2: DEFINE CONDUCTORS, LINES & BASE LOADS
# ---------------------------------------------------------
# Conductor properties
dss.Text.Command("New Linecode.301ACSR nphases=3 r1=0.20 x1=0.18 units=km")
dss.Text.Command("New Linecode.500AL   nphases=3 r1=0.12 x1=0.10 units=km")

# Feeder Power Lines
dss.Text.Command("New Line.L650-632 Bus1=650.1.2.3 Bus2=632.1.2.3 Length=0.6 Units=km Linecode=500AL")
dss.Text.Command("New Line.L632-671 Bus1=632.1.2.3 Bus2=671.1.2.3 Length=0.8 Units=km Linecode=301ACSR")
dss.Text.Command("New Line.L671-675 Bus1=671.1.2.3 Bus2=675.1.2.3 Length=1.0 Units=km Linecode=301ACSR")

# Baseline Loads
dss.Text.Command("New Load.Load632 Bus1=632.1.2.3 phases=3 kV=4.16 kW=500 kvar=150 Model=1")
dss.Text.Command("New Load.Load671 Bus1=671.1.2.3 phases=3 kV=4.16 kW=400 kvar=100 Model=1")
dss.Text.Command("New Load.Load675 Bus1=675.1.2.3 phases=3 kV=4.16 kW=300 kvar=80  Model=1")

# ---------------------------------------------------------
# STEP 3: SOLVE BASE POWER FLOW & EXTRACT VOLTAGES
# ---------------------------------------------------------
dss.Text.Command("Set VoltageBases=[115, 4.16]")
dss.Text.Command("CalcVoltageBases")
dss.Solution.Solve()

# Extract per-unit bus voltages correctly using puVmagAngle
buses = ["650", "632", "671", "675"]
voltages = []

print("--- Phase 1: Baseline Bus Voltages ---")
for bus in buses:
    dss.Circuit.SetActiveBus(bus)
    # puVmagAngle returns [vmag1, angle1, vmag2, angle2, ...] in p.u.
    v_pu = dss.Bus.puVmagAngle()[0]
    voltages.append(v_pu)
    print(f"Bus {bus}: {v_pu:.4f} p.u.")

# ---------------------------------------------------------
# STEP 4: PLOT BASELINE RESULTS VS ANSI STANDARD LIMITS
# ---------------------------------------------------------
plt.figure(figsize=(8, 4))
plt.plot(buses, voltages, marker='o', color='blue', linewidth=2, label="Base Feeder Profile")

# ANSI C84.1 statutory limits
plt.axhline(y=1.05, color='r', linestyle='--', label='ANSI Max Limit (1.05 p.u.)')
plt.axhline(y=0.95, color='g', linestyle='--', label='ANSI Min Limit (0.95 p.u.)')

plt.title("Phase 1: Baseline Feeder Voltage Profile (No Solar PV)")
plt.xlabel("Feeder Bus")
plt.ylabel("Voltage (p.u.)")
plt.ylim(0.90, 1.10)
plt.grid(True, alpha=0.3)
plt.legend()
plt.tight_layout()
plt.show()

# ---------------------------------------------------------
# Step 5: 3 phase Solar PV Generator at Bus 675
# ---------------------------------------------------------
# #kV:4.16(Nominal line to line standard voltage)
#kW:350(power output)
#pf=1.0(Utility power factor0)
dss.Text.Command("New Generator.PV675  Bus1=675.1.2.3 Phases=3 kV=4.16 kW=350 pf=1.0 Model=1 ")

#Power Flow physics with the solve()
dss.Solution.Solve()

#Extract and Display the per unit voltages in a list 

GeneratorVoltage=[]

for bus in buses:
    dss.Circuit.SetActiveBus(bus)
    g_v= dss.Bus.puVmagAngle()[0]  # Retreives the phase A per unit voltage magintirude of the specific avtive bus with Solar PV enabled 
    GeneratorVoltage.append(g_v)


#Now we compare the baseline voltage in phase 1 to phase Solar PV generator attached 

    v_p1 = voltages[buses.index(bus)]
    diff_percent = (g_v - v_p1)*100

    print(f"Bus {bus}: {g_v:.4f} p.u. (Change: {diff_percent:+.2f}%)")

   # 4. Plot Baseline vs. PV Impact Comparison
plt.figure(figsize=(9, 5))
plt.plot(buses, voltages, marker='o', color='blue', linewidth=2, label="Baseline (No PV)")
plt.plot(buses,GeneratorVoltage , marker='s', color='orange', linewidth=2, linestyle='-', label="With 1.5 MW Solar PV")

# ANSI C84.1 statutory limits
plt.axhline(y=1.05, color='r', linestyle='--', label='ANSI Max Limit (1.05 p.u.)')
plt.axhline(y=0.95, color='g', linestyle='--', label='ANSI Min Limit (0.95 p.u.)')

plt.title("Phase 2: Impact of Solar PV Injection on Feeder Voltages")
plt.xlabel("Feeder Bus")
plt.ylabel("Voltage (p.u.)")
plt.ylim(0.90, 1.10)
plt.grid(True, alpha=0.3) 
plt.legend()
plt.tight_layout()
plt.show()

#--------------------
#Step 6: 24 Hour Time-Series Simulation 
# The goal is to capture dyanamic, time varying behavious of the grid across an entire day to evaluate real world PV impacts 
#--------------------

dss.Text.Command("Generator.PV675.enabled=False") # We disable the generator so that openDSS doesn't run two separate generation object with the same name simultaneously on the same bus 

 # Customer usage patterns peaking at "18-20" hours due to the highest power consumption
dss.Text.Command("New Loadshape.DailyLoad  npts=24  interval=1 "                  
          "mult=[0.3 0.25 0.2 0.2 0.25 0.35 0.5 0.65 0.75 0.8 0.85 0.9 "
          "0.95 0.9 0.85 0.8 0.85 0.95 1.0 0.95 0.85 0.7 0.5 0.4]"
     )

# We call the dailyload in our feeder to make these customer demand change dynamically across all 24 hours of the day 
dss.Text.Command("Edit Load.Load632 Bus1=632.1.2.3 phases=3 kV=4.16 kW=500 kvar=150 Model=1 daily=DailyLoad")
dss.Text.Command("Edit Load.Load671 Bus1=671.1.2.3 phases=3 kV=4.16 kW=400 kvar=100 Model=1 daily=DailyLoad")
dss.Text.Command("Edit Load.Load675 Bus1=675.1.2.3 phases=3 kV=4.16 kW=300 kvar=80  Model=1 daily=DailyLoad")

 # We are measuring irradiance for the 24 hours, irradiance(in this context) means how much light is hitting our solar grid at a given time in a fixed area(surface)
                 #0.85 means that it hit 85% of peak capcacity
dss.Text.Command(
                "New LoadShape.SolarProfile  npts=24  interval=1 "
                 "mult=[0 0 0 0 0 0 0.1 0.3 0.6 0.85 1.0 0.95 0.8 0.5 0.2 0 0 0 0 0 0 0 0 0]" 
    )

#-----------------
#Step 7: Transition from a static generator to Dynamic PV system
#-----------------

# Configure a high-capacity PV system at edge Bus 675 referencing the daily curve
dss.Text.Command(
    "New PVSystem.PVSystem675 Bus1=675.1.2.3 phases=3 kV=4.16 "
    "kVA=2500 Pmpp=2500 pf=1.0 daily=SolarProfile"
)

# Initialize voltage bases before solve 
dss.Text.Command("Set VoltageBases=[115, 4.16]")
dss.Text.Command("CalcVoltageBases")

# Configuring openDSS solver parameters to run in daily mode 
dss.Text.Command("Set Mode=daily StepSize=1h Number=1")

buses = ["650", "632", "671", "675"]
time_series_voltages = {} # Empty dictionary 

for bus in buses:
    time_series_voltages[bus] = []

for hour in range(24):
    dss.Solution.Solve()    

    #Store phase A per unit voltage at each feeder 

    for bus in buses:
        dss.Circuit.SetActiveBus(bus)  # The bus that is being focused in the loop 
        v_pu = dss.Bus.puVmagAngle()[0]  # Phase A per-unit voltage
        time_series_voltages[bus].append(v_pu)


#-----------------
#Step 8: Plot the time series against ANSI limits(0.95-1.05 pu)
#-----------------
hours = list(range(24))
plt.figure(figsize=(10, 5))

for bus in buses:
    plt.plot(hours, time_series_voltages[bus], marker='o', label=f"Bus {bus}")

# ANSI C84.1 Voltage Limits
plt.axhline(y=1.05, color='r', linestyle='--', linewidth=1.5, label='ANSI Max Limit (1.05 p.u.)')
plt.axhline(y=0.95, color='g', linestyle='--', linewidth=1.5, label='ANSI Min Limit (0.95 p.u.)')

plt.title("Phase 2: 24-Hour Time-Series Feeder Voltage Profile with Dynamic PV Injection")
plt.xlabel("Hour of Day")
plt.ylabel("Voltage (p.u.)")
plt.ylim(0.93, 1.10)
plt.xticks(range(0, 24, 2))
plt.grid(True, alpha=0.3)
plt.legend(loc='upper right')
plt.tight_layout()
plt.show()    

#-----------------
# Step 9: Configure a VOLT-VAR Smart Inverter Control 
#-----------------

# Define the piecewise Volt-VAR response (IEEE 1547)
dss.Text.Command(
    "New XYCurve.vv_curve npts=4 "
    "Xarray=[0.5, 1.0, 1.05, 1.5] "
    "Yarray=[1.0, 0.0, -1.0, -1.0]"
)

# Attach InvControl and explicitly bind it to PVSystem675
dss.Text.Command(
    "New InvControl.VoltVarControl Mode=VOLTVAR "
    "voltage_curvex_ref=rated "
    "vvc_curve1=vv_curve "
    "derList=[PVSystem.PVSystem675] "  # Binds control directly to the PV system
    "EventLog=yes"
)

# Expand kVA capacity for reactive power headroom
dss.Text.Command("Edit PVSystem.PVSystem675 kVA=3000")

#-----------------
# Step 10: Execute 24-Hour Time-Series Simulation (Mitigated)
#-----------------

# Reset clock to midnight and expand control iteration headroom
dss.Text.Command("Set Mode=daily StepSize=1h Number=1 Hour=0 Sec=0")
dss.Text.Command("Set MaxControlIter=300")

buses_to_track = ["650", "632", "671", "675"]
v_mitigated = {bus: [] for bus in buses_to_track}

for hour in range(24):
    dss.Solution.Solve()  # Line 239 will now execute cleanly
    
    for bus in buses_to_track:
        dss.Circuit.SetActiveBus(bus)
        v_pu = dss.Bus.puVmagAngle()[0]
        v_mitigated[bus].append(v_pu)

# Display Peak Mitigated Voltage
max_v675_mit = max(v_mitigated["675"])
peak_hour_mit = v_mitigated["675"].index(max_v675_mit)

print(f"--- Phase 3 Volt-VAR Mitigation Results ---")
print(f"Peak Mitigated Voltage at Bus 675: {max_v675_mit:.4f} p.u. at Hour {peak_hour_mit}")
if max_v675_mit <= 1.05:
    print("SUCCESS: Volt-VAR control successfully suppressed over-voltage below ANSI 1.05 p.u. limit!")
# =========================================================
# STEP 11: PLOT COMPARISON (PHASE 2 VS PHASE 3)
# =========================================================

hours = list(range(24))

plt.figure(figsize=(10, 5))
plt.plot(hours, time_series_voltages["675"], label="Bus 675: Unmitigated PV (Phase 2)", color="red", linestyle="--", linewidth=2)
plt.plot(hours, v_mitigated["675"], label="Bus 675: Volt-VAR Mitigated (Phase 3)", color="green", linewidth=2.5)

# ANSI C84.1 Statutory Voltage Limits
plt.axhline(y=1.05, color='black', linestyle='--', label='ANSI Max Limit (1.05 p.u.)')
plt.axhline(y=0.95, color='gray', linestyle='--', label='ANSI Min Limit (0.95 p.u.)')

plt.title("Volt-VAR Mitigation System Performance (Bus 675)")
plt.xlabel("Hour of Day")
plt.ylabel("Voltage (p.u.)")
plt.ylim(0.93, 1.08)
plt.xticks(range(0, 24, 2))
plt.grid(True, alpha=0.3)
plt.legend(loc="upper right")
plt.tight_layout()

plt.savefig("phase3_volt_var_mitigation_24h.png", dpi=300)
plt.show()     