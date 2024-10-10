from flask import Flask, render_template,request,jsonify,send_from_directory
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import json
import plotly
import folium
from folium.plugins import HeatMap
from folium import Marker, IFrame
import requests
from bs4 import BeautifulSoup
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
import os

app = Flask(__name__)

# CSV file load
df = pd.read_csv('deprem-senaryosu-analiz-sonuclar.csv', sep=';')
deprem_verisi = df.copy()
data = pd.read_csv("İstanbul_cordinat.csv")

# Özellikler ve KMeans parametreleri
features = {
    'bina': ['cok_agir_hasarli_bina_sayisi', 'agir_hasarli_bina_sayisi', 'orta_hasarli_bina_sayisi'],
    'can_kaybi': ['can_kaybi_sayisi', 'agir_yarali_sayisi'],
    'personel_ihtiyacı': ['hastanede_tedavi_sayisi'],
    'dogalgaz': ['dogalgaz_boru_hasari'],
    'su': ['icme_suyu_boru_hasari', 'atik_su_boru_hasari'],
    'barinma': ['gecici_barinma']
}

risk_kategorileri = {
    'bina_risk_kategorisi': {
        0: ('Düşük Riskli Bölge', 'Yapı hasarı açısından güvenli kabul edilen bir bölgedir. Acil önlem gerektirmez; hasar oranı düşük düzeydedir.'),
        1: ('İzlenmesi Gereken Bölge', 'Mevcut yapılar depremden sonra hafif hasar görmüştür. Tehlike seviyesi düşük olsa da, bölgenin düzenli olarak izlenmesi ve gerekli güçlendirme çalışmalarının yapılması önerilir.'),
        2: ('Ciddi Hasar Görmüş Bölge', 'Çok sayıda yapı ciddi hasar almış durumda. Kısmi tahliyeler gerekebilir; acil müdahale gereken yapılar mevcuttur.'),
        3: ('Yüksek Riskli Bölge', 'Yapılar büyük ölçüde hasar görmüştür. Bölge derhal boşaltılmalı ve acil iyileştirme çalışmaları başlatılmalıdır.')
    },
    'can_kaybi_risk_kategorisi': {
        0: ('Düşük Risk', 'Can kaybı ve ağır yaralanmalar çok azdır. Afet sonrası bölge güvenli olarak değerlendirilir.'),
        1: ('Orta Risk', 'Can kaybı ve ağır yaralanmalar mevcuttur. Acil önlem gerektirmeyen, ancak tedaviye ihtiyaç duyan yaralanmalar oluşmuştur.'),
        2: ('Yüksek Risk - Ciddi Yaralanmalar', 'Ciddi yaralanmalar ve can kaybı yaşanmıştır. Bölge acil müdahale gerektiren alan olarak değerlendirilmelidir.'),
        3: ('Kritik Bölge - Yüksek Ölüm Riski', 'Çok sayıda can kaybı ve ağır yaralanma vardır. Bölge derhal müdahale gerekmektedir ve kurtarma çalışmaları öncelikli olmalıdır.')
    },
    'personel_ihtiyacı_risk_kategorisi': {
        0: ('Düşük Personel İhtiyacı', 'Bölge mevcut personel sayısıyla yeterli durumda, ek personel gereksinimi bulunmamaktadır.'),
        1: ('İzleme Gerektiren Personel İhtiyacı', 'Bölgeye izleme gerektiren bir personel ihtiyacı vardır; az sayıda ek personel gerekli olabilir.'),
        2: ('Ciddi Personel İhtiyacı', 'Personel ihtiyacı belirgin şekilde artmış durumdadır; ek personel desteği gerekmektedir.'),
        3: ('Acil Personel İhtiyacı', 'Bölgede hastanede tedavi görmesi gereken çok sayıda insan var. Sağlık personeli takviyesi acil olarak gerekmektedir.')
    },
    'yangin_risk_kategorisi': {
        0: ('Düşük Yangın Riski', 'Doğalgaz hatlarında az sayıda tespit edilmemiştir; deprem sonraı yangın riski düşüktür.'),
        1: ('Orta Seviyede Yangın Riski', 'Doğalgaz hatlarında hafif hasarlar mevcuttur. Bölgenin izlenmesi ve deprem sonrası yangın riski açısından tedbir alınması gerekmektedir.'),
        2: ('Yüksek Yangın Riski', 'Doğalgaz hatları ciddi hasar görmüştür. Deprem sonrasu yangın çıkma riski yüksektir; acil müdahale gerekmektedir.')
    },
    'hastalik_risk_kategorisi': {
        0: ('Düşük Hastalık Riski', 'Su ve kanalizasyon hatları hasarsız veya düşük düzeyde hasar görmüştür; bölge güvenli kabul edilmektedir.'),
        1: ('Orta Seviyede Hastalık Riski', 'İçme suyu ve atık su hatlarında hasar bulunmaktadır; hastalık riski göz önünde bulundurulmalıdır. Bölge izlenmeli ve su kaynakları kontrol altında tutulmalıdır.'),
        2: ('Yüksek Hastalık Riski', 'Su ve kanalizasyon hatları ciddi hasar görmüştür; bölgede salgın hastalık riski yüksektir. Temiz suya erişim sağlanmalı ve hijyen koşulları iyileştirilmelidir.')
    },
    'barinma_risk_kategorisi': {
        0: ('Yeterli Barınma Kapasitesi', 'Geçici barınma imkânları yeterli seviyededir; bölgedeki insanların barınma ihtiyacı karşılanmaktadır.'),
        1: ('Kısıtlı Barınma Kapasitesi', 'Barınma kapasitesi sınırlıdır; bölgeye daha fazla barınma imkânı sağlanması gerekebilir.'),
        2: ('Yetersiz Barınma Kapasitesi', 'Geçici barınma kapasitesi yetersizdir; bölgedeki insanlar için acil barınma desteği sağlanmalıdır.')
    }
}


