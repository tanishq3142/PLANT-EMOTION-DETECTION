# PowerShell Native PowerPoint Presentation Generator
# Uses Microsoft PowerPoint COM Automation to build a 100% genuine, native PPTX

[CmdletBinding()]
param()

$baseDir = "C:\Users\tanis\Desktop\PLANT-EMOTION-DETECTION"
$outputFile = Join-Path $baseDir "Plant_Electrical_Signal_Capstone_Final.pptx"

# Close any running PowerPoint instances or release locks if needed
try {
    $ppt = New-Object -ComObject PowerPoint.Application
} catch {
    Write-Error "Failed to instantiate PowerPoint COM: $_"
    exit 1
}

# PowerPoint Constants
$msoFalse = 0
$msoTrue = -1
$ppLayoutBlank = 12
$msoShapeRectangle = 1
$msoShapeRoundedRectangle = 5
$msoTextOrientationHorizontal = 1
$ppAlignLeft = 1
$ppAlignCenter = 2
$ppAlignRight = 3

# Helper function for RGB OLE color integer
function RGB([int]$r, [int]$g, [int]$b) {
    return [int]($r + ($g * 256) + ($b * 65536))
}

$cDarkGreen  = RGB 20 65 38
$cForestGreen = RGB 26 92 56
$cMidGreen   = RGB 46 125 50
$cLightGreen = RGB 144 238 144
$cMintGreen  = RGB 200 230 201
$cAccentGold = RGB 212 160 23
$cLightGold  = RGB 255 236 179
$cWhite      = RGB 255 255 255
$cDarkGray   = RGB 33 37 41
$cLightBg    = RGB 245 248 245
$cDeepRed    = RGB 183 28 28
$cAccentBlue = RGB 26 115 138

Write-Host "Creating Presentation..."
$pres = $ppt.Presentations.Add($msoFalse)
$pres.PageSetup.SlideWidth = 960
$pres.PageSetup.SlideHeight = 540

function Add-Header($slide, $title, $tag, $slideNum) {
    # Top banner background
    $h = $slide.Shapes.AddShape($msoShapeRectangle, 0, 0, 960, 68)
    $h.Fill.Solid()
    $h.Fill.ForeColor.RGB = $cDarkGreen
    $h.Line.Visible = $msoFalse

    # Accent line
    $line = $slide.Shapes.AddShape($msoShapeRectangle, 0, 66, 960, 3)
    $line.Fill.Solid()
    $line.Fill.ForeColor.RGB = $cAccentGold
    $line.Line.Visible = $msoFalse

    # Title text
    $tb = $slide.Shapes.AddTextbox($msoTextOrientationHorizontal, 30, 8, 700, 32)
    $tb.TextFrame.WordWrap = $msoTrue
    $tb.TextFrame.MarginLeft = 0; $tb.TextFrame.MarginTop = 0
    $tr = $tb.TextFrame.TextRange
    $tr.Text = $title
    $tr.Font.Name = "Segoe UI"
    $tr.Font.Size = 20
    $tr.Font.Bold = $msoTrue
    $tr.Font.Color.RGB = $cWhite

    # Subtitle / Tag
    if ($tag) {
        $tb2 = $slide.Shapes.AddTextbox($msoTextOrientationHorizontal, 30, 42, 700, 20)
        $tb2.TextFrame.WordWrap = $msoTrue
        $tb2.TextFrame.MarginLeft = 0; $tb2.TextFrame.MarginTop = 0
        $tr2 = $tb2.TextFrame.TextRange
        $tr2.Text = $tag
        $tr2.Font.Name = "Segoe UI"
        $tr2.Font.Size = 10
        $tr2.Font.Color.RGB = $cLightGreen
    }

    # Slide Counter
    $tb3 = $slide.Shapes.AddTextbox($msoTextOrientationHorizontal, 750, 18, 180, 30)
    $tb3.TextFrame.WordWrap = $msoTrue
    $tr3 = $tb3.TextFrame.TextRange
    $tr3.Text = "Slide $slideNum / 23"
    $tr3.Font.Name = "Segoe UI"
    $tr3.Font.Size = 11
    $tr3.Font.Bold = $msoTrue
    $tr3.Font.Color.RGB = $cAccentGold
    $tr3.ParagraphFormat.Alignment = $ppAlignRight
}

function Add-Footer($slide) {
    # Footer background
    $f = $slide.Shapes.AddShape($msoShapeRectangle, 0, 508, 960, 32)
    $f.Fill.Solid()
    $f.Fill.ForeColor.RGB = $cDarkGreen
    $f.Line.Visible = $msoFalse

    # Top gold accent line
    $line = $slide.Shapes.AddShape($msoShapeRectangle, 0, 506, 960, 2)
    $line.Fill.Solid()
    $line.Fill.ForeColor.RGB = $cAccentGold
    $line.Line.Visible = $msoFalse

    # Footer Left Text
    $tb = $slide.Shapes.AddTextbox($msoTextOrientationHorizontal, 30, 513, 600, 22)
    $tb.TextFrame.MarginLeft = 0; $tb.TextFrame.MarginTop = 0
    $tr = $tb.TextFrame.TextRange
    $tr.Text = "NIT Jamshedpur  |  Dept. of Electronics & Communication Engineering  |  Capstone 2026"
    $tr.Font.Name = "Segoe UI"
    $tr.Font.Size = 9
    $tr.Font.Color.RGB = $cMintGreen

    # Footer Right Text
    $tb2 = $slide.Shapes.AddTextbox($msoTextOrientationHorizontal, 650, 513, 280, 22)
    $tb2.TextFrame.MarginLeft = 0; $tb2.TextFrame.MarginTop = 0
    $tr2 = $tb2.TextFrame.TextRange
    $tr2.Text = "Plant Bio-Potential & ML Study"
    $tr2.Font.Name = "Segoe UI"
    $tr2.Font.Size = 9
    $tr2.Font.Color.RGB = $cAccentGold
    $tr2.ParagraphFormat.Alignment = $ppAlignRight
}

function Add-Card($slide, [float]$x, [float]$y, [float]$w, [float]$h, [int]$bgColor, [string]$title, [string]$body, [int]$titleColor = $cAccentGold, [int]$bodyColor = $cWhite) {
    $card = $slide.Shapes.AddShape($msoShapeRoundedRectangle, $x, $y, $w, $h)
    $card.Fill.Solid()
    $card.Fill.ForeColor.RGB = $bgColor
    $card.Line.Visible = $msoFalse

    # Title
    if ($title) {
        $tb = $slide.Shapes.AddTextbox($msoTextOrientationHorizontal, $x + 12, $y + 10, $w - 24, 26)
        $tb.TextFrame.WordWrap = $msoTrue
        $tb.TextFrame.MarginLeft = 0; $tb.TextFrame.MarginTop = 0
        $tr = $tb.TextFrame.TextRange
        $tr.Text = $title
        $tr.Font.Name = "Segoe UI"
        $tr.Font.Size = 12
        $tr.Font.Bold = $msoTrue
        $tr.Font.Color.RGB = $titleColor
    }

    # Body
    if ($body) {
        $topOffset = if ($title) { $y + 36 } else { $y + 10 }
        $bodyH = if ($title) { $h - 44 } else { $h - 20 }
        $tb2 = $slide.Shapes.AddTextbox($msoTextOrientationHorizontal, $x + 12, $topOffset, $w - 24, $bodyH)
        $tb2.TextFrame.WordWrap = $msoTrue
        $tb2.TextFrame.MarginLeft = 0; $tb2.TextFrame.MarginTop = 0
        $tr2 = $tb2.TextFrame.TextRange
        $tr2.Text = $body
        $tr2.Font.Name = "Segoe UI"
        $tr2.Font.Size = 10
        $tr2.Font.Color.RGB = $bodyColor
    }
    return $card
}

# ==============================================================================
# SLIDE 1: TITLE SLIDE
# ==============================================================================
Write-Host "Generating Slide 1: Title Slide"
$s1 = $pres.Slides.Add(1, $ppLayoutBlank)
$bg1 = $s1.Shapes.AddShape($msoShapeRectangle, 0, 0, 960, 540)
$bg1.Fill.Solid(); $bg1.Fill.ForeColor.RGB = $cDarkGreen; $bg1.Line.Visible = $msoFalse

# Left decorative gold border
$edge = $s1.Shapes.AddShape($msoShapeRectangle, 0, 0, 10, 540)
$edge.Fill.Solid(); $edge.Fill.ForeColor.RGB = $cAccentGold; $edge.Line.Visible = $msoFalse

# Right decorative panel
$panel = $s1.Shapes.AddShape($msoShapeRoundedRectangle, 640, 30, 290, 480)
$panel.Fill.Solid(); $panel.Fill.ForeColor.RGB = $cForestGreen; $panel.Line.Visible = $msoFalse

# Institution Header
$tbInst = $s1.Shapes.AddTextbox($msoTextOrientationHorizontal, 45, 30, 560, 40)
$tbInst.TextFrame.WordWrap = $msoTrue
$trInst = $tbInst.TextFrame.TextRange
$trInst.Text = "NATIONAL INSTITUTE OF TECHNOLOGY JAMSHEDPUR`nDepartment of Electronics & Communication Engineering"
$trInst.Font.Name = "Segoe UI"; $trInst.Font.Size = 11; $trInst.Font.Bold = $msoTrue; $trInst.Font.Color.RGB = $cAccentGold

# Gold Divider
$d1 = $s1.Shapes.AddShape($msoShapeRectangle, 45, 80, 560, 2)
$d1.Fill.Solid(); $d1.Fill.ForeColor.RGB = $cAccentGold; $d1.Line.Visible = $msoFalse

# Project Main Title
$tbTitle = $s1.Shapes.AddTextbox($msoTextOrientationHorizontal, 45, 95, 570, 140)
$tbTitle.TextFrame.WordWrap = $msoTrue
$trTitle = $tbTitle.TextFrame.TextRange
$trTitle.Text = "Plant Electrical Signal`nRecording & Machine`nLearning Study"
$trTitle.Font.Name = "Segoe UI"; $trTitle.Font.Size = 34; $trTitle.Font.Bold = $msoTrue; $trTitle.Font.Color.RGB = $cWhite

# Subtitle
$tbSub = $s1.Shapes.AddTextbox($msoTextOrientationHorizontal, 45, 245, 570, 50)
$tbSub.TextFrame.WordWrap = $msoTrue
$trSub = $tbSub.TextFrame.TextRange
$trSub.Text = "Electrophysiological Response Characterisation & State Classification Under Environmental Stimuli"
$trSub.Font.Name = "Segoe UI"; $trSub.Font.Size = 13; $trSub.Font.Italic = $msoTrue; $trSub.Font.Color.RGB = $cLightGreen

