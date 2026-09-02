#!/usr/bin/env python3
"""One-time visual and interaction rebuild for the official site.

Goals:
- keep the portrait and hero geometry stable across Arabic, English, and German;
- remove duplicate language navigation from footers;
- replace oversized identity cards with compact official contact channels;
- remove the public GitHub profile from visible and machine identity surfaces;
- rebuild the legacy German home, profile, and book pages on the current design system;
- correct dark-hero contrast, RTL handle direction, mobile spacing, and footer hierarchy;
- leave research claims, canonical URLs, and unpublished-book status unchanged.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TODAY = "2026-09-02"
MEDIUM = "https://medium.com/@AhmedAlhafiz"
INSTAGRAM = "https://www.instagram.com/ahmed_666_8"
EMAIL = "hhafz9924@gmail.com"

FOOTER_RE = re.compile(r"<footer\b[^>]*>.*?</footer>", re.IGNORECASE | re.DOTALL)
LANG_RE = re.compile(r"<html\b[^>]*\blang=[\"']([^\"']+)[\"']", re.IGNORECASE)
LANGS_RE = re.compile(
    r"(<div\b[^>]*\bclass=[\"'][^\"']*\blangs\b[^\"']*[\"'][^>]*>)(.*?)(</div>)",
    re.IGNORECASE | re.DOTALL,
)
GITHUB_ANCHOR_RE = re.compile(
    r"<a\b[^>]*\bhref=[\"']https://github\.com/Ahmed-Alhafiz/?[\"'][^>]*>.*?</a>",
    re.IGNORECASE | re.DOTALL,
)
MARKER = "/* Site UX Rebuild 10 — multilingual visual consistency */"

MEDIUM_SVG = """<svg viewBox="0 0 42 42" aria-hidden="true" focusable="false"><ellipse cx="11" cy="21" rx="9" ry="13" fill="currentColor"/><ellipse cx="28" cy="21" rx="4.6" ry="11.3" fill="currentColor"/><ellipse cx="38" cy="21" rx="2.1" ry="9.4" fill="currentColor"/></svg>"""
INSTAGRAM_SVG = """<svg viewBox="0 0 24 24" fill="none" aria-hidden="true" focusable="false"><rect x="3" y="3" width="18" height="18" rx="5" stroke="currentColor" stroke-width="1.7"/><circle cx="12" cy="12" r="4" stroke="currentColor" stroke-width="1.7"/><circle cx="17.3" cy="6.7" r="1" fill="currentColor"/></svg>"""
EMAIL_SVG = """<svg viewBox="0 0 24 24" fill="none" aria-hidden="true" focusable="false"><rect x="3" y="5" width="18" height="14" rx="2.5" stroke="currentColor" stroke-width="1.7"/><path d="M4.5 7l7.5 6 7.5-6" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"/></svg>"""


def social_icons(language: str, *, compact: bool = False) -> str:
    labels = {
        "ar": ("ميديوم", "إنستغرام", "البريد الإلكتروني"),
        "en": ("Medium", "Instagram", "Email"),
        "de": ("Medium", "Instagram", "E-Mail"),
    }[language]
    cls = "social-icons compact" if compact else "social-icons"
    return f"""<div class="{cls}" aria-label="{labels[0]}، {labels[1]}، {labels[2]}">
<a class="social-icon medium-mark" href="{MEDIUM}" target="_blank" rel="me noopener noreferrer" aria-label="{labels[0]}" title="{labels[0]}">{MEDIUM_SVG}<span class="sr-only">{labels[0]}</span></a>
<a class="social-icon" href="{INSTAGRAM}" target="_blank" rel="me noopener noreferrer" aria-label="{labels[1]}" title="{labels[1]}">{INSTAGRAM_SVG}<span class="sr-only">{labels[1]}</span></a>
<a class="social-icon" href="mailto:{EMAIL}" aria-label="{labels[2]}" title="{labels[2]}">{EMAIL_SVG}<span class="sr-only">{labels[2]}</span></a>
</div>"""


def footer(language: str) -> str:
    if language == "ar":
        identity = """<a class="footer-name" href="/"><strong>أحمد الحافظ</strong><span dir="ltr">Ahmed Alhafiz</span></a><p>الموقع الرسمي للمؤلفات والملفات البحثية الموثقة.</p>"""
        nav_label = "التنقل في تذييل الموقع"
        nav = """<a href="/">الرئيسية</a><a href="/articles/">الأبحاث</a><a href="/#works">المؤلفات</a><a href="/about/">عن الكاتب</a><a href="/methodology/">المنهج</a>"""
        contact = "تواصل رسمي"
        meta = "<span>© 2026 أحمد الحافظ</span><span>جميع الحقوق محفوظة</span>"
    elif language == "en":
        identity = """<a class="footer-name" href="/en/"><strong>Ahmed Alhafiz</strong><span lang="ar" dir="rtl">أحمد الحافظ</span></a><p>Official home of the books and evidence-led research dossiers.</p>"""
        nav_label = "Footer navigation"
        nav = """<a href="/en/">Home</a><a href="/en/articles/">Research</a><a href="/en/#works">Books</a><a href="/en/about/">About</a><a href="/en/methodology/">Method</a>"""
        contact = "Official contact"
        meta = "<span>© 2026 Ahmed Alhafiz</span><span>All rights reserved</span>"
    else:
        identity = """<a class="footer-name" href="/de/"><strong>Ahmed Alhafiz</strong><span lang="ar" dir="rtl">أحمد الحافظ</span></a><p>Offizielle Website des Autors und seiner Bücher.</p>"""
        nav_label = "Navigation im Seitenfuß"
        nav = """<a href="/de/">Start</a><a href="/de/#works">Bücher</a><a href="/de/about/">Über den Autor</a><a href="/de/#research">Forschung</a>"""
        contact = "Offizieller Kontakt"
        meta = "<span>© 2026 Ahmed Alhafiz</span><span>Alle Rechte vorbehalten</span>"

    return f"""<footer id="site-footer" class="site-footer">
  <div class="wrap footer-shell">
    <div class="footer-identity">{identity}</div>
    <nav class="footer-nav" aria-label="{nav_label}">{nav}</nav>
    <div class="footer-contact"><span class="footer-contact-label">{contact}</span>{social_icons(language, compact=True)}</div>
  </div>
  <div class="wrap footer-meta">{meta}</div>
</footer>"""


def contact_channel(url: str, icon: str, label: str, value: str, *, external: bool = True, medium: bool = False) -> str:
    target = ' target="_blank" rel="me noopener noreferrer"' if external else ""
    extra = " medium-mark" if medium else ""
    return f"""<a class="contact-channel{extra}" href="{url}"{target}>
  <span class="contact-icon">{icon}</span>
  <span class="contact-text"><strong>{label}</strong><small dir="ltr">{value}</small></span>
</a>"""


