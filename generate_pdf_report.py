import os
import sys
from pathlib import Path
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, HRFlowable
)
from reportlab.pdfgen import canvas


class NumberedCanvas(canvas.Canvas):
    """
    Two-pass canvas to dynamically compute and print total page count in footers.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, page_count):
        # Don't draw headers/footers on the cover page (page 1)
        if self._pageNumber == 1:
            return

        self.saveState()
        self.setFont("Helvetica-Bold", 8)
        self.setFillColor(colors.HexColor("#0ea5e9"))
        self.drawString(54, 11 * inch - 36, "INVESTTECH | AI-POWERED INVESTOR INTELLIGENCE PLATFORM")
        
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#64748b"))
        self.drawRightString(8.5 * inch - 54, 11 * inch - 36, "COMPREHENSIVE TECHNICAL & FINANCIAL ARCHITECTURE")

        # Top rule
        self.setStrokeColor(colors.HexColor("#cbd5e1"))
        self.setLineWidth(0.75)
        self.line(54, 11 * inch - 42, 8.5 * inch - 54, 11 * inch - 42)

        # Bottom rule
        self.line(54, 48, 8.5 * inch - 54, 48)

        # Footer
        self.setFont("Helvetica", 8)
        self.drawString(54, 34, "CONFIDENTIAL & PROPRIETARY — ENTERPRISE FINANCIAL DOCUMENT INTELLIGENCE")
        page_str = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(8.5 * inch - 54, 34, page_str)
        self.restoreState()


def build_pdf(output_path: str):
    doc = SimpleDocTemplate(
        output_path,
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=54,
        bottomMargin=54
    )

    styles = getSampleStyleSheet()

    # Custom Color Palette
    PRIMARY = colors.HexColor("#0f172a")    # Deep Navy
    SECONDARY = colors.HexColor("#0284c7")  # Deep Blue
    ACCENT = colors.HexColor("#0ea5e9")     # Cyan / Sky
    SUCCESS = colors.HexColor("#059669")    # Emerald
    WARNING = colors.HexColor("#d97706")    # Amber
    DANGER = colors.HexColor("#dc2626")     # Crimson
    TEXT_MAIN = colors.HexColor("#1e293b")  # Dark Slate
    TEXT_MUTED = colors.HexColor("#475569") # Muted Slate
    BG_LIGHT = colors.HexColor("#f8fafc")   # Off white
    BG_CARD = colors.HexColor("#f1f5f9")    # Slate card

    # Typography Styles
    title_style = ParagraphStyle(
        'CoverTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=28,
        leading=34,
        textColor=PRIMARY,
        alignment=0,
        spaceAfter=12
    )

    subtitle_style = ParagraphStyle(
        'CoverSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=13,
        leading=18,
        textColor=SECONDARY,
        spaceAfter=24
    )

    h1_style = ParagraphStyle(
        'Heading1_Custom',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=18,
        leading=22,
        textColor=PRIMARY,
        spaceBefore=16,
        spaceAfter=8,
        keepWithNext=True
    )

    h2_style = ParagraphStyle(
        'Heading2_Custom',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=13,
        leading=16,
        textColor=SECONDARY,
        spaceBefore=12,
        spaceAfter=6,
        keepWithNext=True
    )

    body_style = ParagraphStyle(
        'Body_Custom',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9.5,
        leading=14,
        textColor=TEXT_MAIN,
        spaceAfter=8
    )

    body_bold = ParagraphStyle(
        'Body_Bold_Custom',
        parent=body_style,
        fontName='Helvetica-Bold'
    )

    bullet_style = ParagraphStyle(
        'Bullet_Custom',
        parent=body_style,
        leftIndent=14,
        firstLineIndent=-10,
        spaceAfter=4
    )

    callout_style = ParagraphStyle(
        'CalloutText',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=13.5,
        textColor=PRIMARY
    )

    code_style = ParagraphStyle(
        'CodeStyle',
        parent=styles['Normal'],
        fontName='Courier',
        fontSize=8,
        leading=11,
        textColor=colors.HexColor("#0f172a")
    )

    th_style = ParagraphStyle(
        'TableHeader',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8.5,
        leading=11,
        textColor=colors.white,
        alignment=1
    )

    td_style = ParagraphStyle(
        'TableCell',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8,
        leading=11,
        textColor=TEXT_MAIN
    )

    td_center = ParagraphStyle(
        'TableCellCenter',
        parent=td_style,
        alignment=1
    )

    td_bold = ParagraphStyle(
        'TableCellBold',
        parent=td_style,
        fontName='Helvetica-Bold'
    )

    story = []

    # =========================================================================
    # COVER PAGE
    # =========================================================================
    story.append(Spacer(1, 40))
    # Brand Pill
    pill_table = Table(
        [[Paragraph("<b>INVESTTECH ENTERPRISE PLATFORM</b>", ParagraphStyle('Pill', fontName='Helvetica-Bold', fontSize=8, leading=10, textColor=ACCENT))]],
        colWidths=[200]
    )
    pill_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#e0f2fe")),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor("#bae6fd")),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(pill_table)
    story.append(Spacer(1, 14))

    story.append(Paragraph("AI-Powered Investor Intelligence Platform", title_style))
    story.append(Paragraph("End-to-End Technical Architecture, Financial KPI Extraction, Real-Time Streaming RAG, and Deployment Specification", subtitle_style))
    
    story.append(HRFlowable(width="100%", thickness=2, color=SECONDARY, spaceAfter=24, spaceBefore=0))

    # Executive Metadata Box
    meta_data = [
        [Paragraph("<b>Document Version:</b>", body_style), Paragraph("v2.4.0 (Production Architecture)", body_style)],
        [Paragraph("<b>Target Audience:</b>", body_style), Paragraph("Executive Stakeholders, Quantitative Analysts, Platform Architects", body_style)],
        [Paragraph("<b>Underlying LLM Engine:</b>", body_style), Paragraph("Azure OpenAI GPT-4o & Local Financial Analyst Reasoning Engine", body_style)],
        [Paragraph("<b>Vector Search:</b>", body_style), Paragraph("Azure AI Search (HNSW Indexing) & Semantic Chunking", body_style)],
        [Paragraph("<b>Relational Database:</b>", body_style), Paragraph("Azure PostgreSQL Flexible Server (Auto SQLite Fallback)", body_style)],
        [Paragraph("<b>Real-Time Protocol:</b>", body_style), Paragraph("Bidirectional WebSockets with Server-Sent Events (SSE) Fallback", body_style)],
        [Paragraph("<b>Containerization & Cloud:</b>", body_style), Paragraph("Docker & Azure Kubernetes Service (AKS)", body_style)],
        [Paragraph("<b>Ingested Benchmark Filings:</b>", body_style), Paragraph("Apple Inc. (AAPL), Microsoft Corp. (MSFT), Tesla Inc. (TSLA) FY2024 Form 10-K", body_style)],
    ]
    meta_table = Table(meta_data, colWidths=[160, 344])
    meta_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), BG_CARD),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor("#cbd5e1")),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('LEFTPADDING', (0, 0), (-1, -1), 10),
        ('RIGHTPADDING', (0, 0), (-1, -1), 10),
    ]))
    story.append(meta_table)

    story.append(Spacer(1, 30))

    # Executive Overview Callout
    exec_summary_p = Paragraph(
        "<b>Executive Summary:</b> Modern corporate annual reports (Form 10-K) exceed 100–300 pages of dense disclosures, making rapid cross-company benchmarking and risk identification challenging for investment committees. "
        "The InvestTech platform automates the end-to-end extraction lifecycle: turning raw PDF filings into Markdown representations, executing semantic text chunking, generating vector embeddings, extracting audited quantitative KPIs via validated Pydantic schemas, and delivering real-time interactive equity research streaming via WebSockets.",
        callout_style
    )
    exec_summary_table = Table([[exec_summary_p]], colWidths=[504])
    exec_summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#eff6ff")),
        ('BOX', (0, 0), (-1, -1), 1.5, colors.HexColor("#3b82f6")),
        ('TOPPADDING', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
        ('LEFTPADDING', (0, 0), (-1, -1), 12),
        ('RIGHTPADDING', (0, 0), (-1, -1), 12),
    ]))
    story.append(exec_summary_table)

    story.append(PageBreak())

    # =========================================================================
    # SECTION 1: SYSTEM ARCHITECTURE & CORE WORKFLOW
    # =========================================================================
    story.append(Paragraph("1. System Architecture & Dual-Storage Model", h1_style))
    story.append(Paragraph(
        "The platform utilizes an asynchronous, decoupled micro-architecture combining a <b>Dual-Storage Model</b>. "
        "Financial data requires two distinct access patterns: precise, structured numbers for comparative balance sheets and high-dimensional embeddings for qualitative semantic retrieval.",
        body_style
    ))

    # Architecture Overview Table
    arch_data = [
        [Paragraph("Pillar", th_style), Paragraph("Technology", th_style), Paragraph("Component Function & Responsibility", th_style)],
        [
            Paragraph("<b>Ingestion Engine</b>", td_bold),
            Paragraph("PyMuPDF4LLM & LangChain", td_style),
            Paragraph("Converts 10-K PDFs to Markdown, preserving tabular schedules and section hierarchies. Applies semantic chunking based on natural thematic shifts.", td_style)
        ],
        [
            Paragraph("<b>Vector Database</b>", td_bold),
            Paragraph("Azure AI Search / HNSW", td_style),
            Paragraph("Indexes 1536-dimensional Ada-002 embeddings with metadata filtering (company, year, source_file) for semantic paragraph retrieval.", td_style)
        ],
        [
            Paragraph("<b>Relational Store</b>", td_bold),
            Paragraph("Azure PostgreSQL / SQLite", td_style),
            Paragraph("Stores structured numerical KPIs in <code>financial_metrics</code> table. Uses SQLAlchemy engine with automatic local SQLite fallback.", td_style)
        ],
        [
            Paragraph("<b>RAG & Extraction</b>", td_bold),
            Paragraph("Azure OpenAI GPT-4o", td_style),
            Paragraph("Extracts certified KPIs via Pydantic model validation. Powers conversational analyst with retrieved filing context.", td_style)
        ],
        [
            Paragraph("<b>Real-Time Streaming</b>", td_bold),
            Paragraph("WebSockets & Starlette SSE", td_style),
            Paragraph("Low-latency token streaming, status signaling, cancellation/stop interruption, and ping-pong connection keep-alives.", td_style)
        ],
        [
            Paragraph("<b>Web Presentation</b>", td_bold),
            Paragraph("FastAPI, Jinja2 & Modern CSS", td_style),
            Paragraph("Executive comparison KPI cards with dynamic bar ratios, qualitative deep-dive inspector, and real-time streaming analyst interface.", td_style)
        ]
    ]
    t_arch = Table(arch_data, colWidths=[90, 110, 304])
    t_arch.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), PRIMARY),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor("#94a3b8")),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, BG_LIGHT])
    ]))
    story.append(t_arch)
    story.append(Spacer(1, 14))

    # End-to-end Pipeline Flow
    story.append(Paragraph("2. End-to-End Data Lifecycle & Processing Steps", h2_style))
    steps = [
        "<b>Step 1 — Document Ingestion:</b> PDF reports uploaded through <code>/api/upload</code> or directory scan are stored in <code>data/raw_pdfs/</code>. Filename metadata is extracted (e.g., <code>2024_Apple.pdf</code> -> company: Apple, year: 2024).",
        "<b>Step 2 — Structural Markdown Parsing:</b> <code>PDFToMarkdownConverter</code> parses tables into GitHub-flavored Markdown tables and extracts headers, saving the resulting document to <code>data/markdown/</code>.",
        "<b>Step 3 — Semantic Chunking:</b> <code>chunk_markdown()</code> splits markdown documents at natural semantic shift boundaries, preventing cutoffs of financial statement line items.",
        "<b>Step 4 — Vector Store Ingestion:</b> Chunks are converted to embeddings and pushed to Azure AI Search with search attributes (<code>company</code>, <code>year</code>, <code>source_file</code>).",
        "<b>Step 5 — Automated KPI Extraction:</b> <code>kpi_extractor_rag.py</code> executes targeted RAG queries against income statements and balance sheets, validating data into the <code>FinancialMetrics</code> Pydantic schema.",
        "<b>Step 6 — Persistent KPI Storage:</b> Extracted metrics are committed into the <code>financial_metrics</code> relational table via <code>save_metrics()</code>.",
        "<b>Step 7 — Dashboard & Real-Time Querying:</b> The executive dashboard reflects new corporate metrics immediately, and the WebSocket AI analyst allows interactive, real-time natural language exploration."
    ]
    for s in steps:
        story.append(Paragraph(f"• {s}", bullet_style))

    story.append(PageBreak())

    # =========================================================================
    # SECTION 2: AUDITED FINANCIAL BENCHMARK DATA (FY2024)
    # =========================================================================
    story.append(Paragraph("3. Audited FY2024 Corporate Financial Benchmark Data", h1_style))
    story.append(Paragraph(
        "Below are the verified corporate metrics extracted from the official SEC Form 10-K filings for the three initial platform benchmark enterprises: "
        "<b>Apple Inc.</b>, <b>Microsoft Corporation</b>, and <b>Tesla, Inc.</b>",
        body_style
    ))

    # Quantitative Financial Table
    fin_headers = [
        Paragraph("Enterprise", th_style),
        Paragraph("Fiscal Year", th_style),
        Paragraph("Total Revenue", th_style),
        Paragraph("Operating Income", th_style),
        Paragraph("Net Income", th_style),
        Paragraph("Operating Cash Flow", th_style),
        Paragraph("Total Assets", th_style),
        Paragraph("Total Liabilities", th_style)
    ]
    fin_data = [
        fin_headers,
        [
            Paragraph("<b>Apple Inc. (AAPL)</b>", td_bold),
            Paragraph("2024", td_center),
            Paragraph("<b>$391,035M</b>", td_center),
            Paragraph("$123,216M", td_center),
            Paragraph("$93,736M", td_center),
            Paragraph("<b>$118,254M</b>", td_center),
            Paragraph("$364,980M", td_center),
            Paragraph("$308,030M", td_center),
        ],
        [
            Paragraph("<b>Microsoft Corp. (MSFT)</b>", td_bold),
            Paragraph("2024", td_center),
            Paragraph("$245,122M", td_center),
            Paragraph("<b>$109,433M</b>", td_center),
            Paragraph("<b>$88,136M</b>", td_center),
            Paragraph("<b>$118,548M</b>", td_center),
            Paragraph("$512,163M", td_center),
            Paragraph("$243,686M", td_center),
        ],
        [
            Paragraph("<b>Tesla, Inc. (TSLA)</b>", td_bold),
            Paragraph("2024", td_center),
            Paragraph("$97,690M", td_center),
            Paragraph("$7,077M", td_center),
            Paragraph("$7,088M", td_center),
            Paragraph("$13,256M", td_center),
            Paragraph("$114,841M", td_center),
            Paragraph("$46,478M", td_center),
        ]
    ]
    t_fin = Table(fin_data, colWidths=[90, 44, 62, 64, 58, 64, 61, 61])
    t_fin.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), PRIMARY),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor("#94a3b8")),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, BG_LIGHT])
    ]))
    story.append(t_fin)
    story.append(Spacer(1, 14))

    # Financial Margin & Leverage Breakdown Table
    story.append(Paragraph("Calculated Margins & Financial Health Ratios", h2_style))
    ratios_data = [
        [
            Paragraph("Company", th_style),
            Paragraph("Operating Margin", th_style),
            Paragraph("Net Profit Margin", th_style),
            Paragraph("Debt-to-Asset Leverage", th_style),
            Paragraph("Cash Conversion (OCF/Net)", th_style),
            Paragraph("Capital Profile", th_style)
        ],
        [
            Paragraph("<b>Apple</b>", td_bold),
            Paragraph("<b>31.5%</b>", td_center),
            Paragraph("24.0%", td_center),
            Paragraph("84.4%", td_center),
            Paragraph("126.2%", td_center),
            Paragraph("High operating leverage, Services expansion, share buybacks", td_style)
        ],
        [
            Paragraph("<b>Microsoft</b>", td_bold),
            Paragraph("<b>44.6%</b> (Leader)", td_center),
            Paragraph("<b>36.0%</b> (Leader)", td_center),
            Paragraph("47.6%", td_center),
            Paragraph("134.5%", td_center),
            Paragraph("Industry-leading software margins, Azure hyperscale scaling", td_style)
        ],
        [
            Paragraph("<b>Tesla</b>", td_bold),
            Paragraph("7.2%", td_center),
            Paragraph("7.3%", td_center),
            Paragraph("<b>40.5%</b> (Lowest Debt)", td_center),
            Paragraph("187.0%", td_center),
            Paragraph("Conservative leverage, high capex reinvestment, Energy growth", td_style)
        ]
    ]
    t_ratios = Table(ratios_data, colWidths=[65, 80, 80, 85, 85, 109])
    t_ratios.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), SECONDARY),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor("#94a3b8")),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, BG_LIGHT])
    ]))
    story.append(t_ratios)
    story.append(Spacer(1, 14))

    # Comparative Key Insights Box
    insights_p = Paragraph(
        "<b>Executive Equity Research Takeaways:</b><br/>"
        "• <b>Scale & Top-Line Dominance:</b> Apple leads the cohort with $391,035M in revenue, backed by its active base of 2.2B+ devices and $96B+ in high-margin Services revenue.<br/>"
        "• <b>Operating Leverage & Pricing Power:</b> Microsoft generates the highest profitability with a 44.6% operating margin and 36.0% net margin, driven by commercial cloud and Microsoft 365 Copilot monetization.<br/>"
        "• <b>Cash Generation:</b> Apple and Microsoft each generated over $118 Billion in operating cash flows in 2024. Tesla generated $13,256M in cash flow while funding intensive manufacturing expansion and Dojo AI compute clusters.",
        callout_style
    )
    t_ins = Table([[insights_p]], colWidths=[504])
    t_ins.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#f0fdf4")),
        ('BOX', (0, 0), (-1, -1), 1, SUCCESS),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('LEFTPADDING', (0, 0), (-1, -1), 10),
        ('RIGHTPADDING', (0, 0), (-1, -1), 10),
    ]))
    story.append(t_ins)

    story.append(PageBreak())

    # =========================================================================
    # SECTION 3: QUALITATIVE INTELLIGENCE DEEP-DIVE
    # =========================================================================
    story.append(Paragraph("4. Qualitative Intelligence: Growth Drivers vs. 10-K Risks", h1_style))
    story.append(Paragraph(
        "Beyond raw balance sheets, Form 10-K Item 1A (Risk Factors) and Item 7 (MD&A) disclose forward-looking catalysts and existential business threats. "
        "The platform automatically extracts and presents these qualitative factors:",
        body_style
    ))

    # Company 1: Apple
    story.append(Paragraph("Apple Inc. (AAPL) — Strategic Catalysts & Principal Headwinds", h2_style))
    apple_drivers = [
        "Record expansion in Services revenue fueled by iCloud, App Store, Apple Pay, and subscription platforms.",
        "Global demand for iPhone 16 series powered by Apple Intelligence on-device neural architecture.",
        "Mac and iPad ecosystem momentum driven by next-generation M-series Apple Silicon efficiency.",
        "Active installed device base surpassing 2.2 billion active devices worldwide.",
        "Disciplined capital allocation with continuous share repurchase programs ($95B+ returned)."
    ]
    apple_risks = [
        "Macroeconomic conditions including inflation, interest rates, and foreign exchange fluctuations impacting consumer electronics demand.",
        "Intense global smartphone competition with aggressive pricing and compressed product refresh cycles.",
        "Dependence on single- or limited-source manufacturing partners (e.g., TSMC, Foxconn), creating supply vulnerability.",
        "Regulatory, antitrust, and tax investigations worldwide, including European Union Digital Markets Act (DMA) compliance.",
        "Geopolitical exposure in Greater China representing a critical manufacturing base and major sales market."
    ]
    app_t_data = [
        [Paragraph("Top Growth Drivers", th_style), Paragraph("Principal 10-K Risk Disclosures", th_style)],
        [
            Paragraph("<br/>".join(f"• {d}" for d in apple_drivers), td_style),
            Paragraph("<br/>".join(f"• {r}" for r in apple_risks), td_style)
        ]
    ]
    t_apple = Table(app_t_data, colWidths=[252, 252])
    t_apple.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, 0), SUCCESS),
        ('BACKGROUND', (1, 0), (1, 0), DANGER),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor("#94a3b8")),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('VALIGN', (0, 0), (-1, -1), 'TOP')
    ]))
    story.append(t_apple)
    story.append(Spacer(1, 10))

    # Company 2: Microsoft
    story.append(Paragraph("Microsoft Corporation (MSFT) — Strategic Catalysts & Principal Headwinds", h2_style))
    msft_drivers = [
        "Exceptional growth across Microsoft Cloud and Azure OpenAI enterprise infrastructure adoption.",
        "Rapid enterprise monetization of Microsoft 365 Copilot, Security Copilot, and GitHub Copilot.",
        "Hybrid cloud expansion across Server products and multi-cloud enterprise deployments.",
        "Integration of Activision Blizzard significantly expanding gaming and Xbox Game Pass content monetization.",
        "Commercial cloud gross margin resilience supported by hyperscale datacenter operational efficiencies."
    ]
    msft_risks = [
        "Substantial capital expenditures required to expand global datacenter and specialized AI computing clusters ($50B+ Capex).",
        "Evolving global regulations and legal scrutiny surrounding artificial intelligence and algorithmic accountability.",
        "Sophisticated cybersecurity threats and nation-state attacks targeting cloud software services.",
        "Intense cloud competition from Amazon AWS and Google Cloud Platform in AI infrastructure.",
        "Geopolitical restrictions on international technology transfers and advanced semiconductor availability."
    ]
    msft_t_data = [
        [Paragraph("Top Growth Drivers", th_style), Paragraph("Principal 10-K Risk Disclosures", th_style)],
        [
            Paragraph("<br/>".join(f"• {d}" for d in msft_drivers), td_style),
            Paragraph("<br/>".join(f"• {r}" for r in msft_risks), td_style)
        ]
    ]
    t_msft = Table(msft_t_data, colWidths=[252, 252])
    t_msft.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, 0), SUCCESS),
        ('BACKGROUND', (1, 0), (1, 0), DANGER),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor("#94a3b8")),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('VALIGN', (0, 0), (-1, -1), 'TOP')
    ]))
    story.append(t_msft)

    story.append(PageBreak())

    # Company 3: Tesla
    story.append(Paragraph("Tesla, Inc. (TSLA) — Strategic Catalysts & Principal Headwinds", h2_style))
    tsla_drivers = [
        "Record expansion in Tesla Energy segment with record Megapack and Powerwall deployment volume (125%+ YoY).",
        "Continued vehicle delivery leadership of Model Y as the world's best-selling passenger vehicle.",
        "Rapid technological advancements in Full Self-Driving (Supervised) end-to-end neural network models.",
        "Ongoing development of next-generation affordable vehicle platforms and Cybercab autonomous robotaxi fleet.",
        "Global adoption of the North American Charging Standard (NACS) and Supercharger licensing agreements."
    ]
    tsla_risks = [
        "Intensifying pricing pressure and aggressive competition across global electric vehicle markets, notably from Chinese OEMs.",
        "Technological and regulatory uncertainty regarding autonomous vehicle validation and commercial robotaxi operation.",
        "Volatility in critical battery raw material costs including lithium, nickel, and refined graphite.",
        "Production scaling hurdles for new vehicle architectures including Cybertruck and 4680 dry-electrode cells.",
        "Key-person dependency on executive leadership and elevated brand sensitivity."
    ]
    tsla_t_data = [
        [Paragraph("Top Growth Drivers", th_style), Paragraph("Principal 10-K Risk Disclosures", th_style)],
        [
            Paragraph("<br/>".join(f"• {d}" for d in tsla_drivers), td_style),
            Paragraph("<br/>".join(f"• {r}" for r in tsla_risks), td_style)
        ]
    ]
    t_tsla = Table(tsla_t_data, colWidths=[252, 252])
    t_tsla.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, 0), SUCCESS),
        ('BACKGROUND', (1, 0), (1, 0), DANGER),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor("#94a3b8")),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('VALIGN', (0, 0), (-1, -1), 'TOP')
    ]))
    story.append(t_tsla)
    story.append(Spacer(1, 14))

    # =========================================================================
    # SECTION 4: REAL-TIME STREAMING CHATBOT ARCHITECTURE
    # =========================================================================
    story.append(Paragraph("5. Real-Time Streaming Chatbot Architecture", h1_style))
    story.append(Paragraph(
        "A standout innovation of the platform is the <b>real-time streaming conversational agent</b>. "
        "Unlike standard chatbots that freeze for several seconds while awaiting a complete payload, this engine streams response tokens and progress status events dynamically.",
        body_style
    ))

    # WebSocket Message Protocol Table
    ws_headers = [
        Paragraph("Direction", th_style),
        Paragraph("Event Type", th_style),
        Paragraph("Payload Example", th_style),
        Paragraph("System Behavior", th_style)
    ]
    ws_data = [
        ws_headers,
        [
            Paragraph("Client -> Server", td_bold),
            Paragraph("<code>chat</code>", td_center),
            Paragraph("<code>{'question': '...', 'company': 'Apple', 'year': 2024}</code>", code_style),
            Paragraph("Initiates retrieval and starts asynchronous response token streaming.", td_style)
        ],
        [
            Paragraph("Server -> Client", td_bold),
            Paragraph("<code>status</code>", td_center),
            Paragraph("<code>{'message': 'Analyzing 10-K filings...'}</code>", code_style),
            Paragraph("Updates the client status indicator with live retrieval feedback.", td_style)
        ],
        [
            Paragraph("Server -> Client", td_bold),
            Paragraph("<code>chunk</code>", td_center),
            Paragraph("<code>{'text': '### Revenue Analysis '}</code>", code_style),
            Paragraph("Appends token chunk into active message bubble with blinking cursor.", td_style)
        ],
        [
            Paragraph("Client -> Server", td_bold),
            Paragraph("<code>stop</code>", td_center),
            Paragraph("<code>{'type': 'stop'}</code>", code_style),
            Paragraph("Cancels the active streaming asyncio Task cleanly on demand.", td_style)
        ],
        [
            Paragraph("Server -> Client", td_bold),
            Paragraph("<code>done</code>", td_center),
            Paragraph("<code>{'full_text': '...'}</code>", code_style),
            Paragraph("Removes streaming cursor, binds Copy and Text-to-Speech action tools.", td_style)
        ],
        [
            Paragraph("Bidirectional", td_bold),
            Paragraph("<code>ping/pong</code>", td_center),
            Paragraph("<code>{'type': 'ping'} -> {'type': 'pong'}</code>", code_style),
            Paragraph("Heartbeat every 25 seconds keeps connection active through firewalls.", td_style)
        ]
    ]
    t_ws = Table(ws_data, colWidths=[80, 60, 180, 184])
    t_ws.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), PRIMARY),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor("#94a3b8")),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, BG_LIGHT])
    ]))
    story.append(t_ws)

    story.append(PageBreak())

    # =========================================================================
    # SECTION 5: COMPLETE API SPECIFICATION
    # =========================================================================
    story.append(Paragraph("6. Platform API Reference & Endpoint Specifications", h1_style))
    story.append(Paragraph(
        "FastAPI delivers automated OpenAPI documentation (Swagger UI accessible at <code>http://localhost:8000/docs</code>). "
        "The primary endpoints are specified below:",
        body_style
    ))

    api_headers = [
        Paragraph("Method", th_style),
        Paragraph("Endpoint Path", th_style),
        Paragraph("Parameters / Payload", th_style),
        Paragraph("Response Output & Description", th_style)
    ]
    api_data = [
        api_headers,
        [
            Paragraph("<b>GET</b>", td_center),
            Paragraph("<code>/</code>", code_style),
            Paragraph("None", td_style),
            Paragraph("Renders dashboard UI with company KPI cards, comparison bars, and chat panel.", td_style)
        ],
        [
            Paragraph("<b>GET</b>", td_center),
            Paragraph("<code>/health</code>", code_style),
            Paragraph("None", td_style),
            Paragraph("Returns <code>{'status': 'healthy'}</code> for Kubernetes liveness/readiness probes.", td_style)
        ],
        [
            Paragraph("<b>GET</b>", td_center),
            Paragraph("<code>/api/metrics</code>", code_style),
            Paragraph("None", td_style),
            Paragraph("Returns raw JSON array of all stored audited company financial metrics and ratios.", td_style)
        ],
        [
            Paragraph("<b>POST</b>", td_center),
            Paragraph("<code>/api/upload</code>", code_style),
            Paragraph("<code>multipart/form-data</code> (file: PDF)", td_style),
            Paragraph("Uploads PDF report, runs Markdown conversion, chunking, and KPI extraction.", td_style)
        ],
        [
            Paragraph("<b>WS</b>", td_center),
            Paragraph("<code>/ws/chat</code>", code_style),
            Paragraph("WebSocket JSON messages", td_style),
            Paragraph("Bidirectional real-time stream for interactive financial analyst conversation.", td_style)
        ],
        [
            Paragraph("<b>POST</b>", td_center),
            Paragraph("<code>/api/chat/stream</code>", code_style),
            Paragraph("<code>{'question': str, 'company': str}</code>", code_style),
            Paragraph("Server-Sent Events (SSE) streaming fallback endpoint.", td_style)
        ],
        [
            Paragraph("<b>POST</b>", td_center),
            Paragraph("<code>/api/chat</code>", code_style),
            Paragraph("<code>{'question': str, 'company': str}</code>", code_style),
            Paragraph("Synchronous non-streaming JSON response endpoint for legacy integrations.", td_style)
        ]
    ]
    t_api = Table(api_data, colWidths=[45, 95, 160, 204])
    t_api.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), PRIMARY),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor("#94a3b8")),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, BG_LIGHT])
    ]))
    story.append(t_api)
    story.append(Spacer(1, 14))

    # =========================================================================
    # SECTION 6: CLOUD DEPLOYMENT & PRODUCTION RUNBOOK
    # =========================================================================
    story.append(Paragraph("7. Cloud Deployment & Container Orchestration", h1_style))
    story.append(Paragraph(
        "The platform is built as a cloud-native microservice ready for Azure Kubernetes Service (AKS) deployment:",
        body_style
    ))

    deploy_points = [
        "<b>Containerization (Docker):</b> Multi-stage Python 3.12-slim base image using Astral UV for fast dependency installation. Exposes port 8000 and runs Uvicorn ASGI server.",
        "<b>Container Registry (ACR):</b> Docker images are tagged and pushed to Azure Container Registry (<code>myacr.azurecr.io/investor-intelligence:latest</code>).",
        "<b>Kubernetes Manifests (k8s/):</b> <code>deployment.yaml</code> provisions pod replicas with CPU/memory limits, liveness/readiness probes to <code>/health</code>, and mounts Azure Key Vault secrets for database credentials.",
        "<b>Automated Provisioning (setup_azure.ps1):</b> PowerShell script provisions resource groups, Azure PostgreSQL Flexible Server, Azure AI Search instance, Azure OpenAI deployments, and AKS clusters in a single command.",
        "<b>Resilient Local Fallback:</b> Zero external lock-in. If Azure credentials are not provided, the platform seamlessly switches to local SQLite storage and internal 10-K filing search, guaranteeing uninterrupted operation."
    ]
    for dp in deploy_points:
        story.append(Paragraph(f"• {dp}", bullet_style))

    story.append(Spacer(1, 20))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#cbd5e1"), spaceAfter=14, spaceBefore=0))
    story.append(Paragraph("<b>Document Status:</b> Verified & Finalized | InvestTech Platform Architecture", ParagraphStyle('DocFooter', fontName='Helvetica-Bold', fontSize=8, textColor=TEXT_MUTED, alignment=1)))

    # Build PDF with dynamic 2-pass page numbering
    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"PDF successfully built at: {output_path}")


if __name__ == "__main__":
    out_dir = Path(__file__).resolve().parent
    target_file = out_dir / "InvestTech_Full_Platform_Documentation.pdf"
    build_pdf(str(target_file))