# Divider 2
$d2 = $s1.Shapes.AddShape($msoShapeRectangle, 45, 305, 560, 1)
$d2.Fill.Solid(); $d2.Fill.ForeColor.RGB = $cMintGreen; $d2.Line.Visible = $msoFalse

# Team Members
$tbTeam = $s1.Shapes.AddTextbox($msoTextOrientationHorizontal, 45, 320, 570, 55)
$tbTeam.TextFrame.WordWrap = $msoTrue
$trTeam = $tbTeam.TextFrame.TextRange
$trTeam.Text = "Presented by:`nTanishq Gupta  |  Sachin Mishra  |  Asim Kumar Mahata"
$trTeam.Font.Name = "Segoe UI"; $trTeam.Font.Size = 13; $trTeam.Font.Bold = $msoTrue; $trTeam.Font.Color.RGB = $cWhite

# Guides
$tbGuide = $s1.Shapes.AddTextbox($msoTextOrientationHorizontal, 45, 385, 570, 50)
$tbGuide.TextFrame.WordWrap = $msoTrue
$trGuide = $tbGuide.TextFrame.TextRange
$trGuide.Text = "Under the Guidance of:`nDr. Subrata Dutta  |  Dr. Mayukh Sarkar  |  Dr. Amit Majumder"
$trGuide.Font.Name = "Segoe UI"; $trGuide.Font.Size = 11; $trGuide.Font.Color.RGB = $cLightGold

# Capstone Tag
$tbTag = $s1.Shapes.AddTextbox($msoTextOrientationHorizontal, 45, 450, 570, 30)
$trTag = $tbTag.TextFrame.TextRange
$trTag.Text = "B.Tech Final Semester Capstone Project  |  Academic Year 2026"
$trTag.Font.Name = "Segoe UI"; $trTag.Font.Size = 10; $trTag.Font.Color.RGB = $cMintGreen

# Stat badges in right panel
$metrics = @(
    @{ Val="27"; Lbl="Recording Sessions" },
    @{ Val="1.29M"; Lbl="Bio-Potential Samples" },
    @{ Val="3,529"; Lbl="Time-Series Windows" },
    @{ Val="95%"; Lbl="Multi-Class Accuracy" }
)
for ($i = 0; $i -lt $metrics.Count; $i++) {
    $my = 55 + ($i * 110)
    $card = $s1.Shapes.AddShape($msoShapeRoundedRectangle, 665, $my, 240, 92)
    $card.Fill.Solid(); $card.Fill.ForeColor.RGB = $cDarkGreen; $card.Line.Visible = $msoFalse
    
    $tbM = $s1.Shapes.AddTextbox($msoTextOrientationHorizontal, 665, $my + 10, 240, 45)
    $trM = $tbM.TextFrame.TextRange
    $trM.Text = $metrics[$i].Val
    $trM.Font.Name = "Segoe UI"; $trM.Font.Size = 28; $trM.Font.Bold = $msoTrue; $trM.Font.Color.RGB = $cAccentGold
    $trM.ParagraphFormat.Alignment = $ppAlignCenter

    $tbL = $s1.Shapes.AddTextbox($msoTextOrientationHorizontal, 665, $my + 55, 240, 25)
    $trL = $tbL.TextFrame.TextRange
    $trL.Text = $metrics[$i].Lbl
    $trL.Font.Name = "Segoe UI"; $trL.Font.Size = 10; $trL.Font.Color.RGB = $cWhite
    $trL.ParagraphFormat.Alignment = $ppAlignCenter
}

# ==============================================================================
# SLIDE 2: INTRODUCTION & ELECTROPOLYSIOLOGY
# ==============================================================================
Write-Host "Generating Slide 2: Introduction"
$s2 = $pres.Slides.Add(2, $ppLayoutBlank)
$bg2 = $s2.Shapes.AddShape($msoShapeRectangle, 0, 0, 960, 540)
$bg2.Fill.Solid(); $bg2.Fill.ForeColor.RGB = $cLightBg; $bg2.Line.Visible = $msoFalse
Add-Header $s2 "Introduction & Biological Motivation" "Understanding Plant Bio-potentials vs Anthropomorphic 'Emotions'" 2
Add-Footer $s2

Add-Card $s2 30 85 435 190 $cForestGreen "What are Plant Bio-potentials?" `
"Plant cell membranes maintain electrical potential differences via active proton pumps (H+-ATPase) and ion channels.`n`nEnvironmental stimuli trigger rapid or slow fluxes of Calcium (Ca2+), Potassium (K+), and Chloride (Cl-), causing measurable transmembrane Action Potentials (APs) and Variation Potentials (VPs)."

Add-Card $s2 495 85 435 190 $cForestGreen "Why Study Plant Electrophysiology?" `
"Systemic Stress Communication: Inter-leaf electrical signaling allows whole-plant defense activation against wounds, drought, and pathogens (Mousavi et al., Nature 2013).`n`nNon-Destructive Sensing: Real-time electrical monitoring provides early alerts hours before physical leaf wilting or necrosis occurs."

Add-Card $s2 30 295 435 195 $cForestGreen "Crucial Scientific Boundary (No Pseudo-Science)" `
"Rule #1: Plants do NOT possess a central nervous system or human emotions.`n`nWhat we record and evaluate are physiological cellular biopotentials and vascular ion currents driven by external environmental triggers.`n`nObjective: Apply rigorous machine learning to classify biological states without subjective bias."

Add-Card $s2 495 295 435 195 $cDarkGreen "The Engineering Challenge & Solution" `
"The Problem: Commercial multi-channel physiological data acquisition systems (e.g., ADInstruments PowerLab) cost upwards of $3,000, limiting broad agricultural deployment.`n`nOur Contribution: Designed a sub-$25 open-source instrumentation pipeline using the AD8232 analog front-end and Arduino Uno, capable of 50 Hz continuous bio-potential stream acquisition."

# ==============================================================================
# SLIDE 3: LITERATURE REVIEW
# ==============================================================================
Write-Host "Generating Slide 3: Literature Survey"
$s3 = $pres.Slides.Add(3, $ppLayoutBlank)
$bg3 = $s3.Shapes.AddShape($msoShapeRectangle, 0, 0, 960, 540)
$bg3.Fill.Solid(); $bg3.Fill.ForeColor.RGB = $cLightBg; $bg3.Line.Visible = $msoFalse
Add-Header $s3 "Literature Review & Research Gap" "Foundations in Plant Electrophysiology & Signal Classification" 3
Add-Footer $s3

$litPapers = @(
    @{ Auth="Mousavi et al. (Nature, 2013)"; Title="Leaf-to-leaf wound signalling via GLUTAMATE RECEPTOR-LIKE genes"; Sum="Proved that plants transmit systemic electrical signals across long distances via vascular bundles when stimulated, confirming biological relevance of electrical recording." },
    @{ Auth="Chatterjee et al. (Royal Society Interface, 2015)"; Title="Exploring classification of external stimuli using statistical features"; Sum="Demonstrated that 11 statistical features (variance, IQR) classify chemical stimuli (NaCl, H2SO4, O3) with 73.67% accuracy using discriminant analysis." },
    @{ Auth="Chatterjee, Malik & Gupta (Biosensors, 2018)"; Title="Plant electrical signal response classification using curve fitting"; Sum="Modeled full signal waveforms using Fourier and Gaussian curve-fitting coefficients, achieving >90% binary classification on chemical stress." },
    @{ Auth="Bhadra, Chatterjee & Das (PLOS ONE, 2023)"; Title="Multiclass classification of chemical stimuli from unbalanced plant data"; Sum="Established benchmarks using Random Forest, SVM, and KNN on imbalanced plant datasets, emphasizing balanced F1-scores and MCC." }
)
for ($i = 0; $i -lt $litPapers.Count; $i++) {
    $ly = 85 + ($i * 78)
    $card = $s3.Shapes.AddShape($msoShapeRoundedRectangle, 30, $ly, 900, 70)
    $card.Fill.Solid(); $card.Fill.ForeColor.RGB = $cForestGreen; $card.Line.Visible = $msoFalse

    $bar = $s3.Shapes.AddShape($msoShapeRectangle, 30, $ly, 6, 70)
    $bar.Fill.Solid(); $bar.Fill.ForeColor.RGB = $cAccentGold; $bar.Line.Visible = $msoFalse

    $tbA = $s3.Shapes.AddTextbox($msoTextOrientationHorizontal, 45, $ly + 5, 870, 22)
    $tbA.TextFrame.WordWrap = $msoTrue; $tbA.TextFrame.MarginLeft = 0; $tbA.TextFrame.MarginTop = 0
    $trA = $tbA.TextFrame.TextRange
    $trA.Text = "$($litPapers[$i].Auth)  --  $($litPapers[$i].Title)"
    $trA.Font.Name = "Segoe UI"; $trA.Font.Size = 11; $trA.Font.Bold = $msoTrue; $trA.Font.Color.RGB = $cAccentGold

    $tbS = $s3.Shapes.AddTextbox($msoTextOrientationHorizontal, 45, $ly + 28, 870, 36)
    $tbS.TextFrame.WordWrap = $msoTrue; $tbS.TextFrame.MarginLeft = 0; $tbS.TextFrame.MarginTop = 0
    $trS = $tbS.TextFrame.TextRange
    $trS.Text = $litPapers[$i].Sum
    $trS.Font.Name = "Segoe UI"; $trS.Font.Size = 9.5; $trS.Font.Color.RGB = $cWhite
}

# Research Gap Box
$gap = $s3.Shapes.AddShape($msoShapeRoundedRectangle, 30, 410, 900, 80)
$gap.Fill.Solid(); $gap.Fill.ForeColor.RGB = $cDeepRed; $gap.Line.Visible = $msoFalse
$tbG = $s3.Shapes.AddTextbox($msoTextOrientationHorizontal, 45, 416, 870, 24)
$tbG.TextFrame.MarginLeft = 0; $tbG.TextFrame.MarginTop = 0
$trG = $tbG.TextFrame.TextRange
$trG.Text = "IDENTIFIED RESEARCH GAP ADDRESSED BY OUR CAPSTONE"
$trG.Font.Name = "Segoe UI"; $trG.Font.Size = 11; $trG.Font.Bold = $msoTrue; $trG.Font.Color.RGB = $cAccentGold