def contact_section(language: str) -> str:
    if language == "ar":
        kicker = "تواصل رسمي"
        title = "قنوات التواصل"
        text = "للتواصل المباشر أو متابعة النشر، استخدم القنوات الرسمية التالية فقط. لا تُعرض هنا حسابات تقنية أو روابط مكررة للغات."
        medium_label, insta_label, email_label = "Medium", "Instagram", "البريد الإلكتروني"
    elif language == "en":
        kicker = "Official contact"
        title = "Contact and publishing channels"
        text = "Use these verified channels for direct contact and publication updates. Technical profiles and duplicate language links are intentionally excluded."
        medium_label, insta_label, email_label = "Medium", "Instagram", "Email"
    else:
        kicker = "Offizieller Kontakt"
        title = "Kontakt und Veröffentlichungen"
        text = "Für direkte Anfragen und Veröffentlichungsneuigkeiten gelten ausschließlich diese offiziellen Kanäle. Technische Profile und doppelte Sprachlinks werden nicht angezeigt."
        medium_label, insta_label, email_label = "Medium", "Instagram", "E-Mail"

    channels = "".join(
        [
            contact_channel(MEDIUM, MEDIUM_SVG, medium_label, "@AhmedAlhafiz", medium=True),
            contact_channel(INSTAGRAM, INSTAGRAM_SVG, insta_label, "@ahmed_666_8"),
            contact_channel(f"mailto:{EMAIL}", EMAIL_SVG, email_label, EMAIL, external=False),
        ]
    )
    return f"""<section class="section contact-section" id="contact">
  <div class="wrap contact-grid">
    <div class="contact-copy"><div class="kicker">{kicker}</div><h2>{title}</h2><div class="rule"></div><p>{text}</p></div>
    <div class="contact-channels">{channels}</div>
  </div>
</section>"""


def header_de(*, current: str = "") -> str:
    def current_attr(name: str) -> str:
        return ' aria-current="page"' if current == name else ""

    return f"""<header class="site-header"><div class="wrap header-inner">
<a class="brand" href="/de/" aria-label="Ahmed Alhafiz — Startseite"><span class="brand-mark" aria-hidden="true">AA</span><span class="brand-copy"><strong>أحمد الحافظ</strong><span>Ahmed Alhafiz</span></span></a>
<nav class="nav" aria-label="Hauptnavigation"><a href="/de/"{current_attr('home')}>Start</a><a href="/de/#research">Forschung</a><a href="/de/#works">Bücher</a><a href="/de/about/"{current_attr('about')}>Über den Autor</a><a href="/de/#contact">Kontakt</a></nav>
<div class="langs" aria-label="Sprachen"><a href="/" hreflang="ar">AR</a><a href="/en/" hreflang="en">EN</a><a href="/de/" hreflang="de" aria-current="page">DE</a></div>
</div></header>"""


def language_switch_de(path: str) -> str:
    return f"""<div class="langs" aria-label="Sprachen"><a href="/books/{path}/" hreflang="ar">AR</a><a href="/en/books/{path}/" hreflang="en">EN</a><a href="/de/books/{path}/" hreflang="de" aria-current="page">DE</a></div>"""


