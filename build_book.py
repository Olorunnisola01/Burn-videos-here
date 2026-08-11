# -*- coding: utf-8 -*-
"""
Generates a beautifully styled, detailed .docx book:
"Cohesive Zone Modeling: A Beginner's Guide to Fracture Mechanics & Abaqus"
"""
from docx import Document
from docx.shared import Pt, Inches, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.section import WD_SECTION
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

# ---------------------------------------------------------------------------
# Colour palette
# ---------------------------------------------------------------------------
NAVY      = RGBColor(0x1F, 0x38, 0x64)
TEAL      = RGBColor(0x1F, 0x7A, 0x8C)
ACCENT    = RGBColor(0x2E, 0x86, 0xAB)
GOLD      = RGBColor(0xB8, 0x86, 0x0B)
DARKTXT   = RGBColor(0x33, 0x33, 0x33)
GRAY      = RGBColor(0x77, 0x77, 0x77)
WHITE     = RGBColor(0xFF, 0xFF, 0xFF)
RED       = RGBColor(0xA9, 0x3A, 0x2E)

CALLOUT_BG   = "EAF1F8"   # light blue callout
ANALOGY_BG   = "FFF6E3"   # cream analogy box
TIP_BG       = "EAF6EC"   # light green tip box
WARN_BG      = "FBEEEC"   # light red warning
EQ_BG        = "F4F6FA"   # equation band
GRAY_BG      = "F2F2F2"

BODY_FONT = "Calibri"
HEAD_FONT = "Calibri"

doc = Document()

# ---------------------------------------------------------------------------
# Base styles
# ---------------------------------------------------------------------------
def set_base_styles():
    normal = doc.styles["Normal"]
    normal.font.name = BODY_FONT
    normal.font.size = Pt(11.5)
    normal.font.color.rgb = DARKTXT
    pf = normal.paragraph_format
    pf.space_after = Pt(8)
    pf.line_spacing = 1.25

    for name, size, color in [
        ("Heading 1", 22, NAVY),
        ("Heading 2", 16, TEAL),
        ("Heading 3", 13, ACCENT),
        ("Title", 34, NAVY),
    ]:
        st = doc.styles[name]
        st.font.name = HEAD_FONT
        st.font.size = Pt(size)
        st.font.bold = True
        st.font.color.rgb = color
        # clean the default blue
        rpr = st.element.get_or_add_rPr()
        # ensure latin font
        rfonts = st.element.rPr.rFonts
        if rfonts is None:
            rfonts = OxmlElement("w:rFonts")
            st.element.rPr.append(rfonts)
        rfonts.set(qn("w:ascii"), HEAD_FONT)
        rfonts.set(qn("w:hAnsi"), HEAD_FONT)

set_base_styles()

# ---------------------------------------------------------------------------
# Low level helpers
# ---------------------------------------------------------------------------
def shade_paragraph(paragraph, hex_color):
    pPr = paragraph._p.get_or_add_pPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:color"), "auto")
    shd.set(qn("w:fill"), hex_color)
    pPr.append(shd)

def shade_cell(cell, hex_color):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:color"), "auto")
    shd.set(qn("w:fill"), hex_color)
    tcPr.append(shd)

def add_run(paragraph, text, bold=False, italic=False, size=None,
            color=None, font=None):
    r = paragraph.add_run(text)
    r.bold = bold
    r.italic = italic
    if size: r.font.size = Pt(size)
    if color: r.font.color.rgb = color
    if font: r.font.name = font
    return r

def para(text="", bold=False, italic=False, size=None, color=None,
         align=None, space_after=8, space_before=0, indent=None):
    p = doc.add_paragraph()
    pf = p.paragraph_format
    pf.space_after = Pt(space_after)
    pf.space_before = Pt(space_before)
    if align is not None:
        p.alignment = align
    if indent is not None:
        pf.left_indent = Inches(indent)
    if text:
        add_run(p, text, bold=bold, italic=italic, size=size, color=color)
    return p

def bullet(text, level=0, bold_lead=None):
    """A paragraph with a manual bullet marker (robust across renderers)."""
    p = doc.add_paragraph()
    pf = p.paragraph_format
    pf.space_after = Pt(4)
    pf.left_indent = Inches(0.35 + level * 0.3)
    pf.first_line_indent = Inches(-0.25 + level * 0.0)
    pf.line_spacing = 1.2
    marker = "•  " if level == 0 else "–  "
    add_run(p, marker, bold=True, color=TEAL)
    if bold_lead:
        add_run(p, bold_lead, bold=True)
    add_run(p, text)
    return p

def numbered_item(num, text, bold_lead=None):
    p = doc.add_paragraph()
    pf = p.paragraph_format
    pf.space_after = Pt(6)
    pf.left_indent = Inches(0.35)
    pf.first_line_indent = Inches(-0.35)
    add_run(p, f"{num}.  ", bold=True, color=TEAL)
    if bold_lead:
        add_run(p, bold_lead, bold=True)
    add_run(p, text)
    return p

def equation(text):
    """Centered equation in a shaded band."""
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    pf = p.paragraph_format
    pf.space_before = Pt(8)
    pf.space_after = Pt(8)
    shade_paragraph(p, EQ_BG)
    add_run(p, text, italic=False, size=13, color=NAVY, font="Cambria Math")
    return p

def equation_ref(text):
    """Small right-aligned equation reference."""
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    p.paragraph_format.space_after = Pt(8)
    add_run(p, text, italic=True, size=9, color=GRAY)
    return p

def callout(title, body, bg=CALLOUT_BG, title_color=NAVY, icon="▸"):
    p = doc.add_paragraph()
    pf = p.paragraph_format
    pf.space_before = Pt(6)
    pf.space_after = Pt(2)
    shade_paragraph(p, bg)
    add_run(p, f"{icon}  {title}", bold=True, color=title_color, size=11.5)
    p2 = doc.add_paragraph()
    pf2 = p2.paragraph_format
    pf2.space_after = Pt(10)
    pf2.left_indent = Inches(0.1)
    shade_paragraph(p2, bg)
    # support multiline body
    if isinstance(body, list):
        first = True
        for line in body:
            if first:
                add_run(p2, line, size=10.5)
                first = False
            else:
                br = p2.add_run()
                br.add_break()
                add_run(p2, line, size=10.5)
    else:
        add_run(p2, body, size=10.5)
    return p

def key_point(text):
    callout("Key Concept", text, bg=TIP_BG, title_color=RGBColor(0x1E,0x5E,0x2B), icon="✔")

def analogy(text):
    callout("Think of it like this", text, bg=ANALOGY_BG, title_color=GOLD, icon="★")

def warning(text):
    callout("Common Pitfall", text, bg=WARN_BG, title_color=RED, icon="⚠")

def chapter_heading(number, title, subtitle=None):
    # decorative band line
    p = para("", space_after=0, space_before=0)
    pPr = p._p.get_or_add_pPr()
    pbdr = OxmlElement("w:pBdr")
    bottom = OxmlElement("w:bottom")
    bottom.set(qn("w:val"), "single"); bottom.set(qn("w:sz"), "18")
    bottom.set(qn("w:space"), "4"); bottom.set(qn("w:color"), "1F7A8C")
    pbdr.append(bottom); pPr.append(pbdr)
    p.add_run("")
    para(f"CHAPTER {number}", bold=True, size=11, color=TEAL, space_before=6, space_after=2)
    h = doc.add_heading(title, level=1)
    h.paragraph_format.space_after = Pt(2)
    if subtitle:
        para(subtitle, italic=True, color=GRAY, size=12, space_after=14)

def section(title):
    doc.add_heading(title, level=2)

def sub(title):
    doc.add_heading(title, level=3)

def page_break():
    doc.add_paragraph().add_run().add_break(WD_BREAK.PAGE)

_FIG_NUM = {"n": 0}
def add_figure(image_path, caption, width_in=5.6):
    """Insert a centered figure with a caption. Auto-numbers figures."""
    _FIG_NUM["n"] += 1
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(10)
    p.paragraph_format.space_after = Pt(2)
    run = p.add_run()
    run.add_picture(image_path, width=Inches(width_in))
    cap = doc.add_paragraph()
    cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
    cap.paragraph_format.space_after = Pt(10)
    add_run(cap, f"Figure {_FIG_NUM['n']} — {caption}", italic=True, size=9.5, color=GRAY)