$tbGT = $s3.Shapes.AddTextbox($msoTextOrientationHorizontal, 45, 442, 870, 42)
$tbGT.TextFrame.WordWrap = $msoTrue; $tbGT.TextFrame.MarginLeft = 0; $tbGT.TextFrame.MarginTop = 0
$trGT = $tbGT.TextFrame.TextRange
$trGT.Text = "Prior works focus almost exclusively on lethal chemical poisoning using expensive laboratory setups. A significant research gap exists for low-cost, open-source streaming systems evaluating natural non-destructive stimuli (water influx, acoustic vibrations, circadian rhythm) alongside biological viability controls."
$trGT.Font.Name = "Segoe UI"; $trGT.Font.Size = 9.5; $trGT.Font.Color.RGB = $cWhite

# ==============================================================================
# SLIDE 4: SYSTEM SETUP & HARDWARE JUSTIFICATION
# ==============================================================================
Write-Host "Generating Slide 4: Hardware Setup & Justification"
$s4 = $pres.Slides.Add(4, $ppLayoutBlank)
$bg4 = $s4.Shapes.AddShape($msoShapeRectangle, 0, 0, 960, 540)
$bg4.Fill.Solid(); $bg4.Fill.ForeColor.RGB = $cLightBg; $bg4.Line.Visible = $msoFalse
Add-Header $s4 "Experimental Setup & Device Selection" "Why each hardware component was chosen for plant electrophysiology" 4
Add-Footer $s4

$devices = @(
    @{ Name="AD8232 Analog Front-End"; Role="Signal Conditioning & Amplification"; Why="• Instrumentation amplifier with integrated 2-pole bandpass filter`n• High-Pass: 0.5 Hz (blocks steady DC electrode half-cell potential drift)`n• Low-Pass: 40 Hz (eliminates 50 Hz AC power line interference)`n• High Common-Mode Rejection Ratio (CMRR) for noisy lab environments`n• Amplifies microvolt-level potentials into Arduino's 0-3.3V range" },
    @{ Name="Arduino Uno (ATmega328P)"; Role="10-Bit ADC & Serial Communication"; Why="• Converts conditioned analog signals into 0-1023 integer counts`n• Resolution: Delta V ≈ 4.88 mV per step at 5V reference`n• Stable 50 Hz continuous hardware timer interrupt sampling`n• Reliable 9600-Baud USB serial streaming directly to computer`n• Eliminates need for expensive specialized DAQ interfaces" },
    @{ Name="Ag/AgCl Differential Leads"; Role="Ionic-to-Electronic Transduction"; Why="• 3-Lead differential montage: Active (leaf), Reference (petiole), Driven Ground (stem base)`n• Ag/AgCl non-polarizing chemistry reduces electrode polarization impedance`n• Conductive electrolyte gel ensures stable surface contact on waxy cuticle`n• Common-mode noise cancellation across plant tissue" },
    @{ Name="Pothos (Epipremnum aureum)"; Role="Botanical Model Organism"; Why="• Robust perennial plant resilient to repeated measurement stress`n• Thick, fleshy petioles provide optimal mechanical anchoring for clips`n• High vascular fluid volume produces clear osmotic hydration signals`n• Epidermal mechanoreceptors react reliably to acoustic vibrations`n• Standardized across all 27 experimental sessions" }
)
for ($i = 0; $i -lt $devices.Count; $i++) {
    $col = $i % 2; $row = [math]::Floor($i / 2)
    $dx = 30 + ($col * 470); $dy = 85 + ($row * 205)
    
    $card = $s4.Shapes.AddShape($msoShapeRoundedRectangle, $dx, $dy, 440, 195)
    $card.Fill.Solid(); $card.Fill.ForeColor.RGB = $cForestGreen; $card.Line.Visible = $msoFalse

    # Device title bar
    $dbar = $s4.Shapes.AddShape($msoShapeRectangle, $dx, $dy, 440, 32)
    $dbar.Fill.Solid(); $dbar.Fill.ForeColor.RGB = $cDarkGreen; $dbar.Line.Visible = $msoFalse
    
    $tbD = $s4.Shapes.AddTextbox($msoTextOrientationHorizontal, $dx + 12, $dy + 6, 416, 24)
    $trD = $tbD.TextFrame.TextRange
    $trD.Text = $devices[$i].Name
    $trD.Font.Name = "Segoe UI"; $trD.Font.Size = 12; $trD.Font.Bold = $msoTrue; $trD.Font.Color.RGB = $cAccentGold

    $tbR = $s4.Shapes.AddTextbox($msoTextOrientationHorizontal, $dx + 12, $dy + 38, 416, 20)
    $trR = $tbR.TextFrame.TextRange
    $trR.Text = "Role: " + $devices[$i].Role
    $trR.Font.Name = "Segoe UI"; $trR.Font.Size = 10; $trR.Font.Bold = $msoTrue; $trR.Font.Color.RGB = $cMintGreen

    $tbW = $s4.Shapes.AddTextbox($msoTextOrientationHorizontal, $dx + 12, $dy + 60, 416, 125)
    $tbW.TextFrame.WordWrap = $msoTrue; $tbW.TextFrame.MarginLeft = 0; $tbW.TextFrame.MarginTop = 0
    $trW = $tbW.TextFrame.TextRange
    $trW.Text = $devices[$i].Why
    $trW.Font.Name = "Segoe UI"; $trW.Font.Size = 9.5; $trW.Font.Color.RGB = $cWhite
}

# ==============================================================================
# SLIDE 5: ACQUISITION PIPELINE & WIRING
# ==============================================================================
Write-Host "Generating Slide 5: Acquisition Pipeline"
$s5 = $pres.Slides.Add(5, $ppLayoutBlank)
$bg5 = $s5.Shapes.AddShape($msoShapeRectangle, 0, 0, 960, 540)
$bg5.Fill.Solid(); $bg5.Fill.ForeColor.RGB = $cLightBg; $bg5.Line.Visible = $msoFalse
Add-Header $s5 "End-to-End Signal Acquisition Pipeline" "From plant biological ion flows to organized machine learning datasets" 5
Add-Footer $s5

$pipeSteps = @(
    @{ N="1"; Title="Plant Leads"; Sub="3-Lead Ag/AgCl placement on leaf, stem & root" },
    @{ N="2"; Title="AD8232 AFE"; Sub="0.5-40 Hz analog bandpass + gain amplification" },
    @{ N="3"; Title="Arduino ADC"; Sub="10-bit digitization at 50 Hz sampling frequency" },
    @{ N="4"; Title="Python Stream"; Sub="pyserial validation & real-time oscillogram display" },
    @{ N="5"; Title="CSV Storage"; Sub="Formatted with session_id, timestamp, stimulus label" },
    @{ N="6"; Title="Sliding Windows"; Sub="W = 200 samples (~4s) tumbling segmentation" },
    @{ N="7"; Title="21-D Features"; Sub="Temporal, statistical & Welch spectral features" },
    @{ N="8"; Title="ML Evaluation"; Sub="Stratified cross-validation across 7 algorithms" }
)
for ($i = 0; $i -lt $pipeSteps.Count; $i++) {
    $col = $i % 4; $row = [math]::Floor($i / 4)
    $px = 30 + ($col * 230); $py = 90 + ($row * 195)
    
    $pcard = $s5.Shapes.AddShape($msoShapeRoundedRectangle, $px, $py, 215, 175)
    $pcard.Fill.Solid(); $pcard.Fill.ForeColor.RGB = $cForestGreen; $pcard.Line.Visible = $msoFalse

    # Step number circle
    $circ = $s5.Shapes.AddShape(9, $px + 12, $py + 12, 34, 34) # 9 = msoShapeOval
    $circ.Fill.Solid(); $circ.Fill.ForeColor.RGB = $cAccentGold; $circ.Line.Visible = $msoFalse
    $tbNum = $s5.Shapes.AddTextbox($msoTextOrientationHorizontal, $px + 12, $py + 14, 34, 30)
    $trNum = $tbNum.TextFrame.TextRange
    $trNum.Text = $pipeSteps[$i].N
    $trNum.Font.Name = "Segoe UI"; $trNum.Font.Size = 14; $trNum.Font.Bold = $msoTrue; $trNum.Font.Color.RGB = $cDarkGreen
    $trNum.ParagraphFormat.Alignment = $ppAlignCenter

    $tbPT = $s5.Shapes.AddTextbox($msoTextOrientationHorizontal, $px + 54, $py + 16, 150, 30)
    $trPT = $tbPT.TextFrame.TextRange
    $trPT.Text = $pipeSteps[$i].Title
    $trPT.Font.Name = "Segoe UI"; $trPT.Font.Size = 12; $trPT.Font.Bold = $msoTrue; $trPT.Font.Color.RGB = $cWhite

    $tbPS = $s5.Shapes.AddTextbox($msoTextOrientationHorizontal, $px + 12, $py + 58, 190, 105)
    $tbPS.TextFrame.WordWrap = $msoTrue; $tbPS.TextFrame.MarginLeft = 0; $tbPS.TextFrame.MarginTop = 0
    $trPS = $tbPS.TextFrame.TextRange
    $trPS.Text = $pipeSteps[$i].Sub
    $trPS.Font.Name = "Segoe UI"; $trPS.Font.Size = 10; $trPS.Font.Color.RGB = $cMintGreen
}

# Wiring Table Callout at bottom
$wbox = $s5.Shapes.AddShape($msoShapeRectangle, 30, 470, 900, 26)
$wbox.Fill.Solid(); $wbox.Fill.ForeColor.RGB = $cDarkGreen; $wbox.Line.Visible = $msoFalse
$tbW = $s5.Shapes.AddTextbox($msoTextOrientationHorizontal, 35, 472, 890, 22)
$trW = $tbW.TextFrame.TextRange
$trW.Text = "Pin Connections: AD8232 OUTPUT -> Arduino A0 | 3.3V -> 3.3V | GND -> GND | LO+ -> D10 | LO- -> D11 | Baud: 9600 bps"
$trW.Font.Name = "Segoe UI"; $trW.Font.Size = 9.5; $trW.Font.Color.RGB = $cAccentGold; $trW.ParagraphFormat.Alignment = $ppAlignCenter

# ==============================================================================
# SLIDE 6: EXPERIMENT VIDEO & METHODOLOGY DEMONSTRATION
# ==============================================================================
Write-Host "Generating Slide 6: Experiment Video Demo"
$s6 = $pres.Slides.Add(6, $ppLayoutBlank)
$bg6 = $s6.Shapes.AddShape($msoShapeRectangle, 0, 0, 960, 540)
$bg6.Fill.Solid(); $bg6.Fill.ForeColor.RGB = $cDarkGray; $bg6.Line.Visible = $msoFalse
Add-Header $s6 "Experimental Protocol & Live Demonstration" "Video presentation of electrode attachment, stimulation, and real-time capture" 6
Add-Footer $s6