def german_home() -> str:
    graph = {
        "@context": "https://schema.org",
        "@graph": [
            {
                "@type": "WebSite",
                "@id": "https://ahmed-alhafiz.github.io/#website",
                "url": "https://ahmed-alhafiz.github.io/",
                "name": "أحمد الحافظ",
                "alternateName": ["Ahmed Alhafiz", "Ahmad Alhafiz"],
                "inLanguage": ["ar", "en", "de"],
                "publisher": {"@id": "https://ahmed-alhafiz.github.io/#person"},
            },
            {
                "@type": "ProfilePage",
                "@id": "https://ahmed-alhafiz.github.io/de/#webpage",
                "url": "https://ahmed-alhafiz.github.io/de/",
                "name": "Ahmed Alhafiz — offizielle Autoren- und Buchseite",
                "description": "Die offizielle deutschsprachige Seite von Ahmed Alhafiz mit Autorenprofil, Büchern in Vorbereitung und Hinweisen auf vollständige Forschungsdossiers.",
                "inLanguage": "de",
                "dateModified": TODAY,
                "isPartOf": {"@id": "https://ahmed-alhafiz.github.io/#website"},
                "mainEntity": {"@id": "https://ahmed-alhafiz.github.io/#person"},
            },
            {
                "@type": "Person",
                "@id": "https://ahmed-alhafiz.github.io/#person",
                "name": "أحمد الحافظ",
                "alternateName": ["Ahmed Alhafiz", "Ahmad Alhafiz"],
                "url": "https://ahmed-alhafiz.github.io/about/",
                "image": {"@type": "ImageObject", "url": "https://ahmed-alhafiz.github.io/ahmed-alhafiz-author.png", "width": 1229, "height": 1536},
                "jobTitle": "Schriftsteller und Autor",
                "sameAs": [MEDIUM, INSTAGRAM],
            },
        ],
    }
    return f"""<!doctype html>
<html lang="de" dir="ltr">
<head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<title>Ahmed Alhafiz — أحمد الحافظ | Offizielle Autoren- und Buchseite</title>
<meta name="description" content="Offizielle deutschsprachige Seite von Ahmed Alhafiz — أحمد الحافظ: Autorenprofil, Bücher in Vorbereitung und vollständige Forschungsdossiers auf Arabisch und Englisch.">
<meta name="robots" content="index,follow,max-image-preview:large,max-snippet:-1"><meta name="theme-color" content="#0b1724">
<link rel="canonical" href="https://ahmed-alhafiz.github.io/de/"><link rel="alternate" hreflang="ar" href="https://ahmed-alhafiz.github.io/"><link rel="alternate" hreflang="en" href="https://ahmed-alhafiz.github.io/en/"><link rel="alternate" hreflang="de" href="https://ahmed-alhafiz.github.io/de/"><link rel="alternate" hreflang="x-default" href="https://ahmed-alhafiz.github.io/">
<link rel="icon" href="/favicon.png" type="image/png" sizes="96x96"><link rel="stylesheet" href="/assets/site-v2.css"><link rel="stylesheet" href="/assets/articles.css">
<meta property="og:type" content="profile"><meta property="og:site_name" content="Ahmed Alhafiz — أحمد الحافظ"><meta property="og:title" content="Ahmed Alhafiz — offizielle Autoren- und Buchseite"><meta property="og:description" content="Bücher in Vorbereitung, Autorenprofil und Hinweise auf überprüfbare Forschungsdossiers."><meta property="og:url" content="https://ahmed-alhafiz.github.io/de/"><meta property="og:image" content="https://ahmed-alhafiz.github.io/ahmed-alhafiz-social-card.png"><meta property="og:image:width" content="1200"><meta property="og:image:height" content="630"><meta property="og:locale" content="de_DE"><meta name="twitter:card" content="summary_large_image">
<script type="application/ld+json">{json.dumps(graph, ensure_ascii=False, separators=(',', ':'))}</script>
</head><body><a class="skip" href="#main">Zum Inhalt springen</a>{header_de(current='home')}
<main id="main">
<section class="home-hero"><div class="wrap home-hero-grid"><div><div class="eyebrow">Offizielle Autoren- und Forschungsplattform</div><h1>Ahmed Alhafiz</h1><div class="latin" lang="ar" dir="rtl">أحمد الحافظ</div><p class="hero-statement">Ein arabischer Schriftsteller an der Schnittstelle von Erzählung und Recherche: Schöpfung und Wissen, Erinnerung und Zivilisation, Angst und menschliche Erfahrung.</p><div class="actions"><a class="btn primary" href="#works">Bücher entdecken</a><a class="btn light" href="#research">Forschung ansehen</a></div><div class="hero-index"><a href="#research"><strong>Forschungsdossiers</strong><span>Behauptung, Beleg, Grenzen, Quellen</span></a><a href="#works"><strong>Bücher in Vorbereitung</strong><span>Romane und intellektuelle Sachtexte</span></a><a href="/de/about/"><strong>Autorenprofil</strong><span>Projekt, Methode und bestätigte Kanäle</span></a></div></div><div class="hero-portrait"><img src="/ahmed-alhafiz-author.png" width="1229" height="1536" alt="Ahmed Alhafiz — أحمد الحافظ" fetchpriority="high"></div></div></section>
<section class="section"><div class="wrap mission-grid"><div><div class="kicker">Das Schreibprojekt</div><h2>Erzählung und Untersuchung unter einer gemeinsamen Frage</h2><div class="rule"></div><div class="prose"><p>Die Bücher bewegen sich zwischen historischem Roman, psychologischem Horror und religiös-intellektueller Sachliteratur. Gemeinsam ist ihnen die Frage, wie Menschen Texte, Ereignisse, Angst, Macht und Erinnerung deuten.</p><p>Die Forschungsdossiers sind keine verlängerte Werbung für unveröffentlichte Bücher. Sie arbeiten mit externen Quellen, benennen Grenzen und legen den jeweiligen Prüfstatus offen.</p></div></div><aside class="mission-note"><strong>Klare Publikationsgrenze</strong><p>Alle Bücher sind weiterhin als „in Vorbereitung“ gekennzeichnet. Unbestätigte Verlags-, ISBN-, Verkaufs- oder Rezensionsangaben werden nicht veröffentlicht.</p></aside></div></section>
<section class="section alt" id="research"><div class="wrap"><div class="kicker">Vollständige Forschungsfassungen</div><h2>Ausgewählte Dossiers auf Englisch</h2><div class="rule"></div><div class="track-grid"><article class="track-card"><div><span class="track-no">COSMOLOGY</span><h3><a href="/en/articles/ratq-fatq-big-bang/" hreflang="en">Ratq, fatq and the Big Bang</a></h3><p>Text, klassische Auslegung, Beobachtung, kosmologisches Modell und philosophische Folgerung werden getrennt geprüft.</p></div><a href="/en/articles/ratq-fatq-big-bang/" hreflang="en">Englisches Dossier öffnen →</a></article><article class="track-card"><div><span class="track-no">WATER / POWER</span><h3><a href="/en/articles/water-civilization-power/" hreflang="en">Water, Civilization and Power</a></h3><p>Eine institutionelle Analyse von Infrastruktur, Daten, Zuteilung, Verantwortung, Wartung und Gerechtigkeit.</p></div><a href="/en/articles/water-civilization-power/" hreflang="en">Englisches Dossier öffnen →</a></article><article class="track-card"><div><span class="track-no">TRANSPARENZ</span><h3><a href="/en/research-status/" hreflang="en">Prüfstatus statt bloßer Behauptung</a></h3><p>Autorenprüfung, automatisierte Kontrolle, Fachprüfung und Peer Review werden ausdrücklich unterschieden.</p></div><a href="/en/research-status/" hreflang="en">Prüfregister öffnen →</a></article></div></div></section>
<section class="section" id="works"><div class="wrap"><div class="kicker">Bücher in Vorbereitung</div><h2>Werke</h2><div class="rule"></div><div class="works-grid">
<article class="book-card"><a href="/de/books/sirou-fi-alard/"><img src="/sirou-fi-alard-cover.webp" width="800" height="1200" alt="قل سيروا في الأرض فانظروا كيف بدأ الخلق" loading="lazy"><h3 lang="ar" dir="rtl">قل سيروا في الأرض فانظروا كيف بدأ الخلق</h3><p>Religiös-intellektuelles Sachbuch · in Vorbereitung</p><span class="more">Buchseite →</span></a></article>
<article class="book-card"><a href="/de/books/umm-abbas/"><img src="/umm-abbas-cover.webp" width="800" height="1200" alt="أم عباس لجلب الحبيب ورد المطلقة" loading="lazy"><h3 lang="ar" dir="rtl">أم عباس لجلب الحبيب ورد المطلقة</h3><p>Psychologischer Horrorroman · in Vorbereitung</p><span class="more">Buchseite →</span></a></article>
<article class="book-card"><a href="/de/books/juhayman/"><img src="/juhayman-cover.webp" width="800" height="1200" alt="جهيمان — القيامة بين الركن والمقام" loading="lazy"><h3 lang="ar" dir="rtl">جهيمان — القيامة بين الركن والمقام</h3><p>Historisch-religiöser Roman · in Vorbereitung</p><span class="more">Buchseite →</span></a></article>
<article class="book-card"><a href="/de/books/kitab-al-kutub/"><img src="/kitab-al-kutub-cover.webp" width="800" height="1200" alt="كتاب الكتب" loading="lazy"><h3 lang="ar" dir="rtl">كتاب الكتب</h3><p>Historisch-philosophischer Roman · in Vorbereitung</p><span class="more">Buchseite →</span></a></article>
</div></div></section>
{contact_section('de')}
</main>{footer('de')}</body></html>"""