def add_table(headers, rows, col_widths=None, header_bg="1F7A8C"):
    t = doc.add_table(rows=1, cols=len(headers))
    t.style = "Table Grid"
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    hdr = t.rows[0].cells
    for i, h in enumerate(headers):
        shade_cell(hdr[i], header_bg)
        hp = hdr[i].paragraphs[0]
        hp.alignment = WD_ALIGN_PARAGRAPH.CENTER
        add_run(hp, h, bold=True, color=WHITE, size=10.5)
    for ridx, row in enumerate(rows):
        cells = t.add_row().cells
        for i, val in enumerate(row):
            cp = cells[i].paragraphs[0]
            if ridx % 2 == 1:
                shade_cell(cells[i], "F2F7FA")
            add_run(cp, val, size=10)
    if col_widths:
        for i, w in enumerate(col_widths):
            for row in t.rows:
                row.cells[i].width = Inches(w)
    # spacing after table
    doc.add_paragraph().paragraph_format.space_after = Pt(2)
    return t

# ---------------------------------------------------------------------------
# Headers / footers
# ---------------------------------------------------------------------------
def setup_headers_footers():
    sec = doc.sections[0]
    sec.top_margin = Inches(0.9)
    sec.bottom_margin = Inches(0.9)
    sec.left_margin = Inches(1.0)
    sec.right_margin = Inches(1.0)
    # Header
    hp = sec.header.paragraphs[0]
    hp.text = ""
    hp.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    add_run(hp, "Cohesive Zone Modeling — A Beginner's Guide", italic=True, size=9, color=GRAY)
    # Bottom border for header
    pPr = hp._p.get_or_add_pPr()
    pbdr = OxmlElement("w:pBdr")
    bottom = OxmlElement("w:bottom")
    bottom.set(qn("w:val"), "single"); bottom.set(qn("w:sz"), "6")
    bottom.set(qn("w:space"), "4"); bottom.set(qn("w:color"), "BFD7E4")
    pbdr.append(bottom); pPr.append(pbdr)
    # Footer with page number
    fp = sec.footer.paragraphs[0]
    fp.text = ""
    fp.alignment = WD_ALIGN_PARAGRAPH.CENTER
    add_run(fp, "Page ", size=9, color=GRAY)
    fld1 = OxmlElement("w:fldSimple"); fld1.set(qn("w:instr"), "PAGE")
    fp._p.append(fld1)

setup_headers_footers()

# ---------------------------------------------------------------------------
# COVER PAGE
# ---------------------------------------------------------------------------
def cover_page():
    for _ in range(3):
        para("", space_after=12)
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    add_run(p, "COHESIVE ZONE MODELING", bold=True, size=40, color=NAVY)
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    add_run(p, "A Beginner’s Guide to Fracture Mechanics, Delamination,\nand the Traction–Separation Law", italic=True, size=18, color=TEAL)
    # decorative divider
    p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    add_run(p, "─────── ◆ ───────", color=GOLD, size=14)
    p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    add_run(p, "From Theory → Mathematical Model → Abaqus Implementation",
            size=13, color=ACCENT)
    for _ in range(6):
        para("", space_after=12)
    # small box with what you will learn
    box = doc.add_paragraph()
    box.alignment = WD_ALIGN_PARAGRAPH.CENTER
    shade_paragraph(box, CALLOUT_BG)
    add_run(box, "Understand the mechanics, not just the menus.\n\n"
                 "In this book you will learn:\n"
                 "• Why cracks grow and how engineers predict it\n"
                 "• Modes I, II & III fracture and mixed-mode behaviour\n"
                 "• Energy release rate — the engine of crack growth\n"
                 "• Delamination in composite laminates\n"
                 "• Cohesive zone theory and why it works\n"
                 "• The traction–separation law, step by step\n"
                 "• How all of it connects to Abaqus settings",
            size=12, color=DARKTXT)
    para("", space_after=6)
    p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    add_run(p, "First Edition  ·  Entry-Level Reader Edition", italic=True, size=10, color=GRAY)

cover_page()
page_break()

# Insert cover art on a dedicated page
from docx.shared import Inches as _In
art = doc.add_paragraph()
art.alignment = WD_ALIGN_PARAGRAPH.CENTER
run = art.add_run()
run.add_picture("cover_art.png", width=_In(6.3))
art.paragraph_format.space_after = Pt(10)
cap = doc.add_paragraph()
cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
add_run(cap, "Figure 0 — A laminated composite with a delamination crack growing along an interface, "
             "overlaid on a finite element mesh.", italic=True, size=9, color=GRAY)
page_break()

# ---------------------------------------------------------------------------
# HOW TO USE THIS BOOK
# ---------------------------------------------------------------------------
chapter_heading("", "How to Use This Book", "A short note before we begin")
para("This book was written for one kind of reader: someone who wants to truly "
     "understand the science behind cohesive zone modelling in Abaqus — not just "
     "memorise which checkboxes to tick. If you have ever felt that the Abaqus "
     "interface presents you with dozens of mysterious buttons and you have no "
     "idea what they actually do, this book is for you.")
para("We will build understanding from the ground up. Each chapter is a single, "
     "self-contained idea. By the end you will be able to look at any cohesive "
     "zone model input in Abaqus and know, in your bones, why every number is "
     "there.")
key_point("Abaqus is only a tool. The real value lives in understanding the "
          "mechanics behind it. Master the mechanics and the software becomes "
          "intuitive; master only the software and you can reproduce results "
          "you do not understand.")
section("How the chapters fit together")
para("The book follows one logical thread, and you should read it in order the "
     "first time. Each chapter lays the foundation for the next:")
add_table(
    ["Stage", "What you will learn", "Abaqus connection"],
    [
        ["1. Fracture Mechanics", "Why cracks grow; stress vs. fracture thinking",
         "Why cohesive elements exist"],
        ["2. Modes I–III", "How cracks open, slide, and tear",
         "Which loading a simulation applies"],
        ["3. Energy Release Rate", "The driving force for crack growth",
         "Sets the fracture energy input"],
        ["4. Delamination", "Composite layers separating",
         "Where cracks usually form in laminates"],
        ["5. Cohesive Zone Theory", "A realistic model of the crack tip",
         "The cohesive element concept"],
        ["6. Traction–Separation Law", "The relationship governing damage",
         "Material definition in Abaqus"],
        ["7. Putting It Together", "From load to failure; theory maps to Abaqus",
         "The whole cohesive model workflow"],
        ["8. Worked Example", "A complete DCB simulation",
         "Cohesive elements, material, and results"],
    ],
    col_widths=[1.9, 2.9, 2.1],
)
section("Reading conventions used in this book")
bullet("Shaded blue boxes highlight a key concept you should remember.", bold_lead="Key Concept — ")
bullet("Cream boxes translate an idea into everyday life so it sticks.", bold_lead="Analogy — ")
bullet("Green boxes offer practical tips.", bold_lead="Tip — ")
bullet("Red boxes warn you about common mistakes and pitfalls.", bold_lead="Warning — ")
bullet("Dark blue bands show important equations.", bold_lead="Equation — ")
section("Prerequisites")
para("You do not need a background in fracture mechanics. This book assumes only "
     "basic familiarity with what stress and strain are (if you have completed an "
     "introductory mechanics of materials course, you are more than ready). Wherever "
     "an advanced idea appears, we introduce it gently and build up to it.")
page_break()

# ---------------------------------------------------------------------------
# CHAPTER 1
# ---------------------------------------------------------------------------
chapter_heading(1, "Fracture Mechanics Fundamentals",
                "Why strength alone is not enough to keep structures safe")

section("1.1  What is fracture mechanics?")
para("Fracture mechanics is the branch of solid mechanics that studies how cracks "
     "initiate, grow, and eventually cause a structure to fail. It is a subtle "
     "shift in perspective from classical strength-of-materials analysis, so let "
     "us make that shift very clear before we go any further.")
para("Classical strength-of-materials analysis asks one central question:")
callout("The traditional question", 
        "How much stress can this material withstand before it yields or breaks?",
        bg=ANALOGY_BG, title_color=GOLD, icon="?")
para("Fracture mechanics, by contrast, begins with a different assumption. It "
     "accepts that every real component already contains flaws — tiny cracks, "
     "voids, machining scratches, manufacturing defects, or impact damage — and "
     "then asks:")
callout("The fracture-mechanics question",
        "If a crack already exists in this material, will it grow, and if so, how fast?",
        bg=ANALOGY_BG, title_color=GOLD, icon="?")
para("This distinction is the entire subject in miniature. A perfect, flawless "
     "material might never crack under a given load, while an identical component "
     "with one small hidden flaw could fail dramatically. Because we can never "
     "guarantee a component is flawless, engineers must be able to answer the "
     "second question. This is what fracture mechanics is designed to do.")