# Normalizasyon işlemleri
def scale_features(dataframe, features):
    scaler = StandardScaler()
    return scaler.fit_transform(dataframe[features])

def apply_kmeans(data, n_clusters):
    kmeans = KMeans(n_clusters=n_clusters, random_state=42)
    return kmeans.fit_predict(data)

# Kategorileri oluştur
def create_risk_categories(df):
    scaled_data = {
        'bina': scale_features(df, features['bina']),
        'can_kaybi': scale_features(df, features['can_kaybi']),
        'personel_ihtiyacı': scale_features(df, features['personel_ihtiyacı']),
        'dogalgaz': scale_features(df, features['dogalgaz']),
        'su': scale_features(df, features['su']),
        'barinma': scale_features(df, features['barinma'])
    }

    df['bina_risk_kategorisi'] = apply_kmeans(scaled_data['bina'], n_clusters=4)
    df['can_kaybi_risk_kategorisi'] = apply_kmeans(scaled_data['can_kaybi'], n_clusters=4)
    df['personel_ihtiyacı_risk_kategorisi'] = apply_kmeans(scaled_data['personel_ihtiyacı'], n_clusters=4)
    df['yangin_risk_kategorisi'] = apply_kmeans(scaled_data['dogalgaz'], n_clusters=4)
    df['hastalik_risk_kategorisi'] = apply_kmeans(scaled_data['su'], n_clusters=3)
    df['barinma_risk_kategorisi'] = apply_kmeans(scaled_data['barinma'], n_clusters=3)

create_risk_categories(df)

@app.route('/get_mahalleler', methods=['GET'])
def get_mahalleler():
    ilce = request.args.get('ilce')
    mahalleler = df[df['ilce_adi'] == ilce]['mahalle_adi'].unique().tolist()
    return jsonify({'mahalleler': mahalleler})

@app.route('/tahmin', methods=['GET', 'POST'])
def tahmin():
    ilce_mahalle = df[['ilce_adi', 'mahalle_adi']].drop_duplicates()
    tahmin_sonuclari = None

    if request.method == 'POST':
        ilce = request.form['ilce']
        mahalle = request.form['mahalle']

        # Seçilen ilçe ve mahalleye göre veri filtreleme
        secilen_bolge = df[(df['ilce_adi'] == ilce) & (df['mahalle_adi'] == mahalle)]

        if not secilen_bolge.empty:
            tahmin_sonuclari = {
                'bina': risk_kategorileri['bina_risk_kategorisi'][secilen_bolge['bina_risk_kategorisi'].values[0]],
                'can_kaybi': risk_kategorileri['can_kaybi_risk_kategorisi'][secilen_bolge['can_kaybi_risk_kategorisi'].values[0]],
                'personel_ihtiyacı': risk_kategorileri['personel_ihtiyacı_risk_kategorisi'][secilen_bolge['personel_ihtiyacı_risk_kategorisi'].values[0]],
                'yangin': risk_kategorileri['yangin_risk_kategorisi'][secilen_bolge['yangin_risk_kategorisi'].values[0]],
                'hastalik': risk_kategorileri['hastalik_risk_kategorisi'][secilen_bolge['hastalik_risk_kategorisi'].values[0]],
                'barinma': risk_kategorileri['barinma_risk_kategorisi'][secilen_bolge['barinma_risk_kategorisi'].values[0]]
            }

    return render_template('model.html', ilce_mahalle=ilce_mahalle, tahmin_sonuclari=tahmin_sonuclari)