# Video Frame Placeholder Box
$vbox = $s6.Shapes.AddShape($msoShapeRoundedRectangle, 30, 85, 560, 395)
$vbox.Fill.Solid(); $vbox.Fill.ForeColor.RGB = RGB 15 20 18; $vbox.Line.Visible = $msoTrue
$vbox.Line.ForeColor.RGB = $cAccentGold; $vbox.Line.Weight = 2

$tbV1 = $s6.Shapes.AddTextbox($msoTextOrientationHorizontal, 50, 200, 520, 60)
$trV1 = $tbV1.TextFrame.TextRange
$trV1.Text = "EMBED EXPERIMENT VIDEO HERE"
$trV1.Font.Name = "Segoe UI"; $trV1.Font.Size = 20; $trV1.Font.Bold = $msoTrue; $trV1.Font.Color.RGB = $cAccentGold
$trV1.ParagraphFormat.Alignment = $ppAlignCenter

$tbV2 = $s6.Shapes.AddTextbox($msoTextOrientationHorizontal, 50, 260, 520, 50)
$trV2 = $tbV2.TextFrame.TextRange
$trV2.Text = "In PowerPoint, select this frame and click:`nInsert -> Video -> This Device to place your MP4/AVI recording."
$trV2.Font.Name = "Segoe UI"; $trV2.Font.Size = 11; $trV2.Font.Color.RGB = RGB 180 180 180
$trV2.ParagraphFormat.Alignment = $ppAlignCenter

# Side Notes for Presentation
$vsteps = @(
    @{ T="1. Electrode Placement"; B="Securing Ag/AgCl leads onto upper branch, petiole, and stem using non-invasive clamps with conductive paste." },
    @{ T="2. Environmental Stabilization"; B="Allowing 10 minutes of undisturbed resting time to minimize mechanical handling potential spikes." },
    @{ T="3. Controlled Stimulation"; B="Applying precise stimuli: 50 mL water addition, 80 dB acoustic speaker exposure, or baseline resting." },
    @{ T="4. Real-Time Oscillogram"; B="Custom Python GUI verifies signal continuity, displays rolling 200 samples, and writes timezone-aware CSVs." }
)
for ($i = 0; $i -lt $vsteps.Count; $i++) {
    $vy = 85 + ($i * 100)
    Add-Card $s6 610 $vy 320 92 $cForestGreen $vsteps[$i].T $vsteps[$i].B $cAccentGold $cWhite
}

# ==============================================================================
# SLIDE 7: DATASET SCALE & CLASS DISTRIBUTION
# ==============================================================================
Write-Host "Generating Slide 7: Dataset Overview"
$s7 = $pres.Slides.Add(7, $ppLayoutBlank)
$bg7 = $s7.Shapes.AddShape($msoShapeRectangle, 0, 0, 960, 540)
$bg7.Fill.Solid(); $bg7.Fill.ForeColor.RGB = $cLightBg; $bg7.Line.Visible = $msoFalse
Add-Header $s7 "Dataset Scale & Class Distribution" "27 Experimental Sessions | 1,294,603 Observations | 3,529 Windows" 7
Add-Footer $s7

# 4 Stat Cards
$dStats = @(
    @{ Val="27"; Lbl="Recording Sessions"; Note="Rigorous Multi-Day Trials" },
    @{ Val="1.29M"; Lbl="Total Observations"; Note="Raw 10-bit ADC Counts" },
    @{ Val="3,529"; Lbl="Segmented Windows"; Note="W = 200 Samples (~4s)" },
    @{ Val="21"; Lbl="Engineered Features"; Note="Temporal, Shape & Spectral" }
)
for ($i = 0; $i -lt $dStats.Count; $i++) {
    $dx = 30 + ($i * 230)
    $card = $s7.Shapes.AddShape($msoShapeRoundedRectangle, $dx, 85, 215, 95)
    $card.Fill.Solid(); $card.Fill.ForeColor.RGB = $cForestGreen; $card.Line.Visible = $msoFalse

    $tbV = $s7.Shapes.AddTextbox($msoTextOrientationHorizontal, $dx, 90, 215, 40)
    $trV = $tbV.TextFrame.TextRange
    $trV.Text = $dStats[$i].Val
    $trV.Font.Name = "Segoe UI"; $trV.Font.Size = 24; $trV.Font.Bold = $msoTrue; $trV.Font.Color.RGB = $cAccentGold
    $trV.ParagraphFormat.Alignment = $ppAlignCenter

    $tbL = $s7.Shapes.AddTextbox($msoTextOrientationHorizontal, $dx, 130, 215, 20)
    $trL = $tbL.TextFrame.TextRange
    $trL.Text = $dStats[$i].Lbl
    $trL.Font.Name = "Segoe UI"; $trL.Font.Size = 10; $trL.Font.Bold = $msoTrue; $trL.Font.Color.RGB = $cWhite
    $trL.ParagraphFormat.Alignment = $ppAlignCenter

    $tbN = $s7.Shapes.AddTextbox($msoTextOrientationHorizontal, $dx, 150, 215, 20)
    $trN = $tbN.TextFrame.TextRange
    $trN.Text = $dStats[$i].Note
    $trN.Font.Name = "Segoe UI"; $trN.Font.Size = 8.5; $trN.Font.Color.RGB = $cMintGreen
    $trN.ParagraphFormat.Alignment = $ppAlignCenter
}

# Class Distribution Table
$tblCard = $s7.Shapes.AddShape($msoShapeRoundedRectangle, 30, 195, 480, 290)
$tblCard.Fill.Solid(); $tblCard.Fill.ForeColor.RGB = $cDarkGreen; $tblCard.Line.Visible = $msoFalse

$tbTH = $s7.Shapes.AddTextbox($msoTextOrientationHorizontal, 45, 205, 450, 30)
$trTH = $tbTH.TextFrame.TextRange
$trTH.Text = "Distribution Across 4 Experimental Conditions"
$trTH.Font.Name = "Segoe UI"; $trTH.Font.Size = 12; $trTH.Font.Bold = $msoTrue; $trTH.Font.Color.RGB = $cAccentGold

$classes = @(
    @{ Name="Acoustic Music Stimulation"; Win="2,195"; Share="62.2%"; Color=$cMidGreen },
    @{ Name="Normal Resting Baseline"; Win="963"; Share="27.3%"; Color=$cMidGreen },
    @{ Name="Water Influx (Hydration)"; Win="341"; Share="9.7%"; Color=$cAccentBlue },
    @{ Name="Dead Tissue Negative Control"; Win="30"; Share="0.9%"; Color=$cDeepRed }
)
for ($i = 0; $i -lt $classes.Count; $i++) {
    $cy = 240 + ($i * 50)
    $row = $s7.Shapes.AddShape($msoShapeRoundedRectangle, 45, $cy, 450, 42)
    $row.Fill.Solid(); $row.Fill.ForeColor.RGB = $classes[$i].Color; $row.Line.Visible = $msoFalse

    $tbCN = $s7.Shapes.AddTextbox($msoTextOrientationHorizontal, 55, $cy + 10, 250, 24)
    $trCN = $tbCN.TextFrame.TextRange
    $trCN.Text = $classes[$i].Name
    $trCN.Font.Name = "Segoe UI"; $trCN.Font.Size = 10; $trCN.Font.Bold = $msoTrue; $trCN.Font.Color.RGB = $cWhite

    $tbCW = $s7.Shapes.AddTextbox($msoTextOrientationHorizontal, 310, $cy + 10, 80, 24)
    $trCW = $tbCW.TextFrame.TextRange
    $trCW.Text = "$($classes[$i].Win) wins"
    $trCW.Font.Name = "Segoe UI"; $trCW.Font.Size = 10; $trCW.Font.Color.RGB = $cAccentGold; $trCW.ParagraphFormat.Alignment = $ppAlignRight

    $tbCS = $s7.Shapes.AddTextbox($msoTextOrientationHorizontal, 400, $cy + 10, 80, 24)
    $trCS = $tbCS.TextFrame.TextRange
    $trCS.Text = $classes[$i].Share
    $trCS.Font.Name = "Segoe UI"; $trCS.Font.Size = 10; $trCS.Font.Bold = $msoTrue; $trCS.Font.Color.RGB = $cWhite; $trCS.ParagraphFormat.Alignment = $ppAlignRight
}

# Scientific Discussion Box
Add-Card $s7 530 195 400 290 $cForestGreen "Addressing Data Scale vs Independence" `
"Critical Methodological Distinction:`nHaving 1.29 million readings does NOT equal 1.29 million independent biological events. Readings within a single session share baseline impedance, electrode contact, and environmental drift.`n`nTo prevent Data Leakage:`n• Signals are chunked into non-overlapping sliding windows of 200 samples (~4 seconds each).`n• Stratified cross-validation and session-aware holdouts are strictly applied during model evaluation.`n• Models are evaluated on precision, recall, and F1-score rather than raw accuracy alone."

# ==============================================================================
# SLIDE 8: RAW TIME-SERIES WAVEFORMS (FIGURE 4)
# ==============================================================================
Write-Host "Generating Slide 8: Raw Waveforms"
$s8 = $pres.Slides.Add(8, $ppLayoutBlank)
$bg8 = $s8.Shapes.AddShape($msoShapeRectangle, 0, 0, 960, 540)
$bg8.Fill.Solid(); $bg8.Fill.ForeColor.RGB = $cLightBg; $bg8.Line.Visible = $msoFalse
Add-Header $s8 "Electrophysiological Waveforms Across Conditions" "Time-domain signal characteristics in raw 10-bit ADC units (0-1023)" 8
Add-Footer $s8

$imgWave = Join-Path $baseDir "plot\01_time_series_eda_and_feature_extraction\1_raw_waveform_comparison.png"
if (Test-Path $imgWave) {
    $s8.Shapes.AddPicture($imgWave, $msoFalse, $msoTrue, 30, 85, 560, 395)
}

Add-Card $s8 610 85 320 395 $cForestGreen "Key Waveform Signatures" `
"1. Normal Resting Baseline (Blue):`nMaintains a steady resting biopotential centering at ~380 ADC counts with continuous physiological micro-oscillations.`n`n2. Water Influx / Osmotic Shock (Green):`nShows abrupt baseline depolarization and high signal velocity (MAD) as water enters roots and ions migrate through vascular bundles.`n`n3. Acoustic Pop Vibration (Red):`nExhibits high transient amplitude swings driven by acoustic pressure waves vibrating leaf mechanoreceptors.`n`n4. Dead Plant Control (Black):`nAbsolute zero flatline (ADC = 0). Conclusively proves our AD8232 is detecting genuine bio-potentials, not 50 Hz ambient room noise."