section("1.2  The unrealistic assumption of perfect materials")
para("Think about how an aircraft wing is manufactured. It is built from layers "
     "of carbon fibre and resin that are cured, cut, drilled, and bolted together. "
     "Every one of those steps can introduce imperfections: a tiny void where air "
     "was trapped during curing, a scratch from a drill bit, a barely visible "
     "impact from a dropped tool. In aerospace, this is not an occasional accident "
     "— it is the norm.")
para("It would be wonderful if we could pretend these flaws do not exist. But "
     "doing so would be dangerous. An analysis that assumes a perfect material "
     "may predict that a panel is safe when, in reality, a small crack is about to "
     "grow through it. This is precisely why fracture mechanics was developed: it "
     "provides a disciplined way to account for the flaws we know are there.")

section("1.3  Why not just use stress?")
para("Let us make the argument concrete with a thought experiment that engineers "
     "return to again and again.")
para("Imagine two identical carbon/epoxy panels, cut from the same sheet and "
     "subjected to the exact same tensile (pulling) load:")
add_table(
    ["Feature", "Panel A", "Panel B"],
    [
        ["Condition", "Flawless, no defects", "Contains a 5 mm delamination"],
        ["Average tensile stress", "Same in both", "Same in both"],
        ["Prediction from classical analysis", "Safe (stress below strength)", "Safe (stress below strength)"],
        ["Reality", "Likely safe", "Likely to fail"],
    ],
    col_widths=[1.7, 2.2, 2.2],
)
para("The classical analysis looks at the average stress across the panel and "
     "compares it with the material's ultimate strength. Both panels have the same "
     "average stress, so both are judged safe. But this ignores what happens "
     "locally at the crack. The crack tip concentrates stress — near a sharp "
     "flaw, the stress is far higher than the average, and it is this local "
     "concentration that actually drives failure.")
key_point("Average stress tells you the overall load level. Fracture mechanics "
          "tells you what happens at the tip of a flaw, which is where failure "
          "actually begins.")

section("1.4  Stress concentration at the crack tip")
para("When you load a cracked component, the load path has to flow around the "
     "crack. Right at the tip, the 'lines of force' are squeezed together into a "
     "tiny region, which makes the local stress enormously higher than the "
     "average. The sharper and longer the crack, the more severe this effect.")
para("Theoretical elasticity actually predicts something striking: the stress "
     "right at an ideal, perfectly sharp crack tip tends toward infinity. This is "
     "called a singularity — the equations say the stress becomes unbounded. Of "
     "course, no real material can support infinite stress. What really happens "
     "is more interesting:")
bullet("microscopic damage develops in a small region around the tip;")
bullet("fibres in a composite begin to bridge across the crack;")
bullet("the resin matrix cracks and microfractures;")
bullet("interfaces between layers debond;")
para("and the sharp crack effectively becomes a small damaged zone rather than a "
     "single point of infinite stress. This behaviour is exactly the physical "
     "reality that the cohesive zone model was created to represent, and it is "
     "why we study it later in this book.")
warning("Do not interpret the singularity as 'the material fails instantly'. It "
        "simply means classical elasticity is incomplete at the crack tip. Real "
        "materials blunt the tip through local damage, and the cohesive model "
        "captures that process.")

section("1.5  Two views of a crack: stress-based vs. energy-based")
para("There are two broad ways to describe how a crack grows, and it is worth "
     "knowing both because they complement each other.")
sub("The stress (local) view")
para("A crack grows when the stress at its tip exceeds some critical value. This "
     "is intuitive but tricky to apply, because the stress at an ideal crack tip "
     "is infinite — so we need more sophisticated measures (like the stress "
     "intensity factor) to make it work. We mention this only so you recognise "
     "the idea; the cohesive model you will use in Abaqus works mostly through the "
     "energy view below.")
sub("The energy (global) view")
para("A crack grows when the energy released by the growing crack is enough to "
     "create new fracture surfaces. This view asks: where does the energy to open "
     "the crack come from, and is there enough of it? This leads directly to the "
     "concept of energy release rate, which we study in detail in Chapter 3.")
key_point("Both views describe the same phenomenon. Abaqus's cohesive zone model "
          "is built on the energy view: it tracks how much energy is released and "
          "how much the material can absorb before failing.")

section("1.6  What you should remember from this chapter")
numbered_item(1, "Fracture mechanics studies how existing cracks grow, rather than assuming perfect materials.")
numbered_item(2, "Real components always contain flaws, so we must predict whether those flaws remain stable.")
numbered_item(3, "A crack tip concentrates stress, and classical stress analysis can be dangerously optimistic.")
numbered_item(4, "The theoretical crack-tip stress is a singularity; real materials respond with local damage.")
numbered_item(5, "Energy-based thinking (energy release rate) is the foundation for cohesive zone models.")
page_break()

# ---------------------------------------------------------------------------
# CHAPTER 2
# ---------------------------------------------------------------------------
chapter_heading(2, "Modes I, II, and III Fracture",
                "The three fundamental ways a crack can open")
para("Cracks do not all open in the same way. A crack can be pulled straight "
     "apart, slid sideways, or twisted. These different motions produce different "
     "types of stress at the crack tip, and engineers have standardised them into "
     "three 'modes', numbered I, II, and III. Learning these modes is essential "
     "because every fracture test, every cohesive model, and every Abaqus "
     "simulation is described in terms of them.")

section("2.1  A shared mental picture")
para("Imagine a crack as a pair of flat faces that were once bonded together. "
     "Now imagine the many different ways you could push and pull those faces "
     "apart. Each distinct motion defines a mode. The modes are defined relative "
     "to the crack plane (the plane that contains the crack) and the crack front "
     "(the edge of the crack, where it is currently growing).")

section("2.2  Mode I — The Opening Mode")
para("Mode I is the simplest and by far the most common mode in practice. The "
     "crack faces are pulled directly apart, perpendicular to the crack plane.")
para("Think of pulling the two halves of a broken cookie apart with your hands — "
     "the two faces separate straight up and down. The loading acts normal (at "
     "right angles) to the crack plane, so the crack faces move away from each "
     "other, opening a gap.")
callout("Mode I in one line",
        "The crack faces move directly apart, normal to the crack plane.",
        bg=CALLOUT_BG, title_color=NAVY, icon="I")
para("The standard laboratory test for Mode I delamination is the Double Cantilever "
     "Beam (DCB) test. In it, a beam with a starter crack is pulled apart at one "
     "end like opening a book, and the crack grows along the bonded interface. "
     "Because it is easy to set up and gives clean results, DCB is the most "
     "commonly performed delamination test for composites.")

section("2.3  Mode II — The Sliding (In-Plane Shear) Mode")
para("In Mode II, the crack faces slide past one another in the plane of the "
     "crack. There is no opening — the two faces move in opposite directions, "
     "parallel to the crack plane, like shearing a deck of cards.")
para("Imagine pressing your palms together flat and rubbing them back and forth. "
     "The surfaces stay in contact but slide. This is an in-plane shearing motion, "
     "and it is driven by shear stress rather than by normal (pulling) stress.")
callout("Mode II in one line",
        "The crack faces slide over one another, in-plane shear.",
        bg=CALLOUT_BG, title_color=NAVY, icon="II")
para("The classic test for Mode II is the End Notched Flexure (ENF) test, in which "
     "a notched beam is bent so that the crack is driven by shear along the "
     "interface. Mode II is very important in real structures because bending "
     "loads generate exactly this kind of sliding along delamination interfaces.")
add_figure("fig_dcb.png",
           "The Double Cantilever Beam (DCB) test for Mode I: the split beam is "
           "pried open at one end like opening a book, growing a delamination "
           "along the bonded interface. It is the standard way to measure G_Ic.",
           width_in=5.2)

section("2.4  Mode III — The Tearing (Out-of-Plane Shear) Mode")
para("Mode III involves out-of-plane shear. Imagine tearing a sheet of paper or "
     "twisting the two halves of a cracked plate in opposite directions about an "
     "axis along the crack. The crack faces slide sideways, but in a direction "
     "that is out of the crack plane, producing a twisting or tearing motion.")
callout("Mode I, II & III at a glance", "", bg=CALLOUT_BG, title_color=NAVY, icon="▸")
add_figure("fig_modes.png",
           "The three fundamental modes of crack loading: Mode I (opening), "
           "Mode II (sliding), and Mode III (tearing). The arrows show the "
           "direction the crack faces move in each mode.",
           width_in=5.8)