# Deprem verilerini çekme fonksiyonu
def deprem_verilerini_al():
    url = "http://www.koeri.boun.edu.tr/scripts/lst9.asp"
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser").text.strip().split("\r")

    # Gerekli listeleri oluştur
    liste_enlem, liste_boylam, liste_tarih, liste_buyukluk, liste_derinlik, liste_yer = [], [], [], [], [], []

    # Verileri ayrıştır ve listelere ekle
    for i in range(15, len(soup) - 20):
        data = soup[i].split()
        liste_tarih.append(f"{data[0]} {data[1]}")
        liste_enlem.append(float(data[2]))
        liste_boylam.append(float(data[3]))
        liste_derinlik.append(data[4])
        liste_buyukluk.append(float(data[6]))
        liste_yer.append(f"{data[8]} {data[9]}")

    # Verileri DataFrame'e çevir
    df = pd.DataFrame({
        "Tarih": liste_tarih,
        "Enlem": liste_enlem,
        "Boylam": liste_boylam,
        "Derinlik": liste_derinlik,
        "Büyüklük": liste_buyukluk,
        "Yer": liste_yer
    })

    return df


# Normal harita route
@app.route('/kandilli_son_depremler')
def son_depremler():
    df = deprem_verilerini_al()

    m = folium.Map(location=[39.1062, 39.5483], zoom_start=6)

    # Legend (Simge Bilgisi) ekle
    legend_html = '''
        <div style="position: fixed; 
                    top: 50px; right: 50px; width: 300px; height: 180px; 
                    border:2px solid grey; z-index:9999; font-size:14px;
                    background-color:white; padding: 10px;">
            &nbsp; <u>Simge Bilgisi</u> <br>
            &nbsp; Son Yaşanan Deprem &nbsp; <i class="fa fa-map-marker fa-2x" style="color:black"></i><br>
            &nbsp; Deprem Büyüklüğü &gt; 5 &nbsp; <i class="fa fa-map-marker fa-2x" style="color:red"></i><br>
            &nbsp; 3 &lt; Deprem Büyüklüğü &lt; 5 &nbsp; <i class="fa fa-map-marker fa-2x" style="color:blue"></i><br>
            &nbsp; Deprem Büyüklüğü &lt; 3 &nbsp; <i class="fa fa-map-marker fa-2x" style="color:green"></i>
        </div>
    '''
    m.get_root().html.add_child(folium.Element(legend_html))

    for i in range(len(df)):
        büyüklük = df["Büyüklük"][i]
        iframe = folium.IFrame(f"""
            <h1><strong>Deprem</strong></h1>
            <p><br/>
            Tarih: {df['Tarih'][i]}<br/>
            Yer: {df['Yer'][i]}<br/>
            Büyüklük: {büyüklük}<br/>
            Derinlik: {df['Derinlik'][i]}<br/>
            </p>
        """)
        popup = folium.Popup(iframe, min_width=290, max_width=290)

        if i == 0:
            icon_color = "black"
        elif büyüklük > 5:
            icon_color = "red"
        elif 3 < büyüklük <= 5:
            icon_color = "blue"
        else:
            icon_color = "green"

        folium.Marker(
            location=[df['Enlem'][i], df['Boylam'][i]],
            popup=popup,
            icon=folium.Icon(color=icon_color, icon='info-sign'),
            tooltip=df['Yer'][i]
        ).add_to(m)

    m.save("templates/kandilli_earthquake.html")

    return render_template("kandilli_earthquake.html")


