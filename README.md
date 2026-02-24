## Reviews Translator 📚

Artık bazı değişkenlerin customer satisfaction üzerindeki etkisine dair ilk anlayışımıza sahibiz. Özellikle, review score’un, order delivery süresinin uzunluğundan olumsuz etkilendiği görülüyor.

Ancak kantitatif analiz tek bilgi kaynağımız değil. Yazılı review içeriğine de erişimimiz var!

Yeni bir dataset keşfederken iyi bir uygulama, her zaman rastgele bazı gözlemler seçmek ve onlar hakkında elimizde ne varsa keşfetmektir.

Nicel bulgularımızı, customers tarafından yazılan review’ların nitel (qualitative) analiziyle ilişkilendirelim.

### Exercise

- Python library [google-trans-new](https://pypi.org/project/google-trans-new/) kullanarak, 1-yıldızlı review’lardan rastgele seçilmiş 100 tanesini Portekizce’den İngilizce’ye çeviren bir Python script implement edin.
- ⚠️ **100.000 yorumun tamamını çevirmeyin, yoksa sınıfın tamamı ücretsiz API translator’lardan geçici olarak ban yiyebilir**
- Bu trendler, önceki bulgularınızla benzer mi?
- Hangi diğer trendleri ortaya çıkarıyorsunuz ve daha fazla keşfetmek istiyorsunuz?

Hints:
- Dokümantasyonu okuyup API’yi kendi başınıza çalıştırmayı deneyin – 10 satırdan fazla kod olmayacak
- Yeni bir notebook oluşturmakta ya da direkt olarak favori code editor’ınızda kod yazmakta özgürsünüz


## Qualitative Insights from 1-Star Reviews
Using `deep-translator`, we sampled and translated 1-star reviews from Portuguese to English. Our qualitative analysis revealed three main themes:
1. **Logistics & Delays:** Confirms our quantitative finding that `wait_time` is a major issue (e.g., "It's been almost a month...").
2. **Wrong/Missing Products (New Hypothesis):** Many customers received completely different or incomplete items, indicating severe seller-side quality control issues.
3. **Poor Customer Service:** Customers often leave 1-star reviews because they cannot get a response from sellers for refunds or cancellations.