add_table(
    ["Mode", "Motion", "Direction of loading", "Driving stress", "Typical test"],
    [
        ["Mode I", "Opening", "Normal to crack plane", "Tension (normal)", "DCB"],
        ["Mode II", "Sliding", "In-plane shear", "Shear", "ENF"],
        ["Mode III", "Tearing", "Out-of-plane shear", "Twist / shear", "—"],
    ],
    col_widths=[0.8, 1.2, 1.9, 1.6, 1.0],
)
para("Mode III is less commonly encountered in laminated composites than Modes I "
     "and II, but it is still important. Real cracks, and real delaminations, "
     "rarely grow under a single clean mode.")

section("2.5  Mixed-Mode Fracture")
para("In the laboratory, we deliberately design tests so that only one mode "
     "occurs — this lets us measure pure Mode I or pure Mode II properties "
     "cleanly. But real aerospace structures are nowhere near that tidy.")
para("A panel inside an aircraft is simultaneously stretched (tension), bent, "
     "twisted, and sheared by the forces of flight. A delamination buried inside "
     "it therefore experiences tension, shear, and bending all at once. The crack "
     "tip sees a combination of Mode I and Mode II (and sometimes Mode III) "
     "loading at the same time. This is called mixed-mode fracture.")
para("Mixed-mode behaviour is one of the main reasons cohesive zone models are so "
     "valuable. A single cohesive model can capture damage driven by any "
     "combination of modes using one unified framework, rather than treating each "
     "mode with separate, incompatible analyses.")
key_point("Pure modes are the building blocks we measure in the lab. Real loading "
          "is almost always mixed-mode, and cohesive zone models handle mixed-mode "
          "naturally — this is one of their greatest strengths.")

section("2.6  Why this matters for Abaqus")
para("When you define a cohesive material in Abaqus, you will specify properties "
     "for each mode: the critical energy release rates G_Ic, G_IIc, and (if "
     "needed) G_IIIc, and the cohesive strengths in each direction. Knowing what "
     "each mode means lets you interpret those inputs correctly. When your model "
     "is loaded in mixed-mode, Abaqus blends these properties using a mixed-mode "
     "criterion — a topic we revisit in Chapters 3 and 6.")
section("2.7  What you should remember")
numbered_item(1, "Mode I is opening: faces pull apart normal to the crack plane (DCB test).")
numbered_item(2, "Mode II is sliding: faces shear in-plane (ENF test).")
numbered_item(3, "Mode III is tearing: out-of-plane shear.")
numbered_item(4, "Real structures are almost always mixed-mode, combining several modes.")
numbered_item(5, "Cohesive models unify all modes, which is why they are so useful.")
page_break()

# ---------------------------------------------------------------------------
# CHAPTER 3
# ---------------------------------------------------------------------------
chapter_heading(3, "Energy Release Rate (G)",
                "The driving force behind every crack")
para("Energy release rate is one of the most important ideas in the whole of "
     "fracture mechanics, and it is the single quantity that connects the theory "
     "you are learning to the numbers you will type into Abaqus. Give this "
     "chapter your full attention — everything else builds on it.")

section("3.1  The basic idea")
para("Here is the question that starts everything: imagine a crack grows by a "
     "tiny amount. Where does the energy for that growth come from?")
para("When a crack extends, the structure can relax slightly. As it relaxes, it "
     "releases some of the elastic strain energy it has stored — energy that was "
     "pumped into it by the external load. The released energy is exactly what "
     "pays for creating the two fresh fracture surfaces.")
para("The rate at which energy is released per unit of new crack area is called "
     "the energy release rate, and it is given the symbol G (capital G).")
equation("G  =  energy released  /  new crack area created")
equation_ref("Units: J/m²  (joules per square metre)")
add_figure("fig_energy.png",
           "A cracked plate under tension. As the crack grows, the structure "
           "relaxes and releases stored elastic strain energy from the crack "
           "front — the energy release rate G.",
           width_in=5.4)
analogy("Slide a heavy box across a floor. Your pushing force does work. If the "
        "force is small, the box does not move and no work is done. If you push "
        "hard enough to overcome friction, the box slides and you spend energy. "
        "A crack behaves the same way: the available energy (G) must overcome the "
        "material's resistance (G_c) before the crack can move.")

section("3.2  Interpretation: is there enough energy?")
para("The value of G tells you whether a crack is hungry for more growth or "
     "content to stay put. The rule is simple and it is the whole game:")
callout("The growth criterion",
        "If the available energy is too small, the crack stays stable. If enough "
        "energy is available, the crack propagates.",
        bg=ANALOGY_BG, title_color=GOLD, icon="→")
para("But 'enough' is not a universal number — it depends on the material. Every "
     "material has a built-in resistance to crack growth, a kind of 'fracture "
     "strength' expressed as an energy. This resistance is called the critical "
     "energy release rate, written G_c. It is a material property, measured in "
     "the laboratory for each material and each mode.")

section("3.3  Critical energy release rate")
para("Because a crack can open in three modes, each mode has its own resistance:",
     )
bullet("G_Ic  — critical energy release rate in Mode I (opening);")
bullet("G_IIc — critical energy release rate in Mode II (sliding);")
bullet("G_IIIc — critical energy release rate in Mode III (tearing).")
para("The subscript 'c' stands for 'critical'. These values are obtained "
     "experimentally. For example, a DCB test measures G_Ic, while an ENF test "
     "measures G_IIc. In a cohesive zone model you will supply exactly these "
     "values to Abaqus, and they will govern how much energy the interface can "
     "absorb before it separates.")
key_point("G_Ic, G_IIc and G_IIIc are material properties, measured in tests, "
          "with units of J/m². They are the 'fuel tank' of your cohesive "
          "interface: once the released energy exceeds them, the interface fails.")

section("3.4  The engineering meaning")
para("Let us connect this to real decision-making. A designer wants to know "
     "whether a flaw detected in a component will grow under service loads. The "
     "calculation proceeds in two steps:")
numbered_item(1, "Compute the energy release rate G for the actual crack, load, and geometry.")
numbered_item(2, "Compare G with the material's critical value G_c.")
para("Then the result falls into one of two regions:")
add_table(
    ["Condition", "Meaning", "Outcome"],
    [
        ["G < G_c", "Released energy below the material's resistance",
         "Crack remains stable (does not grow)"],
        ["G ≥ G_c", "Released energy equals or exceeds the resistance",
         "Crack propagates (grows)"],
    ],
    col_widths=[1.0, 2.7, 2.2],
)
para("Notice how powerful this framing is: we no longer ask 'how strong is the "
     "material?' in some vague sense. We ask a precise energy question that can "
     "be computed and compared against measured data.")

section("3.5  G and the traction–separation law (a first look)")
para("In Chapter 6 we will meet the traction–separation law, which is the heart "
     "of the cohesive zone model. For now, just note the connection: the energy "
     "release rate at failure is exactly the area under the traction–separation "
     "curve. In Abaqus, when you specify the 'fracture energy' for damage "
     "evolution, you are specifying G_c — the very quantity defined in this "
     "chapter. This is a beautiful example of how theory maps directly to "
     "software input.")
section("3.6  What you should remember")
numbered_item(1, "G is the energy released per unit crack area as a crack grows.")
numbered_item(2, "G is compared with the material resistance G_c to decide stability.")
numbered_item(3, "G_c has three flavours: G_Ic, G_IIc, G_IIIc — one per mode.")
numbered_item(4, "G < G_c means stable; G ≥ G_c means the crack grows.")
numbered_item(5, "The fracture energy you enter in Abaqus is G_c, the area under the traction–separation curve.")
page_break()

# ---------------------------------------------------------------------------
# CHAPTER 4
# ---------------------------------------------------------------------------
chapter_heading(4, "Delamination in Laminated Composites",
                "The failure mode that hides beneath the surface")
para("We now zoom in on a specific and extremely important failure mode: "
     "delamination. This is the practical context in which most cohesive zone "
     "models are used, especially in aerospace composites. Understanding "
     "delamination will make every other concept in this book feel concrete.")

section("4.1  What is a laminate?")
para("A composite laminate is built up from many thin layers, called plies, that "
     "are bonded together. Each ply is a thin sheet of fibres (for example carbon "
     "or glass) held in a resin matrix. The plies are stacked at various angles — "
     "some running along the length of a part, others running across it or at 45° "
     "— and cured to form one strong, light structure.")
para("Schematically, a laminate looks like a stack:")
callout("", "Ply 1  ─────────────────────────\n"
            "Ply 2  ─────────────────────────\n"
            "Ply 3  ─────────────────────────\n"
            "Ply 4  ─────────────────────────",
        bg=GRAY_BG, title_color=NAVY, icon="")