# Isı haritası route
@app.route('/kandilli_ısı_haritası')
def deprem_isi_haritasi():
    df = deprem_verilerini_al()

    heat_data = [[row['Enlem'], row['Boylam']] for index, row in df.iterrows()]
    heat_map = folium.Map(location=[39.1062, 39.5483], tiles="OpenStreetMap", zoom_start=6)
    HeatMap(heat_data).add_to(heat_map)

    heat_map.save("templates/kandilli_heatmap.html")

    return render_template("kandilli_heatmap.html")


# Cache repetitive groupby results for performance
grouped_df = df.groupby('ilce_adi').sum().reset_index()

@app.route('/son-depremler')
def earthquake():
    return render_template("earthquake.html")


@app.route('/heat_map')
def show_heat_map():
    # 1. Veri setlerini yükle
    deprem_verisi = pd.read_csv("deprem-senaryosu-analiz-sonuclar.csv", sep=";")

    data = pd.read_csv("İstanbul_cordinat.csv")

    data[['Enlem', 'Boylam']] = data['Enlem-Boylam'].str.split(' X ', expand=True)
    data['Enlem'] = data['Enlem'].str.replace(',', '.').astype(float)
    data['Boylam'] = data['Boylam'].str.replace(',', '.').astype(float)

    # Deprem verilerini ilçeye göre grupla
    deprem_ilce_grup = deprem_verisi.groupby('ilce_adi').agg({
        'can_kaybi_sayisi': 'sum',
        'agir_yarali_sayisi': 'sum',
        'cok_agir_hasarli_bina_sayisi': 'sum',
        'agir_hasarli_bina_sayisi': 'sum',
        'orta_hasarli_bina_sayisi': 'sum',
        'hafif_hasarli_bina_sayisi': 'sum',
        'dogalgaz_boru_hasari': 'sum'
    }).reset_index()

    deprem_ilce_grup['toplam_agir_hasarli_bina'] = deprem_ilce_grup['cok_agir_hasarli_bina_sayisi'] + deprem_ilce_grup[
        'agir_hasarli_bina_sayisi']+ deprem_ilce_grup['orta_hasarli_bina_sayisi']
    deprem_ilce_grup['toplam_yasam_risk'] = deprem_ilce_grup['can_kaybi_sayisi'] + deprem_ilce_grup[
        'agir_yarali_sayisi']

    # 4. Deprem verisi ve enlem-boylam verisini birleştir
    merged_data = pd.merge(deprem_ilce_grup, data, left_on='ilce_adi', right_on='İlçe')

    # 5. Her veri türü için ısı haritası verisini hazırla
    heat_data_can_kaybi = [[row['Enlem'], row['Boylam'], row['toplam_yasam_risk']] for index, row in
                           merged_data.iterrows()]
    heat_data_agir_hasar = [[row['Enlem'], row['Boylam'], row['toplam_agir_hasarli_bina']] for index, row in
                            merged_data.iterrows()]
    heat_data_hafif_hasar = [[row['Enlem'], row['Boylam'], row['hafif_hasarli_bina_sayisi']] for index, row in
                             merged_data.iterrows()]
    heat_data_yangın_risk = [[row['Enlem'], row['Boylam'], row['dogalgaz_boru_hasari']] for index, row in
                             merged_data.iterrows()]

    # Harita oluştur ve ısı haritalarını ekle
    m = folium.Map(location=[41.0082, 28.9784], zoom_start=10, tiles="OpenStreetMap")

    HeatMap(heat_data_can_kaybi, name="Deprem Sonrası Yaşam Riski").add_to(m)

    HeatMap(heat_data_agir_hasar, name="Hasarlı Binalar").add_to(m)

    HeatMap(heat_data_hafif_hasar, name="Hafif Hasarlı Binalar").add_to(m)

    HeatMap(heat_data_yangın_risk, name="Deprem Sonrası Yangın Riski").add_to(m)

    # Haritaya kontrol katmanı ekle
    folium.LayerControl().add_to(m)

    m.save('templates/heat_map.html')
    return render_template('heat_map.html')


