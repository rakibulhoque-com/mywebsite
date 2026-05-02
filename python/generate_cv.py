#!/usr/bin/env python3
"""
Professional PDF CV generator for Md. Rakibul Hoque.
Output: ../RakibulHoque_CV.pdf   (relative to this script's directory)
Requires: pip install reportlab
"""

import os
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm, mm
from reportlab.lib.colors import HexColor, white, black
from reportlab.lib.enums import TA_LEFT, TA_RIGHT, TA_CENTER, TA_JUSTIFY
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, HRFlowable,
    Table, TableStyle, KeepTogether, PageBreak,
)
from reportlab.platypus.flowables import BalancedColumns

# ── Palette ─────────────────────────────────────────────────────────────────
NAVY     = HexColor('#1B3358')   # headers, name
BLUE     = HexColor('#2B6CB0')   # role titles, links
AMBER    = HexColor('#C4841A')   # section rule accent
CHARCOAL = HexColor('#222222')   # body text
MIDGRAY  = HexColor('#555555')   # secondary text
LIGHTGRAY= HexColor('#AAAAAA')   # dates, faint rules
RULE_GR  = HexColor('#DDDDDD')   # horizontal rules between items
BG_ROW   = HexColor('#F7F8FA')   # alternating skill row tint

W, H = A4
LEFT_M = RIGHT_M = 1.55 * cm
TOP_M  = 1.6  * cm
BOT_M  = 1.55 * cm
BODY_W = W - LEFT_M - RIGHT_M


# ── Style Factory ────────────────────────────────────────────────────────────
def S(name='body', **kw):
    """Build a ParagraphStyle on the fly."""
    defaults = dict(
        fontName='Helvetica', fontSize=9.5,
        textColor=CHARCOAL, leading=13.5,
        spaceBefore=0, spaceAfter=0,
        leftIndent=0, firstLineIndent=0,
        alignment=TA_LEFT,
    )
    defaults.update(kw)
    return ParagraphStyle(name, **defaults)


NAME_STYLE    = S('name',    fontName='Helvetica-Bold', fontSize=24,  textColor=NAVY,     leading=28)
TAGLINE_STYLE = S('tagline', fontName='Helvetica',      fontSize=10,  textColor=BLUE,     leading=13, spaceAfter=1)
CONTACT_STYLE = S('contact', fontName='Helvetica',      fontSize=8,   textColor=MIDGRAY,  leading=11, alignment=TA_RIGHT)

SEC_STYLE     = S('sec',     fontName='Helvetica-Bold', fontSize=9,   textColor=NAVY,     leading=11,
                  spaceBefore=0, spaceAfter=0, textTransform='uppercase', letterSpacing=0.8)

CO_STYLE      = S('co',      fontName='Helvetica-Bold', fontSize=9.5,  textColor=CHARCOAL, leading=12, spaceBefore=4)
DATE_STYLE    = S('date',    fontName='Helvetica',      fontSize=8,   textColor=MIDGRAY,   leading=12, alignment=TA_RIGHT, spaceBefore=4)
LOC_STYLE     = S('loc',     fontName='Helvetica',      fontSize=8,   textColor=MIDGRAY,   leading=10)
ROLE_STYLE    = S('role',    fontName='Helvetica-Oblique', fontSize=8.5, textColor=BLUE,   leading=11, spaceAfter=2)

BODY_STYLE    = S('body',    fontName='Helvetica',      fontSize=9,   textColor=CHARCOAL, leading=12.5, spaceAfter=2, alignment=TA_JUSTIFY)
BULLET_STYLE  = S('bul',     fontName='Helvetica',      fontSize=8.8, textColor=CHARCOAL, leading=12.5,
                  leftIndent=10, firstLineIndent=-6, spaceAfter=1.5)
TECH_STYLE    = S('tech',    fontName='Helvetica-Oblique', fontSize=8, textColor=MIDGRAY, leading=10.5, spaceAfter=3, leftIndent=0)

