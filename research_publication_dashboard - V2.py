import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from io import StringIO
import uuid

# Page configuration
st.set_page_config(page_title="Araştırma Yayınları Panosu", layout="centered")

# CSS for styling and full-screen fix
st.markdown("""
    <style>
        .main > div {
            max-width: 900px;
            margin: 0 auto;
            padding: 0 20px;
        }
        .stPlotlyChart, .js-plotly-plot, .plotly {
            width: 100% !important;
            max-width: 900px !important;
            margin: 0 auto;
        }
        /* Hide modebar in full-screen */
        .modebar {
            display: block !important;
        }
        .modebar-group .modebar-btn[data-title="Toggle fullscreen"] {
            display: none !important;
        }
        /* Full-screen mode styling */
        .js-plotly-plot:-webkit-full-screen, .js-plotly-plot:-moz-full-screen, .js-plotly-plot:fullscreen {
            width: 100vw !important;
            height: 100vh !important;
            max-width: 100% !important;
            max-height: 100% !important;
            margin: 0 !important;
            padding: 0 !important;
            position: fixed !important;
            top: 0 !important;
            left: 0 !important;
            right: 0 !important;
            bottom: 0 !important;
            display: flex !important;
            justify-content: center !important;
            align-items: center !important;
            background-color: #fff !important;
        }
        /* Ensure parent container stretches */
        .stPlotlyChart:-webkit-full-screen, .stPlotlyChart:-moz-full-screen, .stPlotlyChart:fullscreen {
            width: 100% !important;
            height: 100% !important;
            margin: 0 !important;
            padding: 0 !important;
        }
        /* Reset Plotly's internal margins */
        .js-plotly-plot:-webkit-full-screen .plotly, .js-plotly-plot:-moz-full-screen .plotly, .js-plotly-plot:fullscreen .plotly {
            margin: 0 !important;
            padding: 0 !important;
        }
        /* Consistent font styling */
        body, h1, h2, h3, p, div, span {
            font-family: 'Roboto', sans-serif !important;
        }
        h1, h2, h3 {
            color: #1F77B4;
        }
    </style>
""", unsafe_allow_html=True)

# JavaScript to enhance full-screen behavior
st.markdown("""
    <script>
        document.addEventListener('DOMContentLoaded', function() {
            const plots = document.querySelectorAll('.js-plotly-plot');
            plots.forEach(plot => {
                plot.on('plotly_fullscreen', function() {
                    plot.style.width = '100vw';
                    plot.style.height = '100vh';
                    plot.style.maxWidth = '100%';
                    plot.style.maxHeight = '100%';
                    plot.style.margin = '0';
                    plot.style.padding = '0';
                    plot.style.position = 'fixed';
                    plot.style.top = '0';
                    plot.style.left = '0';
                    plot.style.display = 'flex';
                    plot.style.justifyContent = 'center';
                    plot.style.alignItems = 'center';
                    // Hide modebar in full-screen
                    const modebar = plot.querySelector('.modebar');
                    if (modebar) modebar.style.display = 'none';
                });
                plot.on('plotly_fullscreen_exit', function() {
                    plot.style.width = '';
                    plot.style.height = '';
                    plot.style.maxWidth = '';
                    plot.style.maxHeight = '';
                    plot.style.margin = '';
                    plot.style.padding = '';
                    plot.style.position = '';
                    plot.style.top = '';
                    plot.style.left = '';
                    plot.style.display = '';
                    // Restore modebar
                    const modebar = plot.querySelector('.modebar');
                    if (modebar) modebar.style.display = 'block';
                });
            });
        });
    </script>
""", unsafe_allow_html=True)

# Table of Contents
toc_items = [
    ("Dosya Yükleme", "dosya-yukleme"),
    ("Özet İstatistikler", "ozet-istatistikler"),
    ("Veri Özeti", "veri-ozeti"),
    ("Veri Hataları", "veri-hatalari"),
    ("Veri Filtreleme", "veri-filtreleme"),
    ("Yıl Bazında Yayın Türü Dağılımı", "yil-bazinda-yayin"),
    ("Yayın Türü Değişim Karşılaştırması (2023 vs 2024)", "yayin-degisim"),
    ("Fakülte/Bölüm Bazında Yayın Çeyreklik Dağılımı", "fakulte-ceyreklik"),
    ("Fakülte ve Yayın Türü Dağılımı", "fakulte-yayin-turu"),
    ("Toplam Yayın Sayısına Göre İlk 5 Birim", "top-5-birim"),
    ("Unvan Bazında Yayın Dağılımı", "unvan-dagilim"),
    ("Yayın Değişimi (2023-2024)", "yayin-degisim-2023-2024"),
    ("Toplam Yayın Sayısına Göre İlk 5 Araştırmacı", "top-5-arastirmaci"),
    ("Etki Puanı", "etki-puani"),
    ("Yayın ve Etki Puanı", "yayin-etki"),
    ("Aktif Araştırmacı Oranı", "aktif-oran"),
    ("Yıl Bazında Yayınlar", "yil-bazinda-yayinlar"),
    ("Çeyreklik Çeşitlilik İndeksi", "cesitlilik-indeksi"),
    ("En Yaygın Yayın Türleri", "en-yaygin-yayin"),
]

# Sidebar with TOC
with st.sidebar:
    st.header("İçindekiler")
    for title, anchor in toc_items:
        st.markdown(f'<a href="#{anchor}" style="text-decoration: none; color: #1f77b4;">{title}</a>', unsafe_allow_html=True)

# Faculty and Department mappings
FACULTY_MAPPING = {
    'Mühendislik Fakültesi': 'Mühendislik Fakültesi',
    'İktisadi ve İdari Bilimler Fakültesi': 'İktisadi ve İdari Bilimler Fakültesi',
    'Fen Edebiyat Fakültesi': 'Fen Edebiyat Fakültesi',
    'Eğitim Fakültesi': 'Eğitim Fakültesi',
    'Mimarlık Fakültesi': 'Mimarlık Fakültesi',
    'Yabancı Diller Yüksek Okulu': 'Yabancı Diller Yüksek Okulu',
    'Rektörlük': 'Rektörlük',
    'Fen Bilimleri Enstitüsü': 'Fen Bilimleri Enstitüsü',
    'Deniz Bilimleri Enstitüsü': 'Deniz Bilimleri Enstitüsü',
    'Uygulamalı Matematik Enstitüsü': 'Uygulamalı Matematik Enstitüsü',
    'Sosyal Bilimler Enstitüsü': 'Sosyal Bilimler Enstitüsü',
    'Enformatik Enstitüsü': 'Enformatik Enstitüsü',
    'Meslek Yüksek Okulu': 'Meslek Yüksek Okulu'
}
FACULTY_ORDER = sorted(FACULTY_MAPPING.keys())