# ==============================================================================
# SLIDE 9: FREQUENCY DOMAIN & POWER SPECTRAL DENSITY (FIGURE 5)
# ==============================================================================
Write-Host "Generating Slide 9: Power Spectral Density"
$s9 = $pres.Slides.Add(9, $ppLayoutBlank)
$bg9 = $s9.Shapes.AddShape($msoShapeRectangle, 0, 0, 960, 540)
$bg9.Fill.Solid(); $bg9.Fill.ForeColor.RGB = $cLightBg; $bg9.Line.Visible = $msoFalse
Add-Header $s9 "Frequency Spectrum & Spectral Energy Distribution" "Welch Power Spectral Density (PSD) and Fourier decomposition" 9
Add-Footer $s9

$imgPSD = Join-Path $baseDir "plot\01_time_series_eda_and_feature_extraction\2_psd_fft_spectrum.png"
if (Test-Path $imgPSD) {
    $s9.Shapes.AddPicture($imgPSD, $msoFalse, $msoTrue, 30, 85, 560, 395)
}

Add-Card $s9 610 85 320 395 $cForestGreen "Spectral Analysis Insights" `
"• Dominant Biological Bandwidth:`nOver 85% of plant bio-potential energy resides in the sub-15 Hz frequency band, characteristic of slow cellular transport.`n`n• Acoustic Resonance Harmonics:`nExposure to devotional and pop music generates clear harmonic spectral peaks (1.8 Hz, 3.5 Hz) corresponding to musical rhythm and percussive beats.`n`n• Hydration Depolarization:`nWater stimulation generates broadband low-frequency energy shifts, reflecting sustained vascular fluid movement.`n`n• Noise Rejection Verification:`nThe AD8232's 40 Hz cutoff eliminates 50 Hz power-line interference, ensuring signal cleanliness."

# ==============================================================================
# SLIDE 10: 21-DIMENSIONAL FEATURE EXTRACTION PIPELINE
# ==============================================================================
Write-Host "Generating Slide 10: Feature Extraction Pipeline"
$s10 = $pres.Slides.Add(10, $ppLayoutBlank)
$bg10 = $s10.Shapes.AddShape($msoShapeRectangle, 0, 0, 960, 540)
$bg10.Fill.Solid(); $bg10.Fill.ForeColor.RGB = $cLightBg; $bg10.Line.Visible = $msoFalse
Add-Header $s10 "21-Dimensional Feature Engineering Pipeline" "Transforming continuous time-series windows (W=200) into rich tabular feature vectors" 10
Add-Footer $s10

$fGroups = @(
    @{ Name="1. Central Tendency & Amplitude (8 Features)"; Items="• Mean (μ): Baseline bio-potential level`n• Median: Robust central tendency`n• Minimum & Maximum: Voltage extremes`n• Range (Max - Min): Peak-to-peak excursion`n• 25th & 75th Percentiles: Interquartile bounds`n• Interquartile Range (IQR): Core spread" },
    @{ Name="2. Dispersion & Waveform Shape (5 Features)"; Items="• Standard Deviation (σ): Signal volatility`n• Variance (σ²): Total energy dispersion`n• Root Mean Square (RMS): Effective AC power`n• Skewness: Asymmetry of bio-potential swings`n• Kurtosis: Heaviness of signal tails / outliers" },
    @{ Name="3. Temporal Kinematics & Events (3 Features)"; Items="• Mean Absolute Difference (MAD): Signal velocity`n  MAD = (1/N) * Σ |x[i+1] - x[i]|`n• Zero-Crossing Rate (ZCR): Oscillation frequency`n• Local Peak Count: Bursts exceeding μ + 1σ" },
    @{ Name="4. Spectral & Frequency Domain (5 Features)"; Items="• Low-Band Spectral Power: 0 to 0.25 fNyq`n• Mid-Band Spectral Power: 0.25 to 0.50 fNyq`n• High-Band Spectral Power: 0.50 to 1.0 fNyq`n• Dominant Frequency Index: Peak FFT component`n• Spectral Entropy (Hspec): Frequency complexity" }
)
for ($i = 0; $i -lt $fGroups.Count; $i++) {
    $col = $i % 2; $row = [math]::Floor($i / 2)
    $fx = 30 + ($col * 470); $fy = 85 + ($row * 205)
    Add-Card $s10 $fx $fy 440 195 $cForestGreen $fGroups[$i].Name $fGroups[$i].Items $cAccentGold $cWhite
}

# ==============================================================================
# SLIDE 11: EXPERIMENT 1 - BIOLOGICAL VIABILITY (FIGURE 6 & 8)
# ==============================================================================
Write-Host "Generating Slide 11: Viability Detection"
$s11 = $pres.Slides.Add(11, $ppLayoutBlank)
$bg11 = $s11.Shapes.AddShape($msoShapeRectangle, 0, 0, 960, 540)
$bg11.Fill.Solid(); $bg11.Fill.ForeColor.RGB = $cLightBg; $bg11.Line.Visible = $msoFalse
Add-Header $s11 "Experiment 1: Biological Viability Detection" "Distinguishing living plant bio-potentials from dead tissue controls" 11
Add-Footer $s11

$imgViab = Join-Path $baseDir "plot\02_viability_dead_vs_alive_rf\1_confusion_matrices.png"
if (Test-Path $imgViab) {
    $s11.Shapes.AddPicture($imgViab, $msoFalse, $msoTrue, 30, 85, 560, 395)
}

Add-Card $s11 610 85 320 395 $cForestGreen "Experimental Outcomes" `
"• Tested Algorithms:`nRandom Forest (100 Trees) and Histogram Gradient Boosting (HistGB).`n`n• Classification Performance:`n- Accuracy: 100% on test splits`n- ROC-AUC: 1.000`n- Average Precision: 1.000`n`n• Top Discriminative Features (Gini):`n1. Signal Velocity (MAD): 10.0% weight`n2. Low-Frequency Spectral Power: 9.0%`n3. Spectral Entropy: 9.0%`n4. Baseline Mean: 9.0%`n`n• Scientific Conclusion:`nLiving plant tissue exhibits intrinsic electrical entropy and non-zero velocity. Dead tissue exhibits absolute flatline variance."

# ==============================================================================
# SLIDE 12: EXPERIMENT 2 - 4-CLASS STIMULUS CLASSIFICATION (FIGURE 9)
# ==============================================================================
Write-Host "Generating Slide 12: 4-Class Classification"
$s12 = $pres.Slides.Add(12, $ppLayoutBlank)
$bg12 = $s12.Shapes.AddShape($msoShapeRectangle, 0, 0, 960, 540)
$bg12.Fill.Solid(); $bg12.Fill.ForeColor.RGB = $cLightBg; $bg12.Line.Visible = $msoFalse
Add-Header $s12 "Experiment 2: 4-Class Stimulus Classification" "Classifying Normal Baseline, Music Exposure, Water Influx, and Dead Control" 12
Add-Footer $s12

$imgMulti = Join-Path $baseDir "plot\03_multiclass_stimulus_svm_knn\1_multiclass_confusion_matrices.png"
if (Test-Path $imgMulti) {
    $s12.Shapes.AddPicture($imgMulti, $msoFalse, $msoTrue, 30, 85, 560, 395)
}

Add-Card $s12 610 85 320 395 $cForestGreen "Performance Comparison" `
"• Evaluated Models:`nSupport Vector Machine (SVM with RBF Kernel) vs K-Nearest Neighbors (KNN with k=7, distance-weighted).`n`n• Overall Accuracy:`n- KNN (k=7): 94.8%`n- SVM (RBF): 94.1%`n`n• Class-Wise F1-Scores:`n- Dead Control: 1.00 (Zero errors)`n- Acoustic Music: 0.97 (F1)`n- Normal Baseline: 0.90 (SVM) / 0.92 (KNN)`n- Water Influx: 0.86 (Shared boundary)`n`n• Finding:`nAcoustic music exhibits distinct periodic vibration. Water events show minor confusion with baseline due to gradual post-watering recovery."

# ==============================================================================
# SLIDE 13: 2D T-SNE MANIFOLD CLUSTERING (FIGURE 10)
# ==============================================================================
Write-Host "Generating Slide 13: t-SNE Clustering"
$s13 = $pres.Slides.Add(13, $ppLayoutBlank)
$bg13 = $s13.Shapes.AddShape($msoShapeRectangle, 0, 0, 960, 540)
$bg13.Fill.Solid(); $bg13.Fill.ForeColor.RGB = $cLightBg; $bg13.Line.Visible = $msoFalse
Add-Header $s13 "t-SNE Manifold Clustering & Feature Separability" "2D non-linear projection of 21-dimensional feature vectors" 13
Add-Footer $s13

$imgTSNE = Join-Path $baseDir "plot\03_multiclass_stimulus_svm_knn\3_tsne_manifold_clusters.png"
if (Test-Path $imgTSNE) {
    $s13.Shapes.AddPicture($imgTSNE, $msoFalse, $msoTrue, 30, 85, 560, 395)
}

Add-Card $s13 610 85 320 395 $cForestGreen "Manifold Topology Analysis" `
"• Dead Control (Red Triangle):`nCompletely isolated point at bottom (-80, 0), reflecting zero-variance flatline.`n`n• Acoustic Music (Purple Squares):`nDominates a broad manifold region characterized by elevated high-frequency energy and rhythm-driven peak counts.`n`n• Water Hydration (Green Diamonds):`nForms an organized cluster centered around (10, 25), reflecting rapid osmotic potential depolarization.`n`n• Baseline Resting (Blue Circles):`nOccupies the compact resting manifold (40 to 60, -10 to 40).`n`nConfirms non-linear boundaries justify SVM (RBF) and non-parametric KNN."

# ==============================================================================
# SLIDE 14: EXPERIMENT 3 - ACOUSTIC GENRE CLASSIFICATION (FIGURE 11)
# ==============================================================================
Write-Host "Generating Slide 14: Acoustic Genre"
$s14 = $pres.Slides.Add(14, $ppLayoutBlank)
$bg14 = $s14.Shapes.AddShape($msoShapeRectangle, 0, 0, 960, 540)
$bg14.Fill.Solid(); $bg14.Fill.ForeColor.RGB = $cLightBg; $bg14.Line.Visible = $msoFalse
Add-Header $s14 "Experiment 3: Acoustic Genre Discrimination" "Can plant leaf mechanoreceptors differentiate musical styles?" 14
Add-Footer $s14

$imgRadar = Join-Path $baseDir "plot\04_music_genre_gradient_boosting\4_genre_radar_profiles.png"
if (Test-Path $imgRadar) {
    $s14.Shapes.AddPicture($imgRadar, $msoFalse, $msoTrue, 30, 85, 560, 395)
}