@app.route('/map')
def show_map():

    data[['Enlem', 'Boylam']] = data['Enlem-Boylam'].str.split(' X ', expand=True)
    data['Enlem'] = data['Enlem'].str.replace(',', '.').astype(float)
    data['Boylam'] = data['Boylam'].str.replace(',', '.').astype(float)

    # Deprem verilerini ilçeye göre grupla
    deprem_ilce_grup = deprem_verisi.groupby('ilce_adi').agg({
        'can_kaybi_sayisi': 'sum',
        'agir_yarali_sayisi': 'sum',
        'cok_agir_hasarli_bina_sayisi': 'sum',
        'agir_hasarli_bina_sayisi': 'sum',
        'orta_hasarli_bina_sayisi': 'sum',
        'hafif_hasarli_bina_sayisi': 'sum',
        'dogalgaz_boru_hasari': 'sum',
        'gecici_barinma': 'sum'
    }).reset_index()

    merged_data = pd.merge(deprem_ilce_grup, data, left_on='ilce_adi', right_on='İlçe')

    # Yaşam riski ve yıkılabilecek bina sayısının ortalamasını al
    merged_data['yasam_riski'] = merged_data['can_kaybi_sayisi'] + merged_data['agir_yarali_sayisi']
    merged_data['yikilabilecek_bina'] = merged_data['cok_agir_hasarli_bina_sayisi'] + merged_data['agir_hasarli_bina_sayisi'] + merged_data['orta_hasarli_bina_sayisi']

    yasam_riski_mean = merged_data['yasam_riski'].mean()
    yikilabilecek_bina_mean = merged_data['yikilabilecek_bina'].mean()

    m = folium.Map(location=[41.0082, 28.9784], zoom_start=10)

    legend_html = '''
        <div style="position: fixed; 
                    top: 50px; right: 50px; width: 250px; height: 140px; 
                    border:2px solid grey; z-index:9999; font-size:14px;
                    background-color:white; padding: 10px;">
        <h4>Risk Kategorileri</h4>
        <i class="fa fa-map-marker" style="color:red"></i> Yüksek Riskli Bölge<br>
        <i class="fa fa-map-marker" style="color:orange"></i> Ciddi Riskli Bölge<br>
        <i class="fa fa-map-marker" style="color:gray"></i> İzleme Gerektiren Bölge<br>
        <i class="fa fa-map-marker" style="color:green"></i> Düşük Riskli Bölge<br>
        </div>
    '''
    m.get_root().html.add_child(folium.Element(legend_html))

    # 8. Her ilçe için risk durumunu belirleyip marker ekle
    for index, row in merged_data.iterrows():
        yasam_riski = row['yasam_riski']
        yikilabilecek_bina = row['yikilabilecek_bina']

        if yasam_riski > yasam_riski_mean * 1.3 or yikilabilecek_bina > yikilabilecek_bina_mean * 1.5:
            kategori = 'Yüksek Riskli Bölge'
            renk = 'red'
        elif yasam_riski > yasam_riski_mean or yikilabilecek_bina > yikilabilecek_bina_mean:
            kategori = 'Ciddi Riskli Bölge'
            renk = 'orange'
        elif yasam_riski > yasam_riski_mean * 0.5 or yikilabilecek_bina > yikilabilecek_bina_mean * 0.5:
            kategori = 'İzleme Gerektiren Bölge'
            renk = 'gray'
        else:
            kategori = 'Düşük Riskli Bölge'
            renk = 'blue'

        popup_html = f'''
        <div style="font-family: Arial; font-size: 12px; ">
        <h3 style="color: {renk};"><strong>{kategori}</strong></h4>
        <strong>İlçe:</strong> {row['ilce_adi']}<br>
        <strong>Can Kaybı Riski:</strong> {yasam_riski}<br>
        <strong>Yıkılabilecek Bina Sayısı:</strong> {yikilabilecek_bina}<br>
        <strong>Doğalgaz Boru Hasarı:</strong> {row['dogalgaz_boru_hasari']}<br>
        <strong>Deprem Sonrası Barınma İhtiyacı:</strong> {row['gecici_barinma']}
        </div>
        '''
        iframe = IFrame(popup_html, width=250, height=150)

        popup = folium.Popup(iframe, max_width=250)

        # Marker ekle
        Marker(
            location=[row['Enlem'], row['Boylam']],
            popup=popup,
            icon=folium.Icon(color=renk),
            tooltip=row['ilce_adi']
        ).add_to(m)

    m.save('templates/map.html')
    return render_template('map.html')

@app.route('/risk_map')
def risk_map_show():
    return render_template("risk_map.html")