DEPARTMENT_MAPPING = {
    'Aktüerya Bilimleri Anabilim Dalı': 'Aktüerya Bilimleri Anabilim Dalı',
    'Beden Eğitimi ve Spor Bölümü': 'Beden Eğitimi ve Spor Bölümü',
    'Bilgisayar Mühendisliği Bölümü': 'Bilgisayar Mühendisliği Bölümü',
    'Bilgisayar ve Öğretim Teknolojileri Eğitimi Bölümü': 'Bilgisayar ve Öğretim Teknolojileri Eğitimi Bölümü',
    'Bilim ve Teknoloji Politikası Çalışmaları Anabilim Dalı': 'Bilim ve Teknoloji Politikası Çalışmaları Anabilim Dalı',
    'Bilimsel Hesaplama Anabilim Dalı': 'Bilimsel Hesaplama Anabilim Dalı',
    'Bilişim Sistemleri Anabilim Dalı': 'Bilişim Sistemleri Anabilim Dalı',
    'Bilişsel Bilimler Anabilim Dalı': 'Bilişsel Bilimler Anabilim Dalı',
    'Biyolojik Bilimler Bölümü': 'Biyolojik Bilimler Bölümü',
    'Çevre Mühendisliği Bölümü': 'Çevre Mühendisliği Bölümü',
    'Deniz Bilimleri Anabilim Dalı': 'Deniz Bilimleri Anabilim Dalı',
    'Deniz Biyolojisi ve Balıkçılık Anabilim Dalı': 'Deniz Biyolojisi ve Balıkçılık Anabilim Dalı',
    'Deniz Jeolojisi ve Jeofiziği Anabilim Dalı': 'Deniz Jeolojisi ve Jeofiziği Anabilim Dalı',
    'Eğitim Bilimleri Bölümü': 'Eğitim Bilimleri Bölümü',
    'Elektrik ve Elektronik Mühendisliği Bölümü': 'Elektrik ve Elektronik Mühendisliği Bölümü',
    'Endüstri Mühendisliği Bölümü': 'Endüstri Mühendisliği Bölümü',
    'Endüstriyel Tasarım Bölümü': 'Endüstriyel Tasarım Bölümü',
    'Fen Bilimleri Enstitüsü': 'Fen Bilimleri Enstitüsü',
    'Felsefe Bölümü': 'Felsefe Bölümü',
    'Finansal Matematik Anabilim Dalı': 'Finansal Matematik Anabilim Dalı',
    'Fizik Bölümü': 'Fizik Bölümü',
    'Gıda Mühendisliği Bölümü': 'Gıda Mühendisliği Bölümü',
    'Havacılık ve Uzay Mühendisliği Bölümü': 'Havacılık ve Uzay Mühendisliği Bölümü',
    'İktisat Bölümü': 'İktisat Bölümü',
    'İnşaat Mühendisliği Bölümü': 'İnşaat Mühendisliği Bölümü',
    'İstatistik Bölümü': 'İstatistik Bölümü',
    'Jeoloji Mühendisliği Bölümü': 'Jeoloji Mühendisliği Bölümü',
    'Kimya Bölümü': 'Kimya Bölümü',
    'Kimya Mühendisliği Bölümü': 'Kimya Mühendisliği Bölümü',
    'Kriptografi Anabilim Dalı': 'Kriptografi Anabilim Dalı',
    'Maden Mühendisliği Bölümü': 'Maden Mühendisliği Bölümü',
    'Makina Mühendisliği Bölümü': 'Makina Mühendisliği Bölümü',
    'Matematik Bölümü': 'Matematik Bölümü',
    'Matematik ve Fen Bilimleri Eğitimi Bölümü': 'Matematik ve Fen Bilimleri Eğitimi Bölümü',
    'Meslek Yüksek Okulu': 'Meslek Yüksek Okulu',
    'Metalurji ve Malzeme Mühendisliği Bölümü': 'Metalurji ve Malzeme Mühendisliği Bölümü',
    'Mimarlık Bölümü': 'Mimarlık Bölümü',
    'Modelleme ve Simülasyon Anabilim Dalı': 'Modelleme ve Simülasyon Anabilim Dalı',
    'Modern Diller Bölümü': 'Modern Diller Bölümü',
    'Mühendislik Bilimleri Bölümü': 'Mühendislik Bilimleri Bölümü',
    'Müzik ve Güzel Sanatlar Bölümü': 'Müzik ve Güzel Sanatlar Bölümü',
    'Petrol ve Doğal Gaz Mühendisliği Bölümü': 'Petrol ve Doğal Gaz Mühendisliği Bölümü',
    'Psikoloji Bölümü': 'Psikoloji Bölümü',
    'Sağlık Bilişimi Anabilim Dalı': 'Sağlık Bilişimi Anabilim Dalı',
    'Siber Güvenlik Anabilim Dalı': 'Siber Güvenlik Anabilim Dalı',
    'Siyaset Bilimi ve Kamu Yönetimi Bölümü': 'Siyaset Bilimi ve Kamu Yönetimi Bölümü',
    'Sosyoloji Bölümü': 'Sosyoloji Bölümü',
    'Şehir ve Bölge Planlama Bölümü': 'Şehir ve Bölge Planlama Bölümü',
    'Tarih Bölümü': 'Tarih Bölümü',
    'Temel Eğitim Bölümü': 'Temel Eğitim Bölümü',
    'Türk Dili Bölümü': 'Türk Dili Bölümü',
    'Uluslararası İlişkiler Bölümü': 'Uluslararası İlişkiler Bölümü',
    'Veri Bilişimi Anabilim Dalı': 'Veri Bilişimi Anabilim Dalı',
    'Yabancı Diller Bölümü': 'Yabancı Diller Bölümü',
    'Yabancı Diller Eğitimi Bölümü': 'Yabancı Diller Eğitimi Bölümü',
    '': 'Bilinmeyen'
}
DEPARTMENT_ORDER = sorted([d for d in DEPARTMENT_MAPPING.keys() if d])

# Column mapping for new file layout
COLUMN_MAPPING = {
    'Unvan': 'Title',
    'Ad Soyad': 'Name',
    'Fakülte': 'Faculty',
    'Bölüm': 'Department',
    'WoS ESCI İndeksinde Taranan Makale': 'ESCI Articles',
    'Scopus Makale (WoS SCIE, AHCI, SSCI, ESCI Taranmayan)': 'Scopus Articles',
    'WoS Q1 Makale Sayısı': 'Q1 Articles',
    'WoS Q2 Makale Sayısı': 'Q2 Articles',
    'WoS Q3 Makale Sayısı': 'Q3 Articles',
    'WoS Q4 Makale Sayısı': 'Q4 Articles',
    'WoS Quartile Bulunmayan Makale Sayısı': 'Non-Quartile Articles'
}

# Title order
title_order = ["Arş. Gör.", "Öğr. Gör.", "Dr. Öğr. Üyesi", "Doç. Dr.", "Prof. Dr.", "Diğer"]

# Publication types definition
pub_types = ['ESCI Articles', 'Scopus Articles', 'Q1 Articles', 'Q2 Articles', 'Q3 Articles', 'Q4 Articles', 'Non-Quartile Articles']
pub_type_labels = {
    'ESCI Articles': 'ESCI Makaleleri',
    'Scopus Articles': 'Scopus Makaleleri',
    'Q1 Articles': 'Q1 Makaleleri',
    'Q2 Articles': 'Q2 Makaleleri',
    'Q3 Articles': 'Q3 Makaleleri',
    'Q4 Articles': 'Q4 Makaleleri',
    'Non-Quartile Articles': 'Çeyreklik Olmayan Makaleler'
}

# Title extraction function
def extract_title(name):
    titles = [
        "Prof. Dr.", "Prof.", "Doç. Dr.", "Dr. Öğr. Üyesi", "Öğr. Gör.", "Arş. Gör.",
        "Asst. Prof.", "Assoc. Prof.", "Lect. PhD", "Res. Asst.",
        "Araştırma Görevlisi", "Öğretim Görevlisi", "Araştırmacı", "İdari Personel"
    ]
    title_mapping = {
        "Prof. Dr.": "Prof. Dr.",
        "Prof.": "Prof. Dr.",
        "Doç. Dr.": "Doç. Dr.",
        "Dr. Öğr. Üyesi": "Dr. Öğr. Üyesi",
        "Öğr. Gör.": "Öğr. Gör.",
        "Arş. Gör.": "Arş. Gör.",
        "Asst. Prof.": "Dr. Öğr. Üyesi",
        "Assoc. Prof.": "Doç. Dr.",
        "Lect. PhD": "Öğr. Gör.",
        "Res. Asst.": "Arş. Gör.",
        "Araştırma Görevlisi": "Arş. Gör.",
        "Öğretim Görevlisi": "Öğr. Gör.",
        "Araştırmacı": "Diğer",
        "İdari Personel": "Diğer"
    }
    if isinstance(name, str):
        for title in titles:
            if title in name:
                return title_mapping[title]
    return "Diğer"

# Error checking and removal function
def check_and_remove_errors(df):
    numeric_cols = ['ESCI Articles', 'Scopus Articles', 'Q1 Articles', 'Q2 Articles', 'Q3 Articles', 'Q4 Articles', 'Non-Quartile Articles']
    removed_entries = []
    neg_mask = df[numeric_cols].lt(0).any(axis=1)
    neg_indices = df[neg_mask].index
    for idx in neg_indices:
        researcher = df.loc[idx, "Name"]
        neg_cols = [col for col in numeric_cols if df.loc[idx, col] < 0]
        for col in neg_cols:
            reason = f"Negatif değer ({df.loc[idx, col]}) {col} sütununda"
            removed_entries.append({"Ad Soyad": researcher, "Sebep": reason})
    indices_to_remove = set(neg_indices)
    removed_df = pd.DataFrame(removed_entries)
    cleaned_df = df.drop(index=indices_to_remove).reset_index(drop=True)
    return cleaned_df, removed_df

# File upload
with st.container():
    st.header("Dosya Yükleme", anchor="dosya-yukleme")
    st.markdown("2023 ve 2024 yayın verilerini içeren Excel dosyalarını yükleyin.")
    uploaded_file_2023 = st.file_uploader("2023 Excel Dosyasını Yükleyin", type=["xlsx"])
    uploaded_file_2024 = st.file_uploader("2024 Excel Dosyasını Yükleyin", type=["xlsx"])