Add-Card $s14 610 85 320 395 $cForestGreen "Acoustic Mechanosensitivity" `
"• Model: Gradient Boosted Decision Trees (GBDT).`n`n• Overall Accuracy: 55.0%`n(Significantly exceeds 25% random guessing across 4 classes).`n`n• Class-Wise Performance:`n- Pop Music: 72% F1-Score`n- Normal Silence: 69% F1-Score`n- Devotional Music: 41% F1-Score`n- Classical Music: 0% F1-Score`n`n• Electrophysiological Reason:`nPop music features heavy percussive bass transients and high sound pressure dynamics that physically vibrate leaf mechanoreceptors, whereas classical and devotional styles exhibit subtle acoustic overlap."

# ==============================================================================
# SLIDE 15: EXPERIMENT 4 - CIRCADIAN DIURNAL DYNAMICS (FIGURE 13 & 14)
# ==============================================================================
Write-Host "Generating Slide 15: Circadian Dynamics"
$s15 = $pres.Slides.Add(15, $ppLayoutBlank)
$bg15 = $s15.Shapes.AddShape($msoShapeRectangle, 0, 0, 960, 540)
$bg15.Fill.Solid(); $bg15.Fill.ForeColor.RGB = $cLightBg; $bg15.Line.Visible = $msoFalse
Add-Header $s15 "Experiment 4: Circadian Rhythm Classification" "Tracking diurnal baseline shifts: Morning vs Afternoon vs Night" 15
Add-Footer $s15

$imgCirc = Join-Path $baseDir "plot\05_circadian_rhythm_mlp_neural_network\1_diurnal_baseline_shifts.png"
if (Test-Path $imgCirc) {
    $s15.Shapes.AddPicture($imgCirc, $msoFalse, $msoTrue, 30, 85, 560, 395)
}

Add-Card $s15 610 85 320 395 $cForestGreen "Circadian Baseline Drift" `
"• Neural Network Architecture:`nMultilayer Perceptron (MLP) with 2 hidden layers (128 and 64 neurons).`n`n• Classification Accuracy: 70.6%`n`n• Diurnal Potential Variations:`n- Morning (11 AM): Baseline ~380 ADC (Stomata opening, transpiration begins)`n- Afternoon (3 PM): Baseline ~440 ADC (Peak metabolic activity & ion transport, 97.2% recall)`n- Night (10 PM): Baseline ~330 ADC (Stomatal closure, resting steady state)`n`n• Finding:`nLiving plants demonstrate endogenous bio-potential cycles correlated with daily photosynthetic and transpiration activity."

# ==============================================================================
# SLIDE 16: EXPERIMENT 5 - UNSUPERVISED ANOMALY DETECTION (FIGURE 16)
# ==============================================================================
Write-Host "Generating Slide 16: Anomaly Detection"
$s16 = $pres.Slides.Add(16, $ppLayoutBlank)
$bg16 = $s16.Shapes.AddShape($msoShapeRectangle, 0, 0, 960, 540)
$bg16.Fill.Solid(); $bg16.Fill.ForeColor.RGB = $cLightBg; $bg16.Line.Visible = $msoFalse
Add-Header $s16 "Experiment 5: Unsupervised Anomaly Detection" "Label-free stress detection using Isolation Forest for smart precision agriculture" 16
Add-Footer $s16

$imgAnom = Join-Path $baseDir "plot\06_unsupervised_anomaly_detection_isolation_forest\3_continuous_anomaly_timeline.png"
if (Test-Path $imgAnom) {
    $s16.Shapes.AddPicture($imgAnom, $msoFalse, $msoTrue, 30, 85, 560, 395)
}

Add-Card $s16 610 85 320 395 $cForestGreen "Agricultural IoT Application" `
"• Concept:`nIn practical farming, labeled stimulus data does NOT exist. Can an algorithm detect stress without prior labels?`n`n• Methodology:`nAn Isolation Forest is trained exclusively on normal healthy baseline data.`n`n• Anomaly Flagging Results:`n- Water Influx Events: 84.2% flagged`n- Dead Tissue Control: 100% flagged`n- Acoustic Stress: 68.2% flagged`n- False Positive on Baseline: < 10%`n`n• Real-Time Trigger:`nInstantaneous anomaly score cross-over (Score < -0.01) triggers autonomous drip irrigation within 10 seconds of hydraulic change."

# ==============================================================================
# SLIDE 17: MASTER ML MODEL BENCHMARK TABLE
# ==============================================================================
Write-Host "Generating Slide 17: Master ML Benchmark Table"
$s17 = $pres.Slides.Add(17, $ppLayoutBlank)
$bg17 = $s17.Shapes.AddShape($msoShapeRectangle, 0, 0, 960, 540)
$bg17.Fill.Solid(); $bg17.Fill.ForeColor.RGB = $cLightBg; $bg17.Line.Visible = $msoFalse
Add-Header $s17 "Comprehensive Machine Learning Benchmark" "Summary of evaluated algorithms across all experimental objectives" 17
Add-Footer $s17

$mlTable = @(
    @{ Model="Random Forest"; Task="Biological Viability (Living vs Dead)"; Class="2"; Metric="100% Accuracy (AUC: 1.00)"; Feature="Signal Velocity (MAD), RMS" },
    @{ Model="HistGradientBoosting"; Task="Biological Viability (Living vs Dead)"; Class="2"; Metric="100% Accuracy (AUC: 1.00)"; Feature="Low-Freq Spectral Power" },
    @{ Model="K-Nearest Neighbors (k=7)"; Task="Environmental Stimulus Classification"; Class="4"; Metric="94.8% Accuracy (Weighted F1: 0.95)"; Feature="Multi-Dimensional Distance" },
    @{ Model="Support Vector Machine (RBF)"; Task="Environmental Stimulus Classification"; Class="4"; Metric="94.1% Accuracy (Weighted F1: 0.94)"; Feature="Non-Linear Support Vectors" },
    @{ Model="Gradient Boosting (GBDT)"; Task="Acoustic Genre Discrimination"; Class="4"; Metric="55.0% Accuracy (Pop F1: 0.72)"; Feature="High-Freq Power & Peaks" },
    @{ Model="Multilayer Perceptron (MLP)"; Task="Circadian Diurnal Phase (Time-of-Day)"; Class="3"; Metric="70.6% Accuracy (Afternoon: 97.2%)"; Feature="Baseline Mean & Variance" },
    @{ Model="Isolation Forest"; Task="Unsupervised Physiological Anomaly"; Class="N/A"; Metric="84.2% Water Influx Detection"; Feature="Outlier Path Length Score" }
)

# Header Row
$hdr = $s17.Shapes.AddShape($msoShapeRoundedRectangle, 30, 85, 900, 32)
$hdr.Fill.Solid(); $hdr.Fill.ForeColor.RGB = $cAccentGold; $hdr.Line.Visible = $msoFalse
$tbH = $s17.Shapes.AddTextbox($msoTextOrientationHorizontal, 35, 90, 890, 24)
$trH = $tbH.TextFrame.TextRange
$trH.Text = "Algorithm                                Experimental Task                                       Classes        Accuracy / Performance          Key Discriminative Feature"
$trH.Font.Name = "Segoe UI"; $trH.Font.Size = 9.5; $trH.Font.Bold = $msoTrue; $trH.Font.Color.RGB = $cDarkGreen

for ($i = 0; $i -lt $mlTable.Count; $i++) {
    $my = 125 + ($i * 48)
    $rowColor = if ($i % 2 -eq 0) { $cForestGreen } else { $cMidGreen }
    $rCard = $s17.Shapes.AddShape($msoShapeRoundedRectangle, 30, $my, 900, 42)
    $rCard.Fill.Solid(); $rCard.Fill.ForeColor.RGB = $rowColor; $rCard.Line.Visible = $msoFalse

    $tbM1 = $s17.Shapes.AddTextbox($msoTextOrientationHorizontal, 40, $my + 10, 180, 22)
    $trM1 = $tbM1.TextFrame.TextRange
    $trM1.Text = $mlTable[$i].Model
    $trM1.Font.Name = "Segoe UI"; $trM1.Font.Size = 9.5; $trM1.Font.Bold = $msoTrue; $trM1.Font.Color.RGB = $cWhite

    $tbM2 = $s17.Shapes.AddTextbox($msoTextOrientationHorizontal, 225, $my + 10, 260, 22)
    $trM2 = $tbM2.TextFrame.TextRange
    $trM2.Text = $mlTable[$i].Task
    $trM2.Font.Name = "Segoe UI"; $trM2.Font.Size = 9; $trM2.Font.Color.RGB = $cMintGreen

    $tbM3 = $s17.Shapes.AddTextbox($msoTextOrientationHorizontal, 490, $my + 10, 50, 22)
    $trM3 = $tbM3.TextFrame.TextRange
    $trM3.Text = $mlTable[$i].Class
    $trM3.Font.Name = "Segoe UI"; $trM3.Font.Size = 9.5; $trM3.Font.Color.RGB = $cWhite; $trM3.ParagraphFormat.Alignment = $ppAlignCenter

    $tbM4 = $s17.Shapes.AddTextbox($msoTextOrientationHorizontal, 545, $my + 10, 190, 22)
    $trM4 = $tbM4.TextFrame.TextRange
    $trM4.Text = $mlTable[$i].Metric
    $trM4.Font.Name = "Segoe UI"; $trM4.Font.Size = 9; $trM4.Font.Bold = $msoTrue; $trM4.Font.Color.RGB = $cAccentGold

    $tbM5 = $s17.Shapes.AddTextbox($msoTextOrientationHorizontal, 740, $my + 10, 180, 22)
    $trM5 = $tbM5.TextFrame.TextRange
    $trM5.Text = $mlTable[$i].Feature
    $trM5.Font.Name = "Segoe UI"; $trM5.Font.Size = 8.5; $trM5.Font.Color.RGB = $cWhite
}

Add-Card $s17 30 468 900 32 $cDarkGreen "" "Key Takeaway: Ensemble tree models excel at viability detection (100% AUC), while non-linear kernel SVM and KNN excel at multi-class discrimination (94-95% accuracy)." $cAccentGold $cMintGreen

# ==============================================================================
# SLIDE 18: COMPARATIVE ANALYSIS ACROSS STIMULUS CONDITIONS
# ==============================================================================
Write-Host "Generating Slide 18: Comparative Analysis"
$s18 = $pres.Slides.Add(18, $ppLayoutBlank)
$bg18 = $s18.Shapes.AddShape($msoShapeRectangle, 0, 0, 960, 540)
$bg18.Fill.Solid(); $bg18.Fill.ForeColor.RGB = $cLightBg; $bg18.Line.Visible = $msoFalse
Add-Header $s18 "Comparative Physiological Analysis Between Conditions" "Contrasting biophysical mechanisms and electrical signatures" 18
Add-Footer $s18

