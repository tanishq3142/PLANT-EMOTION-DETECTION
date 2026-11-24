"""
Plant Electrical Signal Recording - Capstone Final PPT Generator
Builds a valid .pptx using Python stdlib only (zipfile + xml).
Fixed: proper presentation.xml tag, correct namespaces, complete required parts.
"""

import zipfile
import os
from pathlib import Path
from xml.sax.saxutils import escape

# ── Paths ─────────────────────────────────────────────────────────────────────
BASE = Path(r"C:\Users\tanis\Desktop\PLANT-EMOTION-DETECTION")
PLOT = BASE / "plot"
OUT  = BASE / "Plant_Electrical_Signal_Capstone_Final.pptx"

# ── Slide dimensions (EMU) 16:9 ───────────────────────────────────────────────
CX = 9144000
CY = 5143500

# ── Colours ───────────────────────────────────────────────────────────────────
DARK_GREEN  = "1A5C38"
MID_GREEN   = "2E8B57"
LIGHT_GREEN = "90EE90"
ACCENT_GOLD = "D4A017"
WHITE       = "FFFFFF"
DARK_GRAY   = "2C2C2C"
LIGHT_GRAY  = "F0F4F0"
ACCENT_BLUE = "1A6B8A"


# ══════════════════════════════════════════════════════════════════════════════
#  LOW-LEVEL HELPERS
# ══════════════════════════════════════════════════════════════════════════════

def emu(inches): return int(inches * 914400)

_id_counter = [200]
def _nid():
    _id_counter[0] += 1
    return _id_counter[0]

def bg_rect(fill, x=0, y=0, cx=CX, cy=CY):
    return f"""<p:sp>
      <p:nvSpPr><p:cNvPr id="{_nid()}" name="bg"/><p:cNvSpPr><a:spLocks noGrp="1"/></p:cNvSpPr><p:nvPr/></p:nvSpPr>
      <p:spPr><a:xfrm><a:off x="{x}" y="{y}"/><a:ext cx="{cx}" cy="{cy}"/></a:xfrm>
        <a:prstGeom prst="rect"><a:avLst/></a:prstGeom>
        <a:solidFill><a:srgbClr val="{fill}"/></a:solidFill><a:ln><a:noFill/></a:ln></p:spPr>
      <p:txBody><a:bodyPr/><a:lstStyle/><a:p/></p:txBody></p:sp>"""

def header_bar(color=DARK_GREEN, h=None):
    return bg_rect(color, 0, 0, CX, h or emu(0.9))

def footer_bar(color=DARK_GREEN, h=None):
    h = h or emu(0.35)
    return bg_rect(color, 0, CY - h, CX, h)

def rnd_box(x, y, cx, cy, fill):
    return f"""<p:sp>
      <p:nvSpPr><p:cNvPr id="{_nid()}" name="box"/><p:cNvSpPr><a:spLocks noGrp="1"/></p:cNvSpPr><p:nvPr/></p:nvSpPr>
      <p:spPr><a:xfrm><a:off x="{x}" y="{y}"/><a:ext cx="{cx}" cy="{cy}"/></a:xfrm>
        <a:prstGeom prst="roundRect"><a:avLst><a:gd name="adj" fmla="val 20000"/></a:avLst></a:prstGeom>
        <a:solidFill><a:srgbClr val="{fill}"/></a:solidFill><a:ln><a:noFill/></a:ln></p:spPr>
      <p:txBody><a:bodyPr/><a:lstStyle/><a:p/></p:txBody></p:sp>"""

def hline(y, color=LIGHT_GREEN, x=None, cx=None):
    x  = x  or emu(0.4)
    cx = cx or (CX - emu(0.8))
    return bg_rect(color, x, y, cx, 25000)

def txt(text, x, y, cx, cy, sz=18, bold=False, color=WHITE, align="l", italic=False):
    b  = "1" if bold   else "0"
    it = "1" if italic else "0"
    al = {"l": "l", "c": "ctr", "r": "r"}.get(align, "l")
    paras = ""
    for line in text.split("\n"):
        paras += f"""<a:p><a:pPr algn="{al}"/><a:r>
          <a:rPr lang="en-IN" sz="{int(sz*100)}" b="{b}" i="{it}" dirty="0">
            <a:solidFill><a:srgbClr val="{color}"/></a:solidFill>
          </a:rPr><a:t>{escape(line)}</a:t></a:r></a:p>"""
    return f"""<p:sp>
      <p:nvSpPr><p:cNvPr id="{_nid()}" name="t"/><p:cNvSpPr txBox="1"/><p:nvPr/></p:nvSpPr>
      <p:spPr><a:xfrm><a:off x="{x}" y="{y}"/><a:ext cx="{cx}" cy="{cy}"/></a:xfrm>
        <a:prstGeom prst="rect"><a:avLst/></a:prstGeom><a:noFill/></p:spPr>
      <p:txBody><a:bodyPr wrap="square"/><a:lstStyle/>{paras}</p:txBody></p:sp>"""

def img(rId, x, y, cx, cy):
    return f"""<p:pic>
      <p:nvPicPr><p:cNvPr id="{_nid()}" name="img"/>
        <p:cNvPicPr><a:picLocks noChangeAspect="1"/></p:cNvPicPr><p:nvPr/></p:nvPicPr>
      <p:blipFill><a:blip r:embed="{rId}"/><a:stretch><a:fillRect/></a:stretch></p:blipFill>
      <p:spPr><a:xfrm><a:off x="{x}" y="{y}"/><a:ext cx="{cx}" cy="{cy}"/></a:xfrm>
        <a:prstGeom prst="rect"><a:avLst/></a:prstGeom></p:spPr></p:pic>"""


# ══════════════════════════════════════════════════════════════════════════════
#  FOOTER HELPER
# ══════════════════════════════════════════════════════════════════════════════

def footer(slide_num, total=24):
    return [
        footer_bar(DARK_GREEN, emu(0.35)),
        txt("Dept. of ECE, NIT Jamshedpur | B.Tech Capstone 2026",
            emu(0.3), CY - emu(0.32), emu(6), emu(0.3), sz=9, color=LIGHT_GREEN),
        txt(f"Slide {slide_num:02d} / {total}",
            CX - emu(1.2), CY - emu(0.32), emu(1.1), emu(0.3),
            sz=9, color=LIGHT_GREEN, align="r"),
    ]


# ══════════════════════════════════════════════════════════════════════════════
#  SLIDE BUILDERS  (each returns list of shape-xml strings, dict rId->fname)
# ══════════════════════════════════════════════════════════════════════════════

def s01_title():
    sp = []
    sp.append(bg_rect(DARK_GREEN))
    sp.append(bg_rect(ACCENT_GOLD, 0, 0, emu(0.08), CY))
    sp.append(bg_rect("D6EED6", CX - emu(3.5), 0, emu(3.5), CY))
    sp.append(rnd_box(CX - emu(3.35), emu(0.25), emu(3.1), emu(5.1), "165C32"))
    sp.append(txt("NIT JAMSHEDPUR", emu(0.2), emu(0.12), emu(5.5), emu(0.45),
                   sz=11, bold=True, color=ACCENT_GOLD))
    sp.append(txt("Department of Electronics & Communication Engineering",
                   emu(0.2), emu(0.52), emu(5.5), emu(0.35), sz=10, color=LIGHT_GREEN))
    sp.append(hline(emu(0.88), ACCENT_GOLD, emu(0.2), emu(5.3)))
    sp.append(txt("Plant Electrical Signal\nRecording &\nMachine Learning Study",
                   emu(0.2), emu(1.0), emu(5.5), emu(2.1),
                   sz=28, bold=True, color=WHITE))
    sp.append(txt("Electrophysiological Response Characterisation &\nState Classification Under Environmental Stimuli",
                   emu(0.2), emu(3.05), emu(5.5), emu(0.75),
                   sz=13, color="90EE90", italic=True))
    sp.append(hline(emu(3.85), ACCENT_GOLD, emu(0.2), emu(5.3)))
    sp.append(txt("Tanishq Gupta  |  Sachin Mishra  |  Asim Kumar Mahata",
                   emu(0.2), emu(4.0), emu(5.5), emu(0.38),
                   sz=12, bold=True, color=WHITE))
    sp.append(txt("Guide: Dr. Subrata Dutta  |  Dr. Mayukh Sarkar  |  Dr. Amit Majumder",
                   emu(0.2), emu(4.42), emu(5.5), emu(0.35), sz=10, color="BBBBBB"))
    sp.append(txt("B.Tech 7th Semester Final Capstone Project  |  2026",
                   emu(0.2), emu(4.78), emu(5.5), emu(0.3), sz=9, color="888888"))
    # Right panel stat boxes
    for i, (val, label) in enumerate([("27","Sessions"),("1.29M","Samples"),
                                       ("7","ML Models"),("95%","Best Acc.")]):
        bx = CX - emu(3.2)
        by = emu(1.6) + i * emu(0.82)
        sp.append(rnd_box(bx, by, emu(1.6), emu(0.68), MID_GREEN))
        sp.append(txt(val,   bx, by + emu(0.04), emu(1.6), emu(0.38),
                       sz=22, bold=True, color=WHITE, align="c"))
        sp.append(txt(label, bx, by + emu(0.44), emu(1.6), emu(0.22),
                       sz=9, color=LIGHT_GREEN, align="c"))
    return sp, {}