SK_CAT_STYLE  = S('skcat',   fontName='Helvetica-Bold', fontSize=8.2, textColor=NAVY,     leading=11)
SK_VAL_STYLE  = S('skval',   fontName='Helvetica',      fontSize=8.2, textColor=CHARCOAL, leading=11)

EDU_DEG_STYLE = S('edudeg',  fontName='Helvetica-Bold', fontSize=9,   textColor=CHARCOAL, leading=12, spaceBefore=4)
EDU_INS_STYLE = S('eduins',  fontName='Helvetica-Oblique', fontSize=8.5, textColor=MIDGRAY, leading=11)
EDU_GPA_STYLE = S('edugpa',  fontName='Helvetica-Bold', fontSize=8,   textColor=BLUE,     leading=10, spaceAfter=1)

PUB_STYLE     = S('pub',     fontName='Helvetica',      fontSize=8.5, textColor=CHARCOAL, leading=12,
                  leftIndent=14, firstLineIndent=-10, spaceAfter=2)


# ── Helper flowables ─────────────────────────────────────────────────────────
def vsp(pts=4):
    return Spacer(1, pts)

def section_header(title):
    """Section title with a navy + amber double-rule."""
    return KeepTogether([
        vsp(8),
        Paragraph(title, SEC_STYLE),
        HRFlowable(width='100%', thickness=0.8, color=NAVY, spaceAfter=0, spaceBefore=2),
        HRFlowable(width='28', thickness=2.2, color=AMBER, spaceAfter=5, spaceBefore=1),
    ])

def exp_header(company, location, date_range, url=None):
    co_text = (f'<a href="{url}" color="#1B3358"><b>{company}</b></a>' if url
               else f'<b>{company}</b>')
    t = Table(
        [[Paragraph(f'{co_text}&nbsp; <font color="#555555" size="8.5">· {location}</font>', CO_STYLE),
          Paragraph(date_range, DATE_STYLE)]],
        colWidths=[BODY_W * 0.68, BODY_W * 0.32],
    )
    t.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'BOTTOM'),
        ('LEFTPADDING',  (0, 0), (-1, -1), 0),
        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
        ('TOPPADDING',   (0, 0), (-1, -1), 0),
        ('BOTTOMPADDING',(0, 0), (-1, -1), 0),
    ]))
    return t

def bullet(text):
    return Paragraph(f'•&nbsp; {text}', BULLET_STYLE)

def tech(text):
    return Paragraph(f'<i>Stack:</i>&nbsp; {text}', TECH_STYLE)

def thin_rule():
    return HRFlowable(width='100%', thickness=0.4, color=RULE_GR, spaceBefore=3, spaceAfter=0)


# ── Page template with footer ────────────────────────────────────────────────
def make_footer(canvas, doc):
    canvas.saveState()
    canvas.setFont('Helvetica', 7.5)
    canvas.setFillColor(LIGHTGRAY)
    page_w = A4[0]
    canvas.drawString(LEFT_M, BOT_M * 0.55, 'Md. Rakibul Hoque  ·  mohammadrhoque@gmail.com  ·  profile.rakibulhoque.com')
    canvas.drawRightString(page_w - RIGHT_M, BOT_M * 0.55, f'Page {doc.page}')
    # Thin rule above footer
    canvas.setStrokeColor(RULE_GR)
    canvas.setLineWidth(0.4)
    canvas.line(LEFT_M, BOT_M * 0.75, page_w - RIGHT_M, BOT_M * 0.75)
    canvas.restoreState()