def create_bar_chart(data, x, y, title, barmode='group', stacked=False):
    """Creates a Plotly bar chart with given data."""
    fig = px.bar(data, x=x, y=y, title=title, barmode='stack' if stacked else barmode)

    # X ekseni etiketlerini döndürme ve düzenleme
    fig.update_layout(
        xaxis_tickangle=-45,  # Etiketleri 45 derece eğik yapar
        autosize = True,  # Grafik boyutunu otomatik olarak ayarla
        bargap = 0.3,  # Bar grupları arasındaki boşluk (0 ile 1 arasında)
        bargroupgap = 0.4  # Aynı grup içerisindeki barlar arasındaki boşluk
    )

    return fig


def create_scatter_chart(data, x, y, title, x_label, y_label):
    """Creates a Plotly scatter chart."""
    fig = px.scatter(data, x=x, y=y, title=title, labels={x: x_label, y: y_label})
    return fig

def create_pie_chart(data, values, names, title):
    """Creates a Plotly pie chart."""
    return px.pie(values=values, names=names, title=title)

def visualize_top_10_ilce(column, title):
    """Generates bar chart for the top 10 districts in a specified column."""
    top_ilce = grouped_df[['ilce_adi', column]].nlargest(10, column)
    return create_bar_chart(top_ilce, x='ilce_adi', y=column, title=f"En Yüksek 10 İlçe - {title}")


def altyapi_hasari_grafik():
    """Visualizes total infrastructure damage by district."""
    altyapi_columns = ['dogalgaz_boru_hasari', 'icme_suyu_boru_hasari', 'atik_su_boru_hasari']
    altyapi_hasari = grouped_df[['ilce_adi'] + altyapi_columns]
    return create_bar_chart(altyapi_hasari, x='ilce_adi', y=altyapi_columns, title='İlçelere Göre Altyapı Hasarları', stacked=True)

def bina_ve_altyapi_karsilastirma():
    """Compares building and infrastructure damage using bar and line charts."""
    # Total building damage
    bina_hasarlari = grouped_df[['cok_agir_hasarli_bina_sayisi', 'agir_hasarli_bina_sayisi',
                                 'orta_hasarli_bina_sayisi', 'hafif_hasarli_bina_sayisi']].sum(axis=1)

    altyapi_hasarlari = grouped_df[['dogalgaz_boru_hasari', 'icme_suyu_boru_hasari', 'atik_su_boru_hasari']].sum(axis=1)

    fig = go.Figure()
    fig.add_trace(go.Bar(x=grouped_df['ilce_adi'], y=bina_hasarlari, name='Toplam Bina Hasarı', marker_color='red'))
    fig.add_trace(go.Scatter(x=grouped_df['ilce_adi'], y=altyapi_hasarlari, name='Toplam Altyapı Hasarı', mode='lines+markers', yaxis='y2', marker=dict(color='blue')))

    fig.update_layout(
        title='Bina Hasarlarının Altyapı Hasarına Etkisi',
        xaxis_title='İlçe',
        yaxis_title='Bina Hasarı',
        yaxis2=dict(title='Altyapı Hasarı', overlaying='y', side='right'),
        template='plotly_white',
        showlegend=True
    )
    return fig

def bina_hasar_dagilimi():
    """Visualizes the distribution of building damage by district."""
    damage_columns = ['cok_agir_hasarli_bina_sayisi', 'agir_hasarli_bina_sayisi', 'orta_hasarli_bina_sayisi', 'hafif_hasarli_bina_sayisi']
    return create_bar_chart(grouped_df, x='ilce_adi', y=damage_columns, title='İlçelere Göre Bina Hasar Dağılımı', stacked=True)

def can_kaybi_ve_yarali_karsilastirma():
    """Compares death and injury counts across districts."""
    injury_columns = ['can_kaybi_sayisi', 'agir_yarali_sayisi', 'hastanede_tedavi_sayisi', 'hafif_yarali_sayisi']
    return create_bar_chart(grouped_df, x='ilce_adi', y=injury_columns, title='İlçelere Göre Can Kaybı ve Yaralı Sayısı')

def hasar_cankaybi():
    """Shows correlation between heavily damaged buildings and casualties."""
    return create_scatter_chart(df, 'cok_agir_hasarli_bina_sayisi', 'can_kaybi_sayisi', 'Çok Ağır Hasarlı Bina Sayısı ve Can Kaybı İlişkisi', 'Çok Ağır Hasarlı Bina Sayısı', 'Can Kaybı Sayısı')