def s02_intro():
    sp = []
    sp.append(bg_rect(LIGHT_GRAY))
    sp.append(header_bar(DARK_GREEN, emu(0.9)))
    sp.append(txt("Introduction & Motivation", emu(0.3), emu(0.1), emu(7), emu(0.72),
                   sz=22, bold=True, color=WHITE))
    items = [
        ("What are Bio-Electrical Signals?",
         "Plants generate transmembrane potential differences driven by ion fluxes "
         "(Ca2+, K+, Cl-) through cell membranes -- measurable as slow wave potentials "
         "and action potentials without any nervous system."),
        ("Why Study Plant Electrophysiology?",
         "Plants communicate internal stress electrically -- triggering systemic wound "
         "responses, stomatal closure, and vascular fluid dynamics "
         "(Mousavi et al., Nature 2013)."),
        ("Scientific Boundary (Important!)",
         "We do NOT claim plants have human emotions. We measure and classify reproducible "
         "electrophysiological states under controlled stimuli using rigorous ML methodology."),
        ("The Core Problem We Solved",
         "Commercial DAQ hardware costs >$3,000. This project delivers a low-cost "
         "(< Rs.2,000) Arduino-based open-source acquisition system "
         "that is fully reproducible and publishable."),
    ]
    for i, (title, body) in enumerate(items):
        col = i % 2; row = i // 2
        bx = emu(0.2)  + col * emu(4.5)
        by = emu(1.05) + row * emu(1.9)
        sp.append(rnd_box(bx, by, emu(4.3), emu(1.75), DARK_GREEN))
        sp.append(bg_rect(MID_GREEN, bx, by, emu(4.3), emu(0.42)))
        sp.append(txt(title, bx + emu(0.12), by + emu(0.07), emu(4.0), emu(0.35),
                       sz=11, bold=True, color=ACCENT_GOLD))
        sp.append(txt(body,  bx + emu(0.12), by + emu(0.5),  emu(4.0), emu(1.2),
                       sz=10, color=WHITE))
    sp += footer(2)
    return sp, {}

def s03_literature():
    sp = []
    sp.append(bg_rect(LIGHT_GRAY))
    sp.append(header_bar(DARK_GREEN, emu(0.9)))
    sp.append(txt("Literature Survey", emu(0.3), emu(0.1), emu(7), emu(0.72),
                   sz=22, bold=True, color=WHITE))
    papers = [
        ("Chatterjee et al., 2015  [Royal Society Interface]",
         "Statistical features (mean, std, FFT) on chemically-stressed plant signals. "
         "Achieved 73.67% binary classification via Quadratic Discriminant Analysis."),
        ("Chatterjee, Malik & Gupta, 2018  [Biosensors]",
         "Full waveform geometry modelling using Fourier/Gaussian curve-fitting. "
         "Achieved >90% accuracy using waveform shape coefficients as features."),
        ("Bhadra, Chatterjee & Das, 2023  [PLOS ONE]",
         "Addressed severe class imbalance in plant electrophysiology data "
         "using Random Forest, SVM, and KNN with SMOTE oversampling."),
        ("Mousavi et al., 2013  [Nature]",
         "Demonstrated that plant systemic wounding responses are propagated "
         "electrically via glutamate receptor-like channels at cm/s velocity."),
    ]
    for i, (authors, summary) in enumerate(papers):
        by = emu(1.0) + i * emu(0.95)
        sp.append(rnd_box(emu(0.2), by, CX - emu(0.4), emu(0.85), DARK_GREEN))
        sp.append(bg_rect(ACCENT_GOLD, emu(0.2), by, emu(0.07), emu(0.85)))
        sp.append(txt(authors, emu(0.4), by + emu(0.07), emu(8.3), emu(0.3),
                       sz=11, bold=True, color=ACCENT_GOLD))
        sp.append(txt(summary, emu(0.4), by + emu(0.4),  emu(8.3), emu(0.42),
                       sz=10, color=WHITE))
    # Gap box
    by = emu(4.9)
    sp.append(rnd_box(emu(0.2), by, CX - emu(0.4), emu(0.6), "6B0000"))
    sp.append(txt("Research Gap Identified:",
                   emu(0.4), by + emu(0.07), emu(2.5), emu(0.28),
                   sz=11, bold=True, color=ACCENT_GOLD))
    sp.append(txt("No low-cost open-source multi-stimulus pipeline (acoustic + hydration + circadian) "
                   "exists for plant electrophysiology on microcontrollers.",
                   emu(0.4), by + emu(0.3), CX - emu(0.8), emu(0.28),
                   sz=10, color=WHITE))
    sp += footer(3)
    return sp, {}

def s04_objectives():
    sp = []
    sp.append(bg_rect(DARK_GREEN))
    sp.append(header_bar("145229", emu(0.9)))
    sp.append(txt("Project Objectives", emu(0.3), emu(0.1), emu(7), emu(0.72),
                   sz=22, bold=True, color=WHITE))
    objectives = [
        ("01", "Design a low-cost biopotential acquisition system using AD8232 + Arduino Uno for plant electrophysiology."),
        ("02", "Record structured, labelled time-series datasets across four stimulus conditions: Normal, Watering, Acoustic Music, Dead Tissue."),
        ("03", "Extract 21-dimensional spectral-temporal feature vectors from sliding windows of continuous signals (W = 200 samples)."),
        ("04", "Train and evaluate 7 ML models: Random Forest, SVM, KNN, Gradient Boosting, MLP, Isolation Forest, HistGB."),
        ("05", "Demonstrate unsupervised real-time anomaly detection for precision agriculture applications."),
    ]
    for i, (num, text) in enumerate(objectives):
        by = emu(1.05) + i * emu(0.8)
        sp.append(rnd_box(emu(0.2), by, emu(0.6), emu(0.62), ACCENT_GOLD))
        sp.append(txt(num, emu(0.2), by + emu(0.1), emu(0.6), emu(0.42),
                       sz=16, bold=True, color=DARK_GREEN, align="c"))
        sp.append(rnd_box(emu(0.9), by, CX - emu(1.1), emu(0.62), MID_GREEN))
        sp.append(txt(text, emu(1.05), by + emu(0.1), CX - emu(1.3), emu(0.5),
                       sz=12, color=WHITE))
    sp += footer(4)
    return sp, {}

def s05_hardware():
    sp = []
    sp.append(bg_rect(LIGHT_GRAY))
    sp.append(header_bar(DARK_GREEN, emu(0.9)))
    sp.append(txt("Hardware Setup & Device Justification", emu(0.3), emu(0.1), emu(8), emu(0.72),
                   sz=22, bold=True, color=WHITE))
    devices = [
        ("AD8232 Analog Front-End",
         "Instrumentation amplifier with integrated 2-pole bandpass filter.\n"
         "High-pass: 0.5 Hz (removes DC drift) | Low-pass: 40 Hz (kills 50 Hz noise)\n"
         "Amplifies uV-level plant biopotentials into ADC-readable voltage.\n"
         "Differential input cancels common-mode EM interference."),
        ("Arduino Uno (ATmega328P)",
         "10-bit ADC gives 0-1023 integer counts (delta_V ~4.88 mV @ 5V).\n"
         "Stable 50 Hz serial streaming at 9600 Baud over USB.\n"
         "Total cost < Rs.2,000 vs Rs.2,00,000+ NI DAQ hardware.\n"
         "Direct pyserial -> pandas DataFrame pipeline."),
        ("Ag/AgCl Gel Electrodes (3-lead)",
         "Differential surface arrangement on plant tissue:\n"
         "Working: upper leaf petiole | Reference: mid-stem | Ground: root/soil\n"
         "Ag/AgCl minimises half-cell potential drift.\n"
         "Gel reduces impedance at electrode-plant interface."),
        ("Pothos (Epipremnum aureum)",
         "Selected as botanical model organism:\n"
         "Hardy indoor perennial - survives repeated experiments.\n"
         "Thick vascular petioles give stable electrode contact surface.\n"
         "Fast hydraulic response to watering + acoustic vibration."),
    ]
    for i, (device, detail) in enumerate(devices):
        col = i % 2; row = i // 2
        bx = emu(0.15) + col * emu(4.55)
        by = emu(1.0)  + row * emu(2.0)
        sp.append(rnd_box(bx, by, emu(4.35), emu(1.85), DARK_GREEN))
        sp.append(bg_rect(MID_GREEN, bx, by, emu(4.35), emu(0.42)))
        sp.append(txt(device, bx + emu(0.1), by + emu(0.07), emu(4.1), emu(0.35),
                       sz=12, bold=True, color=ACCENT_GOLD))
        sp.append(txt(detail, bx + emu(0.1), by + emu(0.5),  emu(4.1), emu(1.3),
                       sz=9, color=WHITE))
    sp += footer(5)
    return sp, {}