@st.cache_data
def load_and_process_data(file_2023, file_2024):
    try:
        df_2023 = pd.read_excel(file_2023)
        df_2024 = pd.read_excel(file_2024)
        df_2023['Year'] = '2023'
        df_2024['Year'] = '2024'
        df = pd.concat([df_2023, df_2024], ignore_index=True)
        df.columns = df.columns.str.strip()
        df = df.rename(columns=COLUMN_MAPPING)
        df['Faculty'] = df['Faculty'].fillna('Bilinmeyen').astype(str)
        df['Department'] = df['Department'].fillna('Bilinmeyen').astype(str)
        df['Name'] = df['Name'].fillna('Bilinmeyen').astype(str)
        df = df.dropna(subset=['Name'], how='all')
        df = df.fillna({'ESCI Articles': 0, 'Scopus Articles': 0, 'Q1 Articles': 0,
                        'Q2 Articles': 0, 'Q3 Articles': 0, 'Q4 Articles': 0, 'Non-Quartile Articles': 0})
        df[['ESCI Articles', 'Scopus Articles', 'Q1 Articles', 'Q2 Articles', 'Q3 Articles',
            'Q4 Articles', 'Non-Quartile Articles']] = df[['ESCI Articles', 'Scopus Articles', 'Q1 Articles',
                                                          'Q2 Articles', 'Q3 Articles', 'Q4 Articles',
                                                          'Non-Quartile Articles']].astype(int)
        if 'Title' not in df.columns or df['Title'].isna().all():
            df['Title'] = df['Name'].apply(extract_title)
        else:
            df['Title'] = df['Title'].fillna('Diğer').astype(str)
        df['Total Publications'] = df[pub_types].sum(axis=1)
        df['Impact Score'] = (4 * df['Q1 Articles'] + 3 * df['Q2 Articles'] + 2 * df['Q3 Articles'] +
                             1 * df['Q4 Articles'] + 0.5 * (df['ESCI Articles'] + df['Scopus Articles'] +
                                                            df['Non-Quartile Articles']))
        df['Faculty'] = df['Faculty'].apply(lambda x: FACULTY_MAPPING.get(x, x))
        df['Department'] = df['Department'].apply(lambda x: DEPARTMENT_MAPPING.get(x, x))
        df['Faculty'] = pd.Categorical(df['Faculty'], categories=[FACULTY_MAPPING[f] for f in FACULTY_ORDER if FACULTY_MAPPING[f] in df['Faculty'].unique()], ordered=True)
        df['Department'] = pd.Categorical(df['Department'], categories=[DEPARTMENT_MAPPING[d] for d in DEPARTMENT_ORDER if DEPARTMENT_MAPPING[d] in df['Department'].unique()], ordered=True)
        df['Title'] = pd.Categorical(df['Title'], categories=title_order, ordered=True)
        df['Year'] = df['Year'].astype(str)
        df, removed_df = check_and_remove_errors(df)
        return df, removed_df, None
    except Exception as e:
        return None, None, str(e)

# Color mapping
COLOR_MAP = {
    'ESCI Makaleleri': '#1F77B4',
    'Scopus Makaleleri': '#FF7F0E',
    'Q1 Makaleleri': '#2CA02C',
    'Q2 Makaleleri': '#D62728',
    'Q3 Makaleleri': '#9467BD',
    'Q4 Makaleleri': '#8C564B',
    'Çeyreklik Olmayan Makaleler': '#7F7F7F'
}
YEAR_COLOR_MAP = {
    '2023': '#1F77B4',
    '2024': '#4A90E2'
}
CHANGE_COLOR_MAP = {
    'increase': '#2CA02C',
    'decrease': '#D62728'
}