para("The strength of the whole laminate comes from the fibres, but its integrity "
     "depends on the bonds between the plies. Those bonds are relatively weak "
     "compared with the fibres themselves — and they are exactly where "
     "delamination begins.")

section("4.2  What is delamination?")
para("Delamination is the separation of two adjacent plies. If the bond between "
     "Ply 1 and Ply 2 fails, those two layers peel apart, and a crack runs along "
     "the interface between them.")
callout("", "Ply 1  ─────────────────────────\n"
            "        ░░  CRACK  ░░\n"
            "Ply 2  ─────────────────────────",
        bg=GRAY_BG, title_color=NAVY, icon="")
para("The word 'delamination' literally means 'de-laminating' — removing the "
     "lamination, undoing the layered bond. It is a Mode I, Mode II, or "
     "mixed-mode failure depending on how the layers are being pulled or sheared "
     "apart.")
add_figure("fig_delamination.png",
           "Delamination: an impact at the surface drives a crack that runs along "
           "the interface between two plies, separating the laminate internally "
           "even though the outer surface may look intact.",
           width_in=5.6)

section("4.3  Why delamination is so dangerous")
para("Here is what makes delamination especially nasty:")
numbered_item(1, "The fibres may remain perfectly intact.", bold_lead=None)
para("Even though the plies have separated, the individual fibres are not "
     "broken. This means the damage can be completely invisible from the outside, "
     "yet the part has already lost much of its load-carrying ability.")
numbered_item(2, "Stiffness and strength drop sharply.")
para("Once layers separate, they can no longer transfer load to one another. The "
     "laminate effectively becomes a stack of weaker, thinner pieces instead of "
     "one strong unit. Bending stiffness in particular collapses.")
numbered_item(3, "The damage is hidden beneath the surface.")
para("Because the crack is internal, it may not be visible in a visual "
     "inspection. A panel can look perfect while its interior is progressively "
     "falling apart — this is why non-destructive testing (NDT) is so critical "
     "in aerospace maintenance.")

section("4.4  Common causes of delamination")
bullet("Impact damage — a tool dropped on a wing, a stone strike, or a bird "
       "strike can create internal delaminations even when the outer surface "
       "looks undamaged.")
bullet("Manufacturing defects — inconsistent curing, misplaced plies, or poor "
       "consolidation can leave weak bonds.")
bullet("Voids — trapped air or moisture inside the laminate creates weak spots "
       "where cracks can initiate.")
bullet("Fatigue — repeated loading slowly grows microcracks until they link into "
       "a delamination.")
bullet("Thermal stresses — temperature changes during curing or in service "
       "create internal stresses between plies with different orientations.")
bullet("Poor bonding — inadequate surface preparation or adhesive application "
       "leaves interfaces that are easy to separate.")
key_point("Delamination is dangerous precisely because it is a hidden, internal "
          "failure. The structure can look healthy while silently losing "
          "stiffness and strength.")

section("4.5  Why non-destructive testing (NDT) matters")
para("Because delamination hides below the surface, engineers rely on "
     "non-destructive testing methods to find it before it becomes catastrophic. "
     "Common techniques include:")
bullet("X-ray computed tomography (XCT) — builds a 3D image of the internal "
       "structure, revealing delaminations and voids.")
bullet("Ultrasonics — sends sound waves through the part; a delamination reflects "
       "or scatters them, exposing the defect.")
bullet("Thermography — uses heat to reveal defects; damaged regions conduct or "
       "retain heat differently from healthy material.")
para("NDT and fracture analysis work hand in hand: NDT finds the flaw, and "
     "fracture mechanics (via the energy release rate of Chapter 3) tells you "
     "whether that flaw is dangerous.")

section("4.6  Modelling delamination")
para("To simulate delamination in Abaqus, engineers place a cohesive interface "
     "along the plane where separation is expected — typically between the plies. "
     "The cohesive elements or cohesive contact laws there follow the "
     "traction–separation behaviour described in Chapter 6. When the local "
     "loading exceeds the interface's capacity, the cohesive model lets the plies "
     "separate, reproducing delamination realistically. This is the practical "
     "application that ties this whole book together.")
section("4.7  What you should remember")
numbered_item(1, "A laminate is a stack of bonded plies; delamination is failure of the bond between plies.")
numbered_item(2, "Delamination is dangerous because fibres may stay intact while the structure weakens — and the damage is hidden.")
numbered_item(3, "Causes include impact, manufacturing defects, voids, fatigue, thermal stress, and poor bonding.")
numbered_item(4, "NDT methods (XCT, ultrasonics, thermography) find hidden delaminations.")
numbered_item(5, "Cohesive interfaces are placed along ply interfaces to simulate delamination in Abaqus.")
page_break()

# ---------------------------------------------------------------------------
# CHAPTER 5
# ---------------------------------------------------------------------------
chapter_heading(5, "Cohesive Zone Theory",
                "Bridging fracture mechanics and finite element analysis")
para("This is the chapter where we finally connect the fracture mechanics of the "
     "early chapters to the finite element analysis you will perform in Abaqus. "
     "Cohesive zone theory is the bridge, and once you understand it, the whole "
     "landscape of this book clicks into place.")

section("5.1  The problem with classical fracture mechanics")
para("Classical fracture mechanics made a set of simplifying assumptions that "
     "are often too crude for composite materials. It imagined a perfectly sharp "
     "crack that grows instantly, all-or-nothing:")
callout("The classical picture",
        "Perfect material → perfectly sharp crack → crack grows instantly, with "
        "no warning or gradual damage.",
        bg=GRAY_BG, title_color=NAVY, icon="→")
para("Real composite interfaces do not behave this way. Before a crack "
     "completely separates an interface, a whole zone of damage develops ahead of "
     "the crack tip. The material does not fail at a single instant — it "
     "progressively softens and loses its ability to transfer load over a finite "
     "region.")
section("5.2  The cohesive zone idea")
para("The cohesive zone model replaces the 'instant, sharp crack' picture with a "
     "more realistic one. Instead of assuming a perfectly sharp crack, imagine "
     "that there is a small process zone ahead of the crack tip. Inside this "
     "zone, several things happen at once:")
bullet("the resin matrix deforms plastically;")
bullet("interfaces begin to debond;")
bullet("fibres bridge across the developing crack;")
bullet("microcracks form and link together;")
para("and the material gradually loses its ability to transfer load. In the "
     "model, this softening zone is represented by cohesive elements or cohesive "
     "interfaces that obey a traction–separation law.")
section("5.3  Physical interpretation")
para("The beauty of the cohesive zone model is that it trades a mathematically "
     "awkward singularity for a physically meaningful, finite region of damage. "
     "Instead of failure happening at a single point, damage develops "
     "progressively over a finite zone ahead of the crack tip.")
para("This mirrors how composite interfaces actually fail. The gradual softening "
     "is not a numerical trick — it is a faithful representation of the resin "
     "yielding, fibre bridging, and microcracking that occur in the real material. "
     "That is why cohesive models reproduce delamination behaviour so well.")
key_point("The cohesive zone model replaces a sharp, instant crack with a finite, "
          "progressively softening damage zone — a far more realistic picture of "
          "how composite interfaces fail.")
add_figure("fig_cz.png",
           "The cohesive zone: ahead of the crack tip sits a small process zone "
           "where the interface progressively softens — resin deforms, interfaces "
           "debond, and fibres bridge across the developing crack.",
           width_in=5.6)

section("5.4  Cohesive elements and cohesive interfaces")
para("In a finite element model, the cohesive zone must be placed somewhere. "
     "There are two main ways:")
sub("Cohesive elements")
para("These are special finite elements with near-zero thickness (or a small "
     "initial thickness) that sit between the plies. They have no bending or "
     "stretching stiffness of their own in the classic sense — their only job is "
     "to represent the interface's traction–separation behaviour. In Abaqus these "
     "are called cohesive elements, and you place a layer of them along the "
     "expected crack path.")
sub("Cohesive contact")
para("Alternatively, Abaqus can treat the interface as a contact interaction "
     "between two surfaces with a cohesive behaviour definition. This avoids "
     "meshing a separate element layer and is handy when the crack path is "
     "between existing parts.")
para("Both approaches are governed by the same physics: the traction–separation "
     "law of the next chapter.")
section("5.5  The trade-off you should appreciate")
para("A cohesive zone model is not free. It requires you to know the cohesive "
     "properties (strength and fracture energy) and to mesh the expected crack "
     "path carefully. But the payoff is enormous: you get a physically grounded, "
     "grid-independent-ish description of crack growth that handles mixed-mode "
     "loading, crack initiation, and propagation all in one framework. For "
     "delamination in composites, this is usually the best tool available.")