def s06_pipeline():
    sp = []
    sp.append(bg_rect(DARK_GREEN))
    sp.append(header_bar("145229", emu(0.9)))
    sp.append(txt("End-to-End Data Acquisition Pipeline", emu(0.3), emu(0.1), emu(8), emu(0.72),
                   sz=22, bold=True, color=WHITE))
    steps = [
        ("Plant\nElectrodes", "Ag/AgCl\n3-lead"),
        ("AD8232\nAFE", "0.5-40Hz\nbandpass"),
        ("Arduino\n10-bit ADC", "0-1023\n50Hz"),
        ("Python\nSerial", "pyserial\nvalidation"),
        ("CSV\nLogger", "labelled\nsessions"),
        ("Window\nW=200", "21-D\nfeatures"),
        ("ML\nTraining", "7 models\ncross-val"),
        ("Anomaly\nAlert", "IoT\ndeploy"),
    ]
    bw = int((CX - emu(0.3)) // len(steps)) - emu(0.05)
    for i, (title, detail) in enumerate(steps):
        bx = emu(0.15) + i * (bw + emu(0.05))
        by = emu(1.1)
        fc = ACCENT_GOLD if i in (0, len(steps)-1) else MID_GREEN
        sp.append(rnd_box(bx, by, bw, emu(3.5), fc))
        sp.append(txt(str(i+1), bx, by + emu(0.08), bw, emu(0.3),
                       sz=13, bold=True, color=DARK_GREEN, align="c"))
        sp.append(txt(title, bx, by + emu(0.42), bw, emu(0.65),
                       sz=9, bold=True, color=WHITE, align="c"))
        sp.append(txt(detail, bx, by + emu(1.1), bw, emu(0.6),
                       sz=8, color=LIGHT_GREEN, align="c", italic=True))
    # Stats strip
    for i, s in enumerate(["27 Sessions","1.29M Samples","3,529 Windows","21 Features","7 ML Models"]):
        bx = emu(0.2) + i * emu(1.78)
        sp.append(rnd_box(bx, emu(4.72), emu(1.65), emu(0.42), "0D3D22"))
        sp.append(txt(s, bx, emu(4.75), emu(1.65), emu(0.38),
                       sz=10, bold=True, color=ACCENT_GOLD, align="c"))
    sp += footer(6)
    return sp, {}

def s07_video():
    sp = []
    sp.append(bg_rect(DARK_GRAY))
    sp.append(header_bar(DARK_GREEN, emu(0.9)))
    sp.append(txt("Live Experimental Demonstration", emu(0.3), emu(0.1), emu(7.5), emu(0.72),
                   sz=22, bold=True, color=WHITE))
    sp.append(rnd_box(emu(0.3), emu(1.0), emu(5.5), emu(3.5), "111111"))
    sp.append(txt("INSERT EXPERIMENT VIDEO HERE",
                   emu(0.3), emu(2.35), emu(5.5), emu(0.5),
                   sz=16, bold=True, color=ACCENT_GOLD, align="c"))
    sp.append(txt("Go to Insert > Video > This Device in PowerPoint",
                   emu(0.3), emu(2.9), emu(5.5), emu(0.35),
                   sz=11, color="888888", align="c", italic=True))
    callouts = [
        ("Electrode\nPlacement", "Ag/AgCl on\npetiole & stem"),
        ("Water\nStimulus", "50 mL @ room\ntemperature"),
        ("Acoustic\nStimulus", "80 dB speaker\n@ 30 cm"),
        ("Live Signal\nGraph", "Real-time Python\nmatplotlib stream"),
    ]
    for i, (t, d) in enumerate(callouts):
        bx = emu(5.9); by = emu(1.1) + i * emu(0.88)
        sp.append(rnd_box(bx, by, emu(3.05), emu(0.78), DARK_GREEN))
        sp.append(txt(t, bx + emu(0.1), by + emu(0.05), emu(1.4), emu(0.65),
                       sz=10, bold=True, color=ACCENT_GOLD))
        sp.append(txt(d, bx + emu(1.55), by + emu(0.18), emu(1.4), emu(0.5),
                       sz=9, color=WHITE))
    sp += footer(7)
    return sp, {}

def s08_dataset():
    sp = []
    sp.append(bg_rect(LIGHT_GRAY))
    sp.append(header_bar(DARK_GREEN, emu(0.9)))
    sp.append(txt("Dataset Acquisition Overview", emu(0.3), emu(0.1), emu(7.5), emu(0.72),
                   sz=22, bold=True, color=WHITE))
    for i, (val, label) in enumerate([("27","Recording Sessions"),("1.29M","Raw Samples"),
                                       ("3,529","Feature Windows"),("21","Feature Dims"),("4","Classes")]):
        bx = emu(0.15) + i * emu(1.78)
        sp.append(rnd_box(bx, emu(1.0), emu(1.6), emu(1.1), DARK_GREEN))
        sp.append(txt(val,   bx, emu(1.07), emu(1.6), emu(0.5),
                       sz=22, bold=True, color=ACCENT_GOLD, align="c"))
        sp.append(txt(label, bx, emu(1.57), emu(1.6), emu(0.45),
                       sz=9, color=WHITE, align="c"))
    # Table header
    sp.append(txt("Window Distribution by Stimulus", emu(0.3), emu(2.22), emu(5), emu(0.38),
                   sz=13, bold=True, color=DARK_GREEN))
    rows = [("Acoustic Music",     "2,195","62.2%", DARK_GREEN),
            ("Normal Baseline",    "  963","27.3%", MID_GREEN),
            ("Water Hydration",    "  341"," 9.7%", ACCENT_BLUE),
            ("Dead Tissue Control","   30"," 0.9%", "8B0000"),
            ("TOTAL",              "3,529","100.0%",DARK_GRAY)]
    hcols = [emu(0.3), emu(4.2), emu(5.6)]
    for j, h in enumerate(["Stimulus Condition","Windows","Share"]):
        sp.append(bg_rect(MID_GREEN, hcols[j], emu(2.6), emu(1.1) if j==0 else emu(0.8), emu(0.3)))
        sp.append(txt(h, hcols[j]+emu(0.05), emu(2.63), emu(0.95), emu(0.26),
                       sz=9, bold=True, color=WHITE))
    for k, (cond, cnt, pct, col) in enumerate(rows):
        ry = emu(2.93) + k * emu(0.35)
        sp.append(bg_rect(col, emu(0.3), ry, emu(3.85), emu(0.32)))
        sp.append(txt(cond, emu(0.35), ry+emu(0.04), emu(3.5), emu(0.26), sz=10, color=WHITE))
        sp.append(bg_rect(col, emu(4.2), ry, emu(0.8), emu(0.32)))
        sp.append(txt(cnt,  emu(4.2),  ry+emu(0.04), emu(0.78), emu(0.26), sz=10, color=WHITE, align="c"))
        sp.append(bg_rect(col, emu(5.05), ry, emu(0.75), emu(0.32)))
        sp.append(txt(pct,  emu(5.05), ry+emu(0.04), emu(0.73), emu(0.26), sz=10, color=WHITE, align="c"))
    sp.append(txt("CSV columns: session_id | timestamp | elapsed_seconds | sample_number | stimulus | time_of_day | ecg (0-1023 ADC) | bpm",
                   emu(0.3), emu(4.73), CX-emu(0.6), emu(0.3),
                   sz=9, color=DARK_GREEN, italic=True))
    sp += footer(8)
    return sp, {}

def s09_waveform(rId):
    sp = []
    sp.append(bg_rect(LIGHT_GRAY))
    sp.append(header_bar(DARK_GREEN, emu(0.9)))
    sp.append(txt("Raw Bio-Potential Waveforms Across Conditions", emu(0.3), emu(0.1), emu(7.5), emu(0.72),
                   sz=22, bold=True, color=WHITE))
    if rId:
        sp.append(img(rId, emu(0.2), emu(0.98), emu(5.4), emu(3.4)))
        sp.append(txt("Fig. 1: Raw waveform comparison across four stimulus conditions",
                       emu(0.2), emu(4.42), emu(5.4), emu(0.25),
                       sz=8, color=DARK_GREEN, italic=True))
    sp.append(rnd_box(emu(5.75), emu(1.0), emu(3.1), emu(3.5), DARK_GREEN))
    obs = [("BLUE - Normal Baseline", "~380 ADC counts; stable micro-fluctuations (resting potential)."),
           ("GREEN - Water Event",    "Sharp depolarisation + baseline drift -> rapid osmotic ion flux."),
           ("PURPLE - Acoustic Music","Rhythmic high-freq oscillations from leaf mechanoreceptors."),
           ("RED - Dead Tissue",      "Zero flatline (0 ADC). Proves biological, not 50Hz EM noise.")]
    sp.append(txt("Key Electrophysiological Observations",
                   emu(5.9), emu(1.07), emu(2.85), emu(0.35),
                   sz=11, bold=True, color=ACCENT_GOLD))
    for i, (label, detail) in enumerate(obs):
        sp.append(txt(label,  emu(5.9), emu(1.52)+i*emu(0.8), emu(2.85), emu(0.28),
                       sz=10, bold=True, color=LIGHT_GREEN))
        sp.append(txt(detail, emu(5.9), emu(1.8)+i*emu(0.8),  emu(2.85), emu(0.42),
                       sz=9, color=WHITE))
    sp += footer(9)
    return sp, {}

def s10_psd(rId):
    sp = []
    sp.append(bg_rect(LIGHT_GRAY))
    sp.append(header_bar(DARK_GREEN, emu(0.9)))
    sp.append(txt("Power Spectral Density & Frequency Analysis", emu(0.3), emu(0.1), emu(7.5), emu(0.72),
                   sz=22, bold=True, color=WHITE))
    if rId:
        sp.append(img(rId, emu(0.2), emu(0.98), emu(5.4), emu(3.4)))
        sp.append(txt("Fig. 2: Welch PSD spectrum (0-25 Hz band) across conditions",
                       emu(0.2), emu(4.42), emu(5.4), emu(0.25),
                       sz=8, color=DARK_GREEN, italic=True))
    sp.append(rnd_box(emu(5.75), emu(1.0), emu(3.1), emu(3.5), DARK_GREEN))
    sp.append(txt("Key Spectral Insights", emu(5.9), emu(1.07), emu(2.85), emu(0.35),
                   sz=12, bold=True, color=ACCENT_GOLD))
    insights = ["Dominant energy below 15 Hz for all stimuli",
                "Acoustic stimuli: secondary harmonic peaks at speaker frequency",
                "Dead tissue: flat zero PSD -- no biological frequency component",
                "Normal baseline: broad low-freq 1/f-type noise floor",
                "High-freq power (>0.5 Nyquist) is a key discriminative feature",
                "Welch method used over FFT for better spectral stability"]
    for i, ins in enumerate(insights):
        sp.append(txt(f"  {ins}", emu(5.9), emu(1.55)+i*emu(0.47), emu(2.85), emu(0.44),
                       sz=9, color=WHITE))
    sp += footer(10)
    return sp, {}

def s11_features():
    sp = []
    sp.append(bg_rect(DARK_GREEN))
    sp.append(header_bar("145229", emu(0.9)))
    sp.append(txt("21-Dimensional Feature Extraction Pipeline", emu(0.3), emu(0.1), emu(8), emu(0.72),
                   sz=22, bold=True, color=WHITE))
    groups = [
        ("Central Tendency & Amplitude  (8 features)",
         "Mean (u) | Median | Min | Max\nRange (R) | P25 | P75 | IQR",
         MID_GREEN),
        ("Dispersion & Waveform Shape  (5 features)",
         "Std Deviation (s) | Variance (s^2)\nRMS | Skewness | Kurtosis",
         ACCENT_BLUE),
        ("Signal Kinematics & Events  (3 features)",
         "Mean Absolute Difference (MAD - velocity)\nZero-Crossing Rate (ZCR)\nLocal Peak Count (> u + s)",
         "8B4513"),
        ("Frequency Domain / FFT  (5 features)",
         "Low-Freq Power (0 - 0.25 Nyq)\nMid-Freq Power (0.25 - 0.50 Nyq)\nHigh-Freq Power (0.50 - 1.0 Nyq)\nDominant Freq Index | Spectral Entropy",
         "6B238E"),
    ]
    for i, (title, features, color) in enumerate(groups):
        col = i % 2; row = i // 2
        bx = emu(0.15) + col * emu(4.55)
        by = emu(1.0)  + row * emu(2.0)
        sp.append(rnd_box(bx, by, emu(4.35), emu(1.85), color))
        sp.append(txt(title,    bx+emu(0.1), by+emu(0.08), emu(4.1), emu(0.4),
                       sz=11, bold=True, color=ACCENT_GOLD))
        sp.append(txt(features, bx+emu(0.1), by+emu(0.52), emu(4.1), emu(1.28),
                       sz=10, color=WHITE))
    sp.append(txt("Window size W = 200 samples (~2-4 sec) | Tumbling (non-overlapping) | No session data leakage",
                   emu(0.2), emu(4.95), CX-emu(0.4), emu(0.3),
                   sz=9, color=LIGHT_GREEN, italic=True, align="c"))
    sp += footer(11)
    return sp, {}

def s12_ml_overview():
    sp = []
    sp.append(bg_rect(LIGHT_GRAY))
    sp.append(header_bar(DARK_GREEN, emu(0.9)))
    sp.append(txt("Machine Learning Strategy & Models Used", emu(0.3), emu(0.1), emu(8), emu(0.72),
                   sz=22, bold=True, color=WHITE))
    models = [
        ("Random Forest\n(100 estimators)",     "Viability\nLiving vs Dead",  "100%\nAUC"),
        ("HistGradient\nBoosting",               "Viability\nLiving vs Dead",  "100%\nAUC"),
        ("SVM\n(RBF Kernel)",                   "4-Class\nStimulus",          "94.1%\nAcc"),
        ("KNN\n(k=7, weighted)",                "4-Class\nStimulus",          "94.8%\nAcc"),
        ("Gradient Boosting\n(GBDT)",           "Music Genre\n4-class",       "55%\nF1(Pop 72%)"),
        ("MLP Neural Net\n(2 hidden layers)",   "Circadian\nPhase",           "70.6%\nAcc"),
        ("Isolation Forest",                    "Unsupervised\nAnomaly",      "84.2%\nRecall"),
    ]
    for i, (name, task, result) in enumerate(models):
        col = i % 4; row = i // 4
        bx = emu(0.15) + col * emu(2.25)
        by = emu(1.05) + row * emu(1.9)
        sp.append(rnd_box(bx, by, emu(2.1), emu(1.75), DARK_GREEN))
        sp.append(bg_rect(ACCENT_GOLD if row==0 else MID_GREEN, bx, by, emu(2.1), emu(0.08)))
        sp.append(txt(name,   bx, by+emu(0.14), emu(2.1), emu(0.5),  sz=10, bold=True, color=WHITE, align="c"))
        sp.append(txt(task,   bx, by+emu(0.68), emu(2.1), emu(0.4),  sz=9,  color=LIGHT_GREEN, align="c"))
        sp.append(txt(result, bx, by+emu(1.1),  emu(2.1), emu(0.5),  sz=14, bold=True, color=ACCENT_GOLD, align="c"))
    sp.append(txt("Cross-Validation: Stratified K-Fold (k=5)  |  Session-aware splits prevent temporal data leakage",
                   emu(0.2), emu(4.75), CX-emu(0.4), emu(0.35),
                   sz=10, color=DARK_GREEN, italic=True, align="c"))
    sp += footer(12)
    return sp, {}

def s13_viability(rId):
    sp = []
    sp.append(bg_rect(LIGHT_GRAY))
    sp.append(header_bar(DARK_GREEN, emu(0.9)))
    sp.append(txt("Experiment 1 -- Biological Viability: Living vs. Dead Tissue", emu(0.3), emu(0.1), emu(8.5), emu(0.72),
                   sz=21, bold=True, color=WHITE))
    if rId:
        sp.append(img(rId, emu(0.2), emu(0.98), emu(5.5), emu(3.5)))
        sp.append(txt("Fig. 3: Confusion matrices -- Random Forest & HistGB classifiers",
                       emu(0.2), emu(4.52), emu(5.5), emu(0.25), sz=8, color=DARK_GREEN, italic=True))
    sp.append(rnd_box(emu(5.82), emu(1.0), emu(3.08), emu(3.6), DARK_GREEN))
    sp.append(txt("Results (Both Models)", emu(5.97), emu(1.07), emu(2.85), emu(0.35),
                   sz=13, bold=True, color=ACCENT_GOLD))
    for i, (metric, val) in enumerate([("Accuracy","100%"),("ROC-AUC","1.00"),
                                        ("Precision","1.00"),("Recall","1.00"),("F1-Score","1.00")]):
        sp.append(txt(f"{metric}:", emu(5.97), emu(1.5)+i*emu(0.44), emu(1.4), emu(0.38),
                       sz=10, color=LIGHT_GREEN))
        sp.append(txt(val, emu(7.42), emu(1.5)+i*emu(0.44), emu(1.35), emu(0.38),
                       sz=15, bold=True, color=ACCENT_GOLD, align="r"))
    sp.append(txt("Top Discriminative Features:\n1. MAD (signal velocity)  2. Low-freq spectral power\n3. Spectral entropy  4. Signal mean (baseline)",
                   emu(5.97), emu(3.72), emu(2.85), emu(0.75), sz=10, color=WHITE))
    sp += footer(13)
    return sp, {}

def s14_multiclass(rId):
    sp = []
    sp.append(bg_rect(LIGHT_GRAY))
    sp.append(header_bar(DARK_GREEN, emu(0.9)))
    sp.append(txt("Experiment 2 -- 4-Class Stimulus Classification: SVM vs. KNN", emu(0.3), emu(0.1), emu(8.5), emu(0.72),
                   sz=20, bold=True, color=WHITE))
    if rId:
        sp.append(img(rId, emu(0.2), emu(0.98), emu(5.5), emu(3.0)))
        sp.append(txt("Fig. 4: Confusion matrices -- SVM (RBF) and KNN (k=7)",
                       emu(0.2), emu(4.02), emu(5.5), emu(0.25), sz=8, color=DARK_GREEN, italic=True))
    sp.append(rnd_box(emu(5.82), emu(1.0), emu(3.08), emu(3.65), DARK_GREEN))
    sp.append(txt("Comparison Table", emu(5.97), emu(1.07), emu(2.85), emu(0.35),
                   sz=13, bold=True, color=ACCENT_GOLD))
    rows = [("Condition",       "SVM F1","KNN F1"),
            ("Dead Tissue",     "1.00",  "1.00"),
            ("Acoustic Music",  "0.97",  "0.97"),
            ("Normal Baseline", "0.90",  "0.92"),
            ("Water Event",     "0.86",  "0.86"),
            ("OVERALL",         "94.1%", "94.8%")]
    for i, (c, s, k) in enumerate(rows):
        ry = emu(1.5) + i*emu(0.37)
        bl = i==0 or i==len(rows)-1
        rc = ACCENT_GOLD if i==len(rows)-1 else (MID_GREEN if i%2==0 else DARK_GREEN)
        sp.append(bg_rect(rc, emu(5.95), ry, emu(2.9), emu(0.33)))
        sp.append(txt(c, emu(6.0), ry+emu(0.04), emu(1.3), emu(0.27), sz=9, bold=bl, color=WHITE))
        sp.append(txt(s, emu(7.33), ry+emu(0.04), emu(0.65), emu(0.27), sz=9, bold=bl, color=WHITE, align="c"))
        sp.append(txt(k, emu(8.0), ry+emu(0.04), emu(0.65), emu(0.27), sz=9, bold=bl, color=WHITE, align="c"))
    sp += footer(14)
    return sp, {}

def s15_tsne(rId):
    sp = []
    sp.append(bg_rect(LIGHT_GRAY))
    sp.append(header_bar(DARK_GREEN, emu(0.9)))
    sp.append(txt("t-SNE Manifold Visualisation of Feature Space", emu(0.3), emu(0.1), emu(7.5), emu(0.72),
                   sz=22, bold=True, color=WHITE))
    if rId:
        sp.append(img(rId, emu(0.2), emu(0.98), emu(5.5), emu(3.5)))
        sp.append(txt("Fig. 5: 2D t-SNE projection of 21-D feature space by stimulus class",
                       emu(0.2), emu(4.52), emu(5.5), emu(0.25), sz=8, color=DARK_GREEN, italic=True))
    sp.append(rnd_box(emu(5.82), emu(1.0), emu(3.08), emu(3.5), DARK_GREEN))
    sp.append(txt("Cluster Interpretation", emu(5.97), emu(1.07), emu(2.85), emu(0.35),
                   sz=12, bold=True, color=ACCENT_GOLD))
    for i, ins in enumerate([
        "Dead tissue is completely isolated -- zero variance signature.",
        "Acoustic music forms the tightest cluster -- consistent mechanical vibration.",
        "Water and Normal share partial boundary -- variable recovery.",
        "Non-linear separation confirms SVM/KNN are ideal models.",
        "High cluster separability validates 21-D feature quality."
    ]):
        sp.append(txt(f"  {ins}", emu(5.97), emu(1.52)+i*emu(0.47), emu(2.85), emu(0.44), sz=9, color=WHITE))
    sp += footer(15)
    return sp, {}

def s16_music(rId):
    sp = []
    sp.append(bg_rect(LIGHT_GRAY))
    sp.append(header_bar(DARK_GREEN, emu(0.9)))
    sp.append(txt("Experiment 3 -- Acoustic Genre Discrimination (Gradient Boosting)", emu(0.3), emu(0.1), emu(8.5), emu(0.72),
                   sz=20, bold=True, color=WHITE))
    if rId:
        sp.append(img(rId, emu(0.2), emu(0.98), emu(5.5), emu(3.4)))
        sp.append(txt("Fig. 6: Radar bio-potential profile per music genre",
                       emu(0.2), emu(4.42), emu(5.5), emu(0.25), sz=8, color=DARK_GREEN, italic=True))
    sp.append(rnd_box(emu(5.82), emu(1.0), emu(3.08), emu(3.6), DARK_GREEN))
    sp.append(txt("Genre Results (GBDT Classifier)", emu(5.97), emu(1.07), emu(2.85), emu(0.35),
                   sz=12, bold=True, color=ACCENT_GOLD))
    genres = [("Pop Music",        "72% F1",  "High bass transients -- best detected"),
              ("Normal Silence",   "69% F1",  "Compact baseline - easy to identify"),
              ("Devotional Music", "41% F1",  "Moderate amplitude overlap"),
              ("Classical Music",  "Low F1",  "Subtle freq differences, overlaps"),
              ("OVERALL ACCURACY", "55%",     "vs. 25% random baseline (4-class)")]
    for i, (genre, f1, note) in enumerate(genres):
        sp.append(txt(f"{genre}:", emu(5.97), emu(1.5)+i*emu(0.46), emu(1.65), emu(0.28),
                       sz=9, bold=(i==len(genres)-1), color=LIGHT_GREEN))
        sp.append(txt(f1, emu(7.65), emu(1.5)+i*emu(0.46), emu(1.1), emu(0.28),
                       sz=10, bold=True, color=ACCENT_GOLD, align="r"))
        sp.append(txt(note, emu(5.97), emu(1.76)+i*emu(0.46), emu(2.85), emu(0.2),
                       sz=8, color="888888", italic=True))
    sp += footer(16)
    return sp, {}

def s17_circadian(rId):
    sp = []
    sp.append(bg_rect(LIGHT_GRAY))
    sp.append(header_bar(DARK_GREEN, emu(0.9)))
    sp.append(txt("Experiment 4 -- Circadian Rhythm Classification (MLP Neural Network)", emu(0.3), emu(0.1), emu(8.5), emu(0.72),
                   sz=19, bold=True, color=WHITE))
    if rId:
        sp.append(img(rId, emu(0.2), emu(0.98), emu(5.5), emu(3.0)))
        sp.append(txt("Fig. 7: Diurnal baseline shifts: Morning | Afternoon | Night",
                       emu(0.2), emu(4.02), emu(5.5), emu(0.3), sz=8, color=DARK_GREEN, italic=True))
    sp.append(rnd_box(emu(5.82), emu(1.0), emu(3.08), emu(3.5), DARK_GREEN))
    sp.append(txt("MLP Circadian Results", emu(5.97), emu(1.07), emu(2.85), emu(0.35),
                   sz=12, bold=True, color=ACCENT_GOLD))
    for i, (k, v) in enumerate([("Overall Accuracy","70.6%"),("Afternoon Recall","97.2%"),
                                 ("Morning","~65%"),("Night","~68%"),
                                 ("Architecture","21->64->32->3"),("Activation","ReLU + Softmax")]):
        sp.append(txt(f"{k}:", emu(5.97), emu(1.5)+i*emu(0.38), emu(1.8), emu(0.33),
                       sz=9, color=LIGHT_GREEN))
        sp.append(txt(v, emu(7.78), emu(1.5)+i*emu(0.38), emu(1.0), emu(0.33),
                       sz=10, bold=True, color=WHITE, align="r"))
    sp.append(txt("Validates endogenous circadian baseline drift from stomatal conductance & photosynthesis cycles.",
                   emu(5.97), emu(3.85), emu(2.9), emu(0.5), sz=9, color=LIGHT_GREEN, italic=True))
    sp += footer(17)
    return sp, {}

def s18_anomaly(rId):
    sp = []
    sp.append(bg_rect(LIGHT_GRAY))
    sp.append(header_bar(DARK_GREEN, emu(0.9)))
    sp.append(txt("Experiment 5 -- Unsupervised Anomaly Detection (Isolation Forest)", emu(0.3), emu(0.1), emu(8.5), emu(0.72),
                   sz=20, bold=True, color=WHITE))
    if rId:
        sp.append(img(rId, emu(0.2), emu(0.98), emu(5.5), emu(3.2)))
        sp.append(txt("Fig. 8: Real-time anomaly score timeline -- alert threshold shown in red",
                       emu(0.2), emu(4.22), emu(5.5), emu(0.25), sz=8, color=DARK_GREEN, italic=True))
    sp.append(rnd_box(emu(5.82), emu(1.0), emu(3.08), emu(3.6), DARK_GREEN))
    sp.append(txt("How It Works", emu(5.97), emu(1.07), emu(2.85), emu(0.35),
                   sz=12, bold=True, color=ACCENT_GOLD))
    sp.append(txt(
        "Trained ONLY on undisturbed baseline\n(NO stimulus labels needed)\n\n"
        "Scores each incoming window in real-time.\nWatering events spike the anomaly score\n"
        "above threshold (score < -0.01).\n\n"
        "Results:\n"
        "84.2% of watering windows detected\n"
        "100% of dead tissue events flagged\n"
        "False positive rate < 10% on baseline\n\n"
        "Real-World Use Case:\nSmart drip irrigation trigger + greenhouse\nstress monitoring without any labelling.",
        emu(5.97), emu(1.5), emu(2.85), emu(3.0), sz=9, color=WHITE))
    sp += footer(18)
    return sp, {}

def s19_summary():
    sp = []
    sp.append(bg_rect(LIGHT_GRAY))
    sp.append(header_bar(DARK_GREEN, emu(0.9)))
    sp.append(txt("Master ML Performance Summary", emu(0.3), emu(0.1), emu(8), emu(0.72),
                   sz=22, bold=True, color=WHITE))
    hdrs = ["Algorithm", "Task", "Classes", "Accuracy / AUC", "Key Feature"]
    rows_data = [
        ("Random Forest",        "Viability",        "2",  "100% / AUC 1.00", "Signal Velocity (MAD)"),
        ("HistGradientBoosting", "Viability",        "2",  "100% / AUC 1.00", "Low-freq Spectral Power"),
        ("KNN (k=7)",            "Stimulus Class.",  "4",  "94.8% Accuracy",  "Euclidean Dist (21-D)"),
        ("SVM (RBF Kernel)",     "Stimulus Class.",  "4",  "94.1% Accuracy",  "Non-linear SV boundary"),
        ("Gradient Boosting",    "Music Genre",      "4",  "55% / Pop 72% F1","High-Freq Power + Peaks"),
        ("MLP Neural Net",       "Circadian Phase",  "3",  "70.6% Accuracy",  "Baseline Mean + Variance"),
        ("Isolation Forest",     "Anomaly Detect.",  "--", "84.2% Water Det.", "Isolation Score"),
    ]
    col_x  = [emu(0.15), emu(2.2),  emu(3.65), emu(4.3),  emu(5.9)]
    col_cx = [emu(2.0),  emu(1.4),  emu(0.6),  emu(1.55), emu(3.1)]
    for j, (h, cx) in enumerate(zip(hdrs, col_cx)):
        sp.append(bg_rect(ACCENT_GOLD, col_x[j], emu(1.0), cx, emu(0.35)))
        sp.append(txt(h, col_x[j]+emu(0.05), emu(1.03), cx-emu(0.1), emu(0.3),
                       sz=10, bold=True, color=DARK_GREEN))
    for i, row in enumerate(rows_data):
        ry = emu(1.37) + i*emu(0.47)
        rc = DARK_GREEN if i%2==0 else MID_GREEN
        for j, (cell, cx) in enumerate(zip(row, col_cx)):
            sp.append(bg_rect(rc, col_x[j], ry, cx, emu(0.43)))
            fc = ACCENT_GOLD if j==3 else WHITE
            sp.append(txt(cell, col_x[j]+emu(0.05), ry+emu(0.05), cx-emu(0.1), emu(0.35),
                           sz=9, bold=(j==3), color=fc))
    sp.append(txt("All models: Stratified K-Fold (k=5) cross-validation with session-aware holdout splits.",
                   emu(0.2), emu(4.75), CX-emu(0.4), emu(0.3),
                   sz=9, color=DARK_GREEN, italic=True, align="c"))
    sp += footer(19)
    return sp, {}

def s20_insights():
    sp = []
    sp.append(bg_rect(DARK_GREEN))
    sp.append(header_bar("145229", emu(0.9)))
    sp.append(txt("Key Insights & Scientific Discussion", emu(0.3), emu(0.1), emu(8), emu(0.72),
                   sz=22, bold=True, color=WHITE))
    items = [
        ("Biological Signal Confirmed",
         "Dead tissue flatline at 0 ADC under identical conditions conclusively proves the AD8232 "
         "records physiological bio-potentials, not 50 Hz ambient EM noise."),
        ("Hydration = Electrical Signature",
         "Watering produces a rapid, prolonged baseline depolarization wave consistent with osmotic "
         "ion flux (Ca2+, K+) through xylem vascular bundles -- detectable within seconds."),
        ("Acoustic Vibration is Discriminable",
         "Pop music creates the most distinct high-frequency power and MAD signature. Plant "
         "mechanoreceptors physically respond to acoustic pressure transients."),
        ("Circadian Drift is Real",
         "MLP achieved 70.6% time-of-day classification purely from electrophysiological features -- "
         "confirming genuine diurnal baseline drift from stomatal and photosynthetic cycles."),
        ("Label-Free Detection is Feasible",
         "Isolation Forest achieves 84.2% watering recall without any stimulus labels, proving "
         "deployability in real greenhouses without manual annotation."),
    ]
    for i, (title, body) in enumerate(items):
        by = emu(1.0) + i*emu(0.82)
        sp.append(rnd_box(emu(0.2), by, CX-emu(0.4), emu(0.75), MID_GREEN))
        sp.append(bg_rect(ACCENT_GOLD, emu(0.2), by, emu(0.07), emu(0.75)))
        sp.append(txt(title, emu(0.4), by+emu(0.07), emu(3.5), emu(0.3),
                       sz=11, bold=True, color=ACCENT_GOLD))
        sp.append(txt(body,  emu(0.4), by+emu(0.4),  CX-emu(0.6), emu(0.33),
                       sz=10, color=WHITE))
    sp += footer(20)
    return sp, {}

def s21_limitations():
    sp = []
    sp.append(bg_rect(LIGHT_GRAY))
    sp.append(header_bar(DARK_GREEN, emu(0.9)))
    sp.append(txt("Engineering Limitations & Honest Discussion", emu(0.3), emu(0.1), emu(8), emu(0.72),
                   sz=22, bold=True, color=WHITE))
    items = [
        ("Electrode-Plant Interface",
         "Surface contact impedance varies with leaf moisture and cuticle wax. Motion artifacts from "
         "electrode handling can contaminate recordings."),
        ("Acoustic Mechanical Coupling",
         "Sound waves may induce micro-vibrations in electrode leads as well as leaf mechanoreceptors -- "
         "difficult to fully decouple these two effects."),
        ("Class Imbalance",
         "Dead tissue has only 30 windows (0.9%) vs. 2,195 acoustic windows (62.2%). SMOTE or "
         "weighted sampling would improve minority class precision further."),
        ("Single Plant Species",
         "All 27 sessions used Epipremnum aureum (Pothos). Generalisability to other species "
         "(ferns, succulents, crops) remains unvalidated."),
        ("ADC Resolution",
         "10-bit ADC gives delta_V ~4.88 mV/count -- may miss subtle uV-scale slow wave potentials. "
         "16-bit ADS1115 would provide 16x better resolution."),
    ]
    for i, (title, body) in enumerate(items):
        by = emu(1.0) + i*emu(0.82)
        sp.append(rnd_box(emu(0.2), by, CX-emu(0.4), emu(0.75), DARK_GREEN))
        sp.append(bg_rect("8B0000", emu(0.2), by, CX-emu(0.4), emu(0.07)))
        sp.append(txt(title, emu(0.4), by+emu(0.1),  emu(3.5), emu(0.3),
                       sz=11, bold=True, color=ACCENT_GOLD))
        sp.append(txt(body,  emu(0.4), by+emu(0.42), CX-emu(0.6), emu(0.33),
                       sz=10, color=WHITE))
    sp += footer(21)
    return sp, {}

def s22_future():
    sp = []
    sp.append(bg_rect(DARK_GREEN))
    sp.append(header_bar("145229", emu(0.9)))
    sp.append(txt("Future Work & Research Roadmap", emu(0.3), emu(0.1), emu(8), emu(0.72),
                   sz=22, bold=True, color=WHITE))
    phases = [
        ("NEAR TERM", MID_GREEN,
         ["16-bit ADS1115 ADC upgrade (16x better voltage resolution)",
          "Multi-modal sensors: soil moisture + temperature + light",
          "SMOTE class balancing for minority water/dead class windows"]),
        ("MID TERM", ACCENT_BLUE,
         ["Custom DC-coupled AFE PCB with sub-0.1 Hz high-pass filter",
          "Micro-needle electrode array for direct intra-vascular recording",
          "Multi-plant & multi-species validation dataset"]),
        ("LONG TERM", "8B4513",
         ["TinyML: quantised MLP on ESP32 for standalone greenhouse deploy",
          "IoT MQTT dashboard with real-time drip irrigation alerts",
          "IEEE journal publication with extended open-source pipeline"]),
    ]
    for i, (phase, color, items) in enumerate(phases):
        bx = emu(0.15) + i*emu(2.98)
        sp.append(rnd_box(bx, emu(1.0), emu(2.85), emu(3.65), color))
        sp.append(bg_rect(ACCENT_GOLD, bx, emu(1.0), emu(2.85), emu(0.42)))
        sp.append(txt(phase, bx, emu(1.07), emu(2.85), emu(0.32),
                       sz=13, bold=True, color=DARK_GREEN, align="c"))
        for j, item in enumerate(items):
            sp.append(txt(f"-> {item}", bx+emu(0.1), emu(1.52)+j*emu(0.85),
                           emu(2.65), emu(0.78), sz=10, color=WHITE))
    sp += footer(22)
    return sp, {}

def s23_signal_insights(dead_rId, normal_rId):
    sp = []
    sp.append(bg_rect(LIGHT_GRAY))
    sp.append(header_bar(DARK_GREEN, emu(0.9)))
    sp.append(txt("Three Insights from the Raw Signals", emu(0.3), emu(0.1), emu(8), emu(0.72),
                   sz=22, bold=True, color=WHITE))

    sp.append(txt("DEAD CONTROL  |  FIRST 1,000 SAMPLES",
                   emu(0.2), emu(0.98), emu(4.7), emu(0.2),
                   sz=9, bold=True, color=DARK_GREEN))
    sp.append(txt("NORMAL BASELINE  |  FIRST 1,000 SAMPLES",
                   emu(5.1), emu(0.98), emu(4.7), emu(0.2),
                   sz=9, bold=True, color=DARK_GREEN))
    if dead_rId:
        sp.append(img(dead_rId, emu(0.2), emu(1.2), emu(4.7), emu(1.57)))
    if normal_rId:
        sp.append(img(normal_rId, emu(5.1), emu(1.2), emu(4.7), emu(1.57)))

    insights = [
        ("DEAD VS NORMAL",
         "Dead control: 0 ADC SD in the first 1,000 samples (1 recording).\n"
         "Normal baseline: median SD 178 ADC across 11 recordings."),
        ("CLASS-LEVEL SPREAD",
         "Median SD per recording: music 245 ADC (12 recordings); water 70 ADC (3).\n"
         "Descriptive only - not evidence of cause."),
        ("SESSION VARIABILITY",
         "Normal-recording SD ranged from 0.6 to 247 ADC in the first 1,000 samples, "
         "showing substantial session-to-session variation."),
    ]
    for i, (title, body) in enumerate(insights):
        x = emu(0.2) + i * emu(3.3)
        sp.append(rnd_box(x, emu(2.95), emu(3.0), emu(2.0), DARK_GREEN))
        sp.append(bg_rect(ACCENT_GOLD, x, emu(2.95), emu(0.07), emu(2.0)))
        sp.append(txt(title, x + emu(0.15), emu(3.1), emu(2.72), emu(0.35),
                       sz=11, bold=True, color=ACCENT_GOLD))
        sp.append(txt(body, x + emu(0.15), emu(3.55), emu(2.72), emu(1.2),
                       sz=9, color=WHITE))

    sp.append(txt(
        "SD is population standard deviation per recording, using up to the first 1,000 raw ADC samples.",
        emu(0.3), emu(5.02), CX - emu(0.6), emu(0.2),
        sz=8, color=DARK_GREEN, italic=True, align="c"))
    sp += footer(23)
    return sp, {}


def s24_thankyou():
    sp = []
    sp.append(bg_rect(DARK_GREEN))
    sp.append(bg_rect(ACCENT_GOLD, 0, 0, emu(0.08), CY))
    sp.append(bg_rect("D6EED6", CX-emu(3.5), 0, emu(3.5), CY))
    sp.append(rnd_box(CX-emu(3.35), emu(0.25), emu(3.1), emu(5.1), "165C32"))
    sp.append(txt("Thank You", emu(0.2), emu(1.1), emu(5.5), emu(1.1),
                   sz=42, bold=True, color=WHITE))
    sp.append(hline(emu(2.25), ACCENT_GOLD, emu(0.2), emu(5.3)))
    sp.append(txt("We are open for questions and discussion.",
                   emu(0.2), emu(2.42), emu(5.5), emu(0.45),
                   sz=16, color=LIGHT_GREEN, italic=True))
    sp.append(txt("Tanishq Gupta  |  Sachin Mishra  |  Asim Kumar Mahata",
                   emu(0.2), emu(3.0), emu(5.5), emu(0.38), sz=12, bold=True, color=WHITE))
    sp.append(txt("Guide: Dr. Subrata Dutta | Dr. Mayukh Sarkar | Dr. Amit Majumder",
                   emu(0.2), emu(3.42), emu(5.5), emu(0.35), sz=10, color="BBBBBB"))
    sp.append(txt("Department of ECE, NIT Jamshedpur",
                   emu(0.2), emu(3.85), emu(5.5), emu(0.35), sz=11, bold=True, color=ACCENT_GOLD))
    for i, (val, label) in enumerate([("27","Sessions"),("1.29M","Samples"),
                                       ("7","ML Models"),("95%","Best Acc.")]):
        bx = CX - emu(3.2)
        by = emu(1.6) + i * emu(0.82)
        sp.append(rnd_box(bx, by, emu(1.6), emu(0.68), MID_GREEN))
        sp.append(txt(val,   bx, by+emu(0.04), emu(1.6), emu(0.38), sz=22, bold=True, color=WHITE, align="c"))
        sp.append(txt(label, bx, by+emu(0.44), emu(1.6), emu(0.22), sz=9, color=LIGHT_GREEN, align="c"))
    return sp, {}


# ══════════════════════════════════════════════════════════════════════════════
#  PPTX XML SKELETONS
# ══════════════════════════════════════════════════════════════════════════════

A  = "http://schemas.openxmlformats.org/drawingml/2006/main"
P  = "http://schemas.openxmlformats.org/presentationml/2006/main"
R  = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
PKG= "http://schemas.openxmlformats.org/package/2006/relationships"
CT = "http://schemas.openxmlformats.org/package/2006/content-types"

NS = f'xmlns:a="{A}" xmlns:p="{P}" xmlns:r="{R}"'

def slide_xml(shapes):
    body = "\n".join(shapes)
    return f'''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<p:sld {NS}>
  <p:cSld><p:spTree>
    <p:nvGrpSpPr><p:cNvPr id="1" name=""/><p:cNvGrpSpPr/><p:nvPr/></p:nvGrpSpPr>
    <p:grpSpPr><a:xfrm>
      <a:off x="0" y="0"/><a:ext cx="{CX}" cy="{CY}"/>
      <a:chOff x="0" y="0"/><a:chExt cx="{CX}" cy="{CY}"/>
    </a:xfrm></p:grpSpPr>
    {body}
  </p:spTree></p:cSld>
  <p:clrMapOvr><a:masterClrMapping/></p:clrMapOvr>
</p:sld>'''

def slide_rels_xml(media_items):
    rels = ""
    for rId, fname in media_items:
        rels += f'  <Relationship Id="{rId}" Type="{R}/image" Target="../media/{fname}"/>\n'
    return f'''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="{PKG}">
  <Relationship Id="rId0" Type="{R}/slideLayout" Target="../slideLayouts/slideLayout1.xml"/>
{rels}</Relationships>'''

def presentation_xml(n):
    ids = "".join(f'<p:sldId id="{255+i}" r:id="rId{i}"/>' for i in range(1, n+1))
    return f'''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<p:presentation {NS} saveSubsetFonts="1">
  <p:sldMasterIdLst><p:sldMasterId id="2147483648" r:id="rId0"/></p:sldMasterIdLst>
  <p:sldIdLst>{ids}</p:sldIdLst>
  <p:sldSz cx="{CX}" cy="{CY}" type="custom"/>
  <p:notesSz cx="6858000" cy="9144000"/>
</p:presentation>'''

def prs_rels_xml(n):
    rels = "".join(
        f'<Relationship Id="rId{i}" Type="{R}/slide" Target="slides/slide{i}.xml"/>'
        for i in range(1, n+1))
    return f'''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="{PKG}">
  <Relationship Id="rId0" Type="{R}/slideMaster" Target="slideMasters/slideMaster1.xml"/>
{rels}</Relationships>'''

SLIDE_MASTER = f'''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<p:sldMaster {NS}>
  <p:cSld><p:spTree>
    <p:nvGrpSpPr><p:cNvPr id="1" name=""/><p:cNvGrpSpPr/><p:nvPr/></p:nvGrpSpPr>
    <p:grpSpPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="{CX}" cy="{CY}"/>
      <a:chOff x="0" y="0"/><a:chExt cx="{CX}" cy="{CY}"/></a:xfrm></p:grpSpPr>
  </p:spTree></p:cSld>
  <p:clrMap bg1="lt1" tx1="dk1" bg2="lt2" tx2="dk2" accent1="accent1"
            accent2="accent2" accent3="accent3" accent4="accent4"
            accent5="accent5" accent6="accent6" hlink="hlink" folHlink="folHlink"/>
  <p:sldLayoutIdLst><p:sldLayoutId id="2147483649" r:id="rId0"/></p:sldLayoutIdLst>
  <p:txStyles>
    <p:titleStyle><a:lvl1pPr><a:defRPr lang="en-IN" sz="2800" b="1"/></a:lvl1pPr></p:titleStyle>
    <p:bodyStyle><a:lvl1pPr><a:defRPr lang="en-IN" sz="1800"/></a:lvl1pPr></p:bodyStyle>
    <p:otherStyle><a:defPPr><a:defRPr lang="en-IN"/></a:defPPr></p:otherStyle>
  </p:txStyles>
</p:sldMaster>'''

MASTER_RELS = f'''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="{PKG}">
  <Relationship Id="rId0" Type="{R}/slideLayout" Target="../slideLayouts/slideLayout1.xml"/>
</Relationships>'''

SLIDE_LAYOUT = f'''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<p:sldLayout {NS} type="blank" preserve="1">
  <p:cSld name="Blank"><p:spTree>
    <p:nvGrpSpPr><p:cNvPr id="1" name=""/><p:cNvGrpSpPr/><p:nvPr/></p:nvGrpSpPr>
    <p:grpSpPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="{CX}" cy="{CY}"/>
      <a:chOff x="0" y="0"/><a:chExt cx="{CX}" cy="{CY}"/></a:xfrm></p:grpSpPr>
  </p:spTree></p:cSld>
  <p:clrMapOvr><a:masterClrMapping/></p:clrMapOvr>
</p:sldLayout>'''

LAYOUT_RELS = f'''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="{PKG}">
  <Relationship Id="rId0" Type="{R}/slideMaster" Target="../slideMasters/slideMaster1.xml"/>
</Relationships>'''

ROOT_RELS = f'''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="{PKG}">
  <Relationship Id="rId1"
    Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument"
    Target="ppt/presentation.xml"/>
</Relationships>'''


# ══════════════════════════════════════════════════════════════════════════════
#  ASSEMBLE
# ══════════════════════════════════════════════════════════════════════════════

def content_types_xml(n_slides):
    slide_overrides = "".join(
        f'<Override PartName="/ppt/slides/slide{i}.xml" '
        f'ContentType="application/vnd.openxmlformats-officedocument.presentationml.slide+xml"/>'
        for i in range(1, n_slides+1))
    return f'''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="{CT}">
  <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
  <Default Extension="xml"  ContentType="application/xml"/>
  <Default Extension="png"  ContentType="image/png"/>
  <Default Extension="jpg"  ContentType="image/jpeg"/>
  <Default Extension="jpeg" ContentType="image/jpeg"/>
  <Override PartName="/ppt/presentation.xml"
    ContentType="application/vnd.openxmlformats-officedocument.presentationml.presentation.main+xml"/>
  <Override PartName="/ppt/slideMasters/slideMaster1.xml"
    ContentType="application/vnd.openxmlformats-officedocument.presentationml.slideMaster+xml"/>
  <Override PartName="/ppt/slideLayouts/slideLayout1.xml"
    ContentType="application/vnd.openxmlformats-officedocument.presentationml.slideLayout+xml"/>
  {slide_overrides}
</Types>'''


def build_pptx():
    # Map key -> image path
    img_map = {
        "raw_wave":   PLOT/"01_time_series_eda_and_feature_extraction"/"1_raw_waveform_comparison.png",
        "psd":        PLOT/"01_time_series_eda_and_feature_extraction"/"2_psd_fft_spectrum.png",
        "viability":  PLOT/"02_viability_dead_vs_alive_rf"/"1_confusion_matrices.png",
        "multiclass": PLOT/"03_multiclass_stimulus_svm_knn"/"1_multiclass_confusion_matrices.png",
        "tsne":       PLOT/"03_multiclass_stimulus_svm_knn"/"3_tsne_manifold_clusters.png",
        "radar":      PLOT/"04_music_genre_gradient_boosting"/"4_genre_radar_profiles.png",
        "circadian":  PLOT/"05_circadian_rhythm_mlp_neural_network"/"1_diurnal_baseline_shifts.png",
        "anomaly":    PLOT/"06_unsupervised_anomaly_detection_isolation_forest"/"3_continuous_anomaly_timeline.png",
        "dead_signal": BASE/"categorize csv plots"/"dead"/"plant_dead_control_zero_signal_morning_10hrs00min.png",
        "normal_signal": BASE/"categorize csv plots"/"normal"/"plant_normal_morning_10hrs52min48sec.png",
    }

    def get_rid_and_media(key, media):
        p = img_map.get(key)
        if p and p.exists():
            rId = f"rId{len(media)+1}"
            media[rId] = p
            return rId
        return None

    slides_data = []  # list of (shapes_xml_list, {rId: Path})

    def add_slide(shapes, media):
        slides_data.append((shapes, media))

    # ── Plain slides (no images) ──────────────────────────────────────────────
    sp, _ = s01_title();        add_slide(sp, {})
    sp, _ = s02_intro();        add_slide(sp, {})
    sp, _ = s03_literature();   add_slide(sp, {})
    sp, _ = s04_objectives();   add_slide(sp, {})
    sp, _ = s05_hardware();     add_slide(sp, {})
    sp, _ = s06_pipeline();     add_slide(sp, {})
    sp, _ = s07_video();        add_slide(sp, {})
    sp, _ = s08_dataset();      add_slide(sp, {})

    # ── Image slides ──────────────────────────────────────────────────────────
    def img_slide(builder, key):
        m = {}
        rId = get_rid_and_media(key, m)
        sp, _ = builder(rId)
        add_slide(sp, m)

    img_slide(s09_waveform, "raw_wave")
    img_slide(s10_psd,      "psd")

    sp, _ = s11_features();     add_slide(sp, {})
    sp, _ = s12_ml_overview();  add_slide(sp, {})

    img_slide(s13_viability,   "viability")
    img_slide(s14_multiclass,  "multiclass")
    img_slide(s15_tsne,        "tsne")
    img_slide(s16_music,       "radar")
    img_slide(s17_circadian,   "circadian")
    img_slide(s18_anomaly,     "anomaly")

    sp, _ = s19_summary();      add_slide(sp, {})
    sp, _ = s20_insights();     add_slide(sp, {})
    sp, _ = s21_limitations();  add_slide(sp, {})
    sp, _ = s22_future();       add_slide(sp, {})

    m = {}
    dead_rId = get_rid_and_media("dead_signal", m)
    normal_rId = get_rid_and_media("normal_signal", m)
    sp, _ = s23_signal_insights(dead_rId, normal_rId)
    add_slide(sp, m)

    sp, _ = s24_thankyou();     add_slide(sp, {})

    n = len(slides_data)
    print(f"Building {n} slides ...")

    # Collect all media
    all_media = {}
    for _, m in slides_data:
        for rId, p in m.items():
            all_media[p.name] = p

    with zipfile.ZipFile(str(OUT), "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("_rels/.rels",             ROOT_RELS)
        z.writestr("[Content_Types].xml",     content_types_xml(n))
        z.writestr("ppt/presentation.xml",    presentation_xml(n))
        z.writestr("ppt/_rels/presentation.xml.rels", prs_rels_xml(n))
        z.writestr("ppt/slideMasters/slideMaster1.xml",          SLIDE_MASTER)
        z.writestr("ppt/slideMasters/_rels/slideMaster1.xml.rels", MASTER_RELS)
        z.writestr("ppt/slideLayouts/slideLayout1.xml",            SLIDE_LAYOUT)
        z.writestr("ppt/slideLayouts/_rels/slideLayout1.xml.rels", LAYOUT_RELS)

        for i, (shapes, media) in enumerate(slides_data, start=1):
            z.writestr(f"ppt/slides/slide{i}.xml",
                       slide_xml(shapes))
            z.writestr(f"ppt/slides/_rels/slide{i}.xml.rels",
                       slide_rels_xml(list(media.items())))
            print(f"  Slide {i:02d}")

        for fname, fpath in all_media.items():
            with open(str(fpath), "rb") as f:
                z.writestr(f"ppt/media/{fname}", f.read())
            print(f"  Media: {fname}")

    size = OUT.stat().st_size / 1_048_576
    print(f"\nSaved: {OUT}")
    print(f"Size : {size:.2f} MB")


if __name__ == "__main__":
    build_pptx()