def german_about() -> str:
    graph = {
        "@context": "https://schema.org",
        "@graph": [
            {"@type": "ProfilePage", "@id": "https://ahmed-alhafiz.github.io/de/about/#page", "url": "https://ahmed-alhafiz.github.io/de/about/", "name": "Ahmed Alhafiz — Schriftsteller und Autor", "description": "Offizielles deutschsprachiges Autorenprofil von Ahmed Alhafiz.", "inLanguage": "de", "dateModified": TODAY, "isPartOf": {"@id": "https://ahmed-alhafiz.github.io/#website"}, "mainEntity": {"@id": "https://ahmed-alhafiz.github.io/#person"}},
            {"@type": "Person", "@id": "https://ahmed-alhafiz.github.io/#person", "name": "أحمد الحافظ", "alternateName": ["Ahmed Alhafiz", "Ahmad Alhafiz"], "url": "https://ahmed-alhafiz.github.io/about/", "image": {"@type": "ImageObject", "url": "https://ahmed-alhafiz.github.io/ahmed-alhafiz-author.png", "width": 1229, "height": 1536}, "jobTitle": "Schriftsteller und Autor", "sameAs": [MEDIUM, INSTAGRAM]},
            {"@type": "BreadcrumbList", "itemListElement": [{"@type": "ListItem", "position": 1, "name": "Start", "item": "https://ahmed-alhafiz.github.io/de/"}, {"@type": "ListItem", "position": 2, "name": "Über den Autor", "item": "https://ahmed-alhafiz.github.io/de/about/"}]},
        ],
    }
    return f"""<!doctype html><html lang="de" dir="ltr"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover"><title>Ahmed Alhafiz — Schriftsteller und Autor</title><meta name="description" content="Offizielles deutschsprachiges Autorenprofil von Ahmed Alhafiz — أحمد الحافظ: Schreibprojekt, Bücher in Vorbereitung und überprüfbare Forschungsarbeit."><meta name="robots" content="index,follow,max-image-preview:large,max-snippet:-1"><meta name="theme-color" content="#0b1724"><link rel="canonical" href="https://ahmed-alhafiz.github.io/de/about/"><link rel="alternate" hreflang="ar" href="https://ahmed-alhafiz.github.io/about/"><link rel="alternate" hreflang="en" href="https://ahmed-alhafiz.github.io/en/about/"><link rel="alternate" hreflang="de" href="https://ahmed-alhafiz.github.io/de/about/"><link rel="alternate" hreflang="x-default" href="https://ahmed-alhafiz.github.io/about/"><link rel="icon" href="/favicon.png" type="image/png" sizes="96x96"><link rel="stylesheet" href="/assets/site-v2.css"><link rel="stylesheet" href="/assets/articles.css"><meta property="og:type" content="profile"><meta property="og:title" content="Ahmed Alhafiz — Schriftsteller und Autor"><meta property="og:description" content="Offizielles Autorenprofil, Bücher in Vorbereitung und transparente Forschungsarbeit."><meta property="og:url" content="https://ahmed-alhafiz.github.io/de/about/"><meta property="og:image" content="https://ahmed-alhafiz.github.io/ahmed-alhafiz-social-card.png"><meta property="og:locale" content="de_DE"><meta name="twitter:card" content="summary_large_image"><script type="application/ld+json">{json.dumps(graph, ensure_ascii=False, separators=(',', ':'))}</script></head><body><a class="skip" href="#main">Zum Inhalt springen</a>{header_de(current='about')}<main id="main">
<section class="profile-hero"><div class="wrap profile-grid"><div><div class="kicker">Offizielles Autorenprofil</div><h1>Ahmed Alhafiz</h1><div class="profile-latin" lang="ar" dir="rtl">أحمد الحافظ</div><p class="lead">Ein arabischer Schriftsteller, der Erzählung und Recherche als zwei Wege nutzt, um Wissen, Erinnerung, Angst, Glauben und Macht zu prüfen.</p><div class="actions"><a class="btn primary" href="/de/#works">Bücher</a><a class="btn" href="/de/#research">Forschung</a></div></div><div class="profile-portrait"><img src="/ahmed-alhafiz-author.png" width="1229" height="1536" alt="Ahmed Alhafiz — أحمد الحافظ"></div></div></section>
<section class="section"><div class="wrap mission-grid"><div><div class="kicker">Das Projekt</div><h2>Erzählung prüft den Menschen; Recherche prüft die Behauptung</h2><div class="rule"></div><div class="prose"><p>Die Arbeit bewegt sich zwischen historischem und religiösem Roman, psychologischem Horror und intellektueller Sachliteratur. Im Mittelpunkt stehen unsichere Grenzen: Text und Auslegung, Ereignis und Erinnerung, Angst und Ursache, Beleg und Schlussfolgerung.</p><p>Die Forschungsdossiers sind eigenständige Veröffentlichungen. Sie stützen sich auf Quellen außerhalb der Manuskripte, benennen Unsicherheit und zeigen offen, welche Art von Prüfung bereits stattgefunden hat.</p></div></div><aside class="profile-facts"><div><span>Offizieller Name</span><strong>Ahmed Alhafiz · أحمد الحافظ</strong></div><div><span>Publikationsmodell</span><strong>Bücher in Vorbereitung + unabhängige Autorenrecherche</strong></div><div><span>Sprachen</span><strong>Arabisch und Englisch; deutschsprachige Informationsseiten</strong></div><div><span>Prüfstatus</span><strong>Auf jeder Forschungsseite ausdrücklich ausgewiesen</strong></div></aside></div></section>
<section class="section alt"><div class="wrap"><div class="kicker">Arbeitsweise</div><h2>Quellen, begrenzte Aussagen und sichtbarer Prüfstatus</h2><div class="rule"></div><div class="track-grid"><article class="track-card"><div><span class="track-no">01 / QUELLE</span><h3>Quelle vor Ton</h3><p>Originaltexte, Primärstudien und zuständige Institutionen gehen Zusammenfassungen und Rhetorik voraus.</p></div><a href="/en/methodology/" hreflang="en">Englische Methodenseite →</a></article><article class="track-card"><div><span class="track-no">02 / AUSSAGE</span><h3>Begrenzte Behauptungen</h3><p>Ergebnisse werden in prüfbare Einheiten zerlegt, statt Schlusslücken in eleganter Sprache zu verstecken.</p></div><a href="/en/articles/ratq-fatq-big-bang/evidence/" hreflang="en">Beispiel öffnen →</a></article><article class="track-card"><div><span class="track-no">03 / STATUS</span><h3>Offene Prüfung</h3><p>Autorenprüfung, automatisierte Prüfung, Fachprüfung und Peer Review sind nicht dasselbe.</p></div><a href="/en/research-status/" hreflang="en">Prüfregister →</a></article></div></div></section>
<section class="section" id="works"><div class="wrap"><div class="kicker">Bücher in Vorbereitung</div><h2>Werke</h2><div class="rule"></div><div class="works-grid"><article class="book-card"><a href="/de/books/sirou-fi-alard/"><img src="/sirou-fi-alard-cover.webp" width="800" height="1200" alt="قل سيروا في الأرض فانظروا كيف بدأ الخلق" loading="lazy"><h3 lang="ar" dir="rtl">قل سيروا في الأرض فانظروا كيف بدأ الخلق</h3><p>Religion und Wissenschaft</p><span class="more">Buchseite →</span></a></article><article class="book-card"><a href="/de/books/umm-abbas/"><img src="/umm-abbas-cover.webp" width="800" height="1200" alt="أم عباس لجلب الحبيب ورد المطلقة" loading="lazy"><h3 lang="ar" dir="rtl">أم عباس لجلب الحبيب ورد المطلقة</h3><p>Psychologischer Horror</p><span class="more">Buchseite →</span></a></article><article class="book-card"><a href="/de/books/juhayman/"><img src="/juhayman-cover.webp" width="800" height="1200" alt="جهيمان — القيامة بين الركن والمقام" loading="lazy"><h3 lang="ar" dir="rtl">جهيمان — القيامة بين الركن والمقام</h3><p>Historisch-religiöser Roman</p><span class="more">Buchseite →</span></a></article><article class="book-card"><a href="/de/books/kitab-al-kutub/"><img src="/kitab-al-kutub-cover.webp" width="800" height="1200" alt="كتاب الكتب" loading="lazy"><h3 lang="ar" dir="rtl">كتاب الكتب</h3><p>Historisch-philosophischer Roman</p><span class="more">Buchseite →</span></a></article></div></div></section>
{contact_section('de')}
</main>{footer('de')}</body></html>"""