$comparisons = @(
    @{ Cond="Normal Baseline"; Bio="Resting ion homeostasis (H+-ATPase pumps)"; Signal="Steady ~380 ADC counts, low velocity (MAD < 1.5), balanced low-frequency spectral noise floor"; Rec="Serves as foundational reference; 90-92% classification F1-score" },
    @{ Cond="Water Influx"; Bio="Rapid osmotic pressure change, transpiration pull, xylem ion transport"; Signal="Large negative depolarization shift, elevated signal variance, gradual recovery trajectory"; Rec="Detected at 86% F1 (SVM) and 84.2% unsupervised anomaly sensitivity" },
    @{ Cond="Acoustic Pop Music"; Bio="Mechanoreceptive cell wall perturbation from acoustic sound pressure"; Signal="High-frequency periodic oscillations, maximum peak counts, elevated RMS energy"; Rec="Highest multi-class F1-score (97%); Pop genre achieves 72% F1" },
    @{ Cond="Dead Control Tissue"; Bio="Complete absence of metabolic membrane potentials & ion channels"; Signal="Absolute zero counts (ADC = 0), zero variance (σ = 0), zero signal velocity (MAD = 0)"; Rec="100% discriminative separation across all evaluated models" }
)
for ($i = 0; $i -lt $comparisons.Count; $i++) {
    $col = $i % 2; $row = [math]::Floor($i / 2)
    $cx = 30 + ($col * 470); $cy = 85 + ($row * 205)
    
    $card = $s18.Shapes.AddShape($msoShapeRoundedRectangle, $cx, $cy, 440, 195)
    $card.Fill.Solid(); $card.Fill.ForeColor.RGB = $cForestGreen; $card.Line.Visible = $msoFalse

    $cbar = $s18.Shapes.AddShape($msoShapeRectangle, $cx, $cy, 440, 32)
    $cbar.Fill.Solid(); $cbar.Fill.ForeColor.RGB = $cDarkGreen; $cbar.Line.Visible = $msoFalse

    $tbC = $s18.Shapes.AddTextbox($msoTextOrientationHorizontal, $cx + 12, $cy + 6, 416, 24)
    $trC = $tbC.TextFrame.TextRange
    $trC.Text = $comparisons[$i].Cond
    $trC.Font.Name = "Segoe UI"; $trC.Font.Size = 12; $trC.Font.Bold = $msoTrue; $trC.Font.Color.RGB = $cAccentGold

    $cBody = "• Biophysical Cause:`n$($comparisons[$i].Bio)`n`n• Electrical Waveform Profile:`n$($comparisons[$i].Signal)`n`n• Machine Learning Signature:`n$($comparisons[$i].Rec)"
    $tbB = $s18.Shapes.AddTextbox($msoTextOrientationHorizontal, $cx + 12, $cy + 38, 416, 145)
    $tbB.TextFrame.WordWrap = $msoTrue; $tbB.TextFrame.MarginLeft = 0; $tbB.TextFrame.MarginTop = 0
    $trB = $tbB.TextFrame.TextRange
    $trB.Text = $cBody
    $trB.Font.Name = "Segoe UI"; $trB.Font.Size = 9; $trB.Font.Color.RGB = $cWhite
}

# ==============================================================================
# SLIDE 19: SCIENTIFIC INSIGHTS & DISCUSSION
# ==============================================================================
Write-Host "Generating Slide 19: Scientific Insights"
$s19 = $pres.Slides.Add(19, $ppLayoutBlank)
$bg19 = $s19.Shapes.AddShape($msoShapeRectangle, 0, 0, 960, 540)
$bg19.Fill.Solid(); $bg19.Fill.ForeColor.RGB = $cDarkGreen; $bg19.Line.Visible = $msoFalse
Add-Header $s19 "Key Insights & Electrophysiological Findings" "Core scientific and engineering deductions from our study" 19
Add-Footer $s19

$insights = @(
    @{ Num="1"; Title="Biological Authenticity Established"; Text="The 100% flatline separation on desiccated control tissue conclusively proves the AD8232 measures genuine living bio-potentials rather than ambient 50 Hz antenna noise." },
    @{ Num="2"; Title="Time-Series Segmentation is Paramount"; Text="Raw ADC counts have zero context. Segmenting into 200-sample tumbling windows and extracting 21 statistical, kinematic, and spectral features was essential for high classification accuracy." },
    @{ Num="3"; Title="Vascular Hydraulic Signatures"; Text="Water influx produces clear baseline depolarization within seconds. This electrical wave precedes any physical leaf movement by several hours, offering early-warning capabilities." },
    @{ Num="4"; Title="Mechanosensitive Leaf Response"; Text="Plants react mechanically to sound pressure transients. Pop music was distinguished with a 72% F1-score due to distinct high-frequency energy spikes." },
    @{ Num="5"; Title="Label-Free Practical Deployment"; Text="Isolation Forest trained solely on baseline flagged 84.2% of watering events, proving that supervised labeling is unnecessary for real-world automated irrigation monitoring." }
)
for ($i = 0; $i -lt $insights.Count; $i++) {
    $iy = 85 + ($i * 82)
    $icard = $s19.Shapes.AddShape($msoShapeRoundedRectangle, 30, $iy, 900, 72)
    $icard.Fill.Solid(); $icard.Fill.ForeColor.RGB = $cForestGreen; $icard.Line.Visible = $msoFalse

    $ibar = $s19.Shapes.AddShape($msoShapeRectangle, 30, $iy, 8, 72)
    $ibar.Fill.Solid(); $ibar.Fill.ForeColor.RGB = $cAccentGold; $ibar.Line.Visible = $msoFalse

    $tbIT = $s19.Shapes.AddTextbox($msoTextOrientationHorizontal, 50, $iy + 8, 860, 24)
    $trIT = $tbIT.TextFrame.TextRange
    $trIT.Text = "$($insights[$i].Num). $($insights[$i].Title)"
    $trIT.Font.Name = "Segoe UI"; $trIT.Font.Size = 12; $trIT.Font.Bold = $msoTrue; $trIT.Font.Color.RGB = $cAccentGold

    $tbIB = $s19.Shapes.AddTextbox($msoTextOrientationHorizontal, 50, $iy + 32, 860, 35)
    $tbIB.TextFrame.WordWrap = $msoTrue; $tbIB.TextFrame.MarginLeft = 0; $tbIB.TextFrame.MarginTop = 0
    $trIB = $tbIB.TextFrame.TextRange
    $trIB.Text = $insights[$i].Text
    $trIB.Font.Name = "Segoe UI"; $trIB.Font.Size = 10; $trIB.Font.Color.RGB = $cWhite
}

# ==============================================================================
# SLIDE 20: LIMITATIONS & EXPERIMENTAL CONSTRAINTS
# ==============================================================================
Write-Host "Generating Slide 20: Limitations"
$s20 = $pres.Slides.Add(20, $ppLayoutBlank)
$bg20 = $s20.Shapes.AddShape($msoShapeRectangle, 0, 0, 960, 540)
$bg20.Fill.Solid(); $bg20.Fill.ForeColor.RGB = $cLightBg; $bg20.Line.Visible = $msoFalse
Add-Header $s20 "Engineering Limitations & Critical Evaluation" "Honest appraisal of hardware, electrode, and session constraints" 20
Add-Footer $s20

$limits = @(
    @{ Title="1. Electrode Interface & Motion Artifacts"; Body="• Surface contact impedance changes with cuticle wax thickness and gel drying.`n• Physical touching or plant movement can introduce triboelectric cable motion artifacts that mimic biological depolarizations." },
    @{ Title="2. Acoustic-Mechanical Coupling"; Body="• Sound waves not only affect leaf mechanoreceptors but also mechanically vibrate the electrode wires.`n• Decoupling pure cellular response from microphonic wire vibration requires isolated acoustic chambers." },
    @{ Title="3. Hardware Bandpass Filter Cutoffs"; Body="• AD8232's 0.5 Hz high-pass filter blocks ultra-slow DC potential shifts lasting minutes to hours.`n• Useful for AC spikes, but attenuates very slow variation potentials (slow wave responses)." },
    @{ Title="4. Cross-Session Generalization"; Body="• While stratified cross-validation achieved 94-95%, independent holdouts across completely unseen plants yield lower accuracy due to varying resting baselines and plant health." }
)
for ($i = 0; $i -lt $limits.Count; $i++) {
    $col = $i % 2; $row = [math]::Floor($i / 2)
    $lx = 30 + ($col * 470); $ly = 85 + ($row * 205)
    Add-Card $s20 $lx $ly 440 195 $cDeepRed $limits[$i].Title $limits[$i].Body $cAccentGold $cWhite
}

# ==============================================================================
# SLIDE 21: FUTURE WORK & RESEARCH ROADMAP
# ==============================================================================
Write-Host "Generating Slide 21: Future Work"
$s21 = $pres.Slides.Add(21, $ppLayoutBlank)
$bg21 = $s21.Shapes.AddShape($msoShapeRectangle, 0, 0, 960, 540)
$bg21.Fill.Solid(); $bg21.Fill.ForeColor.RGB = $cLightBg; $bg21.Line.Visible = $msoFalse
Add-Header $s21 "Future Work & Research Roadmap" "Next steps for advancing plant electrophysiology and real-world deployment" 21
Add-Footer $s21