# ── CV Content ───────────────────────────────────────────────────────────────
def build_cv(output_path):
    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        leftMargin=LEFT_M, rightMargin=RIGHT_M,
        topMargin=TOP_M,   bottomMargin=BOT_M + 0.35 * cm,
        title='Md. Rakibul Hoque — CV',
        author='Md. Rakibul Hoque',
        subject='Curriculum Vitae',
    )

    story = []

    # ── Header ──────────────────────────────────────────────────────────────
    contact_lines = [
        '+880 1672 868711',
        'mohammadrhoque@gmail.com',
        'linkedin.com/in/rakibul-hoque-37b66a13b',
        'profile.rakibulhoque.com',
        'Dhaka, Bangladesh',
    ]
    hdr = Table(
        [[
            [Paragraph('Md. Rakibul Hoque', NAME_STYLE),
             Paragraph('Lead Data &amp; Platform Engineer<br/><font size="9">Big Data &nbsp;·&nbsp; Fraud Detection &amp; Prevention &nbsp;·&nbsp; Real-time Systems &nbsp;·&nbsp; DevSecOps</font>', TAGLINE_STYLE)],
            [Paragraph(line, CONTACT_STYLE) for line in contact_lines],
        ]],
        colWidths=[BODY_W * 0.58, BODY_W * 0.42],
    )
    hdr.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'BOTTOM'),
        ('LEFTPADDING',  (0, 0), (-1, -1), 0),
        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
        ('TOPPADDING',   (0, 0), (-1, -1), 0),
        ('BOTTOMPADDING',(0, 0), (-1, -1), 4),
    ]))
    story.append(hdr)
    story.append(HRFlowable(width='100%', thickness=1.8, color=NAVY, spaceBefore=2, spaceAfter=2))
    story.append(HRFlowable(width='100%', thickness=2.5, color=AMBER, spaceBefore=0, spaceAfter=0))
    story.append(vsp(6))

    # ── Summary ──────────────────────────────────────────────────────────────
    story += [section_header('Professional Summary')]
    story.append(Paragraph(
        'Lead Data &amp; Platform Engineer with 7+ years of experience spanning big data engineering, '
        'real-time fraud detection &amp; prevention, DevOps, DevSecOps, and AI agent automation across '
        'high-throughput, mission-critical production environments in ride-hailing, global fashion retail, '
        'and EdTech.',
        BODY_STYLE,
    ))
    story.append(vsp(4))
    story.append(Paragraph(
        'Proven technical lead who has managed multinational engineering teams, designed and operated '
        'large-scale data platforms from scratch, and delivered measurable financial impact — fraud '
        'prevention systems that stopped tens of crores of Taka in losses, AI-powered analytics tools '
        'that eliminated millions of dollars in vendor costs, and platform optimisations driving millions '
        'in annual cloud savings.',
        BODY_STYLE,
    ))
    story.append(vsp(4))
    story.append(Paragraph(
        'Brings strong organisational leadership and engineering discipline: GitOps-driven delivery via '
        'Atlantis, infrastructure as code with Terraform, disciplined multi-environment governance, '
        'comprehensive audit traceability, and a security-first design philosophy — consistently '
        'shipping systems that are observable, adaptable, and built to withstand production pressure.',
        BODY_STYLE,
    ))

    # ── Experience ───────────────────────────────────────────────────────────
    story += [section_header('Professional Experience')]

    # — G-Star Raw
    story.append(exp_header('G-Star Raw', 'Amsterdam, Netherlands · Remote from Dhaka, Bangladesh', 'Mar 2023 – Present', url='https://www.g-star.com/en_nl'))
    story.append(Paragraph(
        'Senior Data Engineer (Lead Architect, 10-person multinational team)&nbsp; '
        '<font color="#AAAAAA">Jan 2024 – Present</font>'
        '&nbsp;&nbsp;|&nbsp;&nbsp;'
        'Data Engineer&nbsp; <font color="#AAAAAA">Mar 2023 – Dec 2023</font>',
        ROLE_STYLE,
    ))
    gstar = [
        '<b>DataOps &amp; cost optimisation:</b> Architected a multi-layer BigQuery data warehouse via '
        'Dataform — 1,700+ SQL models across 10 business domains; pipeline-as-code with automated model '
        'promotion across dev / UAT / prod; query and pipeline optimisations delivered '
        '<b>millions of dollars in annual GCP cost savings</b>',

        '<b>AI analyst agent — vendor cost elimination:</b> Designed and delivered a production '
        '<b>multi-agent AI analytics assistant</b> (FastAPI + LangChain + Google Gemini + Svelte) '
        'replacing the need for expensive third-party BI and NLP query tools — '
        '<b>saving millions of dollars in annual vendor licensing costs</b>; '
        'multi-agent domain routing with <b>permission-based access control per data domain</b> '
        '(Keycloak group-level scoping), prompt injection safeguards, and full PostgreSQL audit trail',

        '<b>DevOps / GitOps &amp; self-hosted cost savings:</b> Established a 4-environment GCP platform '
        'via Atlantis + Terraform (100+ IaC resources, peer-reviewed plan/apply gates); '
        'self-hosted Airbyte, Apache Superset, Keycloak, and Traefik on GKE — '
        'replacing paid SaaS equivalents and <b>saving significant recurring vendor licensing costs</b>; '
        'production GKE cluster with Helm-managed releases across all environments',

        '<b>Cross-system data integration:</b> Designed and operated unified data pipelines integrating '
        '<b>POS systems, ERP (SAP ECC / Datasphere), Payment Systems (Adyen), Marketing Tools, '
        'and Fraud Prevention (Forter)</b> into a single BigQuery data platform — '
        'enabling end-to-end visibility across the entire retail and e-commerce data estate; '
        '54 outbound feed models to 7 external SaaS platforms',

        '<b>Fraud monitoring &amp; vendor management:</b> Real-time Adyen payment fraud prevention '
        'in collaboration with <b>Forter</b>; led data &amp; analytics tool evaluation, '
        'integration scoping, and SLA discussions with 3rd-party vendors; '
        'SAP replication stack (ECC, Datasphere, SLT) + Salesforce CRM integration',

        '<b>DevSecOps identity layer:</b> Security-first access platform built entirely as code — '
        'Keycloak OIDC/OAuth2, OAuth2-Proxy forward auth, GCP Workload Identity, '
        'Row-Level Security in Superset, and 40+ prompt injection guards; '
        'all declaratively managed via Terraform across environments',
    ]
    for b in gstar:
        story.append(bullet(b))
    story.append(tech(
        'GCP · Terraform · Kubernetes (GKE) · Helm · BigQuery · Dataform · Cloud Composer (Airflow) · '
        'Airbyte · Apache Superset · FastAPI · LangChain · Google Gemini · Svelte · PostgreSQL · '
        'Keycloak · Traefik · Consul · SAP ECC · SAP Data Intelligence · SAP SLT · Pub/Sub · Python'
    ))

    story.append(thin_rule())

    # — Aajil
    story.append(exp_header('Aajil', 'Remote', 'Nov 2023 – Jan 2024', url='https://www.aajil.sa/en'))
    story.append(Paragraph('Data Engineering Consultant (Contract)', ROLE_STYLE))
    story.append(Paragraph(
        'Brought in as the sole data architect to design and build the entire data and ML infrastructure '
        'from a blank slate on GCP — no prior data platform existed.',
        BODY_STYLE,
    ))
    aajil = [
        'Designed the full <b>data warehouse architecture</b> on BigQuery — schema design, dataset '
        'organisation, incremental loading strategy, and data modeling standards using dbt',
        'Built the <b>ELT ingestion layer</b> with Airbyte, connecting operational data sources to '
        'BigQuery; configured orchestration workflows with Apache Airflow for pipeline scheduling and '
        'dependency management',
        'Established the <b>ML-Ops foundation</b> with MLflow for experiment tracking, model registry, '
        'and versioning — enabling the data science team to manage the full model lifecycle',
        'Provisioned all <b>cloud infrastructure via Terraform</b> — VPCs, service accounts, GCS buckets, '
        'BigQuery datasets, IAM policies, and Composer environments',
    ]
    for b in aajil:
        story.append(bullet(b))
    story.append(tech('GCP · Terraform · BigQuery · dbt · Airbyte · Airflow · MLflow · Python'))

    story.append(thin_rule())

    # — Pathao
    story.append(exp_header('Pathao Limited', 'Dhaka, Bangladesh', 'Dec 2019 – Nov 2023', url='https://pathao.com/bn/'))
    story.append(Paragraph(
        'Data Engineer II – Contract&nbsp; <font color="#AAAAAA">Apr 2023 – Nov 2023</font>'
        '&nbsp; | &nbsp;'
        'Data Engineer II&nbsp; <font color="#AAAAAA">Jan 2020 – Mar 2023</font>'
        '&nbsp; | &nbsp;'
        'Data Engineer I&nbsp; <font color="#AAAAAA">Dec 2019 – Jan 2020</font>',
        ROLE_STYLE,
    ))
    pathao = [
        'Designed and led the <b>real-time fraud detection &amp; prevention platform</b> — '
        'multi-stage batch and streaming pipelines for suspicious activity classification using '
        'rule-based engines and ML models, automated transaction blocking mechanisms, and real-time '
        'alert dispatch across ride-sharing, food delivery, and payment verticals; '
        'processed millions of daily transaction events; '
        '<b>platform prevented tens of crores of Taka in fraudulent transaction losses</b>',

        'Led co-architecture of the <b>big data ELT platform</b> on GCP + BigQuery — ingesting data '
        'from multiple operational systems (ride, food, fintech) into a centralised data warehouse; '
        'established data modeling standards, pipeline governance practices, and observability tooling '
        'that enabled silo-free collaboration between Data Engineers, Data Scientists, and Analysts at scale',

        'Co-architected the <b>production ML lifecycle platform</b> from scratch — Kedro for '
        'reproducible, governed ML pipelines; MLflow for experiment tracking, model registry, and '
        'versioning; MLServer for low-latency model serving on Kubernetes; enabled the data science '
        'team to move efficiently from experimentation to production deployment',

        'Engineered a <b>high-throughput real-time GPS telemetry microservice</b> using Apache Beam '
        '— noise cancellation algorithms for filtering GPS signal drift, confidence scoring from raw '
        'ping data, and accurate distance calculation for millions of live ride events per day; '
        'critical to both fare calculation accuracy and ETA estimation',

        'Built a <b>personalised food recommendation engine</b> using item-item similarity, '
        'user-user similarity, and doc2vec NLP embeddings on the Pathao Food platform — '
        'improving item discovery and order conversion for thousands of daily active users',

        'Developed an <b>ETA correction system</b> incorporating historical peak/off-peak and '
        'weekday/weekend traffic patterns into the baseline ETA model — improving delivery time '
        'prediction accuracy across both ride-sharing and food delivery services',
    ]
    for b in pathao:
        story.append(bullet(b))
    story.append(tech(
        'GCP · BigQuery · dbt · Airflow · Kedro · MLflow · MLServer · Kubernetes · '
        'Apache Beam · Terraform · InfluxDB · Grafana · Python'
    ))

    story.append(thin_rule())

    # — 10MinuteSchool
    story.append(exp_header('10MinuteSchool', 'Dhaka, Bangladesh', 'Jan 2022 – Oct 2022', url='https://10minuteschool.com/'))
    story.append(Paragraph('Data Engineering Consultant', ROLE_STYLE))
    story.append(Paragraph(
        'Engaged to establish the foundational data infrastructure for Bangladesh\'s leading EdTech '
        'platform serving over 10 million students — no data engineering layer existed prior to this engagement.',
        BODY_STYLE,
    ))
    tms = [
        'Designed and implemented the <b>ELT ingestion layer</b> using Airbyte, connecting operational '
        'platforms (LMS, mobile app, CRM) to BigQuery for centralised analytics',
        'Built the <b>BigQuery data warehouse schema</b> for learner behaviour, content performance, '
        'and subscription analytics — the primary data source for all BI reporting',
        'Delivered <b>production-ready reporting dashboards</b> for the BI and analytics team, '
        'enabling data-driven decisions on course quality, learner engagement, and retention',
    ]
    for b in tms:
        story.append(bullet(b))
    story.append(tech('Airbyte · BigQuery · GCP · SQL'))

    # ── Technical Skills ─────────────────────────────────────────────────────
    story += [section_header('Technical Skills')]

    skills = [
        ('DevOps & Platform',
         'GCP, Terraform, Kubernetes (GKE), Helm, Docker, Atlantis, GitOps, CI/CD Pipelines, '
         'Cloud Build, Cloud Composer, Traefik, Consul'),
        ('Big Data & DataOps',
         'BigQuery, Apache Beam, Pub/Sub, Dataform, Apache Airflow, Airbyte, dbt, '
         'Real-time Stream Processing, Batch & Micro-batch Pipelines, '
         'SAP ECC, SAP Data Intelligence, SAP SLT, Salesforce CRM'),
        ('AI, ML & Fraud Systems',
         'Fraud Detection & Prevention, Anomaly Detection, Real-time Alert Pipelines, '
         'LangChain, Google Gemini, n8n, Temporal, Agentic Automation, '
         'FastAPI, Kedro, MLflow, MLServer, Scikit-learn, Pandas'),
        ('DevSecOps & Identity',
         'Keycloak, OAuth2/OIDC, OAuth2-Proxy, GCP IAP, Workload Identity, '
         'Row-Level Security, Prompt Injection Defence (40+ patterns), VPN (IPSec)'),
        ('Analytics Engineering',
         'SQL, Data Modeling, Dimensional Modeling, Incremental Loading, '
         'Partitioning & Clustering, Apache Superset, Grafana, InfluxDB'),
        ('Languages & Frameworks',
         'Python, Go, SQL, JavaScript, TypeScript, Svelte, FastAPI, PostgreSQL, Redis, MSSQL'),
    ]

    skill_rows = [
        [Paragraph(cat, SK_CAT_STYLE), Paragraph(val, SK_VAL_STYLE)]
        for cat, val in skills
    ]
    skill_table = Table(skill_rows, colWidths=[BODY_W * 0.26, BODY_W * 0.74])
    skill_table.setStyle(TableStyle([
        ('VALIGN',        (0, 0), (-1, -1), 'TOP'),
        ('LEFTPADDING',   (0, 0), (-1, -1), 4),
        ('RIGHTPADDING',  (0, 0), (-1, -1), 4),
        ('TOPPADDING',    (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('ROWBACKGROUNDS',(0, 0), (-1, -1), [BG_ROW, white]),
        ('LINEBELOW',     (0, 0), (-1, -2), 0.3, RULE_GR),
    ]))
    story.append(skill_table)

    # ── Education ────────────────────────────────────────────────────────────
    story += [section_header('Education')]

    education = [
        ('BS in Electrical and Electronic Engineering',
         'Bangladesh University of Engineering & Technology (BUET)',
         'Major: Communication  ·  Minor: Electronics',
         '2018', 'GPA 3.35 / 4.00'),
        ('Higher Secondary Certificate (HSC)',
         'Ananda Mohan College, Mymensingh, Bangladesh',
         '', '2013', 'GPA 5.00 / 5.00'),
        ('Secondary School Certificate (SSC)',
         'Premier Ideal High School, Mymensingh, Bangladesh',
         '', '2011', 'GPA 5.00 / 5.00'),
    ]

    for degree, institution, detail, year, gpa in education:
        row = Table(
            [[Paragraph(f'<b>{degree}</b>', EDU_DEG_STYLE),
              Paragraph(year, DATE_STYLE)]],
            colWidths=[BODY_W * 0.75, BODY_W * 0.25],
        )
        row.setStyle(TableStyle([
            ('VALIGN',       (0, 0), (-1, -1), 'BOTTOM'),
            ('LEFTPADDING',  (0, 0), (-1, -1), 0),
            ('RIGHTPADDING', (0, 0), (-1, -1), 0),
            ('TOPPADDING',   (0, 0), (-1, -1), 0),
            ('BOTTOMPADDING',(0, 0), (-1, -1), 1),
        ]))
        story.append(row)
        ins_line = institution + (f'  ·  {detail}' if detail else '')
        story.append(Paragraph(ins_line, EDU_INS_STYLE))
        story.append(Paragraph(gpa, EDU_GPA_STYLE))

    # ── Publications ─────────────────────────────────────────────────────────
    story += [section_header('Publications')]

    pubs = [
        (
            'Application of DenseNet in Camera Model Identification and Post-processing Detection',
            'Uday Kamal, Abdul Muntakim Rafi, <b>Rakibul Hoque</b>, Sowmitra Das, Abid Abrar and Md. Kamrul Hasan',
            'CVPR Workshops (Media Forensics), Jun. 2019',
            'https://openaccess.thecvf.com/content_CVPRW_2019/papers/Media%20Forensics/Rafi_Application_of_DenseNet_in_Camera_Model_Identification_and_Post-processing_Detection_CVPRW_2019_paper.pdf',
        ),
        (
            'Lung Cancer Tumor Region Segmentation Using Recurrent 3D-DenseUNet',
            'Uday Kamal, Abdul Muntakim Rafi, <b>Rakibul Hoque</b> and Md. Kamrul Hasan',
            'arXiv:1812.01951 [eess], Dec. 2018',
            'https://arxiv.org/pdf/1812.01951',
        ),
    ]
    for i, (title, authors, venue, url) in enumerate(pubs, 1):
        story.append(Paragraph(
            f'[{i}]&nbsp; <a href="{url}" color="#2B6CB0"><b>{title}</b></a>.',
            PUB_STYLE,
        ))
        story.append(Paragraph(f'&nbsp;&nbsp;&nbsp;&nbsp;{authors}. <i>{venue}.</i>', PUB_STYLE))
        if i < len(pubs):
            story.append(vsp(2))

    # ── Personal Projects ────────────────────────────────────────────────────
    story += [section_header('Personal Projects')]
    story.append(exp_header('TroyERP', 'Personal Engineering Project', '2024 – Present'))
    story.append(Paragraph(
        '<i>SAP-inspired modular ERP</i> — 13-domain design (SD, MM, FI, CO, PP, QM, PM, EWM, HCM, CS, TR, LE, RE-FX); '
        'FastAPI + async SQLAlchemy on PostgreSQL; Temporal for agentic Order-to-Cash / Procure-to-Pay orchestration.',
        BODY_STYLE,
    ))
    story.append(tech('FastAPI · PostgreSQL · Redis · Temporal · Docker · Python'))

    # ── Awards ───────────────────────────────────────────────────────────────
    story += [section_header('Awards & Recognition')]

    awards = [
        'First Runner-Up, 2018 IEEE VIP Cup Competition (Team: Spectrum)',
        'Top 6 Finalist, Robi Datathon (2019 &amp; 2022)',
        'Regional Champion, Bangladesh Mathematical Olympiad — HSC Category, 2013',
        'Regional Champion, Bangladesh Mathematical Olympiad — SSC Category, 2011',
        'Junior Education Board Scholarship, 2009–2010',
        'Primary Education Board Scholarship, 2006–2008',
    ]
    # Two-column layout for awards to save space
    col1 = [bullet(a) for a in awards[:3]]
    col2 = [bullet(a) for a in awards[3:]]
    # Pad col2 if uneven
    while len(col2) < len(col1):
        col2.append(vsp(2))
    aw_table = Table(
        [[col1, col2]],
        colWidths=[BODY_W * 0.5, BODY_W * 0.5],
    )
    aw_table.setStyle(TableStyle([
        ('VALIGN',       (0, 0), (-1, -1), 'TOP'),
        ('LEFTPADDING',  (0, 0), (-1, -1), 0),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING',   (0, 0), (-1, -1), 0),
        ('BOTTOMPADDING',(0, 0), (-1, -1), 0),
    ]))
    story.append(aw_table)

    # ── Recommendations ──────────────────────────────────────────────────────
    story += [section_header('Recommendations')]

    REF_NAME_STYLE  = S('refname',  fontName='Helvetica-Bold', fontSize=9.5, textColor=CHARCOAL, leading=13)
    REF_ROLE_STYLE  = S('refrole',  fontName='Helvetica-Oblique', fontSize=8.8, textColor=BLUE,  leading=12)
    REF_LINK_STYLE  = S('reflink',  fontName='Helvetica', fontSize=8, textColor=MIDGRAY, leading=11, spaceAfter=2)
    REF_QUOTE_STYLE = S('refquote', fontName='Helvetica-Oblique', fontSize=8.8, textColor=MIDGRAY,
                        leading=12.5, leftIndent=10, spaceAfter=3)

    refs = [
        {
            'name':  'Abdullah Ibn Anwar',
            'title': 'Senior VP Engineering, Pathao Ltd.',
            'linkedin': 'linkedin.com/in/abdullahibnanwar',
            'linkedin_url': 'https://www.linkedin.com/in/abdullahibnanwar/',
            'context': 'Colleague & manager during tenure at Pathao Limited (2019–2023)',
        },
        {
            'name':  'Cezary Skrzypek',
            'title': 'Business Intelligence Team Lead, G-Star RAW',
            'linkedin': 'linkedin.com/in/cskrzypek',
            'linkedin_url': 'https://www.linkedin.com/in/cskrzypek/',
            'context': 'Senior colleague & collaborator at G-Star Raw (2023–present)',
        },
    ]

    ref_cells = []
    for r in refs:
        cell = [
            Paragraph(r['name'],  REF_NAME_STYLE),
            Paragraph(r['title'], REF_ROLE_STYLE),
            Paragraph(f'<a href="{r["linkedin_url"]}" color="#2B6CB0">{r["linkedin"]}</a>', REF_LINK_STYLE),
            Paragraph(f'<i>{r["context"]}</i>', REF_QUOTE_STYLE),
        ]
        ref_cells.append(cell)

    ref_table = Table(
        [ref_cells],
        colWidths=[BODY_W * 0.5, BODY_W * 0.5],
    )
    ref_table.setStyle(TableStyle([
        ('VALIGN',       (0, 0), (-1, -1), 'TOP'),
        ('LEFTPADDING',  (0, 0), (-1, -1), 0),
        ('RIGHTPADDING', (1, 0), (1, 0),   0),
        ('RIGHTPADDING', (0, 0), (0, 0),   16),
        ('TOPPADDING',   (0, 0), (-1, -1), 0),
        ('BOTTOMPADDING',(0, 0), (-1, -1), 0),
        # Vertical divider between the two referees
        ('LINEAFTER',    (0, 0), (0, 0),   0.5, RULE_GR),
        ('LEFTPADDING',  (1, 0), (1, 0),   16),
    ]))
    story.append(ref_table)

    # ── Build ────────────────────────────────────────────────────────────────
    doc.build(story, onFirstPage=make_footer, onLaterPages=make_footer)
    print(f'Done: {output_path}')


if __name__ == '__main__':
    script_dir = os.path.dirname(os.path.abspath(__file__))
    output = os.path.join(script_dir, '..', 'RakibulHoque_CV.pdf')
    build_cv(os.path.normpath(output))