GERMAN_BOOKS = {
    "sirou-fi-alard": {
        "title_ar": "قل سيروا في الأرض فانظروا كيف بدأ الخلق",
        "title_de": "Sirou fi al-Ard — Reist durch die Erde",
        "genre": "Religiös-intellektuelles Sachbuch",
        "cover": "sirou-fi-alard-cover.webp",
        "description": "Ein religiös-intellektuelles Buch von Ahmed Alhafiz über Schöpfung, Offenbarung, Wissenschaft und die Grenzen menschlicher Deutung.",
        "paragraphs": [
            "„قل سيروا في الأرض فانظروا كيف بدأ الخلق“ ist ein religiös-intellektuelles Sachbuch in Vorbereitung. Die koranische Aufforderung zum Reisen und Beobachten wird als Methode des Nachdenkens und Forschens gelesen, nicht nur als rhetorische Formel.",
            "Das Buch trennt sorgfältig die Ebenen: Was sagt der Text tatsächlich? Was kann Wissenschaft tatsächlich zeigen? Wo beginnt die menschliche Auslegung beider Bereiche? Ziel ist kein künstlicher Sieg einer Seite, sondern eine verantwortliche Beziehung zwischen Glauben, Vernunft und Beobachtung.",
            "Die öffentliche Seite beschreibt nur die Themen und den Arbeitsstand. Kapitel, unbestätigte Verlagsdaten, ISBN, Verkaufsangaben und Rezensionen werden vor der offiziellen Veröffentlichung nicht behauptet.",
        ],
        "related": [
            ("/en/articles/ratq-fatq-big-bang/", "Ratq, fatq and the Big Bang", "Vollständiges englisches Dossier zu Text, Auslegung, Beobachtung und kosmologischem Modell."),
            ("/en/articles/water-civilization-power/", "Water, Civilization and Power", "Vollständiges englisches Dossier zu Infrastruktur, Zuteilung, Verantwortung und Gerechtigkeit."),
        ],
    },
    "umm-abbas": {
        "title_ar": "أم عباس لجلب الحبيب ورد المطلقة",
        "title_de": "Umm Abbas — Den Geliebten zurückbringen und die Geschiedene zurückführen",
        "genre": "Psychologischer Horrorroman",
        "cover": "umm-abbas-cover.webp",
        "description": "Ein psychologischer Horrorroman in Vorbereitung über Angst, Zweifel, Familie, Medizin, religiöse Deutung und den Verlust von Vertrauen.",
        "paragraphs": [
            "„أم عباس لجلب الحبيب ورد المطلقة“ ist ein psychologischer Horrorroman in Vorbereitung über ein verängstigtes Haus und eine Familie, die nicht mehr weiß, ob das Geschehen Krankheit, Einbildung, Manipulation oder etwas Unerklärliches ist.",
            "Der Horror entsteht nicht nur aus einem möglichen übernatürlichen Ereignis, sondern aus konkurrierenden Deutungen. Körper, Erinnerung und Verhalten werden zum Streitfeld; Nähe schützt nicht automatisch, wenn Angst die Familie dazu bringt, Verantwortung an eine ungeprüfte Autorität abzugeben.",
            "Diese Seite bleibt absichtlich zurückhaltend: Sie verrät keine entscheidenden Wendungen und veröffentlicht keine unbestätigten Verlags-, ISBN-, Verkaufs- oder Rezensionsdaten.",
        ],
        "related": [
            ("/articles/spiritual-healing-exploitation-safeguarding/", "Wenn spirituelle Heilung zur Ausbeutung wird", "Evidenzbasierter Schutzleitfaden; vollständiger Text derzeit auf Arabisch."),
            ("/articles/sleep-paralysis-jathoom/", "Schlafparalyse und die gefühlte Präsenz", "Medizinisch-kultureller Überblick; vollständiger Text derzeit auf Arabisch."),
        ],
    },
    "juhayman": {
        "title_ar": "جهيمان — القيامة بين الركن والمقام",
        "title_de": "Juhayman — Die Auferstehung zwischen Rukn und Maqam",
        "genre": "Historisch-religiöser Roman",
        "cover": "juhayman-cover.webp",
        "description": "Ein historisch-religiöser Roman in Vorbereitung über die Besetzung der Großen Moschee 1979 und die geistigen Wege geschlossener Gewissheit.",
        "paragraphs": [
            "Der Roman geht von der Besetzung der Großen Moschee in Mekka am 20. November 1979 aus und untersucht nicht nur das Ereignis, sondern den geistigen und psychologischen Weg dorthin.",
            "Im Mittelpunkt steht die Frage, wann religiöser Eifer in eine Auslegung übergeht, die keine Korrektur mehr zulässt, und wie Gruppentreue, Endzeitgewissheit und Macht über die Bedeutung heiliger Texte miteinander verschmelzen.",
            "Das Werk befindet sich in Vorbereitung. Die öffentliche Seite nennt keine unbestätigten Verlags-, ISBN-, Verkaufs- oder Rezensionsangaben und veröffentlicht keine längeren Manuskriptauszüge.",
        ],
        "related": [],
    },
    "kitab-al-kutub": {
        "title_ar": "كتاب الكتب",
        "title_de": "Kitab al-Kutub — Das Buch der Bücher",
        "genre": "Historisch-philosophischer Roman",
        "cover": "kitab-al-kutub-cover.webp",
        "description": "Ein historisch-philosophischer Roman in Vorbereitung über Macht, Erinnerung, Schreiben und inneren Zerfall.",
        "paragraphs": [
            "„كتاب الكتب“ ist ein historisch-philosophischer Roman in Vorbereitung über Macht, Erinnerung, Schreiben und den langen inneren Zerfall, der dem sichtbaren Fall einer Stadt vorausgehen kann.",
            "Geschichte dient nicht als bloße Kulisse. Der Roman untersucht, wer Ereignisse festhält, wie offizielle Erzählungen entstehen und warum ein verfälschtes Gedächtnis länger leben kann als die Gewalt, aus der es hervorging.",
            "Die öffentliche Seite bleibt eine sachliche Vorschau. Verlagsdaten, ISBN, Verkaufsangaben, Rezensionen und längere Auszüge werden erst nach verifizierter Veröffentlichung ergänzt.",
        ],
        "related": [],
    },
}