section("5.6  What you should remember")
numbered_item(1, "Classical fracture mechanics assumed sharp, instant cracks — too crude for composites.")
numbered_item(2, "The cohesive zone model assumes a finite, progressively softening process zone ahead of the crack tip.")
numbered_item(3, "This zone captures resin deformation, debonding, fibre bridging, and microcracking.")
numbered_item(4, "It is implemented with cohesive elements or cohesive contact.")
numbered_item(5, "The model avoids the singularity and matches how composite interfaces really fail.")
page_break()

# ---------------------------------------------------------------------------
# CHAPTER 6
# ---------------------------------------------------------------------------
chapter_heading(6, "The Traction–Separation Law",
                "The heart of every cohesive model")
para("If there is one chapter you must read twice, it is this one. The "
     "traction–separation law is the mathematical engine of the cohesive zone "
     "model. Every parameter you will set in Abaqus's cohesive material "
     "definition comes from this law. We will build it up slowly and completely.")

section("6.1  Two fundamental quantities: traction and separation")
para("Before the law, we need its two variables.")
sub("Traction (t)")
para("Traction is simply stress acting across the interface. When you pull two "
     "bonded plies apart, a stress develops across the interface resisting that "
     "pull; that stress is the traction. It has units of pressure (Pa, or more "
     "practically MPa). The traction can act in any of the three mode directions "
     "we met in Chapter 2 — normal (Mode I) or shear (Modes II and III).")
sub("Separation (δ)")
para("Separation is the relative displacement between the two bonded surfaces. "
     "It measures how far the two faces of the interface have moved apart or slid "
     "past one another. It has units of length (mm in most Abaqus models). Before "
     "damage, this separation is essentially elastic — it stretches and springs "
     "back.")
key_point("Traction is the stress across the interface; separation is how far the "
          "two faces have moved. The traction–separation law is simply the curve "
          "that connects these two quantities.")

section("6.2  The relationship between traction and separation")
para("Now we describe what happens as you gradually load the interface. The "
     "behaviour falls into a clear sequence of three phases.")
sub("Phase 1 — Elastic loading (the ascending part)")
para("Initially, traction increases approximately linearly with separation. The "
     "interface behaves elastically: pull a little, get a little resistance; let "
     "go, and it springs back to its original state. This is the straight, "
     "rising line at the start of the curve. Its slope is the initial stiffness "
     "(see §6.4).")
sub("Phase 2 — Damage initiation (the peak)")
para("As loading continues, the traction reaches a maximum value. This maximum "
     "is the cohesive strength of the interface — the highest stress the bond "
     "can withstand. Once this peak is reached, damage initiates: the interface "
     "begins to permanently degrade, and it will no longer return to its "
     "original state even if the load is removed.")
sub("Phase 3 — Damage evolution (the descending part)")
para("Beyond the peak, traction decreases as separation increases. The interface "
     "is progressively softening. Eventually, traction falls to zero, and at "
     "that point the two surfaces are completely separated — the interface has "
     "failed and the crack has fully formed.")
para("This whole curve — up, peak, down to zero — is the traction–separation "
     "law, and it is shown below.")

section("6.3  A visual picture of the curve")
callout("", "Traction (t)  ↑\n"
            "              │       /\\\n"
            "              │      /  \\\n"
            "  cohesive    │     /    \\   <— descending (damage evolution)\n"
            "  strength    │    /      \\\n"
            "   peak  -----·---/        \\---·\n"
            "              │  /            \\\n"
            "              │ /              \\\n"
            "              │/  elastic       \\\n"
            "              └────────────────────→ Separation (δ)\n"
            "             0        damage     full\n"
            "                      init        failure",
        bg=GRAY_BG, title_color=NAVY, icon="")
add_figure("fig_tscurve.png",
           "The traction–separation law. The shaded triangle under the curve is "
           "the fracture energy G_c — the energy required to fully separate the "
           "interface.",
           width_in=5.4)
para("Reading the curve:")
bullet("The ascending (rising) portion is elastic loading — no damage yet.")
bullet("The peak corresponds to the cohesive strength — damage initiates here.")
bullet("The descending portion is damage evolution — the interface softens.")
bullet("The point where traction reaches zero is complete failure of the interface.")

section("6.4  The three governing parameters")
para("Every cohesive model is controlled by three families of parameters. Let us "
     "explore each one carefully, because these are exactly the inputs you will "
     "provide to Abaqus.")
sub("1.  Initial stiffness")
para("The initial stiffness is the slope of the elastic (ascending) part of the "
     "curve. It controls how much resistance the interface offers for a given "
     "small separation before any damage. Think of it as the 'springiness' of the "
     "undamaged bond.")
para("Setting this value requires judgment:")
bullet("If it is too low, the interface appears unrealistically compliant — the "
       "structure seems too flexible, and results deviate from reality.", bold_lead="Too low → ")
bullet("If it is too high, numerical convergence problems appear — Abaqus has to "
       "work much harder, and the solver may struggle to find a solution.", bold_lead="Too high → ")
para("In practice, a common approach is to use a high stiffness (often related to "
     "the ply elastic modulus divided by the interface thickness) so the interface "
     "behaves like a thin, stiff bond before damage — while keeping it low enough "
     "to converge.")
sub("2.  Cohesive strength")
para("The cohesive strength is the maximum traction the interface can withstand. "
     "It is the height of the peak of the curve, and it determines when damage "
     "initiates. If the local traction reaches this value, the interface begins "
     "to soften. This value is often obtained from tests or estimated from the "
     "resin's strength.")
sub("3.  Fracture energy")
para("The fracture energy is the area under the traction–separation curve. "
     "Because the area under a force-versus-displacement curve is an energy, this "
     "area equals the total energy required to fully separate the interface — "
     "which, as we saw in Chapter 3, is exactly the critical energy release rate "
     "G_c. This is the quantity that governs damage evolution.")
key_point("Initial stiffness sets the elastic slope, cohesive strength sets the "
          "peak (when damage starts), and fracture energy (= G_c) sets the area "
          "under the curve (how much energy is needed to fully fail the interface). "
          "These three define the whole law.")

section("6.5  Damage initiation criteria")
para("We need a precise rule for deciding when damage begins — that is, when the "
     "behaviour stops being elastic and starts degrading. Abaqus offers several "
     "criteria; the two most common are:")
bullet("The crack initiates when the stress in any direction reaches its "
       "cohesive strength. Simple and direct, but it does not combine the modes.",
       bold_lead="Maximum stress criterion — ")
bullet("The crack initiates when a combination of the stress ratios in all "
       "directions reaches 1. This handles mixed-mode loading, which is why it "
       "is often preferred for realistic structures.",
       bold_lead="Quadratic nominal stress criterion — ")
para("The quadratic nominal stress criterion is written in the form of an "
     "interaction equation: the sum of the squared ratios of each traction "
     "component to its strength equals 1 at initiation. When the left-hand side "
     "reaches 1, damage begins. This elegantly handles the mixed-mode situation "
     "from Chapter 2.")
add_figure("fig_mixed.png",
           "The mixed-mode initiation criterion. Each axis is the traction in a "
           "mode normalised by its cohesive strength. Damage initiates when the "
           "interaction curve (here a quarter-circle) is reached; combinations "
           "inside the curve are still elastic.",
           width_in=4.6)
section("6.6  Damage evolution (softening laws)")
para("Once damage has initiated, the interface stiffness gradually degrades until "
     "complete separation. Abaqus lets you choose how the traction decreases on "
     "the descending part of the curve. The main choices are:")
sub("Linear softening")
para("The traction falls in a straight line from the peak to zero. Simple, "
     "robust, and very commonly used.")
sub("Exponential softening")
para("The traction decays exponentially after the peak. This can represent "
     "materials whose resistance drops quickly at first then trails off, and it "
     "can improve stability in some cases.")
sub("Bilinear softening")
para("A two-line approximation that captures an initial steep drop followed by a "
     "gentler tail. It gives a more flexible shape while staying simple.")
para("Which softening law you choose changes the shape of the descending curve — "
     "but as long as the area under the curve (the fracture energy G_c) is the "
     "same, the total energy consumed at failure is the same. The shape mainly "
     "affects how the failure proceeds and how easily the solver converges.")
add_figure("fig_softening.png",
           "The three softening laws compared: linear (a), exponential (b), and "
           "bilinear (c). All rise to the same cohesive strength peak and all "
           "enclose the same fracture energy G_c, but the traction falls in "
           "different ways after damage initiates.",
           width_in=5.6)
