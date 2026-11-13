# Kick AI Co-Streamer

Windows üzerinde yerel çalışan, Kick sohbetindeki mesajları resmî Kick Events API webhook'u ile alan ve seçtiği mesajları Azure Türkçe Neural TTS ile sesli yanıtlayan bir Python uygulaması.

Uygulama yayını başlatmaz veya durdurmaz; OBS API'sine bağlanmaz; kategori, moderatör veya film oynatmasını değiştirmez. Kick'e sohbet mesajı da göndermez. Kontrol paneli `127.0.0.1` üzerinde, Kick webhook'u ise ayrı ve minimal bir portta çalışır.

## Kick entegrasyonunun sınırları

Kick'in güncel, belgelenmiş sohbet okuma yolu `chat.message.sent` olayı için webhook aboneliğidir. Chat API uç noktası mesaj yazma/silme içindir; bu uygulama onları çağırmaz. OAuth 2.1 PKCE ile yalnızca `user:read` ve `events:subscribe` izinlerini ister. Mesajları almak için uygulamanın webhook adresi Kick sunucularından genel internet üzerinden erişilebilir olmalıdır. Yalnızca port `8001`'i tünele açın; kontrol paneli portu `8000` yerelde kalır.

- [Kick Events API](https://docs.kick.com/events/introduction)
- [Webhook imza doğrulaması](https://docs.kick.com/events/webhook-security)
- [Kick OAuth kapsamları](https://docs.kick.com/scopes/scopes)
- [Kick Public API Swagger](https://api.kick.com/swagger/index.html)

Kick webhook'u uygulama Developer ayarlarından açılmalıdır. Hızlı tünellerin adresi değişirse Developer ayarındaki webhook adresini de güncelleyin. Kalıcı bir tünel adresi günlük kullanımda daha rahattır. Uygulama webhook imzasını Kick'in her zaman güncellediği public key ile doğrular; imza geçersiz veya eskiyse olay işlenmez.

## Gereksinimler

- Windows 10/11 ve Python 3.12 (64-bit)
- Kick Developer uygulaması, Client ID ve Client Secret
- OpenAI API anahtarı ve kullanılabilir bir model
- Azure AI Speech kaynağı, anahtarı ve bölgesi
- Ayrı OBS sesi için isteğe bağlı sanal ses aygıtı (VB-CABLE önerilir)
- Kick webhook portu `8001`'i internete ulaştıran bir tünel

OpenAI ve Azure kullanımı sağlayıcı ücretlerine ve hesap kotalarına tabidir. API anahtarlarını yalnızca `.env` içine koyun; repoya eklemeyin.

## Kurulum

PowerShell'de proje klasörüne gidin:

```powershell
cd C:\YayınBot\kick_ai_streamer
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
Copy-Item .env.example .env
```

Python Launcher `py` kurulu Python'ı bulamazsa, ilk satır yerine Python 3.12'nin tam yolunu kullanın; kullanıcı kurulumu için çoğunlukla `& "$env:LOCALAPPDATA\Programs\Python\Python312\python.exe" -m venv .venv` olur.

`.env` dosyasına Kick, OpenAI ve Azure bilgilerinizi girin. Azure portalında bir Speech kaynağı açıp **Keys and Endpoint** bölümündeki anahtarı ve bölgeyi kullanın. Varsayılan Türkçe kadın sesi `tr-TR-EmelNeural`'dır.

## Kick uygulaması ve webhook

1. [Kick Developer](https://dev.kick.com/) hesabında bir uygulama oluşturun. Uygulamanın OAuth Redirect URL listesine `http://localhost:8000/kick/callback` adresini aynen ekleyin. Kick'in belgeleri yerel yönlendirme için `localhost` kullanımını önerir; `127.0.0.1` kullanırsanız uygulama OAuth URL'sine belgelenen uyumluluk parametresini ekler.
2. Uygulama ayarlarında webhook teslimini açın. Uygulama için herkese açık webhook URL'si Kick Developer sayfasında tanımlanır; URL `KICK_WEBHOOK_PATH` ile aynı yola sonlanmalıdır.
3. Bir tünel aracıyla yalnızca webhook dinleyicisinin portunu açın. Örnekler:

   ```powershell
   ngrok http 8001
   ```

   veya:

   ```powershell
   cloudflared tunnel --url http://localhost:8001
   ```

   Tünelin HTTPS adresine `/kick/webhook` ekleyin ve aynı adresi hem Kick Developer uygulamasındaki webhook alanına hem `.env` içindeki `KICK_WEBHOOK_PUBLIC_URL` değerine yazın. `KICK_WEBHOOK_PUBLIC_URL` tanılama panelinde gösterilir; Kick ayarını programatik olarak değiştirmez.
4. Uygulamayı başlatın:

   ```powershell
   python main.py
   ```

5. Tarayıcıda `http://localhost:8000` sayfasını açın. **Kick hesabını bağla** düğmesinden izin verin. OAuth penceresi `user:read events:subscribe` izinlerini gösterir; yetkilendirmenin ardından uygulama `chat.message.sent` aboneliğini oluşturur.
6. OpenAI bağlantısını kontrol edin, ses aygıtını seçin, sesi deneyin ve **Asistanı başlat** düğmesine basın. Uygulamayı ve tüneli yayın boyunca açık tutun.

OAuth tokenları Windows Credential Manager üzerinden `keyring` ile saklanır. Keyring kullanılamıyorsa uygulama tokenı diske yazmaz; yeniden başlatma sonrasında Kick'e tekrar bağlanın.

## OBS'te ayrı AI sesi

1. İsteğe bağlı olarak VB-CABLE kurun. Dashboard ses çıkışında `CABLE Input (VB-Audio Virtual Cable)` aygıtını seçin. Bu, AI sesini Windows varsayılan film/yayın sesinden ayırır.
2. OBS'te **Kaynaklar → + → Ses Girişi Yakalama** ekleyin ve aygıt olarak `CABLE Output (VB-Audio Virtual Cable)` seçin.
3. OBS mikserinde bu kaynak için AI ses seviyesini ayrı ayarlayın. Aynı sanal aygıtı OBS Desktop Audio olarak da yakalıyorsanız çift sesi önlemek için Desktop Audio ayarınızı gözden geçirin.

Uygulama OBS WebSocket, OBS API veya yayın ayarlarına erişmez. Sesi seçilen yerel çıkış aygıtına verir; OBS'teki kaynağı kullanıcı oluşturur.

## Kontroller ve ayarlar

Dashboard; bağlantıları, webhook'un son alınma zamanını, son sohbet mesajlarını, Mira'nın seçtiği mesajları, yanıtları ve konuşma durumunu gösterir. Asistanı durdurmak bekleyen AI işlerini ve sesleri siler. Acil sessize alma, oynatmayı hemen keser ve ses kuyruğunu boşaltır. Ses seviyesi ve konuşma hızı çalışma anında değişir; Kick yanıt aralığı ve filtreler `.env` üzerinden yapılandırılır.

Önemli `.env` değerleri:

| Ayar | Varsayılan | Açıklama |
|---|---:|---|
| `RESPONSE_COOLDOWN_SECONDS` | `18` | İki AI yanıtı arasındaki minimum süre |
| `MAX_RESPONSES_PER_MINUTE` | `3` | Dakikadaki üst sınır |
| `USER_COOLDOWN_SECONDS` | `90` | Aynı izleyicinin yeniden seçilme aralığı |
| `MIN_IMPORTANCE_SCORE` | `24` | Aday mesaj için minimum yerel önem puanı |
| `MESSAGE_BATCH_SECONDS` | `2.5` | Sohbet mesajlarını birlikte değerlendirme aralığı |
| `SPONTANEOUS_MIN_INTERVAL_SECONDS` | `240` | Spontane yorumların değerlendirilebileceği minimum aralık |
| `SPONTANEOUS_MIN_MESSAGES` | `10` | Spontane yorum değerlendirmesi için gereken yeni mesaj sayısı |
| `MAX_MESSAGE_LENGTH` | `350` | Daha uzun mesajları eleme sınırı |
| `TTS_RATE_PERCENT` | `0` | Başlangıç konuşma hızı; panelden değiştirilebilir |
| `AUDIO_DEVICE_NAME` | boş | Başlangıç ses aygıtı adı; panelden değiştirilebilir |

Spam, link, tekrar, kullanıcı flood'u ve `BLOCKED_TERMS` kontrolleri yerelde uygulanır. Önce bu filtreler, sonra OpenAI önem ve bağlam kararını verir. Konuşulacak izleyici mesajı önce “`kullanıcı şöyle yazmış: ...`” biçiminde okunur, ardından AI yanıtı seslendirilir. Model görüntü girdisi almadığından belirli bir sahneyi görmüş gibi konuşmaması istenir.

## Veri ve sorun giderme

- Sohbet belleği, adaylar ve son yanıtlar yalnızca RAM'de tutulur; uygulama kapanınca silinir. Sohbet metinleri dosya loglarına yazılmaz.
- Seçili mesajlar ve kısa sohbet bağlamı yanıt oluşturmak için OpenAI'ye gönderilir. Ses metni Azure Speech'e gönderilir.
- `Kick yetki bekliyor`: Client ID/Secret ve Kick OAuth Redirect URL'sini kontrol edin.
- `chat.message.sent` alınmıyor: webhook URL'sinin tünel üzerinden `http://localhost:8001/kick/webhook`'a ulaştığını, Kick Developer'da webhook tesliminin etkin olduğunu ve `events:subscribe` iznini kontrol edin.
- İmza hatası: saat/tarih eşitlemesini, tünelin POST gövdesini değiştirmediğini ve `logs/assistant.log` dosyasını kontrol edin.
- OpenAI hatası: `/api/openai/check`, anahtar, model adı ve hesap erişimini kontrol edin.
- Ses yok: Dashboard'dan sesi deneyin; Azure Speech bölgesi ve anahtarını, Windows ses aygıtını ve OBS yakalama kaynağını doğrulayın. Windows'ta Azure Speech SDK için Microsoft Visual C++ Redistributable gerekebilir.

Uygulama hataları `logs/assistant.log` dosyasına döner. Gerçek Kick, OpenAI ve Azure hesaplarıyla canlı doğrulama için kullanıcıya ait developer uygulaması, anahtarlar, internet erişimi ve aktif tünel gerekir.

## Testler

```powershell
pytest -q
```

Testler yerel filtreleme, önem puanı, OAuth parametreleri, imza doğrulaması, AI seçimi ve sırayla ses kuyruğu davranışını sahte yanıtlarla kontrol eder; gerçek servis çağrısı veya fiziksel hoparlör kullanmaz.