def german_book(slug: str, data: dict) -> str:
    canonical = f"https://ahmed-alhafiz.github.io/de/books/{slug}/"
    ar = f"https://ahmed-alhafiz.github.io/books/{slug}/"
    en = f"https://ahmed-alhafiz.github.io/en/books/{slug}/"
    graph = {
        "@context": "https://schema.org",
        "@graph": [
            {"@type": "Book", "@id": f"{ar}#book", "name": data["title_ar"], "alternateName": data["title_de"], "url": ar, "image": f"https://ahmed-alhafiz.github.io/{data['cover']}", "author": {"@id": "https://ahmed-alhafiz.github.io/#person"}, "genre": data["genre"], "inLanguage": "ar", "description": data["description"], "creativeWorkStatus": "Forthcoming; not yet officially published"},
            {"@type": "WebPage", "@id": f"{canonical}#page", "url": canonical, "name": f"{data['title_de']} | Ahmed Alhafiz", "description": data["description"], "inLanguage": "de", "dateModified": TODAY, "isPartOf": {"@id": "https://ahmed-alhafiz.github.io/#website"}, "mainEntity": {"@id": f"{ar}#book"}},
            {"@type": "BreadcrumbList", "itemListElement": [{"@type": "ListItem", "position": 1, "name": "Start", "item": "https://ahmed-alhafiz.github.io/de/"}, {"@type": "ListItem", "position": 2, "name": "Bücher", "item": "https://ahmed-alhafiz.github.io/de/#works"}, {"@type": "ListItem", "position": 3, "name": data["title_de"], "item": canonical}]},
        ],
    }
    paragraphs = "".join(f"<p>{p}</p>" for p in data["paragraphs"])
    related = ""
    if data["related"]:
        cards = "".join(
            f'<article class="article-card"><div><div class="kicker">Thematisch verbunden</div><h2><a href="{url}">{title}</a></h2><p>{summary}</p></div><span class="tag">Öffnen</span></article>'
            for url, title, summary in data["related"]
        )
        related = f"""<section class="section alt" id="research"><div class="wrap"><div class="kicker">Vom Buch zur unabhängigen Frage</div><h2>Verwandte Forschungsdossiers</h2><div class="rule"></div><p class="prose">Die Dossiers verwenden externe Quellen. Das unveröffentlichte Buch ist thematischer Ausgangspunkt, nicht Beleg.</p><div class="article-list">{cards}</div></div></section>"""

    header = f"""<header class="site-header"><div class="wrap header-inner"><a class="brand" href="/de/" aria-label="Ahmed Alhafiz — Startseite"><span class="brand-mark" aria-hidden="true">AA</span><span class="brand-copy"><strong>أحمد الحافظ</strong><span>Ahmed Alhafiz</span></span></a><nav class="nav" aria-label="Hauptnavigation"><a href="/de/">Start</a><a href="/de/#research">Forschung</a><a href="/de/#works">Bücher</a><a href="/de/about/">Über den Autor</a><a href="/de/#contact">Kontakt</a></nav>{language_switch_de(slug)}</div></header>"""
    research_action = '<a class="btn primary" href="#research">Verwandte Forschung</a>' if data["related"] else '<a class="btn primary" href="#about-book">Zum Buch</a>'
    return f"""<!doctype html><html lang="de" dir="ltr"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover"><title>{data['title_de']} | Ahmed Alhafiz</title><meta name="description" content="{data['description']}"><meta name="robots" content="index,follow,max-image-preview:large,max-snippet:-1"><meta name="theme-color" content="#0b1724"><link rel="canonical" href="{canonical}"><link rel="alternate" hreflang="ar" href="{ar}"><link rel="alternate" hreflang="en" href="{en}"><link rel="alternate" hreflang="de" href="{canonical}"><link rel="alternate" hreflang="x-default" href="{ar}"><link rel="icon" href="/favicon.png" type="image/png" sizes="96x96"><link rel="stylesheet" href="/assets/site-v2.css"><link rel="stylesheet" href="/assets/articles.css"><meta property="og:type" content="website"><meta property="og:site_name" content="Ahmed Alhafiz — أحمد الحافظ"><meta property="og:title" content="{data['title_de']}"><meta property="og:description" content="{data['description']}"><meta property="og:url" content="{canonical}"><meta property="og:image" content="https://ahmed-alhafiz.github.io/{data['cover']}"><meta property="og:locale" content="de_DE"><meta name="twitter:card" content="summary_large_image"><script type="application/ld+json">{json.dumps(graph, ensure_ascii=False, separators=(',', ':'))}</script></head><body><a class="skip" href="#main">Zum Inhalt springen</a>{header}<main id="main"><section class="book-hero"><div class="wrap book-hero-grid"><div class="book-hero-cover"><img src="/{data['cover']}" width="800" height="1200" alt="{data['title_ar']}"></div><div><div class="breadcrumbs"><a href="/de/">Start</a> / Bücher</div><div class="kicker">{data['genre']} · in Vorbereitung</div><h1 lang="ar" dir="rtl">{data['title_ar']}</h1><div class="subtitle">{data['title_de']}</div><p class="lead">{data['description']}</p><div class="meta-row"><span class="pill">Status: in Vorbereitung</span><span class="pill">{data['genre']}</span><span class="pill">Autor: Ahmed Alhafiz</span></div><div class="actions">{research_action}<a class="btn" href="/de/about/">Über den Autor</a></div></div></div></section><section class="section" id="about-book"><div class="wrap book-editorial"><div><div class="kicker">Über das Werk</div><h2>Sachliche Vorschau ohne unnötige Offenlegung</h2><div class="rule"></div><div class="prose">{paragraphs}</div></div><aside class="publication-note"><strong>Publikationstransparenz</strong><p>Das Werk ist noch nicht offiziell erschienen. Verlag, ISBN, endgültiger Termin, Verkaufsdaten und Rezensionen werden erst nach öffentlicher Bestätigung ergänzt.</p></aside></div></section>{related}</main>{footer('de')}</body></html>"""


def replace_about_contact(path: Path, language: str) -> None:
    html = path.read_text(encoding="utf-8")
    section = contact_section(language)
    if language == "ar":
        pattern = re.compile(
            r'<section class="section"><div class="wrap"><div class="kicker">Official identity</div>.*?</section>',
            re.DOTALL,
        )
        html, count = pattern.subn(section, html, count=1)
        if count != 1:
            raise RuntimeError("Arabic about contact section was not found exactly once")
    else:
        if 'id="contact"' not in html:
            if html.count("</main>") != 1:
                raise RuntimeError(f"{path}: expected one </main>")
            html = html.replace("</main>", section + "\n</main>", 1)
    path.write_text(html, encoding="utf-8")


def remove_github_identity(html: str) -> str:
    html = GITHUB_ANCHOR_RE.sub("", html)
    html = re.sub(r',\s*"https://github\.com/Ahmed-Alhafiz/?"', "", html)
    html = re.sub(r'"https://github\.com/Ahmed-Alhafiz/?"\s*,', "", html)
    return html


def mark_active_language(html: str, language: str) -> str:
    language = language[:2].lower()

    def rewrite(match: re.Match[str]) -> str:
        body = re.sub(r'\s+aria-current=["\']page["\']', "", match.group(2), flags=re.IGNORECASE)
        pattern = re.compile(
            rf'(<a\b(?=[^>]*\bhreflang=["\']{re.escape(language)}["\'])[^>]*)>',
            re.IGNORECASE,
        )
        body, _ = pattern.subn(r'\1 aria-current="page">', body, count=1)
        return match.group(1) + body + match.group(3)

    return LANGS_RE.sub(rewrite, html)