$futureCols = @(
    @{ Phase="PHASE 1: Hardware Upgrades"; Color=$cForestGreen; Items="• Dedicated DC-Coupled AFE:`nDesign custom analog instrumentation with sub-0.05 Hz bandwidth to capture slow variation potentials.`n`n• 16-Bit ADC Resolution:`nIntegrate ADS1115 ADC to achieve 16x finer voltage resolution (microvolt sensitivity).`n`n• Micro-Needle Electrodes:`nTransition from surface gel to non-invasive conductive microneedle arrays directly penetrating leaf veins." },
    @{ Phase="PHASE 2: Environmental Sensing"; Color=$cMidGreen; Items="• Multi-Modal Sensor Fusion:`nSynchronously record ambient temperature, relative humidity, PAR light intensity, and capacitive soil moisture.`n`n• Multi-Species Generalization:`nExpand trials beyond Pothos to crop species (tomatoes, maize, wheat) to validate agronomic applicability.`n`n• Controlled Stimulus Loggers:`nAdd millisecond-accurate hardware event triggers for stimulus onset/offset." },
    @{ Phase="PHASE 3: Edge AI & IoT Deploy"; Color=$cDarkGreen; Items="• TinyML Edge Deployment:`nQuantize Random Forest and MLP models into TensorFlow Lite for microcontrollers (ESP32/RP2040).`n`n• Autonomous Irrigation IoT:`nDeploy standalone solar-powered field nodes triggering relay valves via LoRaWAN/MQTT.`n`n• Open Science Dataset:`nPublish raw 1.29M sample dataset and Python pipeline on IEEE Dataport & GitHub." }
)
for ($i = 0; $i -lt $futureCols.Count; $i++) {
    $fx = 30 + ($i * 310)
    $card = $s21.Shapes.AddShape($msoShapeRoundedRectangle, $fx, 85, 290, 405)
    $card.Fill.Solid(); $card.Fill.ForeColor.RGB = $futureCols[$i].Color; $card.Line.Visible = $msoFalse

    $fbar = $s21.Shapes.AddShape($msoShapeRectangle, $fx, 85, 290, 36)
    $fbar.Fill.Solid(); $fbar.Fill.ForeColor.RGB = $cAccentGold; $fbar.Line.Visible = $msoFalse

    $tbFT = $s21.Shapes.AddTextbox($msoTextOrientationHorizontal, $fx + 10, 92, 270, 24)
    $trFT = $tbFT.TextFrame.TextRange
    $trFT.Text = $futureCols[$i].Phase
    $trFT.Font.Name = "Segoe UI"; $trFT.Font.Size = 11; $trFT.Font.Bold = $msoTrue; $trFT.Font.Color.RGB = $cDarkGreen

    $tbFB = $s21.Shapes.AddTextbox($msoTextOrientationHorizontal, $fx + 12, 130, 266, 350)
    $tbFB.TextFrame.WordWrap = $msoTrue; $tbFB.TextFrame.MarginLeft = 0; $tbFB.TextFrame.MarginTop = 0
    $trFB = $tbFB.TextFrame.TextRange
    $trFB.Text = $futureCols[$i].Items
    $trFB.Font.Name = "Segoe UI"; $trFB.Font.Size = 9.5; $trFB.Font.Color.RGB = $cWhite
}

# ==============================================================================
# SLIDE 22: CONCLUSION & PROJECT SUMMARY
# ==============================================================================
Write-Host "Generating Slide 22: Conclusion"
$s22 = $pres.Slides.Add(22, $ppLayoutBlank)
$bg22 = $s22.Shapes.AddShape($msoShapeRectangle, 0, 0, 960, 540)
$bg22.Fill.Solid(); $bg22.Fill.ForeColor.RGB = $cForestGreen; $bg22.Line.Visible = $msoFalse
Add-Header $s22 "Project Conclusion & Major Milestones" "Summarizing the engineering achievements of our capstone work" 22
Add-Footer $s22

$milestones = @(
    @{ M="1. Low-Cost System Built"; D="Developed an affordable (<$25) acquisition chain using AD8232 + Arduino Uno + Python, replacing multi-thousand-dollar laboratory DAQs." },
    @{ M="2. Large-Scale Empirical Dataset"; D="Captured 27 validated sessions comprising 1,294,603 observations and 3,529 segmented time-series windows across 4 operational conditions." },
    @{ M="3. High-Accuracy Classification"; D="Achieved 100% ROC-AUC on viability detection (Random Forest) and 94.8% accuracy on 4-class stimulus discrimination (KNN, k=7)." },
    @{ M="4. Biological Viability Proved"; D="Dead tissue control flatlined at zero, confirming the hardware measures real electrophysiological transmembrane potentials." },
    @{ M="5. Precision Agriculture Ready"; D="Demonstrated label-free anomaly detection (Isolation Forest), flagging 84.2% of watering events for automated smart irrigation triggers." }
)
for ($i = 0; $i -lt $milestones.Count; $i++) {
    $my = 85 + ($i * 82)
    $card = $s22.Shapes.AddShape($msoShapeRoundedRectangle, 30, $my, 900, 72)
    $card.Fill.Solid(); $card.Fill.ForeColor.RGB = $cDarkGreen; $card.Line.Visible = $msoFalse

    $bar = $s22.Shapes.AddShape($msoShapeRectangle, 30, $my, 8, 72)
    $bar.Fill.Solid(); $bar.Fill.ForeColor.RGB = $cAccentGold; $bar.Line.Visible = $msoFalse

    $tbMT = $s22.Shapes.AddTextbox($msoTextOrientationHorizontal, 50, $my + 8, 860, 24)
    $trMT = $tbMT.TextFrame.TextRange
    $trMT.Text = $milestones[$i].M
    $trMT.Font.Name = "Segoe UI"; $trMT.Font.Size = 12; $trMT.Font.Bold = $msoTrue; $trMT.Font.Color.RGB = $cAccentGold

    $tbMD = $s22.Shapes.AddTextbox($msoTextOrientationHorizontal, 50, $my + 32, 860, 35)
    $tbMD.TextFrame.WordWrap = $msoTrue; $tbMD.TextFrame.MarginLeft = 0; $tbMD.TextFrame.MarginTop = 0
    $trMD = $tbMD.TextFrame.TextRange
    $trMD.Text = $milestones[$i].D
    $trMD.Font.Name = "Segoe UI"; $trMD.Font.Size = 10; $trMD.Font.Color.RGB = $cWhite
}

# ==============================================================================
# SLIDE 23: THANK YOU & Q&A
# ==============================================================================
Write-Host "Generating Slide 23: Thank You Slide"
$s23 = $pres.Slides.Add(23, $ppLayoutBlank)
$bg23 = $s23.Shapes.AddShape($msoShapeRectangle, 0, 0, 960, 540)
$bg23.Fill.Solid(); $bg23.Fill.ForeColor.RGB = $cDarkGreen; $bg23.Line.Visible = $msoFalse

$edge23 = $s23.Shapes.AddShape($msoShapeRectangle, 0, 0, 10, 540)
$edge23.Fill.Solid(); $edge23.Fill.ForeColor.RGB = $cAccentGold; $edge23.Line.Visible = $msoFalse

$panel23 = $s23.Shapes.AddShape($msoShapeRoundedRectangle, 640, 30, 290, 480)
$panel23.Fill.Solid(); $panel23.Fill.ForeColor.RGB = $cForestGreen; $panel23.Line.Visible = $msoFalse

$tbTY = $s23.Shapes.AddTextbox($msoTextOrientationHorizontal, 45, 90, 560, 80)
$trTY = $tbTY.TextFrame.TextRange
$trTY.Text = "Thank You!"
$trTY.Font.Name = "Segoe UI"; $trTY.Font.Size = 52; $trTY.Font.Bold = $msoTrue; $trTY.Font.Color.RGB = $cWhite

$dTY = $s23.Shapes.AddShape($msoShapeRectangle, 45, 180, 560, 3)
$dTY.Fill.Solid(); $dTY.Fill.ForeColor.RGB = $cAccentGold; $dTY.Line.Visible = $msoFalse

$tbQA = $s23.Shapes.AddTextbox($msoTextOrientationHorizontal, 45, 195, 560, 45)
$trQA = $tbQA.TextFrame.TextRange
$trQA.Text = "We are now open for Questions & Discussion."
$trQA.Font.Name = "Segoe UI"; $trQA.Font.Size = 18; $trQA.Font.Italic = $msoTrue; $trQA.Font.Color.RGB = $cLightGreen

$tbPres = $s23.Shapes.AddTextbox($msoTextOrientationHorizontal, 45, 260, 560, 60)
$trPres = $tbPres.TextFrame.TextRange
$trPres.Text = "Presented by:`nTanishq Gupta  |  Sachin Mishra  |  Asim Kumar Mahata"
$trPres.Font.Name = "Segoe UI"; $trPres.Font.Size = 13; $trPres.Font.Bold = $msoTrue; $trPres.Font.Color.RGB = $cWhite

$tbG2 = $s23.Shapes.AddTextbox($msoTextOrientationHorizontal, 45, 335, 560, 60)
$trG2 = $tbG2.TextFrame.TextRange
$trG2.Text = "Guided by:`nDr. Subrata Dutta  |  Dr. Mayukh Sarkar  |  Dr. Amit Majumder"
$trG2.Font.Name = "Segoe UI"; $trG2.Font.Size = 11; $trG2.Font.Color.RGB = $cLightGold

$tbNIT = $s23.Shapes.AddTextbox($msoTextOrientationHorizontal, 45, 410, 560, 50)
$trNIT = $tbNIT.TextFrame.TextRange
$trNIT.Text = "Department of Electronics & Communication Engineering`nNational Institute of Technology Jamshedpur"
$trNIT.Font.Name = "Segoe UI"; $trNIT.Font.Size = 12; $trNIT.Font.Bold = $msoTrue; $trNIT.Font.Color.RGB = $cAccentGold

for ($i = 0; $i -lt $metrics.Count; $i++) {
    $my = 55 + ($i * 110)
    $card = $s23.Shapes.AddShape($msoShapeRoundedRectangle, 665, $my, 240, 92)
    $card.Fill.Solid(); $card.Fill.ForeColor.RGB = $cDarkGreen; $card.Line.Visible = $msoFalse
    
    $tbM = $s23.Shapes.AddTextbox($msoTextOrientationHorizontal, 665, $my + 10, 240, 45)
    $trM = $tbM.TextFrame.TextRange
    $trM.Text = $metrics[$i].Val
    $trM.Font.Name = "Segoe UI"; $trM.Font.Size = 28; $trM.Font.Bold = $msoTrue; $trM.Font.Color.RGB = $cAccentGold
    $trM.ParagraphFormat.Alignment = $ppAlignCenter

    $tbL = $s23.Shapes.AddTextbox($msoTextOrientationHorizontal, 665, $my + 55, 240, 25)
    $trL = $tbL.TextFrame.TextRange
    $trL.Text = $metrics[$i].Lbl
    $trL.Font.Name = "Segoe UI"; $trL.Font.Size = 10; $trL.Font.Color.RGB = $cWhite
    $trL.ParagraphFormat.Alignment = $ppAlignCenter
}

# ==============================================================================
# SAVE PRESENTATION
# ==============================================================================
Write-Host "Saving Presentation to: $outputFile"
if (Test-Path $outputFile) {
    Remove-Item $outputFile -Force
}
$pres.SaveAs($outputFile)
$pres.Close()
$ppt.Quit()
[System.Runtime.Interopservices.Marshal]::ReleaseComObject($ppt) | Out-Null

Write-Host "SUCCESS! Generated Native PowerPoint Presentation at: $outputFile"