section("6.7  How the parameters appear in Abaqus")
para("When you define a cohesive material in Abaqus, you will set:")
bullet("Elastic properties — the initial stiffness (the slope).")
bullet("Damage initiation — the criterion (e.g. quadratic nominal stress) and the "
       "cohesive strengths (e.g. normal and shear strengths).")
bullet("Damage evolution — the fracture energy (G_c) and the softening law "
       "(linear, exponential, bilinear).")
para("Now, instead of filling in random numbers, you will recognise exactly what "
     "each field represents: the slope of the elastic line, the height of the "
     "peak, the area under the curve, and the shape of the descent.")
section("6.8  What you should remember")
numbered_item(1, "Traction is the stress across the interface; separation is the relative displacement.")
numbered_item(2, "The law has three phases: elastic rise, peak (initiation), then softening to zero (failure).")
numbered_item(3, "Initial stiffness = slope; cohesive strength = peak height; fracture energy = area = G_c.")
numbered_item(4, "Damage initiation uses criteria such as maximum stress or quadratic nominal stress.")
numbered_item(5, "Damage evolution uses softening laws: linear, exponential, or bilinear.")
page_break()

# ---------------------------------------------------------------------------
# CHAPTER 7
# ---------------------------------------------------------------------------
chapter_heading(7, "Putting It All Together",
                "How the concepts connect — and how they map to Abaqus")
para("Now that we have every piece, let us assemble the full picture. This "
     "chapter traces one continuous chain from an external load all the way to "
     "structural failure, and then shows you exactly where each concept lives in "
     "the Abaqus interface.")

section("7.1  The complete chain of events")
para("Everything in this book can be compressed into a single logical flow:")
callout("", "External load\n"
            "   │  (a force pushes or pulls the structure)\n"
            "   ▼\n"
            "Stress develops\n"
            "   │  (load spreads through the material)\n"
            "   ▼\n"
            "Crack tip stores elastic energy\n"
            "   │  (energy concentrates at the flaw)\n"
            "   ▼\n"
            "Energy Release Rate (G)\n"
            "   │  (energy available per unit crack area)\n"
            "   ▼\n"
            "Is G ≥ G_c ?\n"
            "   │  no → crack stays stable, analysis ends\n"
            "   │  yes ↓\n"
            "   ▼\n"
            "Damage initiates\n"
            "   │  (traction reaches cohesive strength)\n"
            "   ▼\n"
            "Cohesive Zone forms\n"
            "   │  (finite softening region ahead of the tip)\n"
            "   ▼\n"
            "Traction–Separation Law governs damage evolution\n"
            "   │  (traction falls, energy released)\n"
            "   ▼\n"
            "Crack propagates\n"
            "   │  (interface separates further)\n"
            "   ▼\n"
            "Delamination grows\n"
            "   │  (plies separate along the interface)\n"
            "   ▼\n"
            "Structural failure",
        bg=CALLOUT_BG, title_color=NAVY, icon="→")
add_figure("fig_chain.png",
           "The complete chain of events, from external load to structural "
           "failure. This is the sequence Abaqus effectively solves internally "
           "when you run a cohesive zone model.",
           width_in=5.4)
para("Read this chain from top to bottom and you have essentially re-derived the "
     "logic that Abaqus executes internally when you run a cohesive zone model. "
     "The software is not doing anything mysterious — it is solving precisely this "
     "sequence of physical events, step by step, element by element.")

section("7.2  Mapping the theory to Abaqus")
para("Let us make the connection explicit. Every concept you have learned "
     "corresponds to a concrete setting in the Abaqus interface:")
add_table(
    ["Theory concept", "Abaqus location", "What you enter"],
    [
        ["Modes I, II, III", "Material → Cohesive",
         "Strength & fracture energy in each direction"],
        ["Cohesive strength", "Damage → Initiation",
         "Maximum stress (or interaction) values"],
        ["Mixed-mode initiation", "Damage → Initiation",
         "Choose quadratic nominal stress criterion"],
        ["Fracture energy G_c", "Damage → Evolution",
         "Type: Energy; the G_c value(s)"],
        ["Softening law", "Damage → Evolution",
         "Choose linear / exponential / bilinear"],
        ["Initial stiffness", "Elastic", "The elastic traction–separation moduli"],
        ["Cohesive interface location", "Mesh / Interaction",
         "Cohesive elements or cohesive contact"],
    ],
    col_widths=[1.9, 2.0, 2.2],
)
key_point("When you understand the progression in §7.1, the software settings — "
          "cohesive material properties, damage initiation criteria, and damage "
          "evolution laws — become intuitive, because you know the physical "
          "phenomena they represent rather than just picking options from a menu.")

section("7.3  A worked way of thinking about any cohesive input")
para("Whenever you are faced with a cohesive parameter you do not recognise, ask "
     "yourself these three questions:")
numbered_item(1, "Which mode (I, II, or III) does this direction represent?", bold_lead="Where in the physics? ")
numbered_item(2, "Does this control the elastic slope, the peak, or the area under the curve?", bold_lead="Which part of the law? ")
numbered_item(3, "Does it decide when damage starts (initiation) or how it proceeds (evolution)?", bold_lead="Initiation or evolution? ")
para("Answer those three questions and you will be able to reason about any "
     "cohesive model, in Abaqus or any other finite element package.")

section("7.4  The mindset of an analyst")
para("Two mindsets separate a technician from an engineer. A technician knows "
     "which buttons to press. An engineer knows why the buttons do what they do, "
     "and therefore when the defaults are wrong. By working through this book you "
     "have moved decisively toward the second mindset. You can now look at a "
     "cohesive zone model and see the physics: a real interface, with an elastic "
     "stiffness, a strength, a fracture energy, and a softening law — loaded in "
     "one or more modes until it separates.")
para("This is the difference between reproducing results and trusting them.")
section("7.5  Final summary of the whole book")
add_table(
    ["Chapter", "One-line takeaway"],
    [
        ["1. Fracture Mechanics", "Cracks grow when there is enough driving energy; strength alone can mislead."],
        ["2. Modes I–III", "Cracks open (I), slide (II), or tear (III); real loading is mixed-mode."],
        ["3. Energy Release Rate", "G is the energy per crack area; it is compared with the material's G_c."],
        ["4. Delamination", "Ply separation is hidden and dangerous; NDT finds it, cohesive models simulate it."],
        ["5. Cohesive Zone Theory", "Replace the sharp instant crack with a finite, softening damage zone."],
        ["6. Traction–Separation Law", "Elastic slope, cohesive strength, and fracture energy define the interface."],
        ["7. Putting It Together", "From load to failure is one chain; theory maps directly to Abaqus."],
        ["8. Worked Example", "A DCB simulation ties every concept together in a concrete model."],
    ],
    col_widths=[2.0, 4.1],
)
page_break()

# ---------------------------------------------------------------------------
# GLOSSARY
# ---------------------------------------------------------------------------
chapter_heading(8, "A Worked Abaqus Example",
                "Tying everything together with a DCB simulation")

section("8.1  Setting the scene")
para("So far we have built up the theory piece by piece. Now let us see how it all "
     "comes together in an actual Abaqus model. We will use the classic example "
     "that keeps returning throughout this book: a Double Cantilever Beam (DCB) "
     "test for a carbon-fibre/epoxy composite. This is the most common way to "
     "measure Mode I delamination resistance, and it makes a perfect worked "
     "example because every concept we have covered appears in it.")
key_point("The DCB test is the 'hello world' of cohesive zone modelling. If you "
          "can build and interpret one DCB model, you understand the whole "
          "method.")

section("8.2  What we are simulating")
para("Our specimen is a long, thin beam made of two layers bonded together. At "
     "one end there is a starter crack — the pre-existing delamination. During "
     "the test we pull the two arms apart at the cracked end, opening the beam "
     "like a book. As we pull, the crack grows along the bonded mid-plane, and we "
     "record the applied load and the opening displacement.")
add_figure("fig_abaqus_dcb.png",
           "The meshed DCB model in Abaqus: two arms of composite material, a "
           "starter crack at the left end, a thin layer of cohesive elements "
           "along the mid-plane, and load arrows prying the right-hand end "
           "apart.",
           width_in=5.6)
para("The purpose of the simulation is to reproduce this test: we want the model "
     "to predict the load–displacement behaviour and the growth of the "
     "delamination, given only the material properties of the composite and the "
     "cohesive interface.")

section("8.3  Building the model — the steps")
para("Setting up the model in Abaqus follows a familiar sequence. Let us walk "
     "through it, connecting each step to the theory you now know.")
numbered_item(1, "Create the geometry — model the two composite arms as solid "
                 "or shell regions, with the two halves separated by the mid-plane "
                 "where delamination will occur.", bold_lead="Geometry. ")