def patch_existing_pages() -> None:
    ar_home = ROOT / "index.html"
    html = ar_home.read_text(encoding="utf-8")
    html = html.replace("الموقع الرسمي · Official author &amp; research site", "الموقع الرسمي للكاتب والباحث")
    html = html.replace('<a class="btn light" href="/en/">English edition</a>', "")
    html = html.replace(">المعايير التحريرية</a>", ">المنهج</a>")
    ar_home.write_text(html, encoding="utf-8")

    en_home = ROOT / "en/index.html"
    html = en_home.read_text(encoding="utf-8")
    html = html.replace("Official author and research site", "Official author and research platform")
    html = html.replace('<a class="btn light" href="/">النسخة العربية</a>', "")
    html = html.replace(">Editorial standards</a>", ">Method</a>")
    en_home.write_text(html, encoding="utf-8")

    ar_about = ROOT / "about/index.html"
    html = ar_about.read_text(encoding="utf-8")
    html = html.replace("الصفحة الرسمية · Author profile", "الملف الرسمي للكاتب")
    html = html.replace('<a class="btn" href="/en/about/">English profile</a>', "")
    html = html.replace(">المعايير التحريرية</a>", ">المنهج</a>")
    ar_about.write_text(html, encoding="utf-8")
    replace_about_contact(ar_about, "ar")

    en_about = ROOT / "en/about/index.html"
    html = en_about.read_text(encoding="utf-8")
    html = html.replace("Official profile · الصفحة الرسمية", "Official author profile")
    html = html.replace('<a class="btn" href="/about/">الملف العربي</a>', "")
    html = html.replace(">Editorial standards</a>", ">Method</a>")
    en_about.write_text(html, encoding="utf-8")
    replace_about_contact(en_about, "en")


def rewrite_german_pages() -> None:
    (ROOT / "de/index.html").write_text(german_home(), encoding="utf-8")
    (ROOT / "de/about/index.html").write_text(german_about(), encoding="utf-8")
    for slug, data in GERMAN_BOOKS.items():
        path = ROOT / f"de/books/{slug}/index.html"
        if not path.exists():
            raise FileNotFoundError(path)
        path.write_text(german_book(slug, data), encoding="utf-8")


def rewrite_all_public_html() -> None:
    changed = 0
    for path in sorted(ROOT.rglob("*.html")):
        if ".git" in path.parts or path.name == "404.html":
            continue
        html = path.read_text(encoding="utf-8")
        match = LANG_RE.search(html)
        if not match:
            raise RuntimeError(f"{path.relative_to(ROOT)}: missing html lang")
        language = match.group(1)[:2].lower()
        if language not in {"ar", "en", "de"}:
            continue
        html = remove_github_identity(html)
        footers = FOOTER_RE.findall(html)
        if len(footers) != 1:
            raise RuntimeError(f"{path.relative_to(ROOT)}: expected one footer, found {len(footers)}")
        html = FOOTER_RE.sub(footer(language), html, count=1)
        html = mark_active_language(html, language)
        if language == "ar":
            html = html.replace(">المعايير التحريرية</a>", ">المنهج</a>")
        elif language == "en":
            html = html.replace(">Editorial standards</a>", ">Method</a>")
        path.write_text(html, encoding="utf-8")
        changed += 1
    print(f"Standardized identity and footer surfaces on {changed} public HTML pages")


CSS = r'''

/* Site UX Rebuild 10 — multilingual visual consistency */
.sr-only{position:absolute!important;width:1px!important;height:1px!important;padding:0!important;margin:-1px!important;overflow:hidden!important;clip:rect(0,0,0,0)!important;white-space:nowrap!important;border:0!important}
html[lang="en"] body,html[lang="de"] body{line-height:1.76;hyphens:auto}

/* Stable portrait geometry in every language */
.home-hero-grid,.profile-grid{grid-template-columns:minmax(0,1fr) minmax(250px,340px);gap:clamp(44px,6vw,78px)}
.hero-portrait,.profile-portrait{width:clamp(250px,27vw,340px);aspect-ratio:4/5;justify-self:end;align-self:center}
.hero-portrait img,.profile-portrait img{width:100%;height:100%;aspect-ratio:4/5;object-fit:cover;object-position:center 20%;background:#87796d}
html[dir="rtl"] .hero-portrait::before,html[dir="rtl"] .profile-portrait::after{inset:16px 16px -16px -16px}
html[dir="ltr"] .hero-portrait::before,html[dir="ltr"] .profile-portrait::after{inset:16px -16px -16px 16px}
.home-hero-grid{min-height:620px;padding:70px 0 76px}.profile-grid{min-height:560px;padding:68px 0 74px}
.home-hero h1{font-size:clamp(52px,6.2vw,86px)}.profile-hero h1{font-size:clamp(48px,5.7vw,76px)}
.home-hero .hero-statement,.profile-hero .lead{max-width:720px;line-height:1.72}

/* Readable controls on dark heroes */
.home-hero .btn.primary,.profile-hero .btn.primary,.book-hero .btn.primary{background:var(--copper-2);border-color:var(--copper-2);color:#fff}
.home-hero .btn.primary:hover,.profile-hero .btn.primary:hover,.book-hero .btn.primary:hover{background:#c47a59;border-color:#c47a59}
.home-hero .btn:not(.primary),.profile-hero .btn:not(.primary),.book-hero .btn:not(.primary){color:#f8f5ee;border-color:rgba(255,255,255,.40);background:rgba(255,255,255,.055)}
.home-hero .btn:not(.primary):hover,.profile-hero .btn:not(.primary):hover,.book-hero .btn:not(.primary):hover{border-color:#f0ad85;background:rgba(255,255,255,.10)}
.book-hero .pill{color:#e3ebf0;border-color:rgba(255,255,255,.24);background:rgba(255,255,255,.06)}
.book-hero .breadcrumbs{color:#aebdc8}.book-hero .breadcrumbs a{color:#f0c3a5}

/* Compact, dignified contact surface */
.contact-section{background:linear-gradient(135deg,#f5f1e8 0%,#ece6da 100%)}
.contact-grid{display:grid;grid-template-columns:minmax(260px,.72fr) minmax(0,1.28fr);gap:clamp(38px,6vw,78px);align-items:center}
.contact-copy p{max-width:620px;margin:0;color:#586570;font-size:17px;line-height:1.85}
.contact-channels{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:12px}
.contact-channel{min-width:0;display:flex;align-items:center;gap:13px;padding:16px 17px;border:1px solid var(--line);border-radius:16px;background:rgba(255,253,248,.84);box-shadow:0 8px 25px rgba(15,24,34,.065);transition:transform .2s ease,border-color .2s ease,box-shadow .2s ease}
.contact-channel:hover,.contact-channel:focus-visible{transform:translateY(-3px);border-color:rgba(155,79,55,.58);box-shadow:var(--shadow-soft)}
.contact-icon{flex:0 0 46px;width:46px;height:46px;display:grid;place-items:center;border-radius:50%;background:var(--navy);color:#f3c09f}
.contact-icon svg{width:23px;height:23px}.contact-channel.medium-mark .contact-icon svg{width:28px;height:28px}
.contact-text{min-width:0}.contact-text strong{display:block;font-size:15px;line-height:1.3}.contact-text small{display:block;color:#697681;font:12px/1.45 Arial,sans-serif;margin-top:4px;overflow-wrap:anywhere;unicode-bidi:isolate}

/* Rebuilt footer: no duplicate language selector, no technical profile */
footer.site-footer{background:#08121d;color:#b9c5cd;padding:38px 0 22px}
.footer-shell{display:grid;grid-template-columns:minmax(240px,1.1fr) minmax(280px,.9fr) auto;gap:clamp(28px,5vw,64px);align-items:start}
.footer-name{display:inline-flex;flex-direction:column;gap:2px}.footer-name strong{color:#fff;font-size:19px}.footer-name span{color:#e2a27d;font:14px/1.35 Georgia,"Times New Roman",serif;unicode-bidi:isolate}
.footer-identity p{max-width:390px;margin:10px 0 0;color:#8fa1ad;font-size:13px;line-height:1.75}
.footer-nav{display:grid;grid-template-columns:repeat(2,max-content);gap:7px 22px;padding-top:2px}
.footer-nav a{color:#b4c1c9;font-size:13px;padding:3px 0}.footer-nav a:hover,.footer-nav a:focus-visible{color:#fff}
.footer-contact{display:flex;flex-direction:column;align-items:flex-end;gap:10px}.footer-contact-label{color:#fff;font-size:13px;font-weight:700}
.social-icons{display:flex;align-items:center;gap:10px;direction:ltr}.social-icon{width:48px;height:48px;display:grid;place-items:center;border:1px solid rgba(255,255,255,.18);border-radius:50%;color:#dce5eb;background:rgba(255,255,255,.035);transition:transform .2s ease,border-color .2s ease,background .2s ease,color .2s ease}
.social-icon:hover,.social-icon:focus-visible{transform:translateY(-2px);border-color:#e0a17c;background:rgba(224,161,124,.10);color:#fff}.social-icon svg{width:22px;height:22px}.social-icon.medium-mark svg{width:27px;height:27px}.social-icons.compact .social-icon{width:42px;height:42px}
.footer-meta{display:flex;justify-content:space-between;gap:18px;margin-top:27px;padding-top:17px;border-top:1px solid rgba(255,255,255,.11);color:#718796;font:11px/1.5 Arial,sans-serif}

/* Smaller, calmer mobile hierarchy */
@media(max-width:960px){
  .hero-portrait,.profile-portrait{justify-self:center;width:min(54vw,245px)}
  .contact-grid{grid-template-columns:1fr;gap:28px}.contact-channels{grid-template-columns:repeat(3,minmax(0,1fr))}
  .footer-shell{grid-template-columns:1fr 1fr}.footer-identity{grid-column:1/-1}.footer-contact{align-items:flex-start}
}
@media(max-width:620px){
  .site-header{position:sticky}.header-inner{padding:8px 0 0;gap:8px 12px}.nav{gap:17px;-webkit-overflow-scrolling:touch;scrollbar-width:none}.nav::-webkit-scrollbar{display:none}.nav a{padding:10px 0 9px}
  .home-hero-grid,.profile-grid{padding:34px 0 44px;gap:23px}.hero-portrait,.profile-portrait{width:min(50vw,184px);order:-1}.hero-portrait::before,.profile-portrait::after{inset:10px -10px -10px 10px!important}
  .home-hero h1,.profile-hero h1{font-size:clamp(42px,13vw,52px);margin:7px 0 8px}.home-hero .latin,.profile-latin{font-size:24px}.home-hero .hero-statement,.profile-hero .lead{font-size:16.5px;line-height:1.7;margin-top:15px}
  .home-hero .actions,.profile-hero .actions,.book-hero .actions{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:9px;margin-top:22px}.home-hero .btn,.profile-hero .btn,.book-hero .btn{min-width:0;min-height:44px;padding:0 12px;font-size:12.5px;text-align:center}
  .hero-index{margin-top:25px}.hero-index a{padding:11px 13px}
  .section{padding:52px 0}.contact-channels{grid-template-columns:1fr}.contact-channel{padding:13px 14px}.contact-icon{width:42px;height:42px;flex-basis:42px}
  footer.site-footer{padding:31px 0 19px}.footer-shell{grid-template-columns:1fr;gap:23px}.footer-identity{grid-column:auto}.footer-nav{grid-template-columns:repeat(2,minmax(0,1fr));gap:5px 14px}.footer-contact{align-items:flex-start}.footer-meta{align-items:center;text-align:start;margin-top:22px;padding-top:14px}.footer-meta span{display:block}
}
'''