def bina_hasar_turleri_pie():
    """Shows the distribution of different building damage types."""
    hasar_turleri = grouped_df[['cok_agir_hasarli_bina_sayisi', 'agir_hasarli_bina_sayisi', 'orta_hasarli_bina_sayisi', 'hafif_hasarli_bina_sayisi']].sum()
    return create_pie_chart(hasar_turleri, values=hasar_turleri, names=['Çok Ağır', 'Ağır', 'Orta', 'Hafif'], title='Bina Hasar Türlerinin Dağılımı')

def yasam_riski_pie():
    """Visualizes the distribution of casualties and injuries."""
    yasam_riski = grouped_df[['can_kaybi_sayisi', 'agir_yarali_sayisi', 'hafif_yarali_sayisi']].sum()
    return create_pie_chart(yasam_riski, values=yasam_riski, names=['Can Kaybı', 'Ağır Yaralı', 'Hafif Yaralı'], title='Can Kaybı ve Yaralı Dağılımı')

# Hafif hasarlı bina sayısı ve orta hasarlı bina sayısı için ilişkiyi gösteren fonksiyon
def hafif_ve_orta_hasarli_bina_karsilastirma():
    fig = px.scatter(df,
                     x='hafif_hasarli_bina_sayisi',
                     y='orta_hasarli_bina_sayisi',
                     title='Hafif Hasarlı Bina Sayısı ve Orta Hasarlı Bina Sayısı İlişkisi',
                     labels={'hafif_hasarli_bina_sayisi': 'Hafif Hasarlı Bina Sayısı',
                             'orta_hasarli_bina_sayisi': 'Orta Hasarlı Bina Sayısı'},
                     )  # Doğrusal regresyon çizgisi ekleme

    fig.update_layout(
        xaxis_title='Hafif Hasarlı Bina Sayısı',
        yaxis_title='Orta Hasarlı Bina Sayısı',
        template='plotly_white'
    )
    return fig

@app.route('/data_analysis')
def data_analysis():
    fields = {
        'cok_agir_hasarli_bina_sayisi': 'Çok Ağır Hasarlı Bina Sayısı',
        'agir_hasarli_bina_sayisi': 'Ağır Hasarlı Bina Sayısı',
        'orta_hasarli_bina_sayisi': 'Orta Hasarlı Bina Sayısı',
        'hafif_hasarli_bina_sayisi': 'Hafif Hasarlı Bina Sayısı',
        'can_kaybi_sayisi': 'Can Kaybı Sayısı',
        'agir_yarali_sayisi': 'Ağır Yaralı Sayısı',
        'hastanede_tedavi_sayisi': 'Hastanede Tedavi Edilen Sayısı',
        'hafif_yarali_sayisi': 'Hafif Yaralı Sayısı',
        'dogalgaz_boru_hasari': 'Doğal Gaz Boru Hasarı',
        'icme_suyu_boru_hasari': 'İçme Suyu Boru Hasarı',
        'atik_su_boru_hasari': 'Atık Su Boru Hasarı',
        'gecici_barinma': 'Geçici Barınma Sayısı'
    }

    grafikler = {field: visualize_top_10_ilce(field, label) for field, label in fields.items()}


    # Diğer fonksiyon çağrılarını ekleyelim
    grafikler.update({
        'altyapi_hasari_grafik': altyapi_hasari_grafik(),
        'bina_ve_altyapi_karsilastirma': bina_ve_altyapi_karsilastirma(),
        'bina_hasar_dagilimi': bina_hasar_dagilimi(),
        'can_kaybi_ve_yarali_karsilastirma': can_kaybi_ve_yarali_karsilastirma(),
        'hasar_cankaybi': hasar_cankaybi(),
        'bina_hasar_turleri_pie': bina_hasar_turleri_pie(),
        'yasam_riski_pie': yasam_riski_pie(),
        'hafif_ve_orta_hasarli_bina_karsilastirma': hafif_ve_orta_hasarli_bina_karsilastirma()
    })
    grafikler_json = {k: json.dumps(v, cls=plotly.utils.PlotlyJSONEncoder) for k, v in grafikler.items()}
    return render_template('data_analysis.html', grafikler=grafikler_json)


@app.route('/deprem_hazırlık')
def deprem_hazırlık():
    return render_template("deprem_hazırlık.html")

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static/images'), 'favicon.ico', mimetype='image/vnd.microsoft.icon')

if __name__ == '__main__':
    app.run(debug=True)