numbered_item(2, "Define the composite material — give the carbon/epoxy its "
                 "elastic properties (modulus, Poisson's ratio) as you would any "
                 "material.", bold_lead="Material. ")
numbered_item(3, "Place the cohesive interface — insert a layer of cohesive "
                 "elements (or define cohesive contact) along the mid-plane, "
                 "except in the starter-crack region.", bold_lead="Cohesive interface. ")
numbered_item(4, "Define the cohesive material — set the initial stiffness, the "
                 "cohesive strengths, and the fracture energy G_Ic, plus the "
                 "damage initiation criterion and softening law.", bold_lead="Cohesive properties. ")
numbered_item(5, "Mesh the parts — the cohesive elements need a fine mesh along "
                 "the crack path so the damage zone is resolved.", bold_lead="Mesh. ")
numbered_item(6, "Apply loads and boundary conditions — fix one point and apply "
                 "the opening displacement at the cracked end.", bold_lead="Loading. ")
numbered_item(7, "Run the job and examine results — plot load against opening "
                 "displacement and watch the crack grow.", bold_lead="Solve & post-process. ")

section("8.4  Where the cohesive elements live")
para("The most important modelling choice is where the crack is allowed to grow. "
     "In a cohesive zone model you must place the interface along the expected "
     "crack path in advance. In the DCB specimen that path is the mid-plane "
     "between the two arms.")
add_figure("fig_cohesive_mesh.png",
           "A close-up of the cohesive element layer sandwiched between the two "
           "plies. Each small rectangular element carries the traction–separation "
           "law; when the local traction exceeds the cohesive strength, the "
           "element softens and separates, growing the crack.",
           width_in=5.6)
para("Notice that the cohesive elements are a distinct layer with near-zero "
     "thickness. They are not there to carry bending — they exist purely to model "
     "the bond. Every one of them is governed by the traction–separation law of "
     "Chapter 6: an elastic rise, a peak at the cohesive strength, and a "
     "softening descent to zero traction governed by the fracture energy.")

section("8.5  The cohesive material definition in Abaqus")
para("When you define the cohesive material, you translate the theory into "
     "inputs. Concretely:")
bullet("Elastic type: traction–separation, with the initial stiffness in the "
       "normal and shear directions (the slope of the ascending line).")
bullet("Damage initiation: quadratic nominal stress criterion, with the normal "
       "and shear cohesive strengths (the height of the peak).")
bullet("Damage evolution: type = energy, with G_Ic as the fracture energy (the "
       "area under the curve), and a softening law — linear is a good default.")
key_point("Every number you type maps to a concept in Chapter 6: stiffness → "
          "elastic slope, strength → peak height, G_Ic → area under the curve, "
          "softening law → shape of the descent.")

section("8.6  Interpreting the results")
para("When the job finishes, the most telling result is the load–displacement "
     "curve, the same one measured in the physical test.")
add_figure("fig_crack_growth.png",
           "The load–opening curve from the DCB simulation. The load rises as the "
           "beam bends elastically, then drops sharply as the delamination "
           "initiates and the crack starts to grow; further stable growth appears "
           "as the jagged descending region.",
           width_in=5.4)
para("Reading this curve with the theory in mind:")
bullet("The rising portion is the elastic behaviour of the two beams — the "
       "interface is still intact.", bold_lead="Rise — ")
bullet("The peak is where the traction at the crack tip reaches the cohesive "
       "strength and damage initiates (G reaches G_Ic).", bold_lead="Peak — ")
bullet("The sharp drop is the crack propagating — energy is being released as "
       "the cohesive elements soften and separate.", bold_lead="Drop — ")
para("If you had made the interface too stiff, too weak, or given it the wrong "
     "fracture energy, this curve would look wrong — too brittle, too soft, or "
     "non-convergent. Knowing the physics lets you diagnose and fix it.")

section("8.7  Common modelling mistakes (and how to avoid them)")
warning("Set the initial stiffness too high and the solver may struggle to "
        "converge or show spurious oscillations. Set it too low and the model "
        "becomes unrealistically compliant. Use a sensible value related to the "
        "ply modulus and keep the mesh fine along the crack path.")
warning("If the crack jumps instantly through the whole interface, your mesh is "
        "probably too coarse or the fracture energy is set too low. Resolve the "
        "cohesive zone with enough elements.")
warning("If the model never initiates damage even under high load, check the "
        "cohesive strength values and the damage initiation criterion — they may "
        "be far too high for the applied loading.")

section("8.8  What you should remember")
numbered_item(1, "A DCB model is a concrete application of every concept in this book.")
numbered_item(2, "Place cohesive elements (or contact) exactly along the expected crack path.")
numbered_item(3, "Cohesive inputs map to theory: stiffness, strength, fracture energy, softening law.")
numbered_item(4, "The load–displacement curve reveals damage initiation and crack growth.")
numbered_item(5, "Most modelling problems trace back to mesh resolution or a mis-set cohesive property.")

# ---------------------------------------------------------------------------
# GLOSSARY
# ---------------------------------------------------------------------------
chapter_heading("", "Glossary of Key Terms", "Quick reference")
glossary = [
    ("Cohesive element", "A finite element that represents the bonding interface between two surfaces, obeying a traction–separation law."),
    ("Cohesive strength", "The maximum traction an interface can withstand before damage initiates."),
    ("Critical energy release rate (G_c)", "The energy per unit area required to grow a crack; a material property (G_Ic, G_IIc, G_IIIc)."),
    ("Delamination", "Separation of adjacent plies in a laminated composite, typically a hidden internal failure."),
    ("Energy release rate (G)", "The elastic energy released per unit of new crack area as a crack grows."),
    ("Fracture energy", "The area under the traction–separation curve; equals the critical energy release rate."),
    ("Fracture mechanics", "The study of how cracks initiate, grow, and cause structural failure."),
    ("Initial stiffness", "The slope of the elastic portion of the traction–separation curve; the springiness of the undamaged bond."),
    ("Mixed-mode fracture", "Fracture driven by more than one mode simultaneously, typical of real loading."),
    ("Mode I / II / III", "Opening, sliding, and tearing modes of crack loading, respectively."),
    ("Separation (δ)", "The relative displacement between the two faces of a bonded interface."),
    ("Softening law", "The rule describing how traction decreases after damage initiation (linear, exponential, bilinear)."),
    ("Singularity", "The mathematical point at a sharp crack tip where classical elasticity predicts infinite stress."),
    ("Traction (t)", "The stress acting across an interface; the force per unit area resisting separation."),
    ("Traction–separation law", "The constitutive relationship linking interface traction to separation, governing cohesive damage."),
]
for term, definition in glossary:
    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(6)
    p.paragraph_format.left_indent = Inches(0.0)
    add_run(p, term + "  —  ", bold=True, color=TEAL)
    add_run(p, definition, size=10.5)
page_break()

# ---------------------------------------------------------------------------
# REVIEW QUESTIONS
# ---------------------------------------------------------------------------
chapter_heading("", "Review & Self-Check Questions",
                "Test yourself before moving on")
para("Try to answer these from memory before checking the book. Working through "
     "them out loud or in writing will fix the concepts far more firmly than "
     "re-reading.")
questions = [
    "Why is classical stress analysis insufficient when a crack is present?",
    "Describe the three modes of fracture and give a typical test for each.",
    "Define energy release rate G and state its units.",
    "What is the difference between G and G_c, and what does each condition G < G_c and G ≥ G_c mean?",
    "Why is delamination particularly dangerous in composites?",
    "What are the three phases of a traction–separation curve?",
    "Name and explain the three key parameters of a cohesive model.",
    "What does the area under the traction–separation curve equal, and why?",
    "Explain the difference between damage initiation and damage evolution.",
    "Describe how the concepts map to specific settings in Abaqus.",
    "In a DCB model, where do you place the cohesive elements and why?",
    "If a DCB load–displacement curve drops instantly with no stable growth, what is probably wrong and how would you fix it?",
    "Why is mesh resolution along the crack path critical for a cohesive zone model?",
]
for i, q in enumerate(questions, 1):
    numbered_item(i, q)
doc.add_paragraph()
para("If you can answer all thirteen confidently, you are ready to start setting up "
     "cohesive zone models in Abaqus with a genuine understanding of what you "
     "are doing — and to debug them when they go wrong.", italic=True)

# ---------------------------------------------------------------------------
# Save
# ---------------------------------------------------------------------------
out = "Cohesive_Zone_Modeling_Guide.docx"
doc.save(out)
print("Saved:", out)