def patch_css() -> None:
    path = ROOT / "assets/site-v2.css"
    css = path.read_text(encoding="utf-8")
    if MARKER in css:
        raise RuntimeError("Site UX Rebuild 10 CSS marker already exists")
    path.write_text(css.rstrip() + CSS + "\n", encoding="utf-8")


def validate() -> None:
    errors: list[str] = []
    public_pages = 0
    for path in sorted(ROOT.rglob("*.html")):
        if ".git" in path.parts or path.name == "404.html":
            continue
        public_pages += 1
        rel = path.relative_to(ROOT)
        html = path.read_text(encoding="utf-8")
        if html.count('id="site-footer"') != 1:
            errors.append(f"{rel}: missing unique rebuilt footer")
        if "اللغات والروابط" in html or "Languages and profiles" in html:
            errors.append(f"{rel}: duplicate footer language navigation remained")
        if "https://github.com/Ahmed-Alhafiz" in html:
            errors.append(f"{rel}: public GitHub identity link remained")
        if "identity-links" in html:
            errors.append(f"{rel}: oversized legacy identity cards remained")
        footer_match = FOOTER_RE.search(html)
        if footer_match and 'class="langs"' in footer_match.group(0):
            errors.append(f"{rel}: language selector remained in footer")

    required = {
        "index.html": ("home-hero", "hero-portrait"),
        "en/index.html": ("home-hero", "hero-portrait"),
        "de/index.html": ("home-hero", "hero-portrait"),
        "about/index.html": ("profile-hero", "profile-portrait", 'id="contact"'),
        "en/about/index.html": ("profile-hero", "profile-portrait", 'id="contact"'),
        "de/about/index.html": ("profile-hero", "profile-portrait", 'id="contact"'),
    }
    for rel, tokens in required.items():
        text = (ROOT / rel).read_text(encoding="utf-8")
        for token in tokens:
            if token not in text:
                errors.append(f"{rel}: missing {token}")

    for slug in GERMAN_BOOKS:
        rel = f"de/books/{slug}/index.html"
        text = (ROOT / rel).read_text(encoding="utf-8")
        for token in ("book-hero", "book-hero-cover", "publication-note"):
            if token not in text:
                errors.append(f"{rel}: missing rebuilt {token}")
        if 'class="page-head"' in text or 'class="book-layout"' in text:
            errors.append(f"{rel}: legacy German book layout remained")

    for rel in ("about/index.html", "en/about/index.html", "de/about/index.html"):
        text = (ROOT / rel).read_text(encoding="utf-8")
        if text.count("contact-channel") < 3:
            errors.append(f"{rel}: compact contact channels incomplete")
        if 'dir="ltr">@' not in text and rel != "de/about/index.html":
            errors.append(f"{rel}: RTL-safe social handle missing")

    css = (ROOT / "assets/site-v2.css").read_text(encoding="utf-8")
    for token in (MARKER, ".footer-shell", ".contact-channel", "aspect-ratio:4/5", ".book-hero .pill"):
        if token not in css:
            errors.append(f"assets/site-v2.css: missing {token}")

    if errors:
        raise SystemExit("\n".join(errors))
    print(f"UX validation passed across {public_pages} public HTML pages")


def main() -> None:
    patch_existing_pages()
    rewrite_german_pages()
    rewrite_all_public_html()
    patch_css()
    validate()
    print("Site UX Rebuild 10 applied successfully")


if __name__ == "__main__":
    main()