# Process uploaded files
if uploaded_file_2023 is not None and uploaded_file_2024 is not None:
    df, removed_df, error = load_and_process_data(uploaded_file_2023, uploaded_file_2024)
    if error:
        st.error(f"Dosyalar işlenirken hata oluştu: {error}")
    else:
        with st.container():
            st.success("Dosyalar başarıyla yüklendi ve fakülte/bölüm isimleri standardize edildi.")

            # Expanded Summary Statistics
            st.header("Özet İstatistikler", anchor="ozet-istatistikler")
            st.markdown("Bu bölüm, 2023 ve 2024 yayın verilerinin temel istatistiklerini ve önemli trendlerini özetler.")

            # Metrics
            total_pubs = df['Total Publications'].sum()
            pubs_2023 = df[df['Year'] == '2023']['Total Publications'].sum()
            pubs_2024 = df[df['Year'] == '2024']['Total Publications'].sum()
            pub_change = ((pubs_2024 - pubs_2023) / pubs_2023 * 100) if pubs_2023 > 0 else 0
            active_researchers = df[df['Total Publications'] > 0]['Name'].nunique()
            high_impact_researchers = df[df['Q1 Articles'] + df['Q2 Articles'] > 0]['Name'].nunique()
            avg_impact = df['Impact Score'].mean()
            quartile_cols = ['Q1 Articles', 'Q2 Articles', 'Q3 Articles', 'Q4 Articles']
            diversity_index = df.groupby(['Faculty', 'Year'])[quartile_cols].sum().apply(
                lambda row: -sum((c / sum(row) * np.log(c / sum(row))) for c in row if c > 0) if sum(row) > 0 else 0, axis=1
            ).mean()

            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Toplam Yayın", f"{total_pubs}")
                st.metric("2023 Yayınları", f"{pubs_2023}")
                st.metric("2024 Yayınları", f"{pubs_2024}")
            with col2:
                st.metric("Yayın Değişimi (2023-2024)", f"{pub_change:.1f}%")
                st.metric("Aktif Araştırmacılar", f"{active_researchers}")
                st.metric("Yüksek Etkili Araştırmacılar (Q1/Q2)", f"{high_impact_researchers}")
            with col3:
                st.metric("Ortalama Etki Puanı", f"{avg_impact:.2f}")
                st.metric("Ortalama Çeyreklik Çeşitlilik İndeksi", f"{diversity_index:.2f}")

            # Key Takeaways
            st.subheader("Önemli Bulgular")
            takeaways = []
            if pub_change > 10:
                takeaways.append(f"- **Büyüme Trendi**: 2023'ten 2024'e yayın sayısında %{pub_change:.1f} artış, araştırma çıktılarında güçlü bir yükselişi gösteriyor.")
            elif pub_change < -10:
                takeaways.append(f"- **Düşüş Trendi**: 2023'ten 2024'e yayın sayısında %{pub_change:.1f} azalma, potansiyel kaynak veya odak değişikliğini işaret edebilir.")
            top_pub_type = df[pub_types].sum().idxmax()
            top_pub_count = df[pub_types].sum().max()
            takeaways.append(f"- **Dominant Yayın Türü**: {pub_type_labels[top_pub_type]} ({top_pub_count} adet), toplam çıktının önemli bir kısmını oluşturuyor.")
            if high_impact_researchers / active_researchers > 0.5:
                takeaways.append(f"- **Yüksek Etki Odağı**: Aktif araştırmacıların %{high_impact_researchers/active_researchers*100:.1f}'i Q1 veya Q2 makaleler üretiyor.")
            declining_faculties = df.groupby(['Faculty', 'Year'])['Total Publications'].sum().unstack().fillna(0).pipe(
                lambda x: x[x['2024'] < x['2023'] * 0.8].index.tolist()
            )
            if declining_faculties:
                takeaways.append(f"- **Düşüş Gösteren Fakülteler**: {', '.join(declining_faculties)} 2024'te yayın sayısında önemli düşüşler yaşadı.")
            for takeaway in takeaways:
                st.markdown(takeaway)

            # Visualizations
            st.subheader("Trend Görselleştirmeleri")
            with st.expander("Trendleri Görüntüle"):
                tab1, tab2, tab3 = st.tabs(["Yayın Türü Değişimleri", "Yayın Türü Dağılımı", "En Aktif Fakülteler"])
                with tab1:
                    pub_trend = df.groupby('Year')[pub_types].sum().reset_index()
                    pub_trend_melted = pub_trend.melt(id_vars='Year', value_vars=pub_types, var_name='Publication Type', value_name='Sayı')
                    pub_trend_melted['Publication Type'] = pub_trend_melted['Publication Type'].map(pub_type_labels)
                    change_data = pub_trend.set_index('Year')[pub_types].T
                    change_data['Change'] = change_data['2024'] - change_data['2023']
                    change_data['Change Type'] = change_data['Change'].apply(lambda x: 'increase' if x >= 0 else 'decrease')
                    change_data = change_data.reset_index().rename(columns={'index': 'Publication Type'})
                    change_data['Publication Type'] = change_data['Publication Type'].map(pub_type_labels)
                    fig_trend = px.bar(change_data, x='Change', y='Publication Type', orientation='h',
                                       color='Change Type', title="Yayın Türü Değişimleri (2023-2024)",
                                       color_discrete_map=CHANGE_COLOR_MAP)
                    fig_trend.update_layout(
                        xaxis_title="Değişim (2024 - 2023)",
                        yaxis_title="Yayın Türü",
                        height=500,
                        width=900,
                        xaxis=dict(zeroline=True, zerolinecolor='black', zerolinewidth=2)
                    )
                    st.plotly_chart(fig_trend, use_container_width=True, key="pub_trend_change_bar")
                with tab2:
                    pub_dist = df[pub_types].sum().reset_index()
                    pub_dist.columns = ['Publication Type', 'Sayı']
                    pub_dist['Publication Type'] = pub_dist['Publication Type'].map(pub_type_labels)
                    fig_dist = px.pie(pub_dist, names='Publication Type', values='Sayı',
                                      title="Tüm Yayın Türlerinin Dağılımı", color_discrete_map=COLOR_MAP)
                    fig_dist.update_layout(height=500, width=900)
                    st.plotly_chart(fig_dist, use_container_width=True, key="pub_dist_pie_summary")
                with tab3:
                    faculty_pubs = df.groupby(['Faculty', 'Year'])['Total Publications'].sum().reset_index()
                    faculty_pubs['Faculty'] = faculty_pubs['Faculty'].map(lambda x: list(FACULTY_MAPPING.keys())[list(FACULTY_MAPPING.values()).index(x)] if x in FACULTY_MAPPING.values() else x)
                    top_faculties = faculty_pubs.groupby('Faculty')['Total Publications'].sum().nlargest(5).index
                    top_faculty_data = faculty_pubs[faculty_pubs['Faculty'].isin(top_faculties)]
                    fig_faculty = px.bar(top_faculty_data, x='Faculty', y='Total Publications', color='Year', barmode='group',
                                         title="En Aktif 5 Fakülte (Yayın Sayısı)", color_discrete_map=YEAR_COLOR_MAP)
                    fig_faculty.update_layout(xaxis_tickangle=45, height=500, width=900)
                    st.plotly_chart(fig_faculty, use_container_width=True, key="top_faculties_bar_summary")

            # Check for unmapped faculties or departments
            unmapped_faculties = df['Faculty'][~df['Faculty'].isin(FACULTY_MAPPING.values()) & (df['Faculty'] != 'Bilinmeyen')].unique()
            unmapped_departments = df['Department'][~df['Department'].isin(DEPARTMENT_MAPPING.values()) & (df['Department'] != 'Bilinmeyen')].unique()
            if unmapped_faculties.size > 0 or unmapped_departments.size > 0:
                with st.expander("Eşlenmemiş Fakülte ve Bölümler"):
                    if unmapped_faculties.size > 0:
                        st.warning("Eşlenmemiş Fakülteler:")
                        for faculty in unmapped_faculties:
                            st.write(f"- {faculty}")
                    if unmapped_departments.size > 0:
                        st.warning("Eşlenmemiş Bölümler:")
                        for dept in unmapped_departments:
                            st.write(f"- {dept}")

            # Interactive Filters
            st.header("Veri Filtreleme", anchor="veri-filtreleme")
            st.markdown("Fakülte, bölüm ve unvan bazında filtreleme yapın. Dahil etmek istediğiniz kategorileri seçin veya hariç tutmak istediğiniz kategorileri belirtin.")
            col1, col2, col3 = st.columns(3)
            with col1:
                faculty_options = sorted([f for f in FACULTY_MAPPING.keys() if f in df['Faculty'].map(lambda x: list(FACULTY_MAPPING.keys())[list(FACULTY_MAPPING.values()).index(x)] if x in FACULTY_MAPPING.values() else x).unique()], key=str.lower)
                faculty_filter = st.multiselect("Fakülte Seçin (Dahil Et)", options=faculty_options, default=[])
            with col2:
                dept_options = sorted([d for d in DEPARTMENT_MAPPING.keys() if d in df['Department'].map(lambda x: list(DEPARTMENT_MAPPING.keys())[list(DEPARTMENT_MAPPING.values()).index(x)] if x in DEPARTMENT_MAPPING.values() else x).unique() and d], key=str.lower)
                department_filter = st.multiselect("Bölüm Seçin (Dahil Et)", options=dept_options, default=[])
            with col3:
                title_options = sorted([t for t in df['Title'].unique() if t and isinstance(t, str)], key=str.lower)
                title_filter = st.multiselect("Unvan Seçin (Dahil Et)", options=title_options, default=[])
            
            # Exclusion Filters
            col4, col5, col6 = st.columns(3)
            with col4:
                faculty_exclude = st.multiselect("Fakülte Hariç Tut", options=faculty_options, default=[])
            with col5:
                department_exclude = st.multiselect("Bölüm Hariç Tut", options=dept_options, default=[])
            with col6:
                title_exclude = st.multiselect("Unvan Hariç Tut", options=title_options, default=[])

            # Apply filters
            filtered_df = df.copy()
            # Inclusion filters
            if faculty_filter:
                filtered_df = filtered_df[filtered_df['Faculty'].map(lambda x: list(FACULTY_MAPPING.keys())[list(FACULTY_MAPPING.values()).index(x)] if x in FACULTY_MAPPING.values() else x).isin(faculty_filter)]
            if department_filter:
                filtered_df = filtered_df[filtered_df['Department'].map(lambda x: list(DEPARTMENT_MAPPING.keys())[list(DEPARTMENT_MAPPING.values()).index(x)] if x in DEPARTMENT_MAPPING.values() else x).isin(department_filter)]
            if title_filter:
                filtered_df = filtered_df[filtered_df['Title'].isin(title_filter)]
            # Exclusion filters
            if faculty_exclude:
                filtered_df = filtered_df[~filtered_df['Faculty'].map(lambda x: list(FACULTY_MAPPING.keys())[list(FACULTY_MAPPING.values()).index(x)] if x in FACULTY_MAPPING.values() else x).isin(faculty_exclude)]
            if department_exclude:
                filtered_df = filtered_df[~filtered_df['Department'].map(lambda x: list(DEPARTMENT_MAPPING.keys())[list(DEPARTMENT_MAPPING.values()).index(x)] if x in DEPARTMENT_MAPPING.values() else x).isin(department_exclude)]
            if title_exclude:
                filtered_df = filtered_df[~filtered_df['Title'].isin(title_exclude)]

            # Visualizations
            st.subheader("Veri Görselleştirmeleri")

            # Year-wise Publication Type Distribution
            st.header("Yıl Bazında Yayın Türü Dağılımı", anchor="yil-bazinda-yayin")
            st.markdown("2023 ve 2024 yıllarında yayın türlerinin dağılımı.")
            pub_data = filtered_df.groupby('Year')[pub_types].sum().reset_index()
            pub_data_melted = pub_data.melt(id_vars='Year', value_vars=pub_types, var_name='Publication Type', value_name='Sayı')
            pub_data_melted['Publication Type'] = pub_data_melted['Publication Type'].map(pub_type_labels)
            fig1 = px.bar(pub_data_melted, x='Year', y='Sayı', color='Publication Type', barmode='group',
                          title="Yıl Bazında Yayın Türü Dağılımı", color_discrete_map=COLOR_MAP)
            fig1.update_layout(height=600, width=900)
            st.plotly_chart(fig1, use_container_width=True, key="year_wise_pub_type")

            # Side-by-Side Comparison for 2023 vs 2024
            st.header("Yayın Türü Değişim Karşılaştırması (2023 vs 2024)", anchor="yayin-degisim")
            st.markdown("2023 ve 2024 yıllarında yayın türlerinin karşılaştırması.")
            pub_compare = filtered_df.groupby(['Year'])[pub_types].sum().reset_index()
            pub_compare_melted = pub_compare.melt(id_vars='Year', value_vars=pub_types, var_name='Publication Type', value_name='Sayı')
            pub_compare_melted['Publication Type'] = pub_compare_melted['Publication Type'].map(pub_type_labels)
            fig1b = px.bar(pub_compare_melted, x='Publication Type', y='Sayı', color='Year', barmode='group',
                           title="2023 ve 2024 Yılları Yayın Türü Karşılaştırması",
                           color_discrete_map=YEAR_COLOR_MAP)
            fig1b.update_layout(xaxis_tickangle=45, height=600, width=900)
            st.plotly_chart(fig1b, use_container_width=True, key="year_comparison_bar")

            # Faculty/Department-wise Publication Quartile Distribution (Pie Chart)
            st.header("Fakülte/Bölüm Bazında Yayın Çeyreklik Dağılımı", anchor="fakulte-ceyreklik")
            st.markdown("Fakülteler ve bölümlerdeki Q1-Q4 çeyreklik makalelerin dağılımı.")
            with st.expander("Fakülte/Bölüm Bazında Çeyreklik Dağılımlarını Görüntüle"):
                quartile_cols = ['Q1 Articles', 'Q2 Articles', 'Q3 Articles', 'Q4 Articles']
                tab1, tab2 = st.tabs(["Fakülteler", "Bölümler"])
                with tab1:
                    pub_quartile_data_faculty = filtered_df.groupby(['Faculty', 'Year'])[quartile_cols].sum().reset_index()
                    pub_quartile_data_faculty['Faculty'] = pub_quartile_data_faculty['Faculty'].map(lambda x: list(FACULTY_MAPPING.keys())[list(FACULTY_MAPPING.values()).index(x)] if x in FACULTY_MAPPING.values() else x)
                    pub_quartile_melted_faculty = pub_quartile_data_faculty.melt(id_vars=['Faculty', 'Year'], value_vars=quartile_cols, var_name='Çeyreklik', value_name='Sayı')
                    pub_quartile_melted_faculty['Çeyreklik'] = pub_quartile_melted_faculty['Çeyreklik'].map({
                        'Q1 Articles': 'Q1 Makaleleri',
                        'Q2 Articles': 'Q2 Makaleleri',
                        'Q3 Articles': 'Q3 Makaleleri',
                        'Q4 Articles': 'Q4 Makaleleri'
                    })
                    for year in ['2023', '2024']:
                        for faculty in pub_quartile_data_faculty['Faculty'].unique():
                            faculty_data = pub_quartile_melted_faculty[(pub_quartile_melted_faculty['Faculty'] == faculty) & (pub_quartile_melted_faculty['Year'] == year)]
                            if faculty_data['Sayı'].sum() > 0:
                                fig = px.pie(faculty_data, names='Çeyreklik', values='Sayı', title=f"{year} - {faculty} için Yayın Çeyreklik Dağılımı", color_discrete_map=COLOR_MAP)
                                fig.update_layout(height=500, width=800)
                                st.plotly_chart(fig, use_container_width=True, key=f"pie_faculty_{faculty}_{year}")
                with tab2:
                    pub_quartile_data_dept = filtered_df.groupby(['Department', 'Year'])[quartile_cols].sum().reset_index()
                    pub_quartile_data_dept['Department'] = pub_quartile_data_dept['Department'].map(lambda x: list(DEPARTMENT_MAPPING.keys())[list(DEPARTMENT_MAPPING.values()).index(x)] if x in DEPARTMENT_MAPPING.values() else x)
                    pub_quartile_melted_dept = pub_quartile_data_dept.melt(id_vars=['Department', 'Year'], value_vars=quartile_cols, var_name='Çeyreklik', value_name='Sayı')
                    pub_quartile_melted_dept['Çeyreklik'] = pub_quartile_melted_dept['Çeyreklik'].map({
                        'Q1 Articles': 'Q1 Makaleleri',
                        'Q2 Articles': 'Q2 Makaleleri',
                        'Q3 Articles': 'Q3 Makaleleri',
                        'Q4 Articles': 'Q4 Makaleleri'
                    })
                    for year in ['2023', '2024']:
                        for dept in pub_quartile_data_dept['Department'].unique():
                            dept_data = pub_quartile_melted_dept[(pub_quartile_melted_dept['Department'] == dept) & (pub_quartile_melted_dept['Year'] == year)]
                            if dept_data['Sayı'].sum() > 0:
                                fig = px.pie(dept_data, names='Çeyreklik', values='Sayı', title=f"{year} - {dept} için Yayın Çeyreklik Dağılımı", color_discrete_map=COLOR_MAP)
                                fig.update_layout(height=500, width=800)
                                st.plotly_chart(fig, use_container_width=True, key=f"pie_dept_{dept}_{year}")

            # Faculty and Publication Type Heatmap
            st.header("Fakülte ve Yayın Türü Dağılımı", anchor="fakulte-yayin-turu")
            st.markdown("Fakültelerdeki yayın türlerinin ısı haritası.")
            tab1, tab2 = st.tabs(["Fakülteler", "Bölümler"])
            with tab1:
                heatmap_data_faculty = filtered_df.groupby(['Faculty', 'Year'])[pub_types].sum().reset_index()
                heatmap_data_faculty['Faculty'] = heatmap_data_faculty['Faculty'].map(lambda x: list(FACULTY_MAPPING.keys())[list(FACULTY_MAPPING.values()).index(x)] if x in FACULTY_MAPPING.values() else x)
                for year in ['2023', '2024']:
                    heatmap_year = heatmap_data_faculty[heatmap_data_faculty['Year'] == year].set_index('Faculty')[pub_types]
                    heatmap_year = heatmap_year.loc[heatmap_year.sum(axis=1) > 0, :]
                    heatmap_year = heatmap_year.reindex(index=[FACULTY_MAPPING[f] for f in FACULTY_ORDER if FACULTY_MAPPING[f] in heatmap_year.index])
                    heatmap_year.columns = [pub_type_labels[col] for col in heatmap_year.columns]
                    fig2 = px.imshow(heatmap_year, title=f"{year} - Fakülte ve Yayın Türü Dağılımı",
                                     labels=dict(x="Yayın Türü", y="Fakülte", color="Sayı"), color_continuous_scale="Blues")
                    fig2.update_layout(height=800, width=900, xaxis={'tickangle': 45})
                    st.plotly_chart(fig2, use_container_width=True, key=f"heatmap_faculty_{year}")
            with tab2:
                heatmap_data_dept = filtered_df.groupby(['Department', 'Year'])[pub_types].sum().reset_index()
                heatmap_data_dept['Department'] = heatmap_data_dept['Department'].map(lambda x: list(DEPARTMENT_MAPPING.keys())[list(DEPARTMENT_MAPPING.values()).index(x)] if x in DEPARTMENT_MAPPING.values() else x)
                for year in ['2023', '2024']:
                    heatmap_year = heatmap_data_dept[heatmap_data_dept['Year'] == year].set_index('Department')[pub_types]
                    heatmap_year = heatmap_year.loc[heatmap_year.sum(axis=1) > 0, :]
                    heatmap_year = heatmap_year.reindex(index=[DEPARTMENT_MAPPING[d] for d in DEPARTMENT_ORDER if DEPARTMENT_MAPPING[d] in heatmap_year.index])
                    heatmap_year.columns = [pub_type_labels[col] for col in heatmap_year.columns]
                    fig2 = px.imshow(heatmap_year, title=f"{year} - Bölüm ve Yayın Türü Dağılımı",
                                     labels=dict(x="Yayın Türü", y="Bölüm", color="Sayı"), color_continuous_scale="Blues")
                    fig2.update_layout(height=800, width=900, xaxis={'tickangle': 45})
                    st.plotly_chart(fig2, use_container_width=True, key=f"heatmap_dept_{year}")

            # Top 5 Units by Total Publications
            st.header("Toplam Yayın Sayısına Göre İlk 5 Birim", anchor="top-5-birim")
            st.markdown("2023 ve 2024 için en aktif 5 fakülte ve bölüm.")
            tab1, tab2 = st.tabs(["Fakülteler", "Bölümler"])
            with tab1:
                faculty_year_totals = filtered_df.groupby(['Faculty', 'Year'])['Total Publications'].sum().reset_index()
                faculty_year_totals['Faculty'] = faculty_year_totals['Faculty'].map(lambda x: list(FACULTY_MAPPING.keys())[list(FACULTY_MAPPING.values()).index(x)] if x in FACULTY_MAPPING.values() else x)
                top_5_faculties = faculty_year_totals.groupby('Faculty')['Total Publications'].sum().nlargest(5).index
                top_faculty_data = faculty_year_totals[faculty_year_totals['Faculty'].isin(top_5_faculties)]
                fig3_faculty = px.bar(top_faculty_data, x='Faculty', y='Total Publications', color='Year', barmode='group',
                                      title="Toplam Yayın Sayısına Göre İlk 5 Fakülte",
                                      color_discrete_map=YEAR_COLOR_MAP)
                fig3_faculty.update_layout(xaxis_tickangle=45, height=500, width=900)
                st.plotly_chart(fig3_faculty, use_container_width=True, key="top_5_faculties_bar")
            with tab2:
                dept_year_totals = filtered_df.groupby(['Department', 'Year'])['Total Publications'].sum().reset_index()
                dept_year_totals['Department'] = dept_year_totals['Department'].map(lambda x: list(DEPARTMENT_MAPPING.keys())[list(DEPARTMENT_MAPPING.values()).index(x)] if x in FACULTY_MAPPING.values() else x)
                top_5_depts = dept_year_totals.groupby('Department')['Total Publications'].sum().nlargest(5).index
                top_dept_data = dept_year_totals[dept_year_totals['Department'].isin(top_5_depts)]
                fig3_dept = px.bar(top_dept_data, x='Department', y='Total Publications', color='Year', barmode='group',
                                   title="Toplam Yayın Sayısına Göre İlk 5 Bölüm",
                                   color_discrete_map=YEAR_COLOR_MAP)
                fig3_dept.update_layout(xaxis_tickangle=45, height=500, width=900)
                st.plotly_chart(fig3_dept, use_container_width=True, key="top_5_depts_bar")
            
            # Title-wise Publication Distribution
            st.header("Unvan Bazında Yayın Dağılımı", anchor="unvan-dagilim")
            st.markdown("2023 ve 2024 için akademik unvanların yayın katkıları.")
            
            # Apply title mapping to ensure consistency
            title_mapping = {
                "Prof. Dr.": "Prof. Dr.",
                "Doç. Dr.": "Doç. Dr.",
                "Dr. Öğr. Üyesi": "Dr. Öğr. Üyesi",
                "Araştırma Görevlisi": "Diğer Ünvanlar",
                "Öğretim Görevlisi": "Diğer Ünvanlar",
                "Araştırmacı": "Diğer Ünvanlar",
                "İdari Personel": "Diğer Ünvanlar",
                "Diğer": "Diğer Ünvanlar",
                "Arş. Gör.": "Diğer Ünvanlar",
                "Öğr. Gör.": "Diğer Ünvanlar"
            }
            filtered_df['Title'] = filtered_df['Title'].map(title_mapping).fillna("Diğer Ünvanlar")
            title_year_pubs = filtered_df.groupby(['Title', 'Year'])['Total Publications'].sum().reset_index()
            title_order_updated = ["Dr. Öğr. Üyesi", "Doç. Dr.", "Prof. Dr.", "Diğer Ünvanlar"]
            title_year_pubs['Title'] = pd.Categorical(title_year_pubs['Title'], categories=title_order_updated, ordered=True)
            
            # Debug: Display raw publication counts
            st.write("**Unvan Bazında Yayın Sayıları**")
            st.dataframe(title_year_pubs.pivot(index='Title', columns='Year', values='Total Publications').fillna(0))
            
            # Plot for all titles
            fig_titles = px.bar(title_year_pubs, x='Title', y='Total Publications', color='Year', barmode='group',
                                title="Unvan Bazında Yayın Dağılımı",
                                color_discrete_map=YEAR_COLOR_MAP)
            max_y = title_year_pubs['Total Publications'].max() + 10 if not title_year_pubs.empty else 100
            fig_titles.update_layout(
                xaxis_tickangle=45,
                height=500,
                width=900,
                xaxis_title="Unvan",
                yaxis=dict(range=[0, max_y], title="Toplam Yayın")
            )
            st.plotly_chart(fig_titles, use_container_width=True, key="title_wise_pubs_bar")
            
            # Publication Change (2023-2024)
            st.header("Yayın Değişimi (2023-2024)", anchor="yayin-degisim-2023-2024")
            st.markdown("Birimlerin 2023-2024 arası yayın sayılarındaki değişim.")
            tab1, tab2 = st.tabs(["Fakülteler", "Bölümler"])
            with tab1:
                faculty_year_pubs = filtered_df.groupby(['Faculty', 'Year'])['Total Publications'].sum().unstack().fillna(0)
                faculty_year_pubs['Change'] = faculty_year_pubs['2024'] - faculty_year_pubs['2023']
                faculty_year_pubs['Change Type'] = faculty_year_pubs['Change'].apply(lambda x: 'increase' if x >= 0 else 'decrease')
                change_df_faculty = faculty_year_pubs.reset_index()[['Faculty', 'Change', 'Change Type']]
                change_df_faculty['Faculty'] = change_df_faculty['Faculty'].map(lambda x: list(FACULTY_MAPPING.keys())[list(FACULTY_MAPPING.values()).index(x)] if x in FACULTY_MAPPING.values() else x)
                fig6_faculty = px.bar(change_df_faculty, x='Faculty', y='Change', color='Change Type',
                                      title="Fakülte Bazında Yayın Değişimi (2023-2024)",
                                      color_discrete_map=CHANGE_COLOR_MAP)
                fig6_faculty.update_layout(xaxis_tickangle=45, height=500, width=900)
                st.plotly_chart(fig6_faculty, use_container_width=True, key="pub_change_faculty_bar")
            with tab2:
                dept_year_pubs = filtered_df.groupby(['Department', 'Year'])['Total Publications'].sum().unstack().fillna(0)
                dept_year_pubs['Change'] = dept_year_pubs['2024'] - dept_year_pubs['2023']
                dept_year_pubs['Change Type'] = dept_year_pubs['Change'].apply(lambda x: 'increase' if x >= 0 else 'decrease')
                change_df_dept = dept_year_pubs.reset_index()[['Department', 'Change', 'Change Type']]
                change_df_dept['Department'] = change_df_dept['Department'].map(lambda x: list(DEPARTMENT_MAPPING.keys())[list(DEPARTMENT_MAPPING.values()).index(x)] if x in DEPARTMENT_MAPPING.values() else x)
                fig6_dept = px.bar(change_df_dept, x='Department', y='Change', color='Change Type',
                                   title="Bölüm Bazında Yayın Değişimi (2023-2024)",
                                   color_discrete_map=CHANGE_COLOR_MAP)
                fig6_dept.update_layout(xaxis_tickangle=45, height=500, width=900)
                st.plotly_chart(fig6_dept, use_container_width=True, key="pub_change_dept_bar")

            # Top 5 Researchers by Total Publications
            st.header("Toplam Yayın Sayısına Göre İlk 5 Araştırmacı", anchor="top-5-arastirmaci")
            st.markdown("En aktif 5 araştırmacı.")
            top_researchers = filtered_df.groupby(['Name', 'Faculty', 'Department'])['Total Publications'].sum().reset_index()
            top_researchers['Faculty'] = top_researchers['Faculty'].map(lambda x: list(FACULTY_MAPPING.keys())[list(FACULTY_MAPPING.values()).index(x)] if x in FACULTY_MAPPING.values() else x)
            top_researchers['Department'] = top_researchers['Department'].map(lambda x: list(DEPARTMENT_MAPPING.keys())[list(DEPARTMENT_MAPPING.values()).index(x)] if x in DEPARTMENT_MAPPING.values() else x)
            top_5_researchers = top_researchers.nlargest(5, 'Total Publications')
            fig7 = go.Figure(data=[
                go.Table(
                    header=dict(values=['İsim', 'Fakülte', 'Bölüm', 'Toplam Yayın'],
                                fill_color='paleturquoise', align='left'),
                    cells=dict(values=[top_5_researchers['Name'], top_5_researchers['Faculty'],
                                      top_5_researchers['Department'], top_5_researchers['Total Publications']],
                               fill_color='lavender', align='left'))
            ])
            st.plotly_chart(fig7, use_container_width=True, key="top_5_researchers_table")

            # Impact Score
            st.header("Etki Puanı", anchor="etki-puani")
            st.markdown("2023 ve 2024 için birimlerin toplam etki puanı.")
            tab1, tab2 = st.tabs(["Fakülteler", "Bölümler"])
            with tab1:
                faculty_year_impact = filtered_df.groupby(['Faculty', 'Year'])['Impact Score'].sum().reset_index()
                faculty_year_impact['Faculty'] = faculty_year_impact['Faculty'].map(lambda x: list(FACULTY_MAPPING.keys())[list(FACULTY_MAPPING.values()).index(x)] if x in FACULTY_MAPPING.values() else x)
                fig8_faculty = px.bar(faculty_year_impact, x='Faculty', y='Impact Score', color='Year', barmode='group',
                                      title="Fakülte Bazında Etki Puanı",
                                      color_discrete_map=YEAR_COLOR_MAP)
                fig8_faculty.update_layout(xaxis_tickangle=45, height=500, width=900)
                st.plotly_chart(fig8_faculty, use_container_width=True, key="impact_score_faculty_bar")
            with tab2:
                dept_year_impact = filtered_df.groupby(['Department', 'Year'])['Impact Score'].sum().reset_index()
                dept_year_impact['Department'] = dept_year_impact['Department'].map(lambda x: list(DEPARTMENT_MAPPING.keys())[list(DEPARTMENT_MAPPING.values()).index(x)] if x in DEPARTMENT_MAPPING.values() else x)
                fig8_dept = px.bar(dept_year_impact, x='Department', y='Impact Score', color='Year', barmode='group',
                                   title="Bölüm Bazında Etki Puanı",
                                   color_discrete_map=YEAR_COLOR_MAP)
                fig8_dept.update_layout(xaxis_tickangle=45, height=500, width=900)
                st.plotly_chart(fig8_dept, use_container_width=True, key="impact_score_dept_bar")
            st.markdown("**Hesaplama:** Etki puanı, yayın türlerine göre ağırlıklı bir toplam olarak hesaplanır: Q1 makaleleri için 4 puan, Q2 için 3 puan, Q3 için 2 puan, Q4 için 1 puan, ESCI, Scopus ve çeyreklik olmayan makaleler için 0.5 puan. Formül: **Etki Puanı = (Q1 × 4) + (Q2 × 3) + (Q3 × 2) + (Q4 × 1) + [(ESCI + Scopus + Çeyreklik Olmayan) × 0.5]**. Örnek: Bir fakültede 5 Q1 (5×4=20), 3 Q2 (3×3=9), 2 ESCI (2×0.5=1) makale varsa, toplam etki puanı 20+9+1=30 olur.")

            # Publication and Impact Score (Scatter Plot)
            st.header("Yayın ve Etki Puanı", anchor="yayin-etki")
            st.markdown("Birimlerin toplam yayın ve etki puanı ilişkisi.")
            tab1, tab2 = st.tabs(["Fakülteler", "Bölümler"])
            with tab1:
                scatter_data_faculty = filtered_df.groupby(['Faculty', 'Year'])[['Total Publications', 'Impact Score']].sum().reset_index()
                scatter_data_faculty['Faculty'] = scatter_data_faculty['Faculty'].map(lambda x: list(FACULTY_MAPPING.keys())[list(FACULTY_MAPPING.values()).index(x)] if x in FACULTY_MAPPING.values() else x)
                fig8b_faculty = px.scatter(scatter_data_faculty, x='Total Publications', y='Impact Score', color='Faculty', symbol='Year',
                                           title="Fakülte Bazında Yayın ve Etki Puanı", size='Total Publications')
                fig8b_faculty.update_layout(height=600, width=900)
                st.plotly_chart(fig8b_faculty, use_container_width=True, key="scatter_faculty_plot")
            with tab2:
                scatter_data_dept = filtered_df.groupby(['Department', "Year"])[['Total Publications', 'Impact Score']].sum().reset_index()
                scatter_data_dept['Department'] = scatter_data_dept['Department'].map(lambda x: list(DEPARTMENT_MAPPING.keys())[list(DEPARTMENT_MAPPING.values()).index(x)] if x in DEPARTMENT_MAPPING.values() else x)
                fig8b_dept = px.scatter(scatter_data_dept, x='Total Publications', y='Impact Score', color='Department', symbol='Year',
                                        title="Bölüm Bazında Yayın ve Etki Puanı", size='Total Publications')
                fig8b_dept.update_layout(height=600, width=900)
                st.plotly_chart(fig8b_dept, use_container_width=True, key="scatter_dept_plot")
            st.markdown("**Hesaplama:** Bu görselleştirme, birimlerin toplam yayın sayılarını (tüm yayın türlerinin toplamı) ve etki puanlarını (yukarıda açıklanan formülle hesaplanan) karşılaştırır. Her nokta bir fakülte veya bölümü temsil eder, nokta boyutu toplam yayın sayısını, sembol ise yılı (2023 veya 2024) gösterir.")

            # Active Researcher Ratio
            st.header("Aktif Araştırmacı Oranı", anchor="aktif-oran")
            st.markdown("Birimlerde aktif araştırmacı oranı.")
            tab1, tab2 = st.tabs(["Fakülteler", "Bölümler"])
            with tab1:
                total_researchers_faculty = filtered_df.groupby(['Faculty', 'Year'])['Name'].nunique().reset_index(name='Toplam Araştırmacılar')
                active_researchers_faculty = filtered_df[filtered_df['Total Publications'] > 0].groupby(['Faculty', 'Year'])['Name'].nunique().reset_index(name='Aktif Araştırmacılar')
                total_researchers_faculty['Faculty'] = total_researchers_faculty['Faculty'].map(lambda x: list(FACULTY_MAPPING.keys())[list(FACULTY_MAPPING.values()).index(x)] if x in FACULTY_MAPPING.values() else x)
                active_researchers_faculty['Faculty'] = active_researchers_faculty['Faculty'].map(lambda x: list(FACULTY_MAPPING.keys())[list(FACULTY_MAPPING.values()).index(x)] if x in FACULTY_MAPPING.values() else x)
                ratio_df_faculty = total_researchers_faculty.merge(active_researchers_faculty, on=['Faculty', 'Year'], how='left').fillna({'Aktif Araştırmacılar': 0})
                ratio_df_faculty['Aktif Araştırmacı Oranı'] = ratio_df_faculty['Aktif Araştırmacılar'] / ratio_df_faculty['Toplam Araştırmacılar']
                fig9_faculty = px.bar(ratio_df_faculty, x='Faculty', y='Aktif Araştırmacı Oranı', color='Year', barmode='group',
                                      title="Fakülte Bazında Aktif Araştırmacı Oranı",
                                      color_discrete_map=YEAR_COLOR_MAP)
                fig9_faculty.update_layout(xaxis_tickangle=45, height=500, width=900)
                st.plotly_chart(fig9_faculty, use_container_width=True, key="active_ratio_faculty_bar")
            with tab2:
                total_researchers_dept = filtered_df.groupby(['Department', 'Year'])['Name'].nunique().reset_index(name='Toplam Araştırmacılar')
                active_researchers_dept = filtered_df[filtered_df['Total Publications'] > 0].groupby(['Department', 'Year'])['Name'].nunique().reset_index(name='Aktif Araştırmacılar')
                total_researchers_dept['Department'] = total_researchers_dept['Department'].map(lambda x: list(DEPARTMENT_MAPPING.keys())[list(DEPARTMENT_MAPPING.values()).index(x)] if x in DEPARTMENT_MAPPING.values() else x)
                active_researchers_dept['Department'] = active_researchers_dept['Department'].map(lambda x: list(DEPARTMENT_MAPPING.keys())[list(DEPARTMENT_MAPPING.values()).index(x)] if x in DEPARTMENT_MAPPING.values() else x)
                ratio_df_dept = total_researchers_dept.merge(active_researchers_dept, on=['Department', 'Year'], how='left').fillna({'Aktif Araştırmacılar': 0})
                ratio_df_dept['Aktif Araştırmacı Oranı'] = ratio_df_dept['Aktif Araştırmacılar'] / ratio_df_dept['Toplam Araştırmacılar']
                fig9_dept = px.bar(ratio_df_dept, x='Department', y='Aktif Araştırmacı Oranı', color='Year', barmode='group',
                                   title="Bölüm Bazında Aktif Araştırmacı Oranı",
                                   color_discrete_map=YEAR_COLOR_MAP)
                fig9_dept.update_layout(xaxis_tickangle=45, height=500, width=900)
                st.plotly_chart(fig9_dept, use_container_width=True, key="active_ratio_dept_bar")

            # Publications by Year
            st.header("Yıl Bazında Yayınlar", anchor="yil-bazinda-yayinlar")
            st.markdown("2023 ve 2024 için birimlerin yayın sayıları.")
            tab1, tab2 = st.tabs(["Fakülteler", "Bölümler"])
            with tab1:
                faculty_year_pubs = filtered_df.groupby(['Faculty', 'Year'])['Total Publications'].sum().reset_index()
                faculty_year_pubs['Faculty'] = faculty_year_pubs['Faculty'].map(lambda x: list(FACULTY_MAPPING.keys())[list(FACULTY_MAPPING.values()).index(x)] if x in FACULTY_MAPPING.values() else x)
                fig10_faculty = px.bar(faculty_year_pubs, x='Faculty', y='Total Publications', color='Year', barmode='group',
                                       title="Fakülte Bazında Yıl Bazında Yayınlar",
                                       color_discrete_map=YEAR_COLOR_MAP)
                fig10_faculty.update_layout(xaxis_tickangle=45, height=500, width=900)
                st.plotly_chart(fig10_faculty, use_container_width=True, key="pubs_by_year_faculty_bar")
            with tab2:
                dept_year_pubs = filtered_df.groupby(['Department', 'Year'])['Total Publications'].sum().reset_index()
                dept_year_pubs['Department'] = dept_year_pubs['Department'].map(lambda x: list(DEPARTMENT_MAPPING.keys())[list(DEPARTMENT_MAPPING.values()).index(x)] if x in DEPARTMENT_MAPPING.values() else x)
                fig10_dept = px.bar(dept_year_pubs, x='Department', y='Total Publications', color='Year', barmode='group',
                                    title="Bölüm Bazında Yıl Bazında Yayınlar",
                                    color_discrete_map=YEAR_COLOR_MAP)
                fig10_dept.update_layout(xaxis_tickangle=45, height=500, width=900)
                st.plotly_chart(fig10_dept, use_container_width=True, key="pubs_by_year_dept_bar")

            # Quartile Diversity Index
            st.header("Çeyreklik Çeşitlilik İndeksi", anchor="cesitlilik-indeksi")
            st.markdown("Birimlerin Q1-Q4 makale çeşitliliği.")
            tab1, tab2 = st.tabs(["Fakülteler", "Bölümler"])
            with tab1:
                def shannon_diversity(row):
                    counts = [row[col] for col in quartile_cols]
                    total = sum(counts)
                    if total == 0:
                        return 0
                    proportions = [c / total for c in counts if c > 0]
                    return -sum(p * np.log(p) for p in proportions) if proportions else 0
                faculty_quartile = filtered_df.groupby(['Faculty', 'Year'])[quartile_cols].sum().reset_index()
                faculty_quartile['Diversity Index'] = faculty_quartile[quartile_cols].apply(shannon_diversity, axis=1)
                faculty_quartile['Faculty'] = faculty_quartile['Faculty'].map(lambda x: list(FACULTY_MAPPING.keys())[list(FACULTY_MAPPING.values()).index(x)] if x in FACULTY_MAPPING.values() else x)
                fig11_faculty = px.bar(faculty_quartile, x='Faculty', y='Diversity Index', color='Year', barmode='group',
                                       title="Fakülte Bazında Çeyreklik Çeşitlilik İndeksi",
                                       color_discrete_map=YEAR_COLOR_MAP)
                fig11_faculty.update_layout(xaxis_tickangle=45, height=500, width=900)
                st.plotly_chart(fig11_faculty, use_container_width=True, key="diversity_index_faculty_bar")
            with tab2:
                dept_quartile = filtered_df.groupby(['Department', 'Year'])[quartile_cols].sum().reset_index()
                dept_quartile['Diversity Index'] = dept_quartile[quartile_cols].apply(shannon_diversity, axis=1)
                dept_quartile['Department'] = dept_quartile['Department'].map(lambda x: list(DEPARTMENT_MAPPING.keys())[list(DEPARTMENT_MAPPING.values()).index(x)] if x in DEPARTMENT_MAPPING.values() else x)
                fig11_dept = px.bar(dept_quartile, x='Department', y='Diversity Index', color='Year', barmode='group',
                                    title="Bölüm Bazında Çeyreklik Çeşitlilik İndeksi",
                                    color_discrete_map=YEAR_COLOR_MAP)
                fig11_dept.update_layout(xaxis_tickangle=45, height=500, width=900)
                st.plotly_chart(fig11_dept, use_container_width=True, key="diversity_index_dept_bar")
            st.markdown("**Hesaplama:** Çeyreklik Çeşitlilik İndeksi, Shannon Entropi formülü kullanılarak hesaplanır. Q1, Q2, Q3 ve Q4 makalelerinin toplam yayın içindeki oranları dikkate alınır. Formül: **H = -Σ(p_i * ln(p_i))**; burada p_i, her çeyreklik türünün toplam yayınlara oranıdır. Örneğin, bir fakültede 10 Q1, 5 Q2, 5 Q3 ve 0 Q4 makale varsa, toplam 20 makale olur. Oranlar: Q1=0.5, Q2=0.25, Q3=0.25. H = -[(0.5 * ln(0.5)) + (0.25 * ln(0.25)) + (0.25 * ln(0.25))] ≈ 1.04. Daha yüksek indeks, daha dengeli bir çeyreklik dağılımını gösterir.")

            # Top Publication Types
            st.header("En Yaygın Yayın Türleri", anchor="en-yaygin-yayin")
            st.markdown("Birimlerdeki en yaygın yayın türleri.")
            tab1, tab2 = st.tabs(["Fakülteler", "Bölümler"])
            with tab1:
                pub_type_sums_faculty = filtered_df.groupby(['Faculty', 'Year'])[pub_types].sum().reset_index()
                pub_type_sums_faculty['Faculty'] = pub_type_sums_faculty['Faculty'].map(lambda x: list(FACULTY_MAPPING.keys())[list(FACULTY_MAPPING.values()).index(x)] if x in FACULTY_MAPPING.values() else x)
                pub_type_melted_faculty = pub_type_sums_faculty.melt(id_vars=['Faculty', 'Year'], value_vars=pub_types, var_name='Publication Type', value_name='Sayı')
                pub_type_melted_faculty['Publication Type'] = pub_type_melted_faculty['Publication Type'].map(pub_type_labels)
                top_pub_types_faculty = pub_type_melted_faculty.groupby('Publication Type')['Sayı'].sum().nlargest(5).index
                
                # 2023 Chart
                faculty_2023 = pub_type_melted_faculty[(pub_type_melted_faculty['Publication Type'].isin(top_pub_types_faculty)) & (pub_type_melted_faculty['Year'] == '2023')]
                fig12_faculty_2023 = px.bar(faculty_2023, x='Faculty', y='Sayı', color='Publication Type', barmode='stack',
                                            title="Fakülte Bazında En Yaygın Yayın Türleri (2023)", color_discrete_map=COLOR_MAP)
                fig12_faculty_2023.update_layout(xaxis_tickangle=45, height=600, width=900)
                st.plotly_chart(fig12_faculty_2023, use_container_width=True, key="faculty_top_pub_types_2023")
                
                # 2024 Chart
                faculty_2024 = pub_type_melted_faculty[(pub_type_melted_faculty['Publication Type'].isin(top_pub_types_faculty)) & (pub_type_melted_faculty['Year'] == '2024')]
                fig12_faculty_2024 = px.bar(faculty_2024, x='Faculty', y='Sayı', color='Publication Type', barmode='stack',
                                            title="Fakülte Bazında En Yaygın Yayın Türleri (2024)", color_discrete_map=COLOR_MAP)
                fig12_faculty_2024.update_layout(xaxis_tickangle=45, height=600, width=900)
                st.plotly_chart(fig12_faculty_2024, use_container_width=True, key="faculty_top_pub_types_2024")
                
            with tab2:
                pub_type_sums_dept = filtered_df.groupby(['Department', 'Year'])[pub_types].sum().reset_index()
                pub_type_sums_dept['Department'] = pub_type_sums_dept['Department'].map(lambda x: list(DEPARTMENT_MAPPING.keys())[list(DEPARTMENT_MAPPING.values()).index(x)] if x in DEPARTMENT_MAPPING.values() else x)
                pub_type_melted_dept = pub_type_sums_dept.melt(id_vars=['Department', 'Year'], value_vars=pub_types, var_name='Publication Type', value_name='Sayı')
                pub_type_melted_dept['Publication Type'] = pub_type_melted_dept['Publication Type'].map(pub_type_labels)
                top_pub_types_dept = pub_type_melted_dept.groupby('Publication Type')['Sayı'].sum().nlargest(5).index
                
                # 2023 Chart
                dept_2023 = pub_type_melted_dept[(pub_type_melted_dept['Publication Type'].isin(top_pub_types_dept)) & (pub_type_melted_dept['Year'] == '2023')]
                fig12_dept_2023 = px.bar(dept_2023, x='Department', y='Sayı', color='Publication Type', barmode='stack',
                                         title="Bölüm Bazında En Yaygın Yayın Türleri (2023)", color_discrete_map=COLOR_MAP)
                fig12_dept_2023.update_layout(xaxis_tickangle=45, height=600, width=900)
                st.plotly_chart(fig12_dept_2023, use_container_width=True, key="dept_top_pub_types_2023")
                
                # 2024 Chart
                dept_2024 = pub_type_melted_dept[(pub_type_melted_dept['Publication Type'].isin(top_pub_types_dept)) & (pub_type_melted_dept['Year'] == '2024')]
                fig12_dept_2024 = px.bar(dept_2024, x='Department', y='Sayı', color='Publication Type', barmode='stack',
                                         title="Bölüm Bazında En Yaygın Yayın Türleri (2024)", color_discrete_map=COLOR_MAP)
                fig12_dept_2024.update_layout(xaxis_tickangle=45, height=600, width=900)
                st.plotly_chart(fig12_dept_2024, use_container_width=True, key="dept_top_pub_types_2024")

else:
    with st.container():
        st.warning("Lütfen 2023 ve 2024 Excel dosyalarını yükleyin.")

# Application footer
st.markdown("---")
st.markdown("Kerem Delialioğlu")
st.markdown("Orta Doğu Teknik Üniversitesi — Proje Destek Ofisi")
st.markdown("2025")
